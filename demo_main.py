# -*- coding: utf-8 -*-

# Created by: Justin.Yang,XMASC
#
# Modified Date:2018-5-25

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from get_data import getDialogState, getCardData
import clock
from scroll_list_widget import ScrollListWidget
from watchdog.observers import Observer
from watchdog.events import *
import json
import urllib.request
import threading
import os
import math
import argparse
import sys
import weather
import utils
import alexa_parser
import dueros_parser
import iflytek_parser

class MainUiWindow(QtCore.QObject):
    refreshSignal = QtCore.pyqtSignal(str)
    switchSignal = QtCore.pyqtSignal(str)

    def setupUi(self, MainWindow, sdk_type):
        MainWindow.setObjectName("MainWindow")

        if not utils.FULL_SCREEN:
            MainWindow.resize(utils.WINDOW_WIDTH, utils.WINDOW_HEIGHT)
            self.X_PADDING = 0
            self.Y_PADDING = 0
        else:
            desktop = QtWidgets.QApplication.desktop()
            MainWindow.resize(desktop.width(), desktop.height())
            self.X_PADDING = (desktop.width() - utils.WINDOW_WIDTH)/2
            self.Y_PADDING = (desktop.height() - utils.WINDOW_HEIGHT)/2

        MainWindow.setAutoFillBackground(True)
        palette = QtGui.QPalette()
        palette.setColor(MainWindow.backgroundRole(), QtGui.QColor(000,000,000))
        MainWindow.setPalette(palette)

        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")

        self.sdkType = sdk_type

        #初始化状态
        self.oldState = "none"
        self.firstRun = True
        self.answerItemTotalHeight = 0
        self.respondAnimation = QtGui.QMovie("./res/respond.gif")
        self.dishCount = 0

        #设置List Widget
        self.listWidget = ScrollListWidget(self.centralWidget)
        self.listWidget.setGeometry(QtCore.QRect(self.X_PADDING, self.Y_PADDING, utils.WINDOW_WIDTH, utils.WINDOW_HEIGHT*0.925))
        self.listWidget.setFrameShape(QtWidgets.QListWidget.NoFrame)
        self.listWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listWidget.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.listWidget.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.listWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.listWidget.setFocusPolicy(QtCore.Qt.NoFocus)
        self.listWidget.setObjectName("listWidget")
        self.listWidget.setStyleSheet("border-image:url(./res/bg_dialog.png);")
        self.listWidget.verticalScrollBar().setStyleSheet("border-image:url('')")

        if "Iflytek" in self.sdkType:
            tips = "我能帮你做什么？"
        else:
            tips = "What can I service for you?"
        self.addAnswerItem(tips)

        #设置底部状态显示区
        self.footerWidget = QtWidgets.QWidget(MainWindow)
        self.footerWidget.setGeometry(QtCore.QRect(self.X_PADDING,self.Y_PADDING+self.listWidget.height(), utils.WINDOW_WIDTH, utils.WINDOW_HEIGHT*0.075))
        self.footerWidget.setStyleSheet("background-color:#000000;")

        footerLayout = QtWidgets.QVBoxLayout(self.footerWidget)
        footerLayout.setContentsMargins(0,0,0,0)

        self.stateLabel = QtWidgets.QLabel(self.footerWidget)
        self.stateLabel.setContentsMargins(0,8,0,0)
        self.stateLabel.setStyleSheet("background-color:#00000000;color:#00caff")
        self.stateLabel.setAlignment(QtCore.Qt.AlignCenter)
        textFont = QtGui.QFont()
        textFont.setPixelSize(22)
        self.stateLabel.setFont(textFont)
        self.stateLabel.setText("Online")

        self.stateTipsLabel = QtWidgets.QLabel(self.footerWidget)
        self.stateTipsLabel.setContentsMargins(0,0,0,8)
        self.stateTipsLabel.setStyleSheet("background-color:#00000000;color:#b3ffffff")
        self.stateTipsLabel.setAlignment(QtCore.Qt.AlignCenter)
        textFont = QtGui.QFont()
        textFont.setPixelSize(16)
        self.stateTipsLabel.setFont(textFont)
        self.stateTipsLabel.setText("Please speak wake word to start")
        footerLayout.addWidget(self.stateLabel)
        footerLayout.addWidget(self.stateTipsLabel)

        #设置Standby页面
        self.standbyWidget = QtWidgets.QWidget(self.centralWidget)
        self.standbyWidget.setGeometry(QtCore.QRect(self.X_PADDING,self.Y_PADDING, utils.WINDOW_WIDTH, utils.WINDOW_HEIGHT*0.925))
        self.standbyWidget.setObjectName("standbyWidget")

        self.standbyLabel = QtWidgets.QLabel(self.standbyWidget)
        self.standbyLabel.setGeometry(QtCore.QRect(0, 0, utils.WINDOW_WIDTH, utils.WINDOW_HEIGHT*0.925))
        self.standbyLabel.setStyleSheet("background-color:AliceBlue;")
        self.standbyLabel.setAlignment(QtCore.Qt.AlignVCenter|QtCore.Qt.AlignHCenter)
        pixMap = QtGui.QPixmap("./res/bg_main.png")
        self.standbyLabel.setPixmap(pixMap)
        self.standbyLabel.setScaledContents(True)

        self.standbyTipsBrowser = QtWidgets.QTextBrowser(self.standbyWidget)
        self.standbyTipsBrowser.setGeometry(QtCore.QRect(16,260,448,230))
        self.standbyTipsBrowser.setStyleSheet("background-color:#80000000;font-size:18px;border-radius: 6px;color:#ffffff;")
        self.standbyTipsBrowser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.standbyTipsBrowser.setText("Dear LiMing:\n    We're greatly honored that you can stay at our hotel,thank you for your support and love!\n    The first time is a guest,often come is a friend,we'll treat you as a good friend,forever and ever.May our service bring you homelike warm,super five-star enjoyment!\n                                                      Amazing Hotel")

        #设置order meal页面
        self.orderMealWidget = QtWidgets.QWidget(self.centralWidget)
        self.orderMealWidget.setGeometry(QtCore.QRect(self.X_PADDING,self.Y_PADDING, utils.WINDOW_WIDTH, utils.WINDOW_HEIGHT*0.925))
        self.orderMealWidget.setStyleSheet("border-image:url(./res/bg_dialog.png);")
        self.orderMealLabel = QtWidgets.QLabel(self.orderMealWidget)
        self.orderMealLabel.setGeometry(QtCore.QRect(0, 0, utils.WINDOW_WIDTH, utils.WINDOW_HEIGHT*0.925))
        pixMap = QtGui.QPixmap("./res/meal_menu1.png")
        self.orderMealLabel.setPixmap(pixMap)
        self.orderMealLabel.setAlignment(QtCore.Qt.AlignVCenter|QtCore.Qt.AlignHCenter)
        self.orderMealLabel.setStyleSheet("border-image:url('');");
        self.orderMealLabel.hide()

        #shopping cart
        self.cartLabel = QtWidgets.QLabel(self.orderMealWidget)
        self.cartLabel.setGeometry(QtCore.QRect(400, 20,48,48))
        pixMap = QtGui.QPixmap("./res/shopping_cart.png").scaled(48,48)
        self.cartLabel.setPixmap(pixMap)
        self.cartLabel.setStyleSheet("border-image:url('');");
        self.cartLabel.hide()

        #shopping cart count
        self.cartCountLabel = QtWidgets.QLabel(self.orderMealWidget)
        self.cartCountLabel.setGeometry(QtCore.QRect(425, 28,18,18))
        self.cartCountLabel.setText("1")
        self.cartCountLabel.setStyleSheet("border-image:url('');color:#f07c00;font-size:12px");
        self.cartCountLabel.hide()

        #count1
        self.countLabel1 = QtWidgets.QLabel(self.orderMealWidget)
        self.countLabel1.setGeometry(QtCore.QRect(300, 80,20,20))
        pixMap = QtGui.QPixmap("./res/count_one.png").scaled(20,20)
        self.countLabel1.setPixmap(pixMap)
        self.countLabel1.setStyleSheet("border-image:url('');");
        self.countLabel1.hide()

        #count2
        self.countLabel2 = QtWidgets.QLabel(self.orderMealWidget)
        self.countLabel2.setGeometry(QtCore.QRect(300, 455,20,20))
        pixMap = QtGui.QPixmap("./res/count_one.png").scaled(20,20)  
        self.countLabel2.setPixmap(pixMap)
        self.countLabel2.hide()
        self.countLabel2.setStyleSheet("border-image:url('');");
        self.orderMealWidget.hide()

        #设置服务提示页面
        self.serviceTipsLabel = QtWidgets.QLabel(self.centralWidget)
        self.serviceTipsLabel.setGeometry(QtCore.QRect(self.X_PADDING, self.Y_PADDING, utils.WINDOW_WIDTH, utils.WINDOW_HEIGHT*0.925))
        self.serviceTipsLabel.setAlignment(QtCore.Qt.AlignVCenter|QtCore.Qt.AlignHCenter)
        pixMap = QtGui.QPixmap("./res/service_tips.png").scaled(448,400)  
        self.serviceTipsLabel.setPixmap(pixMap)
        self.serviceTipsLabel.hide()

        #时钟
        self.clock = clock.Clock()
        self.clock.setupUI(self.standbyWidget,utils.WINDOW_WIDTH,utils.WINDOW_HEIGHT)
        self.clock.start()

        #天气
        self.weather = weather.Weather()
        self.weather.setupUI(self.standbyWidget,utils.WINDOW_WIDTH,utils.WINDOW_HEIGHT)
        self.weather.start()

        MainWindow.setCentralWidget(self.centralWidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.refreshSignal.connect(self.updateCardData)
        self.switchSignal.connect(self.switchState)

        #初始化状态
        if not "Iflytek" in self.sdkType:
            self.updateState()

        if utils.FULL_SCREEN:
            MainWindow.showFullScreen()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

    #侧滑动画
    def sideSlipHideAnimation(self,obj,direction):
        self.anim = QtCore.QPropertyAnimation(obj, b"pos")
        self.anim.setDuration(500)
        if "left" in direction:
            self.anim.setStartValue(QtCore.QPointF(self.X_PADDING,self.Y_PADDING))
            self.anim.setEndValue(QtCore.QPointF(self.X_PADDING - utils.WINDOW_WIDTH,self.Y_PADDING))
        if "right" in direction:
            self.anim.setStartValue(QtCore.QPointF(self.X_PADDING, self.Y_PADDING))
            self.anim.setEndValue(QtCore.QPointF(self.X_PADDING + utils.WINDOW_WIDTH,self.Y_PADDING))
        self.anim.finished.connect(lambda:obj.hide())
        self.anim.start()
    
    #侧滑动画
    def sideSlipShowAnimation(self,obj,direction):
        self.anim = QtCore.QPropertyAnimation(obj, b"pos")
        self.anim.setDuration(500)
        if "left" in direction:
            self.anim.setStartValue(QtCore.QPointF(self.X_PADDING + utils.WINDOW_WIDTH,self.Y_PADDING))
            self.anim.setEndValue(QtCore.QPointF(self.X_PADDING,self.Y_PADDING))
        if "right" in direction:
            self.anim.setStartValue(QtCore.QPointF(self.X_PADDING - utils.WINDOW_WIDTH,self.Y_PADDING))
            self.anim.setEndValue(QtCore.QPointF(self.X_PADDING,self.Y_PADDING))
        self.anim.finished.connect(lambda:obj.show())
        self.anim.start()

    #for Iflytek
    def preProcessData(self,data):
        if "JSON:" in data:
        	result = json.loads(data[5:])
        	self.addAskItem(result["text"])
        	self.addAnswerItemForIflytek(result)
        else:
            state = "Online"
            if "IDLE_STATE" in data:
                state = "Online"
            elif "LISTEN_STATE" in data:
                state = "Listening"
            elif "THINK_STATE" in data:
                state = "Thinking"
            elif "SPEAK_STATE" in data:
                state = "Speaking"

            print("state: %s"%(state))

            if self.firstRun == False:
                self.clock.stop()
                self.weather.stop()
                self.sideSlipHideAnimation(self.standbyWidget,"right")

            if state == self.oldState:
                return
            else:
                self.oldState = state

            if "Close" in state:
                MainWindow.close()
            else:
                self.switchSignal.emit(state)

    def switchState(self,state):
        if "Online" in state and not "Thinking" in self.oldState:
            if "Amazon_Alexa" in self.sdkType:
                self.stateLabel.setText("Alexa Online")
                self.stateTipsLabel.setText("Speak 'Alexa' To Start")
                self.stateTipsLabel.show()
                self.orderMealWidget.hide()
            elif "Google_Assistant_Library" in self.sdkType:
                self.stateLabel.setText("Online")
                self.stateTipsLabel.setText("Speak 'OK,Google' To Start")
            elif "Google_Assistant_Service" in self.sdkType:
                self.stateLabel.setText("Online")
                self.stateTipsLabel.setText("Speak 'Jarvis' To Start")
            elif "Iflytek" in self.sdkType:
                self.stateLabel.setText("Online")
                self.stateTipsLabel.setText("Speak '哈囉你好' To Start")
            elif "DuerOs" in self.sdkType:
                self.stateLabel.setText("Online")
                self.stateTipsLabel.setText("Speak '小度小度' To Start")  
            self.respondAnimation.stop()
        elif "Listening" in state:
            if self.firstRun == True:
                self.clock.stop()
                self.weather.stop()
                self.sideSlipHideAnimation(self.standbyWidget,"right")
                self.serviceTipsLabel.show()
                self.firstRun = False
            animation = QtGui.QMovie("./res/listening.gif")
            self.stateLabel.setMovie(animation)
            self.stateTipsLabel.hide()
            animation.start()
        elif "Thinking" in state:
            if "Google_Assistant_Library" in self.sdkType:
                self.refreshSignal.emit("Google_Library_Ask")
            if "DuerOs" in self.sdkType:
                self.refreshSignal.emit("DuerOs_ASK")
            animation = QtGui.QMovie("./res/thinking.gif")
            self.stateLabel.setMovie(animation)
            self.stateTipsLabel.hide()
            self.serviceTipsLabel.hide()
            animation.start()
        elif "Speaking" in state:
            if "Amazon_Alexa" in self.sdkType:
                self.refreshSignal.emit("Alexa_Data")
            elif "DuerOs" in self.sdkType:
                self.refreshSignal.emit("DuerOs_Data")
            elif "Google_Assistant_Library" in self.sdkType:
                self.addAnswerItem(None)
            elif "Google_Assistant_Service" in self.sdkType:
                self.refreshSignal.emit("Google_Service_Data")

            animation = QtGui.QMovie("./res/speaking.gif")
            self.stateLabel.setMovie(animation)
            self.stateTipsLabel.hide()
            animation.start()
        elif "Connecting" in state:
            self.refreshSignal.emit("")
            animation = QtGui.QMovie("./res/connecting.gif")
            self.stateLabel.setMovie(animation)
            self.stateTipsLabel.hide()
            animation.start()
        elif "Disconnected" in state:
            pixMap = QtGui.QPixmap("./res/offline.png")
            self.stateLabel.setPixmap(pixMap)
            self.stateTipsLabel.hide()

    def updateState(self):
        state = getDialogState()
        print("state: %s"%(state))

        if self.firstRun == False:
            self.standbyWidget.hide()

        if state == self.oldState:
            return
        else:
            self.oldState = state

        if "Close" in state:
            MainWindow.close()
        else:
            self.switchSignal.emit(state)

    def updateCardData(self,state):
        data = getCardData()
        if "Google_Library_Ask" in state:
            self.addAskItem(data)
        elif "Google_Service_Data" in state:
            try:
                result = json.loads(data)
            except json.JSONDecodeError:
                return
            self.addAskItem(result['ask'])
            self.addAnswerItem(result['answer'])
        elif "Alexa_Data" in state:
            try:
                result = json.loads(data)
            except json.JSONDecodeError:
                return

            try:
                if "ordermeal" in result['title']['mainTitle']:
                    if "finishOrderMeal" in result['title']['mainTitle']:
                        self.addAnswerItemForAlexa(result)
                        pixMap = QtGui.QPixmap("./res/order_submitted.png")
                        self.orderMealLabel.setPixmap(pixMap)
                        self.orderMealLabel.show()
                        #确认结果界面延迟消失
                        self.submittedOrdertimer = threading.Timer(10, self.hideOrderMeal)
                        self.submittedOrdertimer.start()
                    else:
                        self.orderMeal(result)
                else:
                    self.addAskItem(result['title']['mainTitle'])
                    self.addAnswerItemForAlexa(result)
            except KeyError:
                return
        elif "DuerOs_ASK" in state:
            try:
                result = json.loads(data)
            except json.JSONDecodeError:
                return

            try:
                self.addAskItem(result['text'])
            except KeyError:
                return
        elif "DuerOs_Data" in state:
            try:
                result = json.loads(data)
            except json.JSONDecodeError:
                return
            try:
                self.addAnswerItemForDuerOs(result)
            except KeyError:
                return

    def hideOrderMeal(self):
        self.submittedOrdertimer.cancel()
        self.orderMealWidget.hide()
        #确认结果界面延迟消失
        self.finishOrdertimer = threading.Timer(60, self.finishOrderMeal)
        self.finishOrdertimer.start()

    def finishOrderMeal(self):
        self.finishOrdertimer.cancel()
        pixMap = QtGui.QPixmap("./res/finish_order.png")
        self.orderMealLabel.setPixmap(pixMap)
        self.orderMealLabel.show()
        self.orderMealWidget.show()
        #上菜结果延时显示
        self.quitOrdertimer = threading.Timer(10, self.quitOrderMeal)
        self.quitOrdertimer.start()

    def quitOrderMeal(self):
        self.quitOrdertimer.cancel()
        #完全结束
        self.orderMealWidget.hide()

    def orderMeal(self,result):
        type = result.get('type',  'NA')
        answerText = result.get('textField','NA')
        mainTitle = result['title']['mainTitle']

        if "BodyTemplate1" in type:
            if "one Bibimbap and one Salmon" in answerText:
                self.countLabel1.show()
                self.countLabel2.show()
                self.cartLabel.show()
                self.cartCountLabel.setText("2")
                self.cartCountLabel.show()
                self.dishCount = 2
            elif "one Bibimbap" in answerText:
                self.countLabel1.show()
                self.cartLabel.show()
                self.cartCountLabel.setText("1")
                self.cartCountLabel.show()
                self.dishCount = 1
            self.addAnswerItemForAlexa(result)
        elif "BodyTemplate2" in type:
            imageUrls = [(source .get('size', 'NA'), source .get('url', 'NA')) for source in result.get('image',  'NA').get('sources',  'NA')]
            url = imageUrls[0][1]
            imagePath = url.split('#')[-1]
            pixMap = QtGui.QPixmap("."+imagePath)
            self.orderMealLabel.setPixmap(pixMap)
            self.orderMealLabel.show()
            self.orderMealWidget.show()
            self.cartLabel.show()

            if "ordermealtpvShowMealMenu" in mainTitle:
                self.cartCountLabel.hide()
                self.dishCount = 0
            elif "ordermealtpvFinishOrder" in mainTitle:
                self.countLabel1.hide()
                self.countLabel2.hide()
                self.cartLabel.hide()
                self.cartCountLabel.hide()
                self.dishCount = 0
            elif "ordermealfinishOrderMealtpvConfirmOrder" in mainTitle:
                self.countLabel1.hide()
                self.countLabel2.hide()
                self.cartLabel.hide()
                self.cartCountLabel.hide()
                self.dishCount = 0
            elif "ordermealtpvShowMenuPage" in mainTitle:
                pageNum = url[-5]
                if pageNum == '1':
                    print("self.dishCount: %s"%(self.dishCount))
                    if self.dishCount == 1:
                        self.countLabel1.show()
                        self.countLabel2.hide()
                        self.cartCountLabel.setText("1")
                    elif self.dishCount == 2:
                        self.countLabel1.show()
                        self.countLabel2.show()
                        self.cartCountLabel.setText("2")
                    else:
                        self.countLabel1.hide()
                        self.countLabel2.hide()
                        self.cartCountLabel.hide()
                else:
                    self.countLabel1.hide()
                    self.countLabel2.hide()

    def addAskItem(self,text):
        askWidget = QtWidgets.QWidget(MainWindow)
        askWidget.setContentsMargins(utils.AVATAR_SIZE+16,10,16,0)
        askWidget.setStyleSheet("border-image:url('');background-color:#00ffffff;");
        askLayout = QtWidgets.QHBoxLayout(askWidget)
        askLayout.setAlignment(QtCore.Qt.AlignRight)
        askLayout.setContentsMargins(0,0,0,0)
        askLayout.setSpacing(0)
        
        textBrowser = QtWidgets.QTextBrowser(askWidget)

        textBrowser.setAlignment(QtCore.Qt.AlignRight)
        textBrowser.setStyleSheet(utils.LABEL_USER_STYLE)
        textBrowser.setFont(utils.getGlobalTextFont())
        textBrowser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        askLabelTotalHeight = utils.calculateLabelHeight(textBrowser, text)
        textBrowser.setText(text)
        askLayout.addWidget(textBrowser)
        
        avatarLab = QtWidgets.QLabel(askWidget)
        avatarLab.setAlignment(QtCore.Qt.AlignTop|QtCore.Qt.AlignHCenter)
        pixMap = QtGui.QPixmap("./res/user_avatar.png").scaled(utils.AVATAR_SIZE, utils.AVATAR_SIZE)  
        avatarLab.setPixmap(pixMap)
        askLayout.addWidget(avatarLab)
        
        print("askLabelTotalHeight: %s"%(askLabelTotalHeight))
        
        askItem = QtWidgets.QListWidgetItem(self.listWidget)
        askItem.setSizeHint(QtCore.QSize(0,askLabelTotalHeight+12))
        self.listWidget.setItemWidget(askItem,askWidget)
        self.listWidget.scrollToBottom()

    def addAnswerItem(self,text):
        answerWidget = QtWidgets.QWidget(MainWindow)
        answerWidget.setContentsMargins(16,16,utils.AVATAR_SIZE+16,0)
        answerWidget.setStyleSheet("border-image:url('');background-color:#00E0E0E0;");
        answerLayout = QtWidgets.QHBoxLayout(answerWidget)
        answerLayout.setContentsMargins(0,0,0,0)
        answerLayout.setSpacing(0)

        avatarLab = QtWidgets.QLabel(answerWidget)
        avatarLab.setAlignment(QtCore.Qt.AlignTop|QtCore.Qt.AlignHCenter)
        pixMap = QtGui.QPixmap("./res/robot_avatar.png").scaled(utils.AVATAR_SIZE,utils.AVATAR_SIZE)  
        avatarLab.setPixmap(pixMap)
        answerLayout.addWidget(avatarLab)

        if text:
            textBrowser = QtWidgets.QTextBrowser(answerWidget)
            textBrowser.setContentsMargins(0,0,0,0)
            textBrowser.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
            textBrowser.setStyleSheet(utils.LABEL_ROBOT_STYLE)
            textBrowser.setFont(utils.getGlobalTextFont())
            textBrowser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.answerItemTotalHeight = utils.calculateLabelHeight(textBrowser, text)
            textBrowser.append(text)

            answerLayout.addWidget(textBrowser)
        else:
            animLab = QtWidgets.QLabel(answerWidget)
            animLab.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
            animLab.setStyleSheet(utils.LABEL_ROBOT_STYLE)
            self.respondAnimation = QtGui.QMovie("./res/respond.gif")
            animLab.setMovie(self.respondAnimation)
            animLab.setScaledContents(True)
            self.respondAnimation.start()
            answerLayout.setAlignment(QtCore.Qt.AlignLeft)
            answerLayout.addWidget(animLab)
            self.answerItemTotalHeight = utils.LABEL_SINGLE_HEIGHT

        print("answerItemTotalHeight: %s"%(self.answerItemTotalHeight))

        answerItem = QtWidgets.QListWidgetItem(self.listWidget)
        answerItem.setSizeHint(QtCore.QSize(10,self.answerItemTotalHeight+12))
        self.listWidget.setItemWidget(answerItem,answerWidget)
        self.listWidget.scrollToBottom()

    def addAnswerItemForAlexa(self,result):
        answerWidget = QtWidgets.QWidget(MainWindow)
        answerWidget.setContentsMargins(16,10,utils.AVATAR_SIZE+16,0)
        answerWidget.setStyleSheet("border-image:url('');background-color:#00E0E0E0;");
        answerLayout = QtWidgets.QHBoxLayout(answerWidget)
        answerLayout.setContentsMargins(0,0,0,0)
        answerLayout.setSpacing(0)

        avatarLab = QtWidgets.QLabel(answerWidget)
        avatarLab.setAlignment(QtCore.Qt.AlignTop|QtCore.Qt.AlignHCenter)
        pixMap = QtGui.QPixmap("./res/robot_avatar.png").scaled(utils.AVATAR_SIZE,utils.AVATAR_SIZE)  
        avatarLab.setPixmap(pixMap)
        answerLayout.addWidget(avatarLab)

        tempWidget,self.answerItemTotalHeight = alexa_parser.parseRespondData(MainWindow,result)
        tempWidget.setStyleSheet(utils.LABEL_ROBOT_STYLE);
        answerLayout.addWidget(tempWidget)

        answerItem = QtWidgets.QListWidgetItem(self.listWidget)
        answerItem.setSizeHint(QtCore.QSize(0, self.answerItemTotalHeight+12))
        self.listWidget.setItemWidget(answerItem,answerWidget)
        self.listWidget.scrollToBottom()

    def addAnswerItemForDuerOs(self,result):
        answerWidget = QtWidgets.QWidget(MainWindow)
        answerWidget.setContentsMargins(16,10,utils.AVATAR_SIZE+16,0)
        answerWidget.setStyleSheet("border-image:url('');background-color:#00E0E0E0;");
        answerLayout = QtWidgets.QHBoxLayout(answerWidget)
        answerLayout.setAlignment(QtCore.Qt.AlignLeft)
        answerLayout.setContentsMargins(0,0,0,0)
        answerLayout.setSpacing(0)

        avatarLab = QtWidgets.QLabel(answerWidget)
        avatarLab.setAlignment(QtCore.Qt.AlignTop|QtCore.Qt.AlignHCenter)
        pixMap = QtGui.QPixmap("./res/robot_avatar.png").scaled(utils.AVATAR_SIZE,utils.AVATAR_SIZE)  
        avatarLab.setPixmap(pixMap)
        answerLayout.addWidget(avatarLab)

        tempWidget,self.answerItemTotalHeight = dueros_parser.parseRespondData(MainWindow,result)
        tempWidget.setStyleSheet(utils.LABEL_ROBOT_STYLE);
        answerLayout.addWidget(tempWidget)

        answerItem = QtWidgets.QListWidgetItem(self.listWidget)
        answerItem.setSizeHint(QtCore.QSize(0, self.answerItemTotalHeight+12))
        self.listWidget.setItemWidget(answerItem,answerWidget)
        self.listWidget.scrollToBottom()

    def addAnswerItemIflytek(self,result):
        answerWidget = QtWidgets.QWidget(MainWindow)
        answerWidget.setContentsMargins(16,10,utils.AVATAR_SIZE+16,0)
        answerWidget.setStyleSheet("border-image:url('');background-color:#00E0E0E0;");
        answerLayout = QtWidgets.QHBoxLayout(answerWidget)
        answerLayout.setAlignment(QtCore.Qt.AlignLeft)
        answerLayout.setContentsMargins(0,0,0,0)
        answerLayout.setSpacing(0)

        avatarLab = QtWidgets.QLabel(answerWidget)
        avatarLab.setAlignment(QtCore.Qt.AlignTop|QtCore.Qt.AlignHCenter)
        pixMap = QtGui.QPixmap("./res/robot_avatar.png").scaled(utils.AVATAR_SIZE,utils.AVATAR_SIZE)  
        avatarLab.setPixmap(pixMap)
        answerLayout.addWidget(avatarLab)

        tempWidget,self.answerItemTotalHeight = iflytek_parser.parseRespondData(MainWindow,result)
        tempWidget.setStyleSheet(utils.LABEL_ROBOT_STYLE);
        answerLayout.addWidget(tempWidget)

        answerItem = QtWidgets.QListWidgetItem(self.listWidget)
        answerItem.setSizeHint(QtCore.QSize(0, self.answerItemTotalHeight+12))
        self.listWidget.setItemWidget(answerItem,answerWidget)
        self.listWidget.scrollToBottom()

    def addAnswerItemForIflytek(self,result):
    	if "answer" in result:
    		if "service" in result:
    			self.addAnswerItemIflytek(result)
    		else:
    			self.addAnswerItem(result['answer']['text'])
    	else:
    		self.addAnswerItem("")
        
    class StateObserverThread(QThread):
        _state_signal = pyqtSignal()
        def __init__(self, parent=None):
            super().__init__(parent)          
        
        def notify(self):
            self._state_signal.emit()
        
        def initFileObserver(self):
            observer = Observer()
            path = os.getcwd()
            eventHandler = utils.FileEventHandler(self.notify)
            observer.schedule(eventHandler, path, True)
            observer.start()

        def run(self):
            self.initFileObserver()

    #For Iflytek
    class FifoObserverThread(QThread):
        data_signal = pyqtSignal(str)
        def __init__(self, parent=None):
            super().__init__(parent)

        def run(self):
            fifo=os.path.abspath('.')+"/Iflytek/bin/voice_control_fifo"
            fd=open(fifo,"r")
            while True:
                line = fd.readline()
                if line !="":
                    self.data_signal.emit(line)

if __name__ == "__main__":
    argParser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    argParser.add_argument('--sdk_type', type=str,
                        metavar='SDK_TYPE', required=True,
                        help='The platform of SDK(one of Amazon_Alexa,Google_Assistant_Library,Google_Assistant_Service,Iflytek,DuerOs)')
    args = argParser.parse_args()
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = MainUiWindow()
    ui.setupUi(MainWindow,args.sdk_type)
    MainWindow.show()

    if "Iflytek" in args.sdk_type:
        thread = MainUiWindow.FifoObserverThread()
        thread.data_signal.connect(ui.preProcessData)
        thread.start()
    else:
        thread = MainUiWindow.StateObserverThread()
        thread._state_signal.connect(ui.updateState)
        thread.start()

    sys.exit(app.exec_())
