import cv2 
import mediapipe as mp 
import numpy as np 
from time import time
from pynput.keyboard import Controller

mpHands = mp.solutions.hands
hands = mpHands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mpdraw = mp.solutions.drawing_utils

keyboard = Controller()

cap = cv2.VideoCapture(0)
cap.set(2, 150)

text = ""
tx = ""

class Button():
    def __init__(self, pos, text, size=[70, 70]):
        self.pos = pos
        self.size = size
        self.text = text
        self.start_time = 0
        self.stopped = False

keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "CL"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "SP"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "APR"]]
keys1 = [["q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "CL"],
         ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "SP"],
         ["z", "x", "c", "v", "b", "n", "m", ",", ".", "/", "APR"]]

def drawAll(img, buttonList):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        cv2.rectangle(img, button.pos, (x + w, y + h), (96, 96, 96), cv2.FILLED)
        cv2.putText(img, button.text, (x + 10, y + 40), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
    return img

buttonList = []
buttonList1 = []
list = []

for i in range(len(keys)):
    for j, key in enumerate(keys[i]):
        buttonList.append(Button([80 * j + 10, 80 * i + 10], key))

for i in range(len(keys1)):
    for j, key in enumerate(keys1[i]):
        buttonList1.append(Button([80 * j + 10, 80 * i + 10], key))

app = 0      
delay = 0

def calculate_distance(x1, y1, x2, y2):
    distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return distance

while True:
    success, frame = cap.read()
    frame = cv2.resize(frame, (1000, 580))
    frame = cv2.flip(frame, 1)
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(img)
    landmark = []

    if app == 0:
        frame = drawAll(frame, buttonList)
        list = buttonList
        r = "up"
    if app == 1:
        frame = drawAll(frame, buttonList1)
        list = buttonList1
        r = "down"

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            index_finger_landmark = hand_landmarks.landmark[8]
            hl, wl, cl = frame.shape
            x, y = int(index_finger_landmark.x * wl), int(index_finger_landmark.y * hl)
            landmark.append([8, x, y]) 

            for button in list:
                xb, yb = button.pos
                wb, hb = button.size

                if (xb < x < xb + wb) and (yb < y < yb + hb):
                    cv2.rectangle(frame, (xb - 5, yb - 5), (xb + wb + 5, yb + hb + 5), (160, 160, 160), cv2.FILLED)
                    cv2.putText(frame, button.text, (xb + 20, yb + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                    dis = calculate_distance(x, y, xb + wb // 2, yb + hb // 2)

                    if dis < 50:
                        if not button.stopped:
                            button.start_time = time()
                            button.stopped = True
                    else:
                        button.stopped = False

                    if button.stopped and time() - button.start_time > 3 and delay == 0:
                        k = button.text
                        cv2.rectangle(frame, (xb - 5, yb - 5), (xb + wb + 5, yb + hb + 5), (255, 255, 255), cv2.FILLED)
                        cv2.putText(frame, k, (xb + 20, yb + 65), cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 0), 4)

                        if k == "SP":
                            tx = ' '  
                            text += tx
                            keyboard.press(tx)
                        elif k == "CL":
                            tx = text[:-1]
                            text = ""
                            text += tx
                            keyboard.press('\b')
                        elif k == "APR" and r == "up":
                            app = 1
                        elif k == "APR" and r == "down":
                            app = 0
                        else:
                            text += k
                            keyboard.press(k)
                        delay = 1

    if delay:
        delay += 1
        if delay > 10:
            delay = 0      

    cv2.rectangle(frame, (20, 250), (850, 400), (255, 255, 255), cv2.FILLED)
    cv2.putText(frame, text, (30, 300), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 3)
    cv2.imshow('virtual keyboard', frame)

    if cv2.waitKey(1) & 0xff == ord('q'):
        break
