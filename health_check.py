import os
import cv2
import time

from mysql2 import Mysql 

mysql = Mysql({"ip":'127.0.0.1', "user":'graymatics', "pwd":'graymatics', "db":os.environ['MYSQL_DB'], "table":""})
def get_stream_urls():
    urls = mysql.run_fetch('select stream_out from cameras')
    urls = ['http://127.0.0.1' + c[0] for c in urls]
    return urls

def isWorking(url):
    cap = cv2.VideoCapture(url)
    isHealthy = True
    for i in range(5):
        time.sleep(1)
        r, frame = cap.read()
        if frame is None: 
            print(f'unable to reach {url}')
            isHealthy = False
            break
    cap.release()
    return isHealthy

def run():
    for url in get_stream_urls():
        if not isWorking(url):
            return False
    return True




