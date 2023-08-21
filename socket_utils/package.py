#coding=utf8
'''
        4字节 特殊字符0xF4F4F4F4
        4字节 包标志
        4字节 包体长度
        4字节 包体数据类型
        4字节 CMD
        N字节 包体

'''

HEAD_LEN = 20
MAGIC_NUM = 0xF4

import struct, string

def packMsg(data):
    sign = data['sign']
    type = data['type']
    msg = data['msg']
    size = len(msg)
    cmd = data['cmd']
    fmt = '!5i%ds'%size
    pack = struct.pack(fmt,MAGIC_NUM,sign,size,type,cmd,msg.encode('utf-8'))
    #pack = struct.pack(fmt, MAGIC_NUM, sign, size, type, cmd, bytes(msg, encoding='ascii'))
    return pack

class depackMethod():
    def __init__(self):
        self.buff = ''
        self.lbuff = ''

    def data_push(self,b):
        self.buff = b

    def depackMsg(self):
        index = 0
        ls = []
        while True:
                buff = ''
                if len(self.lbuff) == 0:
                    buff = self.buff
                else:
                    buff = self.lbuff + self.buff
                #是否能够解析出头部
                if len(self.buff) < index + HEAD_LEN:
                    self.lbuff = self.buff[index:]
                    break
                nope,sign, size, type, cmd = struct.unpack('!5i', buff[index:index + HEAD_LEN])

                #size过大
                if index + HEAD_LEN + size > len(buff):
                   self.lbuff = self.buff
                   break

                data = buff[index + HEAD_LEN:index + HEAD_LEN + size]
                index = index + HEAD_LEN + size
                pack = {}
                pack['body'] = data
                pack['cmd'] = cmd
                pack['type'] = type
                pack['sign'] = sign
                ls.append(pack)
        return ls