# -*- coding: utf-8 -*-

# Created by: Justin.Yang,XMASC
#
# Modified Date:2018-6-5

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os
import utils

def setListCardWidget(MainWindow,jsonData):
    itemWidget = QtWidgets.QWidget(MainWindow)
    itemWidget.setContentsMargins(0, 0, 0, 0)
    itemLayout = QtWidgets.QVBoxLayout(itemWidget)
    itemLayout.setContentsMargins(0, 0, 0, 0)
    itemLayout.setSpacing(0)
    itemLayout.setAlignment(QtCore.Qt.AlignLeft)
    textBrowser = QtWidgets.QTextBrowser(MainWindow)
    textBrowser.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
    textBrowser.setStyleSheet(utils.LABEL_USER_STYLE)
    textBrowser.setFont(utils.getGlobalTextFont())
    textBrowser.setStyleSheet(utils.LABEL_ROBOT_STYLE)
    textBrowser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    answerText = jsonData.get('content',  'NA')
    textBrowser.setFont(utils.getGlobalTextFont())
    answerLabelTotalHeight = utils.calculateLabelHeight(textBrowser, answerText)
    print("answerLabelTotalHeight: %s"%(answerLabelTotalHeight))
    textBrowser.setGeometry(0, 0, utils.LABEL_MAX_WIDTH, answerLabelTotalHeight)
    
    
    textBrowserTitle = QtWidgets.QTextBrowser(MainWindow)
    textBrowserTitle.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
    textBrowserTitle.setStyleSheet(utils.LABEL_USER_STYLE)
    textBrowserTitle.setFont(utils.getGlobalTextFont())
    textBrowserTitle.setStyleSheet(utils.LABEL_ROBOT_STYLE)
    textBrowserTitle.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    
    titleText = jsonData.get('title',  'NA')
    textBrowserTitle.setFont(utils.getGlobalTitleFont())
    answerLabelTotalHeight2 = utils.calculateLabelHeight(textBrowserTitle, titleText)
    answerLabelTotalHeight = answerLabelTotalHeight + answerLabelTotalHeight2
    
    textBrowser.setText(answerText)
    textBrowserTitle.setText(titleText)
    itemLayout.addWidget(textBrowserTitle)
    itemLayout.addWidget(textBrowser)
    itemWidget.setLayout(itemLayout)
    return itemWidget,answerLabelTotalHeight

    
    
def setListImagedWidget(MainWindow,jsonData):
    alllistWidget = QtWidgets.QWidget(MainWindow)
    itemWidget = QtWidgets.QWidget(MainWindow)
    itemWidget.setContentsMargins(0, 0, 0, 0)
    itemLayout = QtWidgets.QVBoxLayout(itemWidget)
    itemLayout.setContentsMargins(0, 0, 0, 0)
    itemLayout.setSpacing(0)
    itemLayout.setAlignment(QtCore.Qt.AlignLeft)
    itemLabel = QtWidgets.QLabel(MainWindow)
    itemLabel.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
    itemLabel.setStyleSheet(utils.LABEL_ROBOT_STYLE)
    itemLabel.setWordWrap(True)
    
    answerText = jsonData.get('content',  'NA')
    itemLabel.setFont(utils.getGlobalTextFont())
    answerLabelTotalHeight = utils.calculateLabelHeight(itemLabel, answerText)
    print("answerLabelTotalHeight: %s"%(answerLabelTotalHeight))
    itemLabel.setGeometry(0, 0, utils.LABEL_MAX_WIDTH, answerLabelTotalHeight)
    
    itemLabelTitle = QtWidgets.QLabel(MainWindow)
    itemLabelTitle.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
    itemLabelTitle.setStyleSheet(utils.LABEL_ROBOT_STYLE)
    itemLabelTitle.setWordWrap(True)
    
    #titleText="text"
    titleText = jsonData.get('title',  'NA')
    itemLabelTitle.setFont(utils.getGlobalTitleFont())
    #itemLabelTitle.setGeometry(utils.LABEL_MAX_WIDTH, answerLabelTotalHeight, utils.LABEL_MAX_WIDTH, answerLabelTotalHeight)
    answerLabelTotalHeight2 = utils.calculateLabelHeight(itemLabelTitle, titleText)
    itemLabelTitle.setGeometry(0, 0, utils.LABEL_MAX_WIDTH, answerLabelTotalHeight2)
    answerLabelTotalHeight = answerLabelTotalHeight + answerLabelTotalHeight2
    #itemLabelTitle.setStyleSheet("background-color:#000000;")
    itemLabel.setText(answerText)
    itemLabelTitle.setText(titleText)
    
    itemImageLabel = QtWidgets.QLabel(MainWindow)
    itemImageLabel.setAlignment(QtCore.Qt.AlignLeft)
    itemImageLabel.setScaledContents(True)
    
    url=jsonData.get('image',  'NA').get('src', 'NA')
    fileName = os.path.basename(url)
    filePath = "%s/%s"%(os.getcwd(), fileName)

    #启动线程下载图片
    downloadThread = utils.DownloadImageThread(url, filePath, itemImageLabel, utils.LABEL_MAX_WIDTH, utils.LABEL_MAX_WIDTH/ 2)
    downloadThread.start()
    print("image url: %s"%(url))
    pixmap = QPixmap("./res/loading.png").scaled(80, 80)  
    itemImageLabel.setPixmap(pixmap)
    itemImageLabel.setGeometry(0, 0, utils.LABEL_MAX_WIDTH, utils.LABEL_MAX_WIDTH / 2)

    itemLayout.addWidget(itemLabelTitle)
    itemLayout.addWidget(itemLabel)
    
    hbox = QHBoxLayout(alllistWidget)
    hbox.addWidget(itemWidget)
    hbox.addWidget(itemImageLabel)
    #itemLayout.addWidget(itemImageLabel)
    alllistWidget.setLayout(hbox)
    return alllistWidget,answerLabelTotalHeight
def setListWidget(MainWindow,jsonData):
	answerlistWidget = QtWidgets.QWidget(MainWindow)
	vbox = QVBoxLayout(answerlistWidget)
	list = jsonData.get('list',  'NA')
	answerItemTotalHeight = 0
	for i in list:
		if "image" in i:
			tempWidget,answerItemTotalHeight_i = setListImagedWidget(answerlistWidget,i)
		else:
			tempWidget,answerItemTotalHeight_i = setListCardWidget(answerlistWidget,i)
		answerItemTotalHeight = answerItemTotalHeight + answerItemTotalHeight_i
		vbox.addWidget(tempWidget)
	return answerlistWidget,answerItemTotalHeight
def setTextCardWidget(MainWindow,jsonData):
    itemWidget = QtWidgets.QWidget(MainWindow)
    itemWidget.setContentsMargins(0, 0, 0, 0)
    itemLayout = QtWidgets.QHBoxLayout(itemWidget)
    itemLayout.setContentsMargins(0, 0, 0, 0)
    itemLayout.setSpacing(0)
    itemLayout.setAlignment(QtCore.Qt.AlignLeft)
    itemLabel = QtWidgets.QLabel(MainWindow)
    itemLabel.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
    itemLabel.setStyleSheet(utils.LABEL_ROBOT_STYLE)
    itemLabel.setWordWrap(True)

    answerText = jsonData.get('content',  'NA')
    itemLabel.setFont(utils.getGlobalTextFont())
    answerLabelTotalHeight = utils.calculateLabelHeight(itemLabel, answerText)
    print("answerLabelTotalHeight: %s"%(answerLabelTotalHeight))
    itemLabel.setGeometry(0, 0, utils.LABEL_MAX_WIDTH, answerLabelTotalHeight)

    itemLabel.setText(answerText)
    itemLayout.addWidget(itemLabel)
    itemWidget.setLayout(itemLayout)
    return itemWidget,answerLabelTotalHeight
    
def setStandardCardWidget(MainWindow,jsonData):
    itemWidget = QtWidgets.QWidget(MainWindow)
    itemWidget.setContentsMargins(0, 0, 0, 0)
    itemLayout = QtWidgets.QVBoxLayout(itemWidget)
    itemLayout.setContentsMargins(0, 0, 0, 0)
    itemLayout.setSpacing(0)
    itemLayout.setAlignment(QtCore.Qt.AlignLeft)
    itemLabel = QtWidgets.QLabel(MainWindow)
    itemLabel.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
    itemLabel.setStyleSheet(utils.LABEL_ROBOT_STYLE)
    itemLabel.setWordWrap(True)

    answerText = jsonData.get('content',  'NA')
    itemLabel.setFont(utils.getGlobalTextFont())
    answerLabelTotalHeight = utils.calculateLabelHeight(itemLabel, answerText)
    itemLabel.setGeometry(0, 0, utils.LABEL_MAX_WIDTH, answerLabelTotalHeight)
    itemLabel.setText(answerText)

    itemImageLabel = QtWidgets.QLabel(MainWindow)
    itemImageLabel.setAlignment(QtCore.Qt.AlignLeft)
    itemImageLabel.setScaledContents(True)
    
    url=jsonData.get('image',  'NA').get('src', 'NA')
    fileName = os.path.basename(url)
    filePath = "%s/%s"%(os.getcwd(), fileName)

    #启动线程下载图片
    downloadThread = utils.DownloadImageThread(url, filePath, itemImageLabel, utils.LABEL_MAX_WIDTH, utils.LABEL_MAX_WIDTH/ 2)
    downloadThread.start()
    print("image url: %s"%(url))
    pixmap = QPixmap("./res/loading.png").scaled(utils.LABEL_MAX_WIDTH, utils.LABEL_MAX_WIDTH/ 2)  
    itemImageLabel.setPixmap(pixmap)
    itemImageLabel.setGeometry(0, 0, utils.LABEL_MAX_WIDTH, utils.LABEL_MAX_WIDTH / 2)
    itemLayout.addWidget(itemLabel)
    itemLayout.addWidget(itemImageLabel)
    answerLabelTotalHeight = answerLabelTotalHeight + utils.LABEL_MAX_WIDTH/ 2
    return itemWidget,answerLabelTotalHeight
    
def setWeatherTemplateWidget(MainWindow,jsonData):
    itemWidget = QtWidgets.QWidget(MainWindow)
    itemWidget.setContentsMargins(0, 0, 0, 0)
    itemLayout = QtWidgets.QVBoxLayout(itemWidget)
    itemLayout.setContentsMargins(0, 0, 0, 0)
    itemLayout.setSpacing(0)

    #当前温度的widget
    currentWeatherWidget = QtWidgets.QWidget(MainWindow)
    currentWeatherLayout = QtWidgets.QHBoxLayout(currentWeatherWidget)
    
    mainTitleLabel = QtWidgets.QLabel(MainWindow)
    mainTitleLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
    mainTitleLabel.setScaledContents(True)
    mainTitleLabel.adjustSize()
    mainTitleLabel.setWordWrap(True)
    mainTitleLabel.setFont(utils.getGlobalTextFont())

    mianTitleText = jsonData.get('title',  'NA').get('mainTitle', 'NA')
    mainTitleLabelTotalHeight = utils.calculateLabelHeight(mainTitleLabel, mianTitleText)
    mainTitleLabel.setGeometry(0, 0, utils.LABEL_MAX_WIDTH, mainTitleLabelTotalHeight)
    mainTitleLabel.setText(mianTitleText)
    
    #设置描述label
    descriptionLabel = QtWidgets.QLabel(MainWindow)
    
    #设置居中、边框和背景色
    descriptionLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
    #自动换行
    descriptionLabel.setScaledContents(True)
    descriptionLabel.adjustSize()
    descriptionLabel.setWordWrap(True)
    descriptionLabel.setFont(utils.getGlobalTextFont())

    descriptionText = jsonData.get('description', 'NA')
    #自适应获取当前text对应的label高度
    descriptionLabelTotalHeight = utils.calculateLabelHeight(descriptionLabel, descriptionText)
    descriptionLabel.setGeometry(0, 0, utils.LABEL_MAX_WIDTH, descriptionLabelTotalHeight)
    descriptionLabel.setText(descriptionText)
    
    #设置日期label
    dateItemLabel = QtWidgets.QLabel(MainWindow)
    
    #设置居中、边框和背景色
    dateItemLabel.setAlignment(QtCore.Qt.AlignCenter)
    #自动换行
    dateItemLabel.setScaledContents(True)
    dateItemLabel.adjustSize()
    dateItemLabel.setWordWrap(True)
    dateItemLabel.setFont(utils.getGlobalTextFont())

    date_text = jsonData.get('title',  'NA').get('subTitle', 'NA')
    #自适应获取当前text对应的label高度
    dateItemLabel.setGeometry(0, 0, utils.LABEL_MAX_WIDTH / 3, 2 * utils.LABEL_SINGLE_HEIGHT)
    dateItemLabel.setText(date_text)
    
    #设置图片
    itemImageLabel = QtWidgets.QLabel(MainWindow)
    itemImageLabel.setAlignment(QtCore.Qt.AlignCenter)
    itemImageLabel.setScaledContents(True)
    
    imageUrls = [(source.get('url', 'NA')) for source in jsonData.get('currentWeatherIcon',  'NA').get('sources',  'NA')]
    url = imageUrls[0]
    fileName = os.path.basename(url)
    filePath = "%s/%s"%(os.getcwd(), fileName)
    #启动线程下载图片
    downloadThread = utils.DownloadImageThread(url, filePath, itemImageLabel, utils.LABEL_MAX_WIDTH / 6, 2 * utils.LABEL_SINGLE_HEIGHT)
    downloadThread.start()
    pixmap = QPixmap("./res/loading.png").scaled(utils.LABEL_MAX_WIDTH / 6, 2 * utils.LABEL_SINGLE_HEIGHT)  
    itemImageLabel.setPixmap(pixmap)
    itemImageLabel.setGeometry(0, 0, utils.LABEL_MAX_WIDTH / 6, 2 * utils.LABEL_SINGLE_HEIGHT)
    
    #温度label
    temperatureItemLabel = QtWidgets.QLabel(MainWindow)
    #设置居中、边框和背景色
    temperatureItemLabel.setAlignment(QtCore.Qt.AlignCenter)
    #自动换行
    temperatureItemLabel.setScaledContents(True)
    temperatureItemLabel.adjustSize()
    temperatureItemLabel.setWordWrap(True)
    temperatureItemLabel.setFont(utils.getGlobalTextFont())
    currentTemp = str(jsonData.get('currentWeather',  'NA'))
    lowTemp = str(jsonData.get('lowTemperature', 'NA').get('value', 'NA'))
    highTemp = str(jsonData.get('highTemperature', 'NA').get('value', 'NA'))
    temperatureText = "%s\n%s/%s"%(currentTemp, lowTemp, highTemp)
    temperatureItemLabel.setGeometry(0, 0, utils.LABEL_MAX_WIDTH / 3, 2 * utils.LABEL_SINGLE_HEIGHT)
    temperatureItemLabel.setText(temperatureText)
    #将三个label加入current_weather_layout
    currentWeatherLayout.addWidget(dateItemLabel)
    currentWeatherLayout.addWidget(itemImageLabel)
    currentWeatherLayout.addWidget(temperatureItemLabel)
    
    #将currentWeatherWidget加入temLayout中
    itemLayout.addWidget(mainTitleLabel)
    itemLayout.addWidget(descriptionLabel)
    itemLayout.addWidget(currentWeatherWidget)
    count = 0
    for forcast in jsonData.get('weatherForecast', 'NA'):
        #天气预报部分
        forcastItemWeatherWidget = QtWidgets.QWidget(MainWindow)
        forcastItemWeatherLayout = QtWidgets.QHBoxLayout(forcastItemWeatherWidget)
        #设置日期label
        forcastDateItemLabel = QtWidgets.QLabel(MainWindow)
    
        #设置居中、边框和背景色
        forcastDateItemLabel.setAlignment(QtCore.Qt.AlignCenter)
        #自动换行
        forcastDateItemLabel.setScaledContents(True)
        forcastDateItemLabel.adjustSize()
        forcastDateItemLabel.setWordWrap(True)
        forcastDateItemLabel.setFont(utils.getGlobalTextFont())
        forcast_day_text = str(forcast.get('day',  'NA'))
        forcast_date_text = str(forcast.get('date',  'NA'))
        forcast_date = "%s\n%s"%(forcast_day_text, forcast_date_text)
        #自适应获取当前text对应的label高度
        forcastDateItemLabel.setGeometry(0, 0, utils.LABEL_MAX_WIDTH / 3, 2 * utils.LABEL_SINGLE_HEIGHT)
        forcastDateItemLabel.setText(forcast_date)
    
        #设置图片
        forcastItemImageLabel = QtWidgets.QLabel(MainWindow)
        forcastItemImageLabel.setAlignment(QtCore.Qt.AlignCenter)
        forcastItemImageLabel.setScaledContents(True)
    
        forcastImageUrls = [(forcastSource.get('url', 'NA')) for forcastSource in forcast.get('image',  'NA').get('sources',  'NA')]
        forcastUrl = forcastImageUrls[0]
        forcastFileName = os.path.basename(forcastUrl)
        forcastFilePath = "%s/%s"%(os.getcwd(), forcastFileName)
        #启动线程下载图片
        forcastDownloadImagesThread = utils.DownloadImageThread(forcastUrl, forcastFilePath, forcastItemImageLabel, utils.LABEL_MAX_WIDTH / 6, 2 * utils.LABEL_SINGLE_HEIGHT)
        forcastDownloadImagesThread.start()
        forcastPixmap = QPixmap("./res/loading.png").scaled(utils.LABEL_MAX_WIDTH / 6, 2 * utils.LABEL_SINGLE_HEIGHT)  
        forcastItemImageLabel.setPixmap(forcastPixmap)
        forcastItemImageLabel.setGeometry(0, 0, utils.LABEL_MAX_WIDTH / 6, 2 * utils.LABEL_SINGLE_HEIGHT)
    
        #温度label
        forcastTemperatureItemLabel = QtWidgets.QLabel(MainWindow)
        #设置居中、边框和背景色
        forcastTemperatureItemLabel.setAlignment(QtCore.Qt.AlignCenter)
        #自动换行
        forcastTemperatureItemLabel.setScaledContents(True)
        forcastTemperatureItemLabel.adjustSize()
        forcastTemperatureItemLabel.setWordWrap(True)
        forcastTemperatureItemLabel.setFont(utils.getGlobalTextFont())
        forcastLowTemp = str(forcast.get('lowTemperature', 'NA'))
        forcastHighTemp = str(forcast.get('highTemperature', 'NA'))
        forcastTemperatureText = "%s/%s"%(forcastLowTemp, forcastHighTemp)
        forcastTemperatureItemLabel.setGeometry(0, 0, utils.LABEL_MAX_WIDTH / 3, 2 * utils.LABEL_SINGLE_HEIGHT)
        forcastTemperatureItemLabel.setText(forcastTemperatureText)
        #将三个label加入current_weather_layout
        forcastItemWeatherLayout.addWidget(forcastDateItemLabel)
        forcastItemWeatherLayout.addWidget(forcastItemImageLabel)
        forcastItemWeatherLayout.addWidget(forcastTemperatureItemLabel)
        #将forcast_weather_widget加入tem_layout中
        itemLayout.addWidget(forcastItemWeatherWidget)
        count = count + 1
        if count == 2:
            break

    answerItemTotalHeight = (1 + count) * 2 * utils.LABEL_SINGLE_HEIGHT + mainTitleLabelTotalHeight + descriptionLabelTotalHeight
    itemWidget.setStyleSheet("background-color:00ff66;border:0.5px solid;border-color:Gainsboro;border-radius:5px;");
    return itemWidget,answerItemTotalHeight

def setListWidget_bak(MainWindow,jsonData):
    itemWidget = QtWidgets.QWidget(MainWindow)
    itemWidget.setContentsMargins(0, 0, 0, 0)
    itemLayout = QtWidgets.QVBoxLayout(itemWidget)
    itemLayout.setContentsMargins(0, 0, 0, 0)
    itemLayout.setSpacing(0)
    
    #设置main title label
    mainTitleLabel = QtWidgets.QLabel(MainWindow)
    
    #设置居中、边框和背景色
    mainTitleLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
    #自动换行
    mainTitleLabel.setScaledContents(True)
    mainTitleLabel.adjustSize()
    mainTitleLabel.setWordWrap(True)
    mainTitleLabel.setFont(utils.getGlobalTextFont())

    mianTitleText = jsonData.get('title',  'NA').get('mainTitle', 'NA')
    #自适应获取当前text对应的label高度
    mainTitleLabelTotalHeight = utils.calculateLabelHeight(mainTitleLabel, mianTitleText)
    mainTitleLabel.setGeometry(0, 0, utils.LABEL_MAX_WIDTH, mainTitleLabelTotalHeight)
    mainTitleLabel.setText(mianTitleText)
    
    #设置描述label
    subtitleLabel = QtWidgets.QLabel(MainWindow)
    
    #设置居中、边框和背景色
    subtitleLabel.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
    #自动换行
    subtitleLabel.setScaledContents(True)
    subtitleLabel.adjustSize()
    subtitleLabel.setWordWrap(True)
    subtitleLabel.setFont(utils.getGlobalTextFont())

    subtitleText = jsonData.get('title',  'NA').get('subTitle', 'NA')
    #自适应获取当前text对应的label高度
    subtitleLabelTotalHeight = utils.calculateLabelHeight(subtitleLabel, subtitleText)
    subtitleLabel.setGeometry(0, 0, utils.LABEL_MAX_WIDTH, subtitleLabelTotalHeight)
    subtitleLabel.setText(subtitleText)
    
    #将titel label加入tem_layout中
    itemLayout.addWidget(mainTitleLabel)
    itemLayout.addWidget(subtitleLabel)
    count = 0
    for listItems in jsonData.get('listItems', 'NA'):
        count = count + 1
        #天气预报部分
        listItemWidget = QtWidgets.QWidget(MainWindow)
        listItemLayout = QtWidgets.QHBoxLayout(listItemWidget)
        #计数label
        numberLabel = QtWidgets.QLabel(MainWindow)
    
        #设置居中、边框和背景色
        numberLabel.setAlignment(QtCore.Qt.AlignCenter)
        #自动换行
        numberLabel.setScaledContents(True)
        numberLabel.adjustSize()
        numberLabel.setWordWrap(True)
        numberLabel.setFont(utils.getGlobalTextFont())
        countText = "%s\t"%(count)
        #自适应获取当前text对应的label高度
        numberLabel.setGeometry(0, 0, utils.LABEL_SINGLE_HEIGHT / 2, 2* utils.LABEL_SINGLE_HEIGHT)
        numberLabel.setText(countText)
    
        #left text label
        leftTextLabel = QtWidgets.QLabel(MainWindow)
        #设置居中、边框和背景色
        leftTextLabel.setAlignment(QtCore.Qt.AlignCenter)
        #自动换行
        leftTextLabel.setScaledContents(True)
        leftTextLabel.adjustSize()
        leftTextLabel.setWordWrap(True)
        leftTextLabel.setFont(utils.getGlobalTextFont())
        leftText = listItems.get('leftTextField', 'NA')
        #自适应获取当前text对应的label高度
        leftTextLabel.setGeometry(utils.LABEL_SINGLE_HEIGHT, 0, utils.LABEL_SINGLE_HEIGHT, 2 * utils.LABEL_SINGLE_HEIGHT)
        leftTextLabel.setText(leftText)
    
        #left text label
        rightTextLabel = QtWidgets.QLabel(MainWindow)
        #设置居中、边框和背景色
        rightTextLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignCenter)
        #自动换行
        rightTextLabel.setScaledContents(True)
        rightTextLabel.adjustSize()
        rightTextLabel.setWordWrap(True)
        rightTextLabel.setFont(utils.getGlobalTextFont())
        rightText = listItems.get('rightTextField', 'NA')
        #自适应获取当前text对应的label高度
        rightTextLabel.setGeometry(utils.LABEL_SINGLE_HEIGHT, 0, utils.LABEL_SINGLE_HEIGHT, 2 * utils.LABEL_SINGLE_HEIGHT)
        rightTextLabel.setText(rightText)
        #将三个label加入current_weather_layout
        listItemLayout.addWidget(numberLabel)
        listItemLayout.addWidget(leftTextLabel)
        listItemLayout.addWidget(rightTextLabel)
        #将forcast_weather_widget加入tem_layout中
        itemLayout.addWidget(listItemWidget)
        if count == 2:
            break
    answerItemTotalHeight = count * 2 * utils.LABEL_SINGLE_HEIGHT + mainTitleLabelTotalHeight + subtitleLabelTotalHeight
    itemWidget.setStyleSheet("background-color:00ff66;border:0.5px solid;border-color:Gainsboro;border-radius:5px;");
    return itemWidget,answerItemTotalHeight

def parseRespondData(MainWindow,jsonData):
    itemWidget = QtWidgets.QWidget(MainWindow)
    answerItemTotalHeight = 0
    if jsonData:
        type = jsonData.get('type','NA')
        if "TextCard" in type:
            itemWidget,answerItemTotalHeight = setTextCardWidget(MainWindow,jsonData)
        elif "StandardCard" in type:
            itemWidget,answerItemTotalHeight = setStandardCardWidget(MainWindow,jsonData)
        elif "ListCard" in type:
            itemWidget,answerItemTotalHeight = setListWidget(MainWindow,jsonData)
        elif "WeatherTemplate" in type:
            itemWidget,answerItemTotalHeight = setWeatherTemplateWidget(MainWindow,jsonData)
    return itemWidget,answerItemTotalHeight