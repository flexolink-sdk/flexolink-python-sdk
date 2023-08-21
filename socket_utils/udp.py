'''-----------------socket通信模块----------------------------------------------
socket通信类型：UDP

发送端口 6012

监听端口 6010

您可以根据您的需要自行实现UDP通信
---------------------------------------------------------------------------'''


import socket
from socket_utils.package import *
from PyQt5.QtCore import QThread, pyqtSignal

from mapping import reflextion

'''UDP侦听线程'''
class myThreadUDP(QThread):
    #发送状态名称
    stateSignal = pyqtSignal(str)
    def __init__(self,port,parent = None):
        super (myThreadUDP,self).__init__(parent)
        self.listenPort = port
        self.db = depackMethod()

    # 侦听的主循环
    def UDPlistener(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        PORT = self.listenPort
        try:
            s.bind(('', PORT))
        except:
            return

        print('Listening for broadcast at ', s.getsockname())

        while True:
            data, address = s.recvfrom(65535)  # recvfrom(BUFFERSIZE)
            self.db.data_push(data)
            unpacked = self.db.depackMsg()
            for seq in unpacked:
                cmd = seq['cmd']
                body = seq['body'].decode()
                reflextion.reflex(body,cmd)

    def run(self):
        self.UDPlistener()


class UdpManager:
    def __init__(self):
        self.sendPort = 6012
        self.listenPort = 6010
        self.udpThread = None

    #初始化
    def UDPserverInit(self):
        #发广播的sockert,端口6012
        self.sendSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sendSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        #收广播的线程，端口6010
        self.udpThread = myThreadUDP(self.listenPort)
        self.udpThread.start()

        print("SOCKET 服务器启动完成...")

    # UDP广播
    def sendCMD(self, msg, cmd):
        _msg = msg
        data = dict(sign=1, type=1, msg=_msg, cmd=cmd)
        pack = packMsg(data)

        # 广播
        self.sendSocket.sendto(pack, ('127.0.0.1', self.sendPort))  # <broadcast>

    def shutDownThread(self):
        if self.udpThread:
            self.udpThread.terminate()  # 结束此进程
            self.udpThread.wait()  # 等待结束完成
            if self.udpThread.isFinished():  # 如果当前线程已经完成工作，则删除
                del self.udpThread