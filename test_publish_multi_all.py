import os
import multiprocessing as mp

from mysql2 import Mysql
import test_publish_multi
import time


mysql_args = {
    "ip":'127.0.0.1',
    "user":'graymatics',
    "pwd":'graymatics',
    "db":os.environ['MYSQL_DB'],
    "table":'',
}
mysql = Mysql(mysql_args)

def get_stream_info():
    cmd = 'select id, rtsp, atlas_stream_port, atlas_json_port, cam_id, stream_in from cameras'
    urls = mysql.run_fetch(cmd)
    return([u for u in urls])

def get_algo_info(id_):
    cmd = f'select analytics from analytics where id={id_}'
    algo = mysql.run_fetch(cmd)
    return {a[0] for a in algo}

class Publisher:
    def __init__(self):
        self.processes = []

    def stop(self):
        for p in self.processes:
            p.terminate()
            time.sleep(2)
            print(f'kill')

    def run(self):
        self.stop()
        cameras = get_stream_info()
        while cameras:
            cameras_sub, cameras = cameras[:4], cameras[4:] # atlas process 4 streams at a time
            algo_dict = {}
            for camera in cameras_sub:
                id_, rtsp, stream_port, json_port, cam_id, stream_in = camera
                algo_dict[cam_id] = {}
                algo_dict[cam_id]['algo_names'] = get_algo_info(id_)
                algo_dict[cam_id]['rtsp'] = rtsp
                algo_dict[cam_id]['id'] = id_
                algo_dict[cam_id]['stream_in'] = stream_in
            
            print(f'starting process {json_port} - {stream_port}')
            p = mp.Process(target=test_publish_multi.main, args=(len(cameras_sub), 'localhost', stream_port, json_port, algo_dict))
            p.daemon = True
            p.start()
            self.processes.append(p)
            time.sleep(1)


if __name__ == '__main__':
    p = Publisher()
    p.run()
    time.sleep(1000)


