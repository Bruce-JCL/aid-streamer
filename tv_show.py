import os
import time
import json
import ctypes
import numpy as np
import multiprocessing
from multiprocessing import Process, sharedctypes
import android
from AidLux import Aashmem
import json
import sys
droid = android.Android()
import aidstream
import cv2
import json

cap = aidstream.ast()
with open('config.json','r',encoding = 'utf-8') as fp:
    data = json.load(fp)
for url in data:
    if "h265" in data[str(url)]:
        cap.add(data[str(url)], inputFormat = "video/hevc") 
    else:
        cap.add(data[str(url)], inputFormat = "video/avc") 
cap.build()
numChan=4

def rtsp_worker(video_id):
    t1=int(round(time.time()*1000))
    index=0
    while True:
        img = cap.read(video_id)
        if img is None:
            time.sleep(0.01)
            continue
        index=index+1
        t2=int(round(time.time()*1000))
        if (t2-t1)>=1000:
            print("video_id",video_id,"fps:",index)
            t1=t2
            index=0
        # cap.show(img, video_id)
        
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
