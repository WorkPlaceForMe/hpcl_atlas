import cv2

class Motion:
    def __init__(self):
        self.bgSubtractor = cv2.createBackgroundSubtractorMOG2()
        self.bgSubtractor.setNMixtures(5) # increase to reduce detection
        self.bgSubtractor.setDetectShadows(False)
        self.bgSubtractor.setVarThreshold(100) # increase to reduce detection

        self.minAODSize = 50
        self.frameShape = (320,180)
        self.frameShapeOriginal = (1280,720)

    def compareBG_with(self, frame): 
        mask = self.bgSubtractor.apply(frame, learningRate=0.1)
        ret, mask = cv2.threshold(mask,200,255,cv2.THRESH_BINARY)
        #kernel = np.ones((5,5), np.uint8)
        #mask = cv2.dilate(mask, kernel, iterations=1)
        #mask = cv2.erode(mask, kernel, iterations=1)
        return mask

    def getAOD(self, mask):
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
                aod['xyxy'] = [x1,y1,x2,y2]
                aod['xyxy'] = self.resizeToOriginal(aod['xyxy'])
                aod['text'] = ['motion']
                aods.append(aod)
        return aods

    def resizeToOriginal(self, xyxy):
        X, Y = self.frameShape
        X0, Y0 = self.frameShapeOriginal
        x1,y1,x2,y2 = xyxy

        x1 = int(x1/X*X0)
        y1 = int(y1/Y*Y0)
        x2 = int(x2/X*X0)
        y2 = int(y2/Y*Y0)
        return (x1,y1,x2,y2)

    def detect(self, frame):
        frame = cv2.resize(frame, self.frameShape)
        mask = self.compareBG_with(frame)
        dets = self.getAOD(mask)
        return dets
