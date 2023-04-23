
import os
import time
import json
import ctypes
import numpy as np
import multiprocessing
from multiprocessing import Process, sharedctypes
import android
import aidlite_gpu
from AidLux import Aashmem
import json
import sys
droid = android.Android()
import aidstream
import cv2
import json

pushUrl="rtsp://127.0.0.1:8554/"

showH=1080
showW=1920
numChan=4
cap = aidstream.ast()
with open('config.json','r',encoding = 'utf-8') as fp:
    data = json.load(fp)
for index,url in enumerate(data):
    if "h264" in data[str(url)]:
        cap.add(data[str(url)], inputFormat = "video/avc", inputshape = [showW, showH],outputinfo = [pushUrl+str(index), 25, showW, showH]) 
    elif "h265" in data[str(url)]:
        cap.add(data[str(url)], inputFormat = "video/hevc",inputshape = [showW, showH],outputinfo = [pushUrl+str(index), 25, showW, showH]) 

cap.build()




def rtsp_worker(video_id):
    while True:
        img = cap.read(video_id)
        if img is None:
            time.sleep(0.01)
            continue
        cap.push(img,video_id)


if __name__ == "__main__":
    '''
    主进程
    '''
    pools = []

    # 将每一路监控视频进程进行初始化
    for i in range(numChan):
        pools.append(Process(target = rtsp_worker, args = (i, )))

    # 开始运行
    for p in pools:
        # p.daemon = True
        p.start()
