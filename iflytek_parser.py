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
import requests

def setListCardWidget(MainWindow,answerText,titleText):
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

    #answerText = jsonData['address']
    #if "phone" in jsonData:
        #if jsonData['phone']:
            #answerText = answerText + " TEL:" + jsonData['phone']
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
    
    #titleText = jsonData['name']
    textBrowserTitle.setFont(utils.getGlobalTitleFont())
    answerLabelTotalHeight2 = utils.calculateLabelHeight(textBrowserTitle, titleText)
    answerLabelTotalHeight = answerLabelTotalHeight + answerLabelTotalHeight2
    
    textBrowser.setText(answerText)
    textBrowserTitle.setText(titleText)
    itemLayout.addWidget(textBrowserTitle)
    itemLayout.addWidget(textBrowser)
    itemWidget.setLayout(itemLayout)
    return itemWidget,answerLabelTotalHeight


def setListImagedWidget(MainWindow,answerText,titleText,url):
    allWidget = QtWidgets.QWidget(MainWindow)
    itemWidget = QtWidgets.QWidget(MainWindow)
    itemWidget.setContentsMargins(0, 0, 0, 0)
    itemLayout = QtWidgets.QVBoxLayout(itemWidget)
    itemLayout.setContentsMargins(0, 0, 0, 0)
    itemLayout.setSpacing(0)
    itemLayout.setAlignment(QtCore.Qt.AlignLeft)
    itemLabel = QtWidgets.QLabel(itemWidget)
    itemLabel.setAlignment(QtCore.Qt.AlignLeft)
    itemLabel.setStyleSheet(utils.LABEL_ROBOT_STYLE)
    itemLabel.setWordWrap(True)
    
    #answerText = jsonData['address']
    #if "phone" in jsonData:
        #if jsonData['phone']:
            #answerText = answerText + " TEL:" + jsonData['phone']
    itemLabel.setFont(utils.getGlobalTextFont())
    answerLabelTotalHeight1 = utils.calculateLabelHeight(itemLabel, answerText)
    print("answerLabelTotalHeight1: %s"%(answerLabelTotalHeight1))
    itemLabel.setGeometry(0, 0, utils.LABEL_MAX_WIDTH, answerLabelTotalHeight1)
    
    itemLabelTitle = QtWidgets.QLabel(itemWidget)
    itemLabelTitle.setAlignment(QtCore.Qt.AlignLeft)
    #itemLabelTitle.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
    itemLabelTitle.setStyleSheet(utils.LABEL_ROBOT_STYLE)
    itemLabelTitle.setWordWrap(True)
    
    #titleText="text"
    #titleText = jsonData['name']
    itemLabelTitle.setFont(utils.getGlobalTitleFont())
    #itemLabelTitle.setGeometry(utils.LABEL_MAX_WIDTH, answerLabelTotalHeight, utils.LABEL_MAX_WIDTH, answerLabelTotalHeight)
    answerLabelTotalHeight2 = utils.calculateLabelHeight(itemLabelTitle, titleText)
    itemLabelTitle.setGeometry(0, 0, utils.LABEL_MAX_WIDTH, answerLabelTotalHeight2)
    answerLabelTotalHeight = answerLabelTotalHeight1 + answerLabelTotalHeight2
    #itemLabelTitle.setStyleSheet("background-color:#000000;")
    itemLabel.setText(answerText)
    itemLabelTitle.setText(titleText)
    
    itemImageLabel = QtWidgets.QLabel(allWidget)
    itemImageLabel.setAlignment(QtCore.Qt.AlignRight)
    #itemImageLabel.setGeometry(0, 0, 10, 10)
    itemImageLabel.setScaledContents(True)

    #url=jsonData['img']
    fileName = os.path.basename(url)
    filePath = "%s/%s"%(os.getcwd(), fileName)

    #启动线程下载图片
    downloadThread = utils.DownloadImageThread(url, filePath, itemImageLabel, utils.LABEL_MAX_WIDTH, utils.LABEL_MAX_WIDTH/ 2)
    downloadThread.start()
    
    
    print("image url: %s"%(url))
    pixmap = QPixmap("./res/loading.png").scaled(20, 20)
    #req = requests.get(url)
    #pixmap.loadFromData(req.content)
    itemImageLabel.setPixmap(pixmap)

    itemLayout.addWidget(itemLabelTitle)
    itemLayout.addWidget(itemLabel)
    #itemWidget.setGeometry(0, 0, utils.LABEL_MAX_WIDTH, 250)

    
    itemHbox = QHBoxLayout(allWidget)
    itemHbox.setContentsMargins(0, 0, 0, 0)
    itemHbox.setSpacing(0)    
    itemHbox.addWidget(itemWidget)
    itemHbox.addWidget(itemImageLabel)
    #hbox.setAlignment(QtCore.Qt.AlignLeft)
    #hbox.setStretchFactor(itemWidget,3)
    #hbox.setStretchFactor(itemImageLabel,1)
    #itemLayout.addWidget(itemImageLabel)
    allWidget.setLayout(itemHbox)
    return allWidget,answerLabelTotalHeight

def setListWidget(MainWindow,jsonData):
    answerlistWidget = QtWidgets.QWidget(MainWindow)
    vbox = QVBoxLayout(answerlistWidget)
    list = jsonData.get('data',  'NA').get('result')
    service = jsonData.get('service','NA')
    answerItemTotalHeight = 0
    j = 0
    if "LEIQIAO.historyToday" in service:
        answerItem,answerItemTotalHeight0 = setTextWidget(MainWindow,jsonData)
        answerItemTotalHeight = answerItemTotalHeight + answerItemTotalHeight0
        vbox.addWidget(answerItem)
    for i in list:
        j = j +1
        if j< 3:
            if ("hotelSearch" in service) or ("parkingLot" in service):
                    answerText = i['address']
                    if "phone" in i:
                        if i['phone']:
                            answerText = answerText + " TEL:" + i['phone']
                    titleText = i['name']
                    if "img" in i:
                        url = i['img']
                        if url:
                            tempWidget,answerItemTotalHeight_i = setListImagedWidget(answerlistWidget,answerText,titleText,url)
                        else:
                            tempWidget,answerItemTotalHeight_i = setListCardWidget(answerlistWidget,answerText,titleText)
                    else:
                        tempWidget,answerItemTotalHeight_i = setListCardWidget(answerlistWidget,answerText,titleText)
                        
                    answerItemTotalHeight = answerItemTotalHeight_i + answerItemTotalHeight
                    vbox.addWidget(tempWidget)

    return answerlistWidget,answerItemTotalHeight
    
def setTextWidget(MainWindow,jsonData):
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

    answerText = jsonData['answer']['text']
    itemLabel.setFont(utils.getGlobalTextFont())
    answerLabelTotalHeight = utils.calculateLabelHeight(itemLabel, answerText)
    print("answerLabelTotalHeight: %s"%(answerLabelTotalHeight))
    itemLabel.setGeometry(0, 0, utils.LABEL_MAX_WIDTH, answerLabelTotalHeight)

    itemLabel.setText(answerText)
    itemLayout.addWidget(itemLabel)
    itemWidget.setLayout(itemLayout)
    return itemWidget,answerLabelTotalHeight
    
def setTextImgWidget(MainWindow,jsonData,url):
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

    answerText = jsonData['answer']['text']
    itemLabel.setFont(utils.getGlobalTextFont())
    answerLabelTotalHeight = utils.calculateLabelHeight(itemLabel, answerText)
    itemLabel.setGeometry(0, 0, utils.LABEL_MAX_WIDTH, answerLabelTotalHeight)
    itemLabel.setText(answerText)

    itemImageLabel = QtWidgets.QLabel(MainWindow)
    itemImageLabel.setAlignment(QtCore.Qt.AlignLeft)
    itemImageLabel.setScaledContents(True)
    #url_text = jsonData.get('data','NA').get('result')
    #url=url_text[0]['img']
    fileName = os.path.basename(url)
    filePath = "%s/%s"%(os.getcwd(), fileName)

    #启动线程下载图片
    #downloadThread = utils.DownloadImageThread(url, filePath, itemImageLabel, utils.LABEL_MAX_WIDTH, utils.LABEL_MAX_WIDTH/ 2)
    #downloadThread.start()
    print("image url: %s"%(url))
    pixmap = QPixmap("./res/loading.png").scaled(utils.LABEL_MAX_WIDTH, utils.LABEL_MAX_WIDTH/ 2)
    req = requests.get(url)
    pixmap.loadFromData(req.content)
    pixmap.scaled(utils.LABEL_MAX_WIDTH, utils.LABEL_MAX_WIDTH/ 2)
    itemImageLabel.setPixmap(pixmap)
    itemImageLabel.setGeometry(0, 0, utils.LABEL_MAX_WIDTH, utils.LABEL_MAX_WIDTH / 2)
    itemLayout.addWidget(itemLabel)
    itemLayout.addWidget(itemImageLabel)
    answerLabelTotalHeight = answerLabelTotalHeight + utils.LABEL_MAX_WIDTH/ 2
    return itemWidget,answerLabelTotalHeight
    

def parseRespondData(MainWindow,jsonData):
    itemWidget = QtWidgets.QWidget(MainWindow)
    answerItemTotalHeight = 0
    if jsonData:
        service = jsonData.get('service','NA')
        print(service)
        if ("AIUI.cyclopedia" in service) or ("baike" in service):
            try:
                result = jsonData.get('data','NA').get('result')
                url=result[0]['img']
                itemWidget,answerItemTotalHeight = setTextImgWidget(MainWindow,jsonData,url)
            except:
                itemWidget,answerItemTotalHeight = setTextWidget(MainWindow,jsonData)
        elif "englishEveryday" in service:
            try:
                result = jsonData.get('data','NA').get('result')
                url=result[0]['imgUrl']
                itemWidget,answerItemTotalHeight = setTextImgWidget(MainWindow,jsonData,url)
            except:
                itemWidget,answerItemTotalHeight = setTextWidget(MainWindow,jsonData)
        elif ("hotelSearch" in service) or ("parkingLot" in service) or ("LEIQIAO.historyToday" in service):                
                itemWidget,answerItemTotalHeight = setListWidget(MainWindow,jsonData)
        elif ("crossTalk" in service) or ("drama" in service):
            try:
                result = jsonData.get('data','NA').get('result')
                titleText = jsonData['answer']['text']
                answerText = result[0]['actor'] + " " + result[0]['album']
                itemWidget,answerItemTotalHeight = setListCardWidget(MainWindow,answerText,titleText)
            except:
                itemWidget,answerItemTotalHeight = setTextWidget(MainWindow,jsonData)
        else:
            itemWidget,answerItemTotalHeight = setTextWidget(MainWindow,jsonData)
            
                
    return itemWidget,answerItemTotalHeight
