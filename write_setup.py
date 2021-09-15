import os
import glob
from mysql2 import Mysql
import generate_graph

MYSQL_DB = os.environ['MYSQL_DB']

class Writer:
    def __init__(self, filename):
        self.f = open(filename, 'w')

    def write_line(self, line):
        self.f.write(line)
        self.f.write('\n')

    def close(self):
        self.f.close()

def write_setup_single_chip(setup_info, paths):
    filename, device_id, graph_id, json_port, stream_port = setup_info
    writer = Writer(filename)
    writer.write_line("# Chip config")
    writer.write_line("device_id = {} # Use the device to run the program".format(device_id))
    writer.write_line("")
    writer.write_line("# Graph config")
    writer.write_line("graph_id = {}".format(graph_id))
    writer.write_line("")
    writer.write_line("# Python output port")
    writer.write_line("python = {}".format(stream_port))
    writer.write_line("")
    writer.write_line("# Json output port, http")
    writer.write_line("json = {}".format(json_port))
    writer.write_line("")
    writer.write_line("# Cam config")
    writer.write_line("used_cam_num = {} # Use top n cams in cam list".format(len(paths)))
    writer.write_line("")
    writer.write_line("# Cam list")

    for i, path in enumerate(paths):
        writer.write_line("cam{} = {}".format(i, path))
    writer.write_line("cam4 = ./C20_Final.264")
    writer.write_line("cam5 = ./C20_Final.264")
    writer.write_line("cam6 = ./C6_Final.264")
    writer.write_line("cam7 = ./C6_Final.264")
    writer.write_line("cam8 = ./C6_Final.264")
    writer.write_line("cam9 = ./C6_Final.264")
    writer.write_line("cam10 = ./C6_Final.264")
    writer.write_line("cam11 = ./C20_Final.264")
    writer.write_line("cam12 = ./C6_Final.264")
    writer.write_line("cam13 = ./C20_Final.264")
    writer.write_line("cam14 = ./C20_Final.264")
    writer.write_line("cam15 = ./C20_Final.264")
    writer.write_line("# rtsp://127.0.0.1:8554/test")

    writer.close()

def get_setup_info(dir0, num):
    filename = '{}setup{}.config'.format(dir0, num)
    device_id = num
    graph_id = 100 + num
    json_port = 8070 + num
    stream_port = 7200 + num
    return filename, device_id, graph_id, json_port, stream_port

def write_setup(dir0, input_paths):
    device_id = 0
    setup_files = []
    while input_paths:
        curr_paths, input_paths = input_paths[:4], input_paths[4:]
        setup_info = get_setup_info(dir0, device_id)
        device_id += 1
        write_setup_single_chip(setup_info, curr_paths)
        setup_files.append(setup_info[0])
    return setup_files

def get_camera_urls():
    mysql_args = {
        "ip":'127.0.0.1',
        "user":'graymatics',
        "pwd":'graymatics',
        "db":MYSQL_DB,
        "table":'cameras',
    }
    mysql = Mysql(mysql_args)
    cmd = 'select rtsp from cameras'
    urls = mysql.run_fetch(cmd)
    return([u[0] for u in urls])

def clear_dir(dir0):
    files = glob.glob(dir0 + '*')
    for f in files:
        os.remove(f)

def write_setup_main(dir0):
    clear_dir(dir0)
    urls = get_camera_urls()
    setup_files = write_setup(dir0, urls)
    for i, setup_filename in enumerate(setup_files):
        graph_filename = f'{dir0}graph{i}.config' 
        generate_graph.main(setup_filename, graph_filename)
    print(f'generated {setup_files}')
    return setup_files


if __name__ == '__main__':
    #paths = ['./C20_Final.264', './C6_Final.264', './C20_Final.264', './C6_Final.264']
    #paths_test = [f'{i}.264' for i in range(13)]
    write_setup_main('config/')
