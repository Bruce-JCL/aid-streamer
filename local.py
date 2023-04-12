import os
import sys
sys.path.append(os.getcwd())

import aidstream
import cv2

cap = aidstream.ast()

soure_path = "/sdcard/test_kobe.mp4"

cap.add(soure_path)
cap.build()
    
while True:
    frame = cap.read()
   
    if frame is None:
        continue
    print(len(frame),len(frame[0]))
    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    cv2.imshow("img",rgb_image)
    cv2.waitKey(1)
