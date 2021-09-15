import subprocess
from mysql2a import Mysql
import time
import shlex
import zmq
import os
import argparse

class Objectdemo:
    def __init__(self, db):
        self.table = 'hpcl3.camera_attr'
        mysql_args = {
            "ip":'127.0.0.1',
            "user":'graymatics',
            "pwd":'graymatics',
            "db":db,
            "table":'',
        }
        self.mysql = Mysql(mysql_args)
        self.process = []

    def get_id(self):
        cmd = 'select distinct(cameras.setup_id) from cameras'
        ids = self.mysql.run_fetch(cmd)
        return ids

    def start(self, dir_yolo, dir_src):
        self.stop_all2()
        ids = [i[0] for i in self.get_id()]
        for id in ids:
            cmd = "sudo ./objectdemo_main -graph {}config/graph{}.config -setup {}config/setup{}.config -disp 0".format(dir_src, id, dir_src, id)
            print(cmd)
            cmd = shlex.split(cmd)
            os.chdir(dir_yolo)
            p = subprocess.Popen(cmd)
            self.process.append(p)

    def stop_all(self):
        for p in self.process:
            p.terminate()

    def stop_all2(self):
        subprocess.run('pkill -f objectdemo_main', shell=True)
        time.sleep(3)


def main(dir_yolo, dir_src, db):
    port = 5560
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind('tcp://127.0.0.1:{}'.format(port))
    objectdemo = Objectdemo(db)
    
    while True:
        print('waiting for signal to start objectdemo')
        socket.recv()
        socket.send(b'')
        print('start object demo')
        objectdemo.start(dir_yolo, dir_src)
        time.sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--yolo')
    parser.add_argument('--src')
    parser.add_argument('--db')
    args = parser.parse_args()

    main(args.yolo, args.src, args.db)
