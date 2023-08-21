'''
-----------------主界面功能模块----------------------------------------------
这里显示了一个简单的例子，利用SDK实现一个操作界面

每个按钮对应一个相应的接口

您可以在这里找到它们是如何对应以及被调用的

同时您也可以看到有一些回调的值，比如电生理数据和实时计算的注意力、力量以及手势解码结果等

在这个界面中用简单的方法将这些值显示了出来
---------------------------------------------------------------------------
'''

import sys,os
import time,datetime
import pyqtgraph as pg
from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSlot, pyqtSignal,QCoreApplication
from PyQt5.QtWidgets import *

import threading
import subprocess
import psutil

from UI.ui0 import Ui_MainWindow
from UI.ArrowWidget import ArrowWidget
from UI.RoundWidget import RoundWidget
from socket_utils.udp import UdpManager
from mapping import reflextion

# 主体功能框体
class MyApp(QMainWindow,Ui_MainWindow):
    markSignal = pyqtSignal(int)
    msgSignal = pyqtSignal(str)            #for box message
    dataSignal = pyqtSignal(str)            #for data defer
    impendanceSignal = pyqtSignal(str)      #for impendance defer
    attetionSignal = pyqtSignal(str)        #for attetion defer
    controlSignal = pyqtSignal(str)         #for control defer
    deviceNameSignal = pyqtSignal(str)     #添加设备名
    powerSignal = pyqtSignal(str)           #for control defer

    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        #params
        self.udp = None
        self.temEventStart = None           #事件起点
        self.temEventDuration = None        #事件持续事件
        self.record_start_timeStamp = None  #记录起始时间戳
        self.impendanceCnt = 0              #用来显示阻抗值的计数
        self.sdkServerName = 'main.exe'     #SDK服务名称，不包含相对路径

        # 绑定按钮按下信号
        self.intBtn.clicked.connect(reflextion.InitSDK)
        self.findBtn.clicked.connect(reflextion.searchDevice)
        self.connectBtn.clicked.connect(self.connectFun)
        self.pulldataBtn.clicked.connect(reflextion.startPulldata)
        self.stopPulldataBtn.clicked.connect(reflextion.stopPulldata)
        self.startTranningBtn.clicked.connect(reflextion.startAttetionTest)
        self.abortTranningBtn.clicked.connect(reflextion.stopAttetionTest)
        self.startTestingBtn.clicked.connect(reflextion.startImpedance)
        self.endTestingBtn.clicked.connect(reflextion.stopImpedance)
        self.disconnectBtn.clicked.connect(reflextion.abortConnection)
        self.startRecordingBtn.clicked.connect(self.record_begin_fun)
        self.endRecordingBtn.clicked.connect(reflextion.stopRecording)
        self.filterBtn.clicked.connect(self.filterChangeFun)
        self.powerButton.clicked.connect(reflextion.startPowerCaculation)
        self.powerStopButton.clicked.connect(reflextion.stopPowerCaculation)
        self.controlButton.clicked.connect(reflextion.startGestureCaculation)
        self.controlStopButton.clicked.connect(reflextion.stopGestureCaculation)
        # 用户定义手动事件
        self.annotationBtn.pressed.connect(self.userEventFun_start)
        self.annotationBtn.released.connect(self.userEventFun_end)

        # Message
        self.msgSignal.connect(self.show_msg)
        self.dataSignal.connect(self.show_data)
        self.impendanceSignal.connect(self.show_impendance)
        self.attetionSignal.connect(self.show_attetion_data)
        self.controlSignal.connect(self.setControlStatus)
        self.deviceNameSignal.connect(self.addDeviceNames)
        self.powerSignal.connect(self.drawPower)

        #电生理UI
        self.EMG_chart_layout = QHBoxLayout(self.eegWidget)
        pg.setConfigOption('background', '#FFFFFF')
        pg.setConfigOption('foreground', 'black')
        eeg_chart = pg.GraphicsLayoutWidget()
        self.EMG_chart_layout.addWidget(eeg_chart)
        self.EMG_chart = eeg_chart.addPlot()
        self.EMG_chart.hideAxis('left')
        self.p1_xrange = [0, 500]
        self.p1_yrange = [-500, 500]
        self.EMG_chart.setYRange(self.p1_yrange[0], self.p1_yrange[1])
        self.EMG_chart.setXRange(self.p1_xrange[0], self.p1_xrange[1],padding=0)
        self.EMG_chart.setClipToView(True)
        #self.EMG_chart.setLabel(axis='left', text='电生理')
        self.EMG_curve = self.EMG_chart.plot(pen='red', name='Power')
        self.EMG_data = (list(range(500)), [0]*500)

        # 力量值UI
        self.power_chart_layout = QHBoxLayout(self.powerWidget)
        # self.powerWidget.setWindowTitle("Power ploting")
        pg.setConfigOption('background', '#FFFFFF')
        pg.setConfigOption('foreground', 'black')
        power_chart = pg.GraphicsLayoutWidget()
        self.power_chart_layout.addWidget(power_chart)
        self.power_chart = power_chart.addPlot()
        self.p2_xrange = [0, 50]
        self.p2_yrange = [0, 100]
        self.power_chart.setYRange(self.p2_yrange[0], self.p2_yrange[1])
        self.power_chart.setXRange(self.p2_xrange[0], self.p2_xrange[1],padding=0)
        self.power_chart.setClipToView(True)
        self.power_chart.setLabel(axis='left', text='力量值')
        self.power_curve = self.power_chart.plot(pen='red', name='Power')
        self.power_data = (list(range(50)), list(range(50)))

        #注意力UI
        self.attention_chart_layout = QHBoxLayout(self.attentionWidget)
        pg.setConfigOption('background', '#FFFFFF')
        pg.setConfigOption('foreground', 'black')
        attention_chart = pg.GraphicsLayoutWidget()
        self.attention_chart_layout.addWidget(attention_chart)
        self.attention_chart = attention_chart.addPlot()
        self.attention_chart.hideAxis('bottom')
        self.attention_chart.hideAxis('left')
        self.p3_xrange = [0, 200]
        self.p3_yrange = [0, 100]
        self.attention_chart.setYRange(self.p3_yrange[0], self.p3_yrange[1])
        self.attention_chart.setXRange(self.p3_xrange[0], self.p3_xrange[1],padding=0)
        self.attention_chart.setClipToView(True)
        #self.attention_chart.setLabel(axis='left', text='注意力')
        self.attention_curve = self.attention_chart.plot(pen='red', name='Power')
        self.attention_data = (list(range(200)),list(range(200)))

        # 上、下、左、右、变身，ArrowWidget是三角形组件，0-3分别朝向上下左右，RoundWidget是圆形组件
        self.controlWidgetLayout = QGridLayout(self.controlWidget)
        self.controlSubWidget = (
            ArrowWidget(self.controlWidget, 0),
            ArrowWidget(self.controlWidget, 1),
            ArrowWidget(self.controlWidget, 2),
            ArrowWidget(self.controlWidget, 3),
            RoundWidget(self.controlWidget),
        )
        # 将组件添加到布局中
        self.controlWidgetLayout.addWidget(self.controlSubWidget[0], 0, 1)
        self.controlWidgetLayout.addWidget(self.controlSubWidget[1], 2, 1)
        self.controlWidgetLayout.addWidget(self.controlSubWidget[2], 1, 0)
        self.controlWidgetLayout.addWidget(self.controlSubWidget[3], 1, 2)
        self.controlWidgetLayout.addWidget(self.controlSubWidget[4], 1, 1)

        #init UDP
        self.init()

    #########################服务#########################
    # region --------------服务
    '''启动服务'''
    def init(self):
        reflextion.app = self

        # 启动UDP服务
        self.udp = UdpManager()
        self.udp.app = self
        self.udp.UDPserverInit()

        # 启动SDK服务
        t1 = threading.Thread(target=self.sdk_server_start)
        t1.start()

    '''启动SDK服务'''
    def sdk_server_start(self):
        # 相对路径到你的.exe文件
        currentPath = os.path.dirname(os.path.abspath(__file__))
        exePath = (currentPath + '/sdk/' + self.sdkServerName)
        try:
            # 使用subprocess模块运行.exe文件
            subprocess.run(exePath, shell=True, check=True)
            _msg = 'SDK路径正确'
            self.msgSignal.emit(_msg)
            return True
        except subprocess.CalledProcessError:
            _msg = 'SDK路径错误'
            self.msgSignal.emit(_msg)
            return False
        except Exception as e:
            _msg = 'SDK未知错误'
            self.msgSignal.emit(_msg)
            return False, str(e)

    '''关闭SDK服务'''
    def closeSDKserver(self):
        for process in psutil.process_iter(attrs=['pid', 'name']):
            if process.info['name'] == self.sdkServerName:
                try:
                    # 关闭进程
                    psutil.Process(process.info['pid']).terminate()
                    return True
                except Exception as e:
                    return False
        return False

    '''关闭事件，同时关闭可能打开的SDK服务程序务'''
    def closeEvent(self, event):
        self.closeSDKserver()
        event.accept()

    # endregion
    #########################显示#########################
    # region --------------显示
    '''显示注意力数据'''
    def show_attetion_data(self,dataString):
        self.attention_data[1].append(float(dataString))
        self.attention_data[1].pop(0)
        self.attention_curve.setData(self.attention_data[0], self.attention_data[1])

    '''显示电生理数据'''
    def show_data(self,dataString):
        extracted_data = dataString[dataString.find('[') + 1:dataString.find(']')]
        dataArray = extracted_data.split(',')
        for data in dataArray:
            self.EMG_data[1].append(float(data))
            self.EMG_data[1].pop(0)
        self.EMG_curve.setData(self.EMG_data[0], self.EMG_data[1])

    '''显示阻抗数据'''
    def show_impendance(self,dataString):
        if self.impendanceCnt >= 5:
            self.impendanceCnt = 0
            self.msgSignal.emit('当前阻抗值为：%sΩ'%dataString)

    '''显示log'''
    def show_msg(self, msg):
        _dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        _cnt = self.myMsgBox.count() + 1
        msg = '%s :  %s' % (_dt, msg)

        cnt = self.myMsgBox.count()
        if cnt > 15:                    #最多显示N条信息
            self.myMsgBox.takeItem(0)
        self.myMsgBox.addItem(msg)

    '''显示箭头'''
    def setControlStatus(self, dataString):
        index = int(dataString)
        if index == -1:
            status = False
        else:
            status = True

        for i in range(0, 5):
            if index == i:
                self.controlSubWidget[i].setFilled(status)
            else:
                self.controlSubWidget[i].setFilled(False)

    """显示设备列表"""
    def addDeviceNames(self,deviceNames):
        self.deviceBox.clear()
        if deviceNames:
            deviceNameList = deviceNames.split(',')
            if deviceNameList:
                nameList = []
                if deviceNameList:
                    for nameNew in deviceNameList:
                        if not nameNew in nameList:
                            nameList.append(nameNew)
                            self.deviceBox.addItem(nameNew)
                self.deviceBox.setCurrentIndex(0)

    """显示力量曲线"""
    def drawPower(self,powerString):
        self.power_data[1].append(float(powerString))
        self.power_data[1].pop(0)
        self.power_curve.setData(self.power_data[0], self.power_data[1])

    # endregion
    #########################按钮#########################
    # region --------------按钮
    """记录数据按钮功能"""
    def record_begin_fun(self):
        self.record_start_timeStamp = self.currentPoitStamp()

        patientName = ''
        gender = 0
        age = 18

        _name, ok = QInputDialog.getText(self, '姓名', u'请输入姓名', QLineEdit.Normal)
        if ok and _name:
            patientName = _name

        _gender, ok = QInputDialog.getItem(self, '性别', '请选择性别', ['男', '女'])
        if ok and _gender:
            gender = _gender

        _age, ok = QInputDialog.getInt(self, "年龄", "请输入年龄", value=21)
        if ok and _age:
            age = _age

        # fileName
        now = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
        fileName = now + '_EEG.edf'

        #存储路径
        currentPath = os.path.dirname(os.path.abspath(__file__))
        savePath = (currentPath + '/tempDatas/' + fileName)

        # channelNum
        channelNum = '3'
        # sflist
        sflist = '@'.join(['250', '30', '30'])
        # channelNameList
        channelNameList = '@'.join(['FP1-FP2', 'Accelerometer', 'Gyroscope'])
        # gender
        gender = str(['女', '男'].index(gender))
        # deviceName
        deviceName = 'BM01'
        birthday = '1991-1-1'
        framelenth = '5'

        #调用存储命令
        reflextion.startRecording(savePath, channelNum, sflist, channelNameList, gender, deviceName, birthday, patientName, framelenth)

    """连接按钮功能"""
    def connectFun(self):
        deviceName = self.deviceBox.currentText()
        protocal = self.protocalBox.currentIndex()
        reflextion.connectDevice(deviceName,protocal)

    """更改滤波器按钮功能"""
    def filterChangeFun(self):
        hp = float(self.hpBox.text())
        lp = float(self.lpBox.text())
        filterType = self.filterBox.currentIndex()
        allowFiltering = self.butterBox.isChecked()
        allowNorch = self.northBox.isChecked()
        #陷波中心频率
        main = 50
        #滤波器阶数
        order = 4
        #滤波器编号
        filterIndex = 0
        #采样频率，默认250
        samplerate = 250
        if not allowFiltering:
            body = str(filterIndex)
            #销毁滤波器
            reflextion.destroyFilter()
        else:
            #更改滤波器
            reflextion.changeFilter(filterType,hp,lp,samplerate,allowNorch,main,order,filterIndex)

    '''事件按钮按下'''
    def userEventFun_start(self):
        if not self.record_start_timeStamp:
            return

        #记录事件起始时间
        self.temEventStart = (self.currentPoitStamp() - self.record_start_timeStamp) * 10

    '''事件按钮抬起'''
    def userEventFun_end(self):
        if not self.temEventStart:
            return

        #计算出持续时间
        temEventDuration = int((self.currentPoitStamp() - self.temEventStart/10.0 - self.record_start_timeStamp) * 10)  # E.g. 34.071 seconds must be written as 340710
        if temEventDuration < 500:
            temEventDuration = 0

        #描述
        des = self.eventBox.text()
        if not des:
            des = 'undefined'

        reflextion.writeAnnotation(des,str(self.temEventStart),str(temEventDuration))

    '''获取系统时间戳'''
    def currentPoitStamp(self):
        t = time.time()
        diag_tickTime = (int(round(t * 1000)))  # 毫秒
        return diag_tickTime
    # endregion

    #####################################################
'''启动程序'''
if __name__ == '__main__':
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # 防止控件变形
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())