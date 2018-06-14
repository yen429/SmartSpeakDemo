from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import urllib.request
import threading
import os
import math
import datetime
import random
from watchdog.events import *
import requests

WINDOW_HEIGHT = 800
WINDOW_WIDTH = 480
FULL_SCREEN = True #True is full screen

LABEL_ROBOT_STYLE = '''
                border-radius: 6px;
                padding: 10px;
                color:#212121;
                background-color: #e8e8e8;
        '''

LABEL_USER_STYLE = '''
                border-radius: 6px;
                padding: 10px;
                color:#ffffff;
                background-color: #00caff;
        '''

AVATAR_SIZE = 56

#label宽度
LABEL_MAX_WIDTH = WINDOW_WIDTH-AVATAR_SIZE*2
#label单行高度
LABEL_SINGLE_HEIGHT = 56

def getGlobalTextFont():
    globalTextFont = QtGui.QFont()
    globalTextFont.setFamily("Bookman Old Style")
    globalTextFont.setPixelSize(16)
    return globalTextFont
    
def getGlobalTitleFont():
    globalTextFont = QtGui.QFont()
    globalTextFont.setFamily("Bookman Old Style")
    globalTextFont.setPixelSize(19)
    return globalTextFont    

#计算高度
def calculateLabelHeight(label,text):
    answerMetrics = QFontMetrics(label.font())
    textWidth = answerMetrics.width(text)
    labelRows = textWidth / LABEL_MAX_WIDTH
    realLabelRows = math.ceil(labelRows)
    return realLabelRows * LABEL_SINGLE_HEIGHT

#线程：图片下载
class DownloadImageThread(threading.Thread):
    def __init__(self, url, file_path, item_image_label, width, height):
        threading.Thread.__init__(self)
        self.nowTime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        self.number = random.randint(0,1000)
        self.now_url = self.nowTime+"_"+str(self.number)
        self.nowfilePath =  "./"+self.now_url
        self.url = url
        self.file_path = file_path
        self.path_url= "%s/%s"%(os.getcwd(), self.now_url)
        self.item_image_label = item_image_label
        self.width = width
        self.height = height

    def run(self):
        if os.path.exists(self.file_path):
            print("image exist")
            self.image_download_success()
            return
        #f = open(self.path_url,'wb') #注意第二个参数要写成wb，写成w会报错
        f = open(self.file_path,'wb')
        req = urllib.request.urlopen(self.url)  
        buf = req.read()
        f.write(buf)
        f.close()
        #self.fileName = os.path.basename(self.url)
        #os.rename(self.fileName,self.now_url)
        self.image_download_success()

    #下载图片后更新image_label
    def image_download_success(self):
        pixmap = QPixmap(self.file_path).scaled(80, 80)
        self.item_image_label.setPixmap(pixmap)
        self.item_image_label.setGeometry(self.width, self.height, self.width, self.height)

class FileEventHandler(FileSystemEventHandler):
    def __init__(self, f):
        FileSystemEventHandler.__init__(self)
        self.func = f

    #文件移动
    def on_moved(self, event):
        if event.is_directory:
            print("directory moved from {0} to {1}".format(event.src_path,event.dest_path))
        else:
            print("file moved from {0} to {1}".format(event.src_path,event.dest_path))

    #文件创建
    def on_created(self, event):
        if event.is_directory:
            print("directory created:{0}".format(event.src_path))
        else:
            print("file created:{0}".format(event.src_path))
            self.func()
                
    #文件删除
    def on_deleted(self, event):
        if event.is_directory:
            print("directory deleted:{0}".format(event.src_path))
        else:
            print("file deleted:{0}".format(event.src_path))

    #文件修改
    def on_modified(self, event):
        if event.is_directory:
            print("directory modified:{0}".format(event.src_path))
        else:
            self.func()
  
