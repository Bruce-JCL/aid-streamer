'''
多路rtsp视频流推拉流及AI多路处理demo
在该demo中,我们一共对16路rtsp流进行了推拉流处理,同时开启了4路ai检测进程进行检测,最终在安卓端进行了输出显示
author: aidlux_xh
time: 2022/05/25
'''
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


# start andorid rtsp service
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

# showH=270
# showW=480
showH=1080
showW=1920
# showH=360
# showW=640
numChan=1



        
# get 16 rtsp streamer to sharememory and show the streamer
def rtsp_worker(video_id):
    while True:
        img = cap.read(video_id)
        if img is None:
            time.sleep(0.01)
            continue
        cap.show(img, video_id)


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
