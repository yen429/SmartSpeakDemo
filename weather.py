import json
import re
import requests

from PyQt5 import QtCore, QtGui, QtWidgets
import threading
import time

# 获取外网IP
def getIP():
    response = requests.get('http://ip.chinaz.com/getip.aspx')
    try:
        response.raise_for_status()
    except:
        print("网址请求出错")
        return "null"
    result = re.findall(".*ip:'(.*)',.*",response.text)
    return result[0]

# 获取IP所在国家/省份/城市
def getCityFromIP(ip):
    response = requests.get('http://int.dpool.sina.com.cn/iplookup/iplookup.php?format=json&ip=' + ip)
    try:
        response.raise_for_status()
    except:
        print("网址请求出错")
        return "null"
    result = json.loads(response.text)
    return result["city"]

# 获取城市天气
def getCityWeather(city):
    response = requests.get('http://wthrcdn.etouch.cn/weather_mini?city='+city)
    try:  
        response.raise_for_status()  
    except:  
        print("网址请求出错")
        return "null"
    result = json.loads(response.text)
    return result

#返回当前城市天气
def getCurrentCityWeather():
    return getCityWeather(getCityFromIP(getIP()))

class Weather:
    def setupUI(self,parentWidget,screen_width,screen_height):
        self.weather = QtWidgets.QLabel(parentWidget)
        self.weather.setGeometry(QtCore.QRect(screen_width/2+40, screen_height*0.12, 96, 96))
        self.weather.setObjectName("weather")

        self.temperature = QtWidgets.QLabel(parentWidget)
        self.temperature.setGeometry(QtCore.QRect(screen_width/2+40, screen_height*0.12+58, 96, 96))
        font = QtGui.QFont()
        font.setPixelSize(18)
        self.temperature.setFont(font)
        self.temperature.setStyleSheet("color: rgb(255, 255, 255);")
        self.temperature.setObjectName("temperature")

    def isNight(self):
        localTime = time.localtime(time.time())
        hour = str(localTime[3])
        return (int(hour) > 18)

    def start(self):
        _translate = QtCore.QCoreApplication.translate
        pixMap = QtGui.QPixmap("./res/weather/cloud_day.png").scaled(96,96)
        self.weather.setPixmap(pixMap)
        self.temperature.setText(_translate("MainWindow","20℃/26℃"))
        self.weatherTimer = threading.Timer(1, self.update)
        self.weatherTimer.start()

    def update(self):
        _translate = QtCore.QCoreApplication.translate
        weatherData = getCityWeather("台北")#getCurrentCityWeather()
        try:
            weatherType = weatherData['data']['forecast'][0]['type']
        except KeyError:
            return

        if "晴" in weatherType:
            if self.isNight():
                imgPath = "./res/weather/sunny_night.png"
            else:
                imgPath = "./res/weather/sunny_day.png"
        elif "多云" in weatherType:
            if self.isNight():
                imgPath = "./res/weather/cloud_night.png"
            else:
                imgPath = "./res/weather/cloud_day.png"
        elif "雷" in weatherType:
            if self.isNight():
                imgPath = "./res/weather/lei_night.png"
            else:
                imgPath = "./res/weather/lei_day.png"
        elif "阴" in weatherType:
            if self.isNight():
                imgPath = "./res/weather/yin_night.png"
            else:
                imgPath = "./res/weather/yin_day.png"
        elif "雪" in weatherType:
            if self.isNight():
                imgPath = "./res/weather/snow_night.png"
            else:
                imgPath = "./res/weather/snow_day.png"
        elif "雨" in weatherType:
            imgPath = "./res/weather/rain.png"
        else:
            imgPath = "./res/weather/cloud_day.png"
        pixMap = QtGui.QPixmap(imgPath).scaled(self.weather.width(),self.weather.height())
        self.weather.setPixmap(pixMap)
        lowTemp = weatherData['data']['forecast'][0]['low'][2:]
        highTemp = weatherData['data']['forecast'][0]['high'][2:]
        self.temperature.setText(_translate("MainWindow",lowTemp+"/"+highTemp))
        self.weatherTimer = threading.Timer(1800, self.update)
        self.weatherTimer.start()

    def stop(self):
        self.weatherTimer.cancel()
