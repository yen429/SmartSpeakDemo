from PyQt5 import QtCore, QtGui, QtWidgets
import threading
import time

def getTime():
    my_time = time.localtime(time.time())
    if my_time[3] < 10:
        hour = '0' + str(my_time[3])
    else:
        hour = str(my_time[3])
    if my_time[4] < 10:
        min = '0' + str(my_time[4])
    else:
        min = str(my_time[4])
    if my_time[5] < 10:
        second = '0' + str(my_time[5])
    else:
        second = str(my_time[5])
    return hour,min,second

def getDate():
    return time.strftime("%A %m/%d")

class Clock:
    def setupUI(self,parentWidget,screen_width,screen_height):
        self.hourAndMin = QtWidgets.QLabel(parentWidget)
        self.hourAndMin.setGeometry(QtCore.QRect(screen_width/2 - 160, screen_height*0.15, 200, 100))
        font = QtGui.QFont()
        font.setPixelSize(60)
        self.hourAndMin.setFont(font)
        self.hourAndMin.setStyleSheet("color: rgb(255, 255, 255);")
        self.hourAndMin.setObjectName("hourAndMin")

        self.date = QtWidgets.QLabel(parentWidget)
        self.date.setGeometry(QtCore.QRect(screen_width/2 - 135, screen_height*0.15+40, 200, 100))
        font = QtGui.QFont()
        font.setPixelSize(18)
        self.date.setFont(font)
        self.date.setStyleSheet("color: rgb(255, 255, 255);")
        self.date.setObjectName("date")

    def start(self):
        _translate = QtCore.QCoreApplication.translate
        hour_time, min_time, sec_time = getTime()
        ahead_time = hour_time + ':' + min_time
        self.hourAndMin.setText(_translate("MainWindow",ahead_time))
        self.date.setText(_translate("MainWindow",getDate()))
        self.clockTimer = threading.Timer(1, self.start)
        self.clockTimer.start()

    def stop(self):
        self.clockTimer.cancel()

