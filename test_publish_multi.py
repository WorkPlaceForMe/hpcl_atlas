from threading import Thread
import socket
import sys
import pycurl
import json
import numpy as np
import math 
import time
#import cv2

from run_algo import Algos

BASE_WIDTH = 1280
BASE_HEIGHT = 720
    
CLASSES=["person","bicycle","car","motorbike","aeroplane","bus","train","truck","boat","trafficlight","firehydrant","stopsign","parkingmeter","bench","bird","cat","dog","horse","sheep","cow","elephant","bear","zebra","giraffe","backpack","umbrella","handbag","tie","suitcase","frisbee","skis","snowboard","sportsball","kite","baseballbat","baseballglove","skateboard","surfboard","tennisracket","bottle","wineglass","cup","fork","knife","spoon","bowl","banana","apple","sandwich","orange","broccoli","carrot","hotdog","pizza","donut","cake","chair","sofa","pottedplant","bed","diningtable","toilet","tvmonitor","laptop","mouse","remote","keyboard","cellphone","microwave","oven","toaster","sink","refrigerator","book","clock","vase","scissors","teddybear","hairdrier","toothbrush"]
    
def socketToNumpy(cameraFeed, sockData):
    k = 3
    j = cameraFeed.shape[1]
    i = cameraFeed.shape[0]
    sockData = np.fromstring(sockData, np.uint8)
    cameraFeed = np.tile(sockData, 1).reshape((i, j, k))
    return cameraFeed
    
class VideoStream:
    def __init__(self, host, port, frameShape):
        self.connect(host, port)
        self.shape = frameShape
        self.cameraFeed = np.zeros(self.shape, np.uint8)
        self.port = port

    def connect(self, host, port):
        for res in socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
            self.af, self.socktype, self.proto, self.canonname, self.sa = res
            print(res)
            try:
                self.s = socket.socket(self.af, self.socktype, self.proto)
            except socket.error as msg:
                print(msg)
                self.s = None
                continue
            try:
                self.s.bind(self.sa)
                self.s.listen(1)
            except socket.error as msg:
                print(msg)
                self.s.close()
                self.s = None
                continue
            break
        if self.s is None:
            print('Could not open socket')
            sys.exit(1)
        self.conn, self.addr = self.s.accept()
        print('Connected by', self.addr)
        print(self.conn)

    def start(self):
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()

    def update(self):
        while True:
            sockData = b''
            buffSize = self.cameraFeed.size
            broken = False
            while buffSize > 0:
                nbytes = self.conn.recv(buffSize)
                if not nbytes: 
                    broken = True
                    print(f'video stream from atlas stopped - {self.port}')
                    break
                sockData += nbytes
                buffSize -= len(nbytes)

            if broken:
                self.conn.close()
                break
            else:
                self.cameraFeed = socketToNumpy(self.cameraFeed, sockData)

    def update2(self):
        while True:
            sockData = b''
            buffSize = self.cameraFeed.size
            broken = False
            while buffSize > 0:
                nbytes = self.conn.recv(buffSize)
                if not nbytes: 
                    broken = True
                    print(f'video stream from atlas stopped - {self.port}')
                    break
                sockData += nbytes
                buffSize -= len(nbytes)

            if broken:
                self.conn.close()
                break
            else:
                self.cameraFeed = socketToNumpy(self.cameraFeed, sockData)

    def read(self):
        return self.cameraFeed.copy()

class Frame_cropper:
    def __init__(self, CAMERA_NUMBER, BASE_WIDTH, BASE_HEIGHT):
        self.cam_num = self.get_cam_num(CAMERA_NUMBER)
        self.BASE_WIDTH = BASE_WIDTH
        self.BASE_HEIGHT = BASE_HEIGHT

    def get_shape(self):
        return self.BASE_WIDTH * self.cam_num[0], self.BASE_HEIGHT * self.cam_num[1]

    def get_cam_num(self, num): # num of frame on x, y axes
        if num in {1}:
            x = 1
        elif num in {2,3,4}:
            x = 2
        elif num in {5,6,9}:
            x = 3
        elif num in {7,8,10,11,12,13,14,15,16}:
            x = 4
        y = math.ceil(num/x)
        return x, y

    def get_position(self, idx):
        x = idx % self.cam_num[0]
        y = idx // self.cam_num[0]
        return x,y

    def get_left_top_coordinate(self, idx):
        x1, y1 = self.get_position(idx)
        x1 *= self.BASE_WIDTH
        y1 *= self.BASE_HEIGHT
        return x1, y1

    def crop(self, frame, idx):
        x1, y1 = self.get_left_top_coordinate(idx)
        x2 = x1 + self.BASE_WIDTH
        y2 = y1 + self.BASE_HEIGHT
        frame_crop = frame[y1:y2, x1:x2]
        frame_crop = frame_crop.astype(np.uint8)
        return frame_crop
    
#==============================================

def locs_to_dets(locs, idx):
    dets = []
    for loc in locs:
        det = {}
        det['conf'] = loc['conf'] 
        det['cls'] = CLASSES[int(loc['objID'])]

        pos = loc['pos']
        x1 = pos['ltx']
        y1 = pos['lty']
        x2 = pos['rbx']
        y2 = pos['rby']
        x = int((x1+x2)/2)
        y = int((y1+y2)/2)
        w = int(x2-x1)
        h = int(y2-y1)

        det['xywh'] = [x,y,w,h]
        det['xyxy'] = [x1,y1,x2,y2]
        dets.append(det)
    return dets
    
class Receiver:
    def __init__(self, cap, frame_cropper, algo_dict):
        self.cap = cap
        self.algo_dict = algo_dict
        self.frame_cropper = frame_cropper
    
    def on_receive(self, data):
        frame = self.cap.read()
        content = data.decode()
        length_content = len(content)
        json_list = []
        if length_content > 40:
            cams = content.split("&")
            for cam in cams:
                if "cam_id" in cam:
                    json_list.append(cam)
            
            for i, cam in enumerate(json_list): # splitting is incomplete, cam may not be dict
                try:
                    res = json.loads(cam)
                    idx = int(res["cam_id"])
                    locs = res['objs']
                    dets = locs_to_dets(locs, idx)
                    frame_crop = self.frame_cropper.crop(frame, idx)
                    self.algo_dict[idx]['algo'].run(frame_crop, dets)
                    #cv2.imshow('a', frame)
                    #cv2.waitKey(1)
                except:
                    pass


def create_algos(algo_dict):
    for cam_id, v in algo_dict.items():
        v['algo'] = Algos(v['id'], v['rtsp'], v['algo_names'], v['stream_in'])
    return algo_dict

def main(CAMERA_NUMBER, host, stream_port, json_port, algo_dict):
    STREAM_URL = f"localhost:{json_port}/"

    frame_cropper = Frame_cropper(CAMERA_NUMBER, BASE_WIDTH, BASE_HEIGHT)
    frame_width, frame_height = frame_cropper.get_shape()
    cap = VideoStream(host, stream_port, (frame_height, frame_width, 3))
    cap.start()
    algo_dict = create_algos(algo_dict)
    receiver = Receiver(cap, frame_cropper, algo_dict)

    conn = pycurl.Curl()
    conn.setopt(pycurl.URL, STREAM_URL)
    conn.setopt(pycurl.WRITEFUNCTION, receiver.on_receive)

    last_perform_time = time.time()
    print(f'starting loop to receive atlas {json_port}')
    while True:
        try:
            conn.perform()
            last_perform_time = time.time()
        except:
            if time.time() - last_perform_time > 30:
                print(f'disconnected: {stream_port} - {json_port}')
                last_perform_time = time.time()


if __name__ == "__main__":
    main(2, 'localhost', 7200, 8070, 9000)
