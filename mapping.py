'''
-----------------接口显示模块----------------------------------------------
这里显示了所有您可能会用到的接口，用一个mapping类来管理

这些接口包括两个部分：1.下行命令  2.回调命令

下行命令是您发给SDK的命令，包含了所有您可用的方法，比如连接设备、获取数据等等

回调命令是SDK回传给您的命令，包含了操作的结果（成功与否）以及回调的数据

reflex方法将回调命令和一些函数绑定在一起，请注意，您并不需要实现所有的函数，根据需要选择
---------------------------------------------------------------------------
'''

#coding=utf8
from enum import Enum
class result(Enum):
    Passed = 0
    Faild = 1
    NA = 2

class Mapping:
    def __init__(self,app = None):
        self.app = app
    ###############################回调命令################################
    # region --------------回调命令
    def reflex(self, body, cmd):
        if (cmd == 1000):# SDK服务被重置
            self.onInitfun(body)
        if (cmd == 1001):# 找到了设备
            self.onDeviceFound(body)
        elif (cmd == 1002):# 设备被连接
            self.onDeviceConnect(body)
        elif (cmd == 1003):# 电生理数据回调
            self.onDataPull(body)
        elif (cmd == 1005):# 注意力数据回调
            self.onRecieveAttentionData(body)
        elif (cmd == 1006):# 停止注意力动作回调
            self.onEndAttention(body)
        elif (cmd == 1007):# 阻抗数据回调
            self.onDependanceDataPull(body)
        elif (cmd == 1008):# 阻抗测试被关闭
            self.onDependanceDataStop(body)
        elif (cmd == 1009):# 设备主动断开
            self.onDevicedisConnect(body)
        elif (cmd == 1010):# 滤波器被改变
            self.onFilterChanged(body)
        elif (cmd == 1011):# 滤波器被销毁
            self.onFilterDestroyed(body)
        elif (cmd == 1012):# 已经开始记录数据
            self.onRecordingStarted(body)
        elif (cmd == 1013):# 已经停止记录数据
            self.onRecordingStopped(body)
        elif (cmd == 1014):# 成功写入事件
            self.onWritternEvent(body)
        elif (cmd == 1015):# 力量值回调
            self.onRecievePowerData(body)
        elif (cmd == 1016):# 停止力量值动作回调
            self.onEndPower(body)
        elif (cmd == 1017):# 手势数据回调
            self.onRecievePositionData(body)
        elif (cmd == 1018):# 停止位置数据动作回调
            self.onEndPosition(body)
        elif (cmd == 1019):# 上一个动作回调
            self.onAction(body)
        elif (cmd == 1020):# 通知信息
            self.onRecieveInfos(body)
    # endregion

    ###############################回调方法################################
    # region --------------回调方法-----------------
    # SDK返回的结果可以通过这些方法获取
    '''初始化SDK'''
    def onInitfun(self, re):
        pass

    '''收到通知信息'''
    def onRecieveInfos(self,dataString):
        self.app.msgSignal.emit(dataString)

    '''找到设备（名）'''
    def onDeviceFound(self, dataString):
        self.app.deviceNameSignal.emit(dataString)

    '''设备是否已经成功连接'''
    def onDeviceConnect(self, re):
        pass

    '''数据回调'''
    def onDataPull(self, dataString):
        self.app.dataSignal.emit(dataString)

    '''阻抗回调'''
    def onDependanceDataPull(self, dataString):
        self.app.impendanceSignal.emit(dataString)

    '''注意力数值回调'''
    def onRecieveAttentionData(self, dataString):
        self.app.attetionSignal.emit(dataString)

    '''姿态数值回调'''
    def onRecievePositionData(self, dataString):
        self.app.controlSignal.emit(dataString)

    '''力量数值回调'''
    def onRecievePowerData(self, powerString):
        self.app.powerSignal.emit(powerString)

    '''停止阻抗回调'''
    def onDependanceDataStop(self, re):
        pass

    '''设备已经断开'''
    def onDevicedisConnect(self, re):
        pass

    '''滤波器被改变'''
    def onFilterChanged(self, re):
        pass

    '''滤波器被销毁'''
    def onFilterDestroyed(self, re):
        pass

    '''停止注意力数值回调'''
    def onEndAttention(self, re):
        pass

    '''停止力量数值回调'''
    def onEndPower(self, re):
        pass

    '''开始记录数据'''
    def onRecordingStarted (self, re):
        pass

    '''停止记录数据'''
    def onRecordingStopped (self, re):
        pass

    '''成功写入事件'''
    def onWritternEvent (self, re):
        pass

    '''姿态计算停止'''
    def onEndPosition(self, re):
        pass

    '''上一个指令是否成功'''
    def onAction(self, re):
        _re = result(int(re))
        if _re == result.Passed:
            print('上一个动作成功了')
        else:
            print('上一个动作失败了')

    # endregion
    ###############################下行命令################################
    # region --------------下行命令
    def InitSDK(self):
        '''
        初始化SDK
        '''
        self.app.udp.sendCMD('', 2000)

    def searchDevice(self):
        '''
        查找设备（名）.对应的回调：1001
        '''
        self.app.udp.sendCMD('', 2001)

    def connectDevice(self,deviceName,protocal):
        '''
        连接设备，对应的回调：1002
        :param deviceName：设备名，可以通过searchDevice获取
        :param protocal: 协议，可以取0，1，2，默认为0，不建议修改
        '''
        self.samplerate = [250, 250, 500, 1000][protocal]  # 采样率
        _cmd = deviceName + ',' + str(protocal)
        self.app.udp.sendCMD(_cmd, 2002)

    def startPulldata(self):
        '''
        开始拉取数据，对应回调1003
        '''
        self.app.udp.sendCMD('', 2003)

    def stopPulldata(self):
        '''
        停止拉取数据，对应回调1004
        '''
        self.app.udp.sendCMD('', 2004)

    def startAttetionTest(self):
        '''
        开始进行注意力测试
        '''
        self.app.udp.sendCMD('', 2005)

    def stopAttetionTest(self):
        '''
        停止注意力测试
        '''
        self.app.udp.sendCMD('', 2006)

    def startImpedance(self):
        '''
        开始阻抗检测
        '''
        self.app.udp.sendCMD('', 2007)

    def stopImpedance(self):
        '''
        停止阻抗检测
        '''
        self.app.udp.sendCMD('', 2008)

    def abortConnection(self):
        '''
        断开设备连接
        '''
        self.app.udp.sendCMD('', 2009)

    def startRecording(self,savePath, channelNum, sflist, channelNameList, gender, deviceName, birthday, patientName, framelenth):
        '''
        开始记录数据，数据将以edf格式保存在指定目录
        :param savePath:                    保存路径
        :param channelNum:                  通道数，固定为3
        :param sflist:                      采样率，固定为[‘250’,‘30’,‘30’]
        :param channelNameList:             通道名列表
        :param gender:                      性别，男（‘1’）女（‘0’）
        :param deviceName:                  设备名
        :param birthday:                    生日
        :param patientName:                 用户姓名
        :param framelenth:                  记录频率，固定为'5'
        '''
        body = ','.join(
            [savePath, channelNum, sflist, channelNameList, gender, deviceName, birthday, patientName, framelenth])
        self.app.udp.sendCMD(body, 2012)

    def stopRecording(self):
        '''
        停止数据记录
        '''
        self.app.udp.sendCMD('', 2013)

    def changeFilter(self, filterType, hp, lp, samplerate, allowNorch, main = 50, order = 4, filterIndex = 0):
        '''
        更改滤波器参数
        :param hp:                  高通
        :param lp:                  低通
        :param filterType:          滤波器类型
        :param allowFiltering:      是否滤波
        :param allowNorch:          是否陷波滤波
        :param main:                中心频率
        :param order:               滤波器阶数
        :param filterIndex:         滤波器序号
        '''
        body = '%d,%f,%f,%d,%d,%d,%d,%d' % (filterType, hp, lp, samplerate, allowNorch, main, order, filterIndex)
        self.app.udp.sendCMD(body, 2010)

    def destroyFilter(self,filterIndex = 0):
        '''
        销毁滤波器
        '''
        self.app.udp.sendCMD(str(filterIndex), 2011)

    def startPowerCaculation(self):
        '''
        开始计算力量值
        '''
        self.app.udp.sendCMD('', 2015)

    def stopPowerCaculation(self):
        '''
        停止力量值计算
        '''
        self.app.udp.sendCMD('', 2016)

    def startGestureCaculation(self):
        '''
        开始手势解算
        '''
        self.app.udp.sendCMD('', 2017)

    def stopGestureCaculation(self):
        '''
        停止手势解算
        '''
        self.app.udp.sendCMD('', 2018)

    def writeAnnotation(self,description,startStamp,duration):
        '''
        事件记录
        :param description: 事件的描述（事件名）
        :param startStamp: 开始记录的时间点
        :param duration: 事件的持续时间
        '''
        seq = (description,startStamp,duration)
        _body = ','.join(seq)
        self.app.udp.sendCMD(_body, 2014)
    # endregion
    #####################################################################
reflextion = Mapping()
