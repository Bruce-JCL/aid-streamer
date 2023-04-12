import os
import cv2
import numpy as np
import multiprocessing
import time
import json
import android
from AidLux import Aashmem


class ast():
    def __init__(self):
        self.js = []
        self.used_device = []
        self.allow_push_device = [0, 1]
        self.allow_save_device = [0]
        self.allow_push_save_device = [0]
        self.avaliable_device = ["inputUrl", "camera_id", "usbDeviceId", "file_path"]
        
        self.input_resize = []
    
        self.kv = []
        self.diskv = []
        self.eskv = []
        
        self.__version__ = "1.0.0"


    def add(self, input, utype=None, inputFormat=None, inputshape=None, outputinfo=None):
        js = {}
        used_device = -1
        
        # 记录该条配置使用的设备信息与输入源
        if utype is None:
            if isinstance(input,str):
                if "://" in input:
                    js["inputUrl"] = input
                    used_device = 0
                    self.used_device.append(used_device)
                elif os.path.exists(input):
                    if input[:7] == "/sdcard":
                        js["file_path"] = input
                    else:
                        js["file_path"] = "/data/data/com.aidlux/files/home/debian-fs" + os.path.abspath(input)
                        
                    cap = cv2.VideoCapture(input)
                    self.input_resize.append( ( int( 16 * np.ceil(cap.get(4) / 16) ), int( 16 * np.ceil(cap.get(3) / 16) ), 3 ) )
                    cap.release()
                    
                    used_device = 3
                    self.used_device.append(used_device)
                else:
                    raise("not support input")
                    
            elif isinstance(input,int):
                js["camera_id"] = input
                used_device = 1
                self.used_device.append(used_device)
            else:
                raise("input must be str for net stream/file or int for carmer")
        
        elif utype in self.avaliable_device:
            js[utype] = input
            used_device = self.avaliable_device.index(utype)
            self.used_device.append(used_device)
        else:
            raise("the utype must be inputUrl, camera_id or usbDeviceID")
            
        # inpufFormat 仅拉流有效
        if used_device == 0 and inputFormat in ["video/avc","video/hevc"] :
            js["inputFormat"] = inputFormat
        
        # 记录该组流对应的size 如果需要输入，则size为用户指定
        if used_device in self.allow_push_device and outputinfo is not None:
            self.input_resize.append((inputshape[1],inputshape[0],3))
            
            if inputshape is None:
                raise("if you want to push or save frames,you must fix inputshape")
            
            js["inputResizeWidth"] = inputshape[0]
            js["inputResizeHeight"] = inputshape[1]
            
            if len(outputinfo) == 4:
                if isinstance(outputinfo[0],str):
                    if "://" in outputinfo[0]:
                        js["outUrl"] = outputinfo[0]
                    elif used_device in self.allow_save_device:
                        if outputinfo[0][:7] == "/sdcard":
                            js["outPath"] = outputinfo[0]
                        else:
                            js["outPath"] = "/data/data/com.aidlux/files/home/debian-fs/" + os.path.abspath(outputinfo[0])
                    else:
                        raise("plase check outputinfo")
                else:
                    raise("输出必须是str")
                    
                js["outFrameRate"] = outputinfo[1]
                
                js["outWidth"] = outputinfo[2]
                
                js["outHeight"] = outputinfo[3]
                
            elif len(outputinfo) == 5 and used_device in self.allow_push_save_device:
                if isinstance(outputinfo[0],str) and isinstance(outputinfo[1],str):
                
                    if "://" in outputinfo[0] and "://" not in outputinfo[1]:
                        js["outUrl"] = outputinfo[0]
                    
                        if outputinfo[1][:7] == "/sdcard":
                            js["outPath"] = outputinfo[1]
                        else:
                            js["outPath"] = "/data/data/com.aidlux/files/home/debian-fs/" + os.path.abspath(outputinfo[1])
                        
                        js["outFrameRate"] = outputinfo[2]
                        
                        js["outWidth"] = outputinfo[3]
                        
                        js["outHeight"] = outputinfo[4]
                    
                    elif "://" in outputinfo[1] and "://" not in outputinfo[0]:
                        
                        js["outUrl"] = outputinfo[1]
                    
                        if outputinfo[1][:7] == "/sdcard":
                            js["outPath"] = outputinfo[0]
                        else:
                            js["outPath"] = "/data/data/com.aidlux/files/home/debian-fs/" + os.path.abspath(outputinfo[0])
                        
                        js["outFrameRate"] = outputinfo[2]
                        
                        js["outWidth"] = outputinfo[3]
                        
                        js["outHeight"] = outputinfo[4]
                    else:
                        raise("输出不能相同")
                
                else:
                    raise("输出必须都是字符串")
        
        self.js.append(js)
        return js
        
    def _check(self):
        use_type = -1
        
        if len(set(self.used_device)) > 1:
            raise("inputs must be same type")

        if self.used_device[0] == 0:
            sign = set(["outUrl" in js or "outPath" in js for js in self.js])
            if len(sign) > 1:
                raise("所有的输出类型必须一致")
            if sign.pop():
                sign = set(["outPath" in js for js in self.js])
  
                if len(sign) > 1:
                    use_type = 3
                else:
                    if sign.pop():
                        use_type = 3
                    else:
                        use_type = 2
            else:
                use_type = 1
                
        if self.used_device[0] == 1:
            sign = set(["outUrl" in js for js in self.js])
            
            if len(sign) > 1:
                raise("所有的输出类型必须一致")
                
            if sign.pop():
                use_type = 5
            else:
                use_type = 4
            
        if self.used_device[0] == 2:
            use_type = 6
            
        if self.used_device[0] == 3:
            use_type = 7
            
        return use_type
        
    def build(self):
        print(self.js)
        use_type = self._check()
        num = len(self.js)
        pid = os.getpid()
        thread = multiprocessing.Process(target=self._keep)
        thread.start()
        
        droid = android.Android()
        res = droid.stream(json.dumps(self.js), use_type, pid)
        info=json.loads(res.result)
        print(info)
        
        if use_type == 1 or use_type == 4:
            for i in range(num):
                self.input_resize.append((int(info['content']['rgbheight']), int(info['content']['rgbwidth']),3))
        
        
        if use_type == 6:
            for js in self.js:
                res = droid.requestPermission(js['usbDeviceId'])
        
        for i in range(num):
            self.kv.append(Aashmem("/tmp/mmkv/tmp_ipc_rtsp" + str(i)))
            self.diskv.append(Aashmem("/tmp/mmkv/tmp_ipc_display_" + str(i)))
            self.eskv.append(Aashmem("/tmp/mmkv/tmp_ipc_es_rtsp" + str(i)))

        time.sleep(3)
        print("build over")
        return self.input_resize
        
    def read(self,index=0):
        l = int.from_bytes(self.kv[index].get_bytes(4, 0), byteorder='little')
        if l==0:
            return None
        trig = int.from_bytes(self.kv[index].get_bytes(4, 4), byteorder='little')
        if trig == 0:
            return None
        bt = self.kv[index].get_bytes(l, 8)
        img = np.frombuffer(bt, dtype=np.uint8).reshape(self.input_resize[index])
        trig=0
        self.kv[index].set_bytes(trig.to_bytes(4, byteorder='little', signed=True), 4, 4)
        return img
    
    def show(self,frame,index=0):
        binput = frame.tobytes()
        self.diskv[index].set_bytes(len(binput).to_bytes(4, byteorder='little', signed=True), 4, 0)
        self.diskv[index].set_bytes(binput, len(binput), 4)
        
    def push(self,frame,index=0):
        binput = frame.tobytes()
        self.eskv[index].set_bytes(len(binput).to_bytes(4, byteorder='little', signed=True), 4, 0)
        self.eskv[index].set_bytes(binput, len(binput), 8)
    
    def _keep(self):
        counter = 0
        while True:
            f = open("/tmp/mmkv/info.txt","w")
            f.write(str(counter))
            f.close()
            if counter < 10:
                counter = counter + 1
            else:
                counter = 0
            time.sleep(1)
    
    def getUsbDeviceId(self):
        available_device = []
        droid = android.Android()
        res = droid.searchUSB()
        info=json.loads(res.result)
        for id in info['content']:
            if id['deviceClass'] == 239 and id['deviceSubclass']==2:
                available_device.append(id['deviceID'])
        if len(available_device) < info['count']:
            print("some usb camera not support")
        return available_device
        
    def add_from_json(self, json_path):
        f = open(json_path,"r")
        configs = json.load(f)
        f.close()
        for config in configs:
            input = config["input"]
            
            if config["utype"] != "None":
                utype = config["utype"]
            else:
                utype = None
                
            if config["inputFormat"] != "None":
                inputFormat = config["inputFormat"]
            else:
                inputFormat = None
                
            if config["inputshape"] != "None":
                inputshape = config["inputshape"]
            else:
                inputshape = None
                
            if config["outputinfo"] != "None":
                outputinfo = config["outputinfo"]
            else:
                outputinfo = None
            
            self.add(input, utype, inputFormat, inputshape, outputinfo)
        
            