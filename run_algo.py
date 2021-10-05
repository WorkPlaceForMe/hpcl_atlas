import cv2
import ffmpeg 
import time
from datetime import datetime
import traceback

from algo_use.tracking9 import Tracker
from algo_use import algo
from algo_use.motion import Motion
from algo_use.aod import AOD
from algo_use import milestone
from mysql2 import Mysql
from alarm_int import send_milestone

LOITER_TIME = 30
PARK_DURATION = 30
MYSQL_TABLES = ['aod', 'crowd', 'intrude_loiter', 'motion', 'obj_type', 'speed_park']
MILESTONE = True

def putTexts(img, texts, x1, y1, size=1, thick=1, color=(255,255,255)):
    for text1 in texts[::-1]:
        text1 = str(text1)
        (text_x, text_y) = cv2.getTextSize(text1, cv2.FONT_HERSHEY_SIMPLEX, fontScale=size, thickness=thick)[0]
        x1, y1 = int(x1), int(y1)
        cv2.rectangle(img, (x1,y1-text_y), (x1+text_x, y1), (0, 0, 0), -1)
        cv2.putText(img, text1, (x1,y1), cv2.FONT_HERSHEY_SIMPLEX, size, color, thick, cv2.LINE_AA)
        y1 -= text_y

def categorize(dets):
    dets_out = {'all':dets, 'person':[], 'vehicle':[]}
    for det in dets:
        det['text'] = []
        if det['cls'] == 'person':
            dets_out['person'].append(det)
        elif det['cls'] in {'car', 'truck', 'bus', 'motorbike'}:
            dets_out['vehicle'].append(det)
    return dets_out


algo_abbrev = {'object classification':'obj', 'crowd detection':'crowd', 'intrusion and loitering':'intrude', 'vehicle speed and parking':'speed', 'abandoned object':'aod', 'motion detection':'motion'}
def draw(dets, algos, frame):
    if 'object classification' in algos:
        for det in dets['all']:
            x1,y1,x2,y2 = det['xyxy']
            cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
            putTexts(frame, det['text'], x1,y1)
    else:
        if 'intrusion and loitering' in algos or 'crowd detection' in algos:
            for det in dets['person']:
                x1,y1,x2,y2 = det['xyxy']
                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
                putTexts(frame, det['text'], x1,y1)

        if 'vehicle speed and parking' in algos:
            for det in dets['vehicle']:
                x1,y1,x2,y2 = det['xyxy']
                cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
                putTexts(frame, det['text'], x1,y1)

    if 'crowd detection' in algos:
        texts = ['No. of people on screen now: {}'.format(len(dets['person']))]
        putTexts(frame, texts, 350, 600)

    date = timer.now.strftime('%Y-%m-%d %H:%M:%S')
    putTexts(frame, [', '.join([algo_abbrev[a] for a in algos]), date], 10, 60)

class Timer:
    def __init__(self):
        self.now = datetime.now()
        self.now_t = time.time()
        self.count = 0
        self.dt = 0
        self.last_sent = {}

    def update(self):
        self.now = datetime.now()
        self.count += 1
        self.dt = time.time() - self.now_t
        self.now_t = time.time()

    def time_pass(self, key, duration):
        if key not in self.last_sent:
            self.last_sent[key] = self.now_t
            return False
        elif self.now_t - self.last_sent[key] > duration:
            self.last_sent[key] = self.now_t
            return True
        else:
            return False

def loiter(timer, tracks, send_alert):
    for i, track in enumerate(tracks):
        if track.miss > 0:
            continue
        x,y,w,h = track.attr['xyxy']
        x1,y1,x2,y2 = track.attr['xyxy']

        if 'loiter' not in track.dict:
            track.dict['loiter'] = 0
        track.dict['loiter'] += timer.dt

        # intrude
        track.attr['text'].append('intrude')
        if 'alert_intrude' not in track.tag:
            track.tag.add('alert_intrude')
            send_alert('intrude_loiter', ['intrude', 0])

        # loiter
        if track.dict['loiter'] > LOITER_TIME:
            track.attr['text'].append('loiter')
            if 'alert_loiter' not in track.tag:
                track.tag.add('alert_loiter')
                send_alert('intrude_loiter', ['loiter', LOITER_TIME])

def speed(timer, tracks, send_alert):
    for i, track in enumerate(tracks):
        if track.miss > 0:
            continue
        x,y,w,h = track.attr['xyxy']
        x1,y1,x2,y2 = track.attr['xyxy']

        speed, _ = algo.getVelocity(track, 20)
        if speed is not None:
            speed = min(int(speed * 30), 70)
            track.attr['text'].append(str(speed) + "km/h")
            if 'alert_speed' not in track.tag:
                track.tag.add('alert_speed')
                send_alert('speed_park', ['speed-km/h', speed])

            # parking
            if speed < 2:
                if 'park' not in track.dict:
                    track.dict['park'] = 0
                track.dict['park'] += timer.dt
                if track.dict['park'] > PARK_DURATION:
                    track.attr['text'].append('parking')
                    if 'alert_park' not in track.tag:
                        track.tag.add('alert_park')
                        send_alert('speed_park', ['park-s', PARK_DURATION])
            else:
                track.dict['park'] = 0


motion = Motion()
def run_motion(timer, frame, send_alert):
    dets = motion.detect(frame)
    if timer.time_pass('motion', 30) and dets:
        send_alert('motion', [])

    for det in dets:
        x1,y1,x2,y2 = det['xyxy']
        cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
        putTexts(frame, det['text'], x1,y1)


aod = AOD([])
def run_aod(timer, frame, det_person, send_alert):
    dets = aod.detect(frame, det_person, timer.now_t)
    if timer.time_pass('aod', 30) and dets:
        send_alert('aod', [aod.minAODduration])

    for det in dets:
        x1,y1,x2,y2 = det['xyxy']
        cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0), 2)
        putTexts(frame, det['text'], x1,y1)


timer = Timer()
ms = milestone.Milestone('0.tcp.ap.ngrok.io:16480', 'graymatics', 'graymatics')
event_ip = 'http://127.0.0.1:9090'
client_ip = 'http://127.0.0.1:8090'

class OutStream:
    def __init__(self, outxy, output_path):
        self.output_path = output_path
        self.outxy = outxy
        self._start()

    def _start(self):
        self.process = (
            ffmpeg
            .input('pipe:', format='rawvideo', pix_fmt='bgr24', s='{}x{}'.format(self.outxy[0], self.outxy[1]))
            .output('{}'.format(self.output_path))
            .overwrite_output()
            .global_args('-loglevel', 'error')
            .run_async(pipe_stdin=True))

    def write(self, frame):
        try:
            frame = cv2.resize(frame, self.outxy)
            self.process.stdin.write(frame)
        except Exception:
            print('restart out stream')
            self.process.stdin.close()
            self._start()

class Algos:
    def __init__(self, id_, rtsp, algos, stream_in, stream_in2):
        self.id = id_
        self.rtsp = rtsp
        self.algos = algos
        #self.stream_in = stream_in
        self.outxy = (640,480)
        self.process2 = OutStream(self.outxy, stream_in)
        self.process3 = OutStream(self.outxy, stream_in2)
        #self.process2 = (
        #    ffmpeg
        #    .input('pipe:', format='rawvideo', pix_fmt='bgr24', s='{}x{}'.format(self.outxy[0], self.outxy[1]))
        #    .output('{}'.format(stream_in))
        #    .overwrite_output()
        #    .global_args('-loglevel', 'error')
        #    .run_async(pipe_stdin=True))
        #self.process3 = (
        #    ffmpeg
        #    .input('pipe:', format='rawvideo', pix_fmt='bgr24', s='{}x{}'.format(self.outxy[0], self.outxy[1]))
        #    .output('{}'.format(stream_in2))
        #    .overwrite_output()
        #    .global_args('-loglevel', 'error')
        #    .run_async(pipe_stdin=True))
        self.yoloTrackers = {}
        self.yoloTrackers['person'] = Tracker((1280,720))
        self.yoloTrackers['vehicle'] = Tracker((1280,720))
        self.mysql = Mysql({"ip":'127.0.0.1', "user":'graymatics', "pwd":'graymatics', "db":'hpcl', 'table':''})
        for a in MYSQL_TABLES:
            self.mysql.add_table(a)
    
    def send_alert(self, table, values):
        values0 = [self.rtsp, timer.now.strftime('%Y-%m-%d %H:%M:%S')]
        values0.extend(values)
        self.mysql.insert_fast(table, values0)

        if MILESTONE:
            #ms.send_alarm(event_ip, client_ip, self.id, table)
            cam_ip = self.rtsp.split('@')[-1].split(':')[0]
            send_milestone(table, cam_ip)

    def run(self, frame, dets):
        timer.update()
        dets = categorize(dets)
        tracks = {}
        tracks['person'] = self.yoloTrackers['person'].update(dets['person'])
        tracks['vehicle'] = self.yoloTrackers['vehicle'].update(dets['vehicle'])

        if 'object classification' in self.algos:
            for det in dets['all']:
                det['text'].append(det['cls'])
                if timer.time_pass('object classification', 30):
                    self.send_alert('obj_type', [det['cls']])

        if 'crowd detection' in self.algos:
            if timer.time_pass('crowd', 30):
                self.send_alert('crowd', [len(dets['person'])])

        if 'intrusion and loitering' in self.algos:
            loiter(timer, tracks['person'], self.send_alert)

        if 'vehicle speed and parking' in self.algos:
            speed(timer, tracks['vehicle'], self.send_alert)

        if 'abandoned object' in self.algos:
            run_aod(timer, frame, dets['person'], self.send_alert)

        if 'motion detection' in self.algos:
            run_motion(timer, frame, self.send_alert)

        # stream
        draw(dets, self.algos, frame)
        frame = cv2.resize(frame, self.outxy)
        self.process2.write(frame)
        self.process3.write(frame)

        if timer.time_pass('commit', 30):
            for table in self.mysql.values:
                self.mysql.commit_insert(table)



