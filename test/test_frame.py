import socket
import cv2
import time
import numpy as np

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 7200        # The port used by the server

cap = cv2.VideoCapture('walk.mp4')
#r, frame = cap.read()
#print(frame.size)
#frame_bytes = frame.tobytes()
#print(len(frame_bytes))
#sockData = np.fromstring(frame_bytes, np.uint8) 
#print(sockData.shape)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        r, frame = cap.read()
        frame = np.tile(frame,(1,2,1))
        print(frame.shape)
        frame_bytes = frame.tobytes()
        s.sendall(frame_bytes)
        time.sleep(.1)
        #data = s.recv(1024)
