import os
import cv2
from mysql2 import Mysql

IP = '127.0.0.1'
HTTP_PORT = 8090
PUB_PORT_FIRST = 9000
CAMERA_TOTAL = 80

mysql_args = {
    "ip":'127.0.0.1',
    "user":'graymatics',
    "pwd":'graymatics',
    "db":os.environ['MYSQL_DB'],
    "table":"",
    #"column": [
    #    ['rtsp','varchar(100)'],
    #    ['analytics','varchar(100)'],
    #    ['id','int(11)'],
    #    ['stream_in','varchar(100)'],
    #    ['stream_out','varchar(100)'],
    #    ['pub_port','int(11)']
    #    ]
    }
mysql = Mysql(mysql_args)

# ===========================================================================================

def get_all_cams(rtsp, analytic):
    cams = get_cams_from_db()
    if rtsp is not None:
        cams.append((rtsp, analytic))
    return format0(cams)

def get_cams_from_db():
    cmd = 'select cameras.rtsp, analytics.analytics from cameras inner join analytics where cameras.id = analytics.id'
    cams = mysql.run_fetch(cmd)
    return list(cams)

def format0(cams):
    cams_out = {}
    for rtsp, analytic in cams:
        if rtsp not in cams_out:
            cams_out[rtsp] = {'algo':[analytic]}
        elif analytic not in cams_out[rtsp]['algo']:
            cams_out[rtsp]['algo'].append(analytic)
    return cams_out

def clear_db():
    mysql.run(f'delete from cameras')
    mysql.run(f'delete from analytics')

def remove_bad_rtsp(cams):
    for rtsp, value in cams.copy().items():
        cap = cv2.VideoCapture(rtsp)
        if not cap.isOpened():
            del cams[rtsp]
            print(f'bad rtsp {rtsp}')

def add_id_and_ports(cams):
    #stream_count = 0
    for i, rtsp in enumerate(cams):
        setup_id = i//4
        cams[rtsp]['id'] = i
        cams[rtsp]['setup_id'] = setup_id
        cams[rtsp]['atlas_stream_port'] = 7200 + setup_id
        cams[rtsp]['atlas_json_port'] = 8070 + setup_id
        cams[rtsp]['cam_id'] = i % 4
        #cams[rtsp]['pub_port'] = i + PUB_PORT_FIRST
        cams[rtsp]['stream_in'] = 'http://{}:{}/feed{}.ffm'.format(IP, HTTP_PORT, i+CAMERA_TOTAL)
        cams[rtsp]['stream_out'] = ':{}/stream{}.mjpeg'.format(HTTP_PORT, i)

        #cams[rtsp]['stream_in'] = []
        #cams[rtsp]['stream_out'] = []
        #for algo in cams[rtsp]['algo']:
        #    cams[rtsp]['stream_in'].append('http://{}:{}/feed{}.ffm'.format(IP, HTTP_PORT, stream_count+CAMERA_TOTAL))
        #    cams[rtsp]['stream_out'].append(':{}/stream{}.mjpeg'.format(HTTP_PORT, stream_count))
        #    stream_count += 1

def add_to_camera_db(cams):
    if not cams:
        return 
    mysql.add_table('cameras')
    mysql.add_table('analytics')
    for rtsp, v in cams.items():
        res = v['id'], rtsp, v['setup_id'], v['atlas_stream_port'], v['atlas_json_port'], v['cam_id'], v['stream_in'], v['stream_out']
        mysql.insert_fast('cameras', res)
    mysql.commit_insert('cameras')

    for rtsp, v in cams.items():
        for i, algo in enumerate(v['algo']):
            res = v['algo'][i], v['id']
            mysql.insert_fast('analytics', res)
    mysql.commit_insert('analytics')

def add(rtsp, analytics):
    cams = get_all_cams(rtsp, analytics)
    clear_db()
    #remove_bad_rtsp(cams)
    add_id_and_ports(cams)
    add_to_camera_db(cams)

# ===========================================================================================

def remove_camera(user_rtsp, user_analytic):
    #user_analytic = user_analytic.replace('&amp;','&')
    #mysql.run("DELETE FROM cameras WHERE rtsp='{}' AND analytics='{}'".format(user_rtsp, user_analytic))
    print(user_rtsp)
    mysql.run(f"delete analytics from analytics inner join cameras where cameras.id = analytics.id and rtsp='{user_rtsp}' and analytics='{user_analytic}'")
    mysql.run('delete from cameras where id not in (select id from analytics)')


if __name__ == '__main__':
    add(None, None)
#    add('rtsp://123', 'algo1')
#    add('rtsp://123', 'algo2')
#    add('rtsp://1234', 'algo2')
