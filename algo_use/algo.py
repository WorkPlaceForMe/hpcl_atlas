from algo_use.point_in_poly import point_in_poly, point_in_poly_single
import time
from collections import deque, Counter
import math
import numpy as np
import cv2

from sklearn.cluster import KMeans
from sklearn.utils import shuffle

class ImgQuantizer:
    def __init__(self, img, n_color):
        self.w, self.h, d = tuple(img.shape)
        img = img.astype(np.float32) / 255
        image_array = np.reshape(img, (self.w * self.h, d))
        image_array_sample = shuffle(image_array, random_state=0)[:1000]
        self.kmeans = KMeans(n_clusters=n_color, random_state=0).fit(image_array_sample)

    def recreate_image(self, labels):
        image = np.zeros((self.w*self.h, 3), dtype=np.uint8)
        codebook = self.kmeans.cluster_centers_ * 255
        for i in range(codebook.shape[0]):
            image[labels==i] = codebook[i]
        img = image.reshape((self.w, self.h, 3))
        return img

    def do(self, img):
        img = img.astype(np.float32) / 255
        image_array = np.reshape(img, (self.w * self.h, 3))
        labels = self.kmeans.predict(image_array)
        img = self.recreate_image(labels)
        return img

def isPark(track, rois, speedThres, dt):
    x,y,w,h = track.attr['xywh']
    if 'park' not in track.dict:
        track.dict['park'] = 0
        track.dict['park_roi'] = 0
    if np.sum(track.move.dx**2)**.5 < speedThres:
        track.dict['park'] += dt

        if point_in_poly(x,y, rois):
            track.dict['park_roi'] += dt
    else:
        track.dict['park'] -= dt
        track.dict['park_roi'] -= dt
        track.dict['park'] = max(0, track.dict['park'])
        track.dict['park_roi'] = max(0, track.dict['park_roi'])

def count_pass(rois, tracks):                                                                                                                                            
    count = [0,0]                                                                                                                                                        
    for track in tracks:                                                                                                                                                 
        if track.miss > 0:
            continue
        x = track.attr['xywh'][0]                                                                                                                                        
        y = track.attr['xyxy'][3]                                                                                                                                        
        if 'pass_roi' not in track.dict:                                                                                                                                 
            track.dict['pass_roi'] = None                                                                                                                                
        if point_in_poly_single(x, y, rois[0]):                                                                                                                          
            if track.dict['pass_roi'] == 1:                                                                                                                              
                count[0] += 1                                                                                                                                            
            track.dict['pass_roi'] = 0                                                                                                                                   
        elif point_in_poly_single(x, y, rois[1]):                                                                                                                        
            if track.dict['pass_roi'] == 0:                                                                                                                              
                count[1] += 1                                                                                                                                            
            track.dict['pass_roi'] = 1                                                                                                                                   
    return count 

def drawArrow(frame, x1, dx, color):
    x1 = tuple(x1) # [x,y]
    x2 = tuple((np.array(x1) - np.array(dx)*3).astype(int))
    cv2.circle(frame, x1, 7, color, thickness=2, lineType=8, shift=0)
    cv2.line(frame, x1, x2, color, thickness=2)

def isParking(track, rois, thres):
    x1,y1,x2,y2 = track.attr['xyxy']
    x,y,w,h = track.attr['xywh']
    if point_in_poly(x,y2, rois):
        if 'parkTime1' in track.dict:
            if time.time() - track.dict['parkTime0'] > thres:
                return True
        else:
            track.dict['parkTime0'] = time.time()
    return False

def isParkingAuto(track, screenXY, part, thres):
    x1,y1,x2,y2 = track.attr['xyxy']
    x,y,w,h = track.attr['xywh']

    xMax, yMax = screenXY
    xZone = int(x/xMax * part)
    yZone = int(y/yMax * part)

    if 'parkTime' in track.dict:
        if track.dict['parkTime'][0] == (xZone, yZone):
            if time.time() - track.dict['parkTime'][1] > thres:
                return True
            else:
                return False
    track.dict['parkTime'] = [(xZone, yZone), time.time()]
    return False

def getVelocity(track, maxlen):
    #x1,y1,x2,y2 = track.attr['xyxy']
    x,y,w,h = track.attr['xywh']
    key = 'getVelocity'
    if key not in track.dict:
        track.dict[key] = deque(maxlen=maxlen)
    track.dict[key].append((x,y))

    if len(track.dict[key]) == maxlen and w > 0:
        x0,y0 = track.dict[key][0]
        x1,y1 = track.dict[key][-1]
        dx = x1 - x0
        dy = y1 - y0
        dist = (dx**2 + dy**2)**.5/w
        direct = math.degrees(math.atan2(dy,dx))
        return dist, int(direct)
    else:
        return (None, None)

def isLoiter(track, dist, distThres, timeThres, reset): # 5,3,5
    # update loiter status
    key = 'isLoiter'
    if key not in track.dict:
        track.dict[key] = [time.time(), 0] # loiter start time, non-loiter count
    if dist < distThres: # loiter
        pass
    elif track.dict[key][1] > reset: # reset loiter
        track.dict[key] = [time.time(), 0]
    else:
        track.dict[key][1] += 1

    # check if loiter
    if time.time() - track.dict[key][0] > timeThres:
        return True
    else:
        return False

def stabilize2(track):
    key = 'stabilize2'
    if key not in track.dict:
        track.dict[key] = track.attr['cls']
    return track.dict[key]
    
def stabilize(track, maxlen):
    key = 'stabilize'
    cls = track.attr['cls']

    if key not in track.dict:
        track.dict[key] = deque(maxlen=maxlen)
        
    if len(track.dict[key]) != maxlen:
        if cls not in {'motorbike'} or track.attr['conf']>.8:
            track.dict[key].append(cls)

    if len(track.dict[key]) == maxlen:
        track.dict[key].append(cls)
        return Counter(track.dict[key]).most_common(1)[0][0]
    else:
        return ''

def socialDist(tracks):
    tracks = [t for t in tracks if t.miss==0]
    if not tracks:
        return [],[]
    x,y,w,h = [],[],[],[]
    for track in tracks:
        x.append(track.attr['xywh'][0])
        y.append(track.attr['xywh'][1])
        w.append(track.attr['xywh'][2])
        h.append(track.attr['xywh'][3])

    x = np.array(x)[None,:]
    y0 = np.array(y)[None,:]
    dist = ((x-x.T)**2 + (y0-y0.T)**2)**.5

    w = np.array(w)
    w1 = np.broadcast_to(w[None,:], (len(w),len(w)))
    w2 = np.broadcast_to(w[:,None], (len(w),len(w)))
    w_min = np.amin(np.array([w1,w2]),axis=0)

    dist = dist/ w_min
    np.fill_diagonal(dist, 20000)
    distMin = np.amin(dist,axis=0)
    index = np.where(dist == distMin)

    for i, track in enumerate(tracks):
        track.dict['distMin'] = distMin[i]
    #return distMin, index


        
        
    




