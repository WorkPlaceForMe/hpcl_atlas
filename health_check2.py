import os
import cv2
import time

from mysql2 import Mysql 

mysql = Mysql({"ip":'127.0.0.1', "user":'graymatics', "pwd":'graymatics', "db":os.environ['MYSQL_DB'], "table":""})
def get_stream_urls():
    urls = mysql.run_fetch('select rtsp, stream_out from cameras')
    urls2 = []
    for rtsp, out in urls:
        out = 'http://127.0.0.1' + out
        urls2.append([rtsp, out])
    return urls2

def isWorking(url):
    cap = cv2.VideoCapture(url)
    isHealthy = True
    for i in range(5):
        r, frame = cap.read()
        if frame is None: 
            isHealthy = False
            break
    cap.release()
    return isHealthy

def run():
    for urls in get_stream_urls():
        for url in urls:
            if not isWorking(url):
                print(f'BAD-{url}')
            else:
                print(f'GOOD-{url}')
    print('finish')


run()
