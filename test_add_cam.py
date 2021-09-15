import manage_camDB

algos = ['object classification', 'intrusion and loitering', 'vehicle speed and parking', 'crowd detection', 'motion detection', 'abandoned object']


for algo in algos:
    manage_camDB.add('rtsp://service:Siemens%23123@172.30.1.102:554', algo)
    manage_camDB.add('rtsp://service:Siemens%23123@172.30.2.34:554', algo)
