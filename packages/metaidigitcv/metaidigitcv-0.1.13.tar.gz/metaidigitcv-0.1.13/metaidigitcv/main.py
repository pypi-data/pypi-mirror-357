import cv2
import mediapipe as mp
import time
import math
import numpy as np

class Handtracker:
    def __init__(self, staticMode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, minTrackCon=0.5):
        #InitializeMediaPipeHandsclass
        self.staticMode = staticMode
        self.maxHands = maxHands
        self.modelComplexity = modelComplexity
        self.detectionCon = detectionCon
        self.minTrackCon = minTrackCon

        #MediaPipeHandssetup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=self.staticMode, max_num_hands=self.maxHands,
                                         model_complexity=self.modelComplexity, min_detection_confidence=self.detectionCon,
                                         min_tracking_confidence=self.minTrackCon)
        self.mp_draw = mp.solutions.drawing_utils

    def identifyHands(self, img, draw=True, flipType=False):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)  #Storeresultsinself.results

        hands = []
        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                hand = {}
                landmarks = []
                for id, lm in enumerate(hand_landmarks.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    landmarks.append([cx, cy])
                hand["lmList"] = landmarks
                hands.append(hand)

                if draw:
                    self.mp_draw.draw_landmarks(img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        if flipType:
            img = cv2.flip(img, 1)

        return hands, img

    def trackPosition(self, img, handNo=0, draw=True):
        xList = []
        yList = []
        bbox = []
        self.lmList = []
        if img is None:
            return self.lmList, bbox

        self.results = self.hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))  #Ensurewegetfreshresults
        if self.results.multi_hand_landmarks:
            if len(self.results.multi_hand_landmarks) > handNo:
                myHand = self.results.multi_hand_landmarks[handNo]
                for id, lm in enumerate(myHand.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    xList.append(cx)
                    yList.append(cy)
                    self.lmList.append([id, cx, cy])
                    if draw:
                        cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

                if xList and yList:  #Preventmin()fromemptylisterror
                    xmin, xmax = min(xList), max(xList)
                    ymin, ymax = min(yList), max(yList)
                    bbox = (xmin, ymin, xmax, ymax)

                    if draw:
                        cv2.rectangle(img, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20), (0, 255, 0), 2)

        return self.lmList, bbox

    def trackRaisedFingers(self, hand):
        #Findhowmanyfingersareup
        fingers = []

        #Checkifhandhaslandmarks
        if "lmList" not in hand or len(hand["lmList"]) < 21:
            return fingers  #Returnemptylistifhanddataisinvalid

        lmList = hand["lmList"]  #Extractlandmarklist

        #Thumb(Checkx-coordinates)
        if lmList[4][0] > lmList[3][0]:
            fingers.append(1)  #Thumbisup
        else:
            fingers.append(0)  #Thumbisdown

        #Otherfingers(Checky-coordinates)
        for i in range(8, 21, 4):  #Index(8),Middle(12),Ring(16),Pinky(20)
            if lmList[i][1] < lmList[i - 2][1]:
                fingers.append(1)  #Fingerisup
            else:
                fingers.append(0)  #Fingerisdown

        return fingers

    def trackDistance(self, p1, p2, img, draw=True,r=15, t=3):
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
            cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)
            length = math.hypot(x2 - x1, y2 - y1)

        return length, img, [x1, y1, x2, y2, cx, cy]

def main():
    pTime = 0
    cap = cv2.VideoCapture(0)  #Use0forbuilt-inwebcam
    detector = Handtracker()

    while True:
        success, img = cap.read()
        if not success or img is None:
            print("Error:Failedtocaptureimage")
            continue

        hands, img = detector.identifyHands(img)
        if hands:
            lmList = hands[0]["lmList"]
            print(lmList[4])  #Printcoordinatesofthetipofthethumb

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
        cv2.imshow("Image", img)
        cv2.waitKey(1)

if __name__ == "__main__":
    main()