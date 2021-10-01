import sys
import MySQLdb
import traceback

IP = '127.0.0.1'
HTTP_PORT = 8090
RTSP_PORT = 8091
PUB_PORT_FIRST = 9000
TABLE1 = 'hpcl3.cameras'
TABLE2 = 'hpcl3.analytics'
TABLE3 = 'hpcl3.algo'
CAMERA_TOTAL = 80

def execute(cursor, cmd):
    try:
        cursor.execute(cmd)
    except:
        traceback.print_exc()
        print(cmd)
        sys.exit()

def create_cameras(table):
    db = MySQLdb.connect(IP, 'graymatics', 'graymatics')
    cursor = db.cursor()
    cursor.execute('create database if not exists {}'.format(table.split('.')[0]))
    cursor.execute('drop table if exists {}'.format(table))
    cmd = 'create table if not exists {} (id int(11), rtsp varchar(100), setup_id int(11), atlas_stream_port int(11), atlas_json_port int(11), cam_id int(11), stream_in varchar(100), stream_out varchar(100), stream_in2 varchar(100), stream_out2 varchar(100))'.format(table)
    execute(cursor, cmd)
    db.commit()

    #for i in range(CAMERA_TOTAL): 
    #    #stream_in = 'http://{}:{}/feed{}.ffm'.format(IP, HTTP_PORT, i+CAMERA_TOTAL)
    #    ##stream_out = 'http://{}:{}/stream{}.mjpeg'.format(IP, HTTP_PORT, i)
    #    #stream_out = ':{}/stream{}.mjpeg'.format(HTTP_PORT, i)
    #    setup_id = i//4
    #    atlas_stream_port = 7200 + setup_id
    #    atlas_json_port = 8070 + setup_id
    #    cam_id = i % 4
    #    pub_port = i + PUB_PORT_FIRST
    #    execute(cursor, "insert into {} values ({},'{}','{}',{},{})".format(table, i, setup_id, atlas_stream_port, atlas_json_port, cam_id, pub_port))
    #    execute(cursor, cmd)

    db.commit()
    cursor.close()
    db.close()

def create_analytics(table):
    db = MySQLdb.connect(IP, 'graymatics', 'graymatics')
    cursor = db.cursor()
    cursor.execute('create database if not exists {}'.format(table.split('.')[0]))
    cursor.execute('drop table if exists {}'.format(table))
    cmd = 'create table if not exists {} (analytics varchar(100), id int(11))'.format(table)
    execute(cursor, cmd)
    db.commit()

    ## mock
    #analytics = ['object classification', 
    #    'intrusion & loitering', 
    #    'vehicle speed & parking', 
    #    'crowd detection', 
    #    'motion detection', 
    #    'abandoned object']
    #for i in range(3):
    #    rtsp = 'videos/out2.avi'
    #    if i == 2:
    #        rtsp = 'videos/out1.avi'
    #    analytic = analytics[i%len(analytics)]
    #    execute(cursor, "insert into {} values ('{}', '{}', '{}')".format(table, rtsp, i, analytic))
    #    execute(cursor, cmd)

    db.commit()
    cursor.close()
    db.close()


def create_algo(table):
    db = MySQLdb.connect(IP, 'graymatics', 'graymatics')
    cursor = db.cursor()
    cursor.execute('create database if not exists {}'.format(table.split('.')[0]))
    cursor.execute('drop table if exists {}'.format(table))
    cmd = 'create table if not exists {} (analytics varchar(40), cmd varchar(100))'.format(table)
    print(cmd)
    execute(cursor, cmd)
    db.commit()

    id_ = '"object classification"'
    cmd = '"select * from obj_type order by time"'
    cursor.execute("insert into {} values ({}, {})".format(table, id_, cmd))
    
    id_ = '"intrusion and loitering"'
    cmd = '"select * from intrude_loiter order by time"'
    cursor.execute("insert into {} values ({}, {})".format(table, id_, cmd))
    
    id_ = '"vehicle speed and parking"'
    cmd = '"select * from speed_park order by time"'
    cursor.execute("insert into {} values ({}, {})".format(table, id_, cmd))
    
    id_ = '"crowd detection"'
    cmd = '"select * from crowd order by time"'
    cursor.execute("insert into {} values ({}, {})".format(table, id_, cmd))
    
    id_ = '"motion detection"'
    cmd = '"select * from motion order by time"'
    cursor.execute("insert into {} values ({}, {})".format(table, id_, cmd))
    
    id_ = '"abandoned object"'
    cmd = '"select * from aod order by time asc"'
    cursor.execute("insert into {} values ({}, {})".format(table, id_, cmd))

    db.commit()
    cursor.close()
    db.close()


if __name__ == '__main__':
    #create_cameras(TABLE1)
    #create_analytics(TABLE2)
    create_algo(TABLE3)

