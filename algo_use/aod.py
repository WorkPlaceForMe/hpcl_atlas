import numpy as np
import cv2

from algo_use.tracking9 import Tracker

class AOD:
    def __init__(self, mask):
        self.bgSubtractor = cv2.createBackgroundSubtractorMOG2()
        self.bgSubtractor.setNMixtures(2) # increase to reduce detection
        self.bgSubtractor.setDetectShadows(True)
        self.bgSubtractor.setVarThreshold(200) # increase to reduce detection

        self.minAODSize = 100
        self.minAODduration = 300
        self.mask = mask

        self.lastTracks = []
        self.iniCount = 0
        self.iniCountRequired = 100
        self.frameShape = (320,180)
        self.frameShapeOriginal = None
        self.bgImg = None

        self.tracker = Tracker((1280,720), dist_thres=5)

    def isInitialized(self):
        if self.iniCount > self.iniCountRequired:
            return True
        else:
            self.iniCount += 1
            return False

    def removePeople(self, frame, yoloDets):
        for det in yoloDets:
            x1,y1,x2,y2 = self.resizeFromOriginal(det['xyxy'])
            frame[y1:y2,x1:x2] = self.bgImg[y1:y2,x1:x2] 

    def maskArea(self, frame):
        frame = frame.copy()
        for x1,y1,x2,y2 in self.mask:
            frame[y1:y2, x1:x2] = 0
        return frame

    def initializeBG(self, frame, frame0):
        self.bgSubtractor.apply(frame, learningRate=.01)
        if self.iniCount >= self.iniCountRequired:
            self.frameShapeOriginal = (frame0.shape[1], frame0.shape[0])
            self.bgImg = frame.copy()

    def compareBG_with(self, frame): 
        mask = self.bgSubtractor.apply(frame, learningRate=0)
        ret, mask = cv2.threshold(mask,200,255,cv2.THRESH_BINARY)
        kernel = np.ones((2,2), np.uint8)
        mask = cv2.dilate(mask, kernel, iterations=1)
        #mask = cv2.erode(mask, kernel, iterations=1)
        return mask

    def getDets(self, mask):
        aods = []
        try:
            _, cnts, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        except:
            cnts, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for i, cnt in enumerate(cnts):
            aodSize = cv2.contourArea(cnt)
            if aodSize > self.minAODSize:
                aod = {}
                x1,y1,w,h = cv2.boundingRect(cnt)
                x2 = x1 + w
                y2 = y1 + h
                x = int(x1 + w/2)
                y = int(y1 + h/2)
                aod['xyxy'] = [x1,y1,x2,y2]
                aod['xywh'] = [x,y,w,h]
                aod['size'] = aodSize

                x1 = int(max(0, x1-w*.1))
                y1 = int(max(0, y1-h*.1))
                x2 = int(min(mask.shape[1], x2+w*.1))
                y2 = int(min(mask.shape[0], y2+h*.1))
                aod['xyxy_enlarge'] = [x1,y1,x2,y2]
                aods.append(aod)
        return aods
    
    def resizeFromOriginal(self, xyxy):
        X, Y = self.frameShape
        X0, Y0 = self.frameShapeOriginal
        x1,y1,x2,y2 = xyxy

        x1 = int(x1/X0*X)
        y1 = int(y1/Y0*Y)
        x2 = int(x2/X0*X)
        y2 = int(y2/Y0*Y)
        return (x1,y1,x2,y2)

    def resizeToOriginal(self, xyxy):
        X, Y = self.frameShape
        X0, Y0 = self.frameShapeOriginal
        x1,y1,x2,y2 = xyxy

        x1 = int(x1/X*X0)
        y1 = int(y1/Y*Y0)
        x2 = int(x2/X*X0)
        y2 = int(y2/Y*Y0)
        return (x1,y1,x2,y2)

    def updateBG(self, frame, tracks):
        frameWithoutAOD = frame.copy()
        for track in tracks:
            #if 'alerted' not in track.tag:
            x1,y1,x2,y2 = track.attr['xyxy_enlarge']
            frameWithoutAOD[y1:y2,x1:x2] = self.bgImg[y1:y2,x1:x2] 
        self.bgImg = frameWithoutAOD
        self.bgSubtractor.apply(self.bgImg, learningRate=.01)
    
    def updateTrack(self, dets):
        X, Y = self.frameShape
        X0, Y0 = self.frameShapeOriginal
        dets_out = []
        for det in dets:
            det_out = det.copy()
            #det_out['xyxy_enlarge'] = det['xyxy_enlarge']
            det_out['xyxy'] = self.resizeToOriginal(det['xyxy'])
            det_out['xywh'] = self.resizeToOriginal(det['xywh'])
            dets_out.append(det_out)
        tracks = self.tracker.update(dets_out)
        self.lastTracks = tracks
        return tracks

    def getAlert(self, tracks, now_t):
        X, Y = self.frameShape
        X0, Y0 = self.frameShapeOriginal
        aods_out = []
        for track in tracks:
            aod_out = {}
            aod_out['duration'] = now_t - track.time0
            if aod_out['duration'] > self.minAODduration:
                if 'alerted' in track.tag:
                    aod_out['alerted'] = True
                else:
                    track.tag.add('alerted')
                aod_out['xyxy'] = track.attr['xyxy']
                aod_out['xywh'] = track.attr['xywh']
                aod_out['type'] = 'aod'
                aod_out['size'] = track.attr['size']
                aod_out['id'] = track.id
                aod_out['text'] = ['aod']
                aods_out.append(aod_out)
        return aods_out

    def detect(self, frame, yoloDets, now_t):
        frame0 = frame.copy()
        frame = self.maskArea(frame)
        frame = cv2.resize(frame, self.frameShape)
        if self.isInitialized():
            self.removePeople(frame, yoloDets)
            mask = self.compareBG_with(frame)
            dets = self.getDets(mask)
            tracks = self.updateTrack(dets)
            self.updateBG(frame, tracks)
            alerts = self.getAlert(tracks, now_t)
        else:
            self.initializeBG(frame, frame0)
            alerts = []
        return alerts


