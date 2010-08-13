# -*- coding: UTF-8 -*-
import operator

import gevent
from gevent import socket

from base import BaseAvatar


class Avatar(BaseAvatar):
    cmp = operator.gt #lt或gt
    step = 1 #-1或1
    end = 100 #maxint或minint
    def __init__(self, sock):
        BaseAvatar.__init__(self, sock)

    def remote_echo(self, a):
        return a


class Client(object):
    def __init__(self, host, port):
        self.sock = socket.socket()
        self.address = (host, port)
        self.avatar = Avatar(self.sock)

    def connect(self):
        print 'connect'
        self.sock.connect(self.address)
        print 'connecting'
        gevent.spawn(self.avatar._recv)

    def close(self):
        self.sock.close()


if __name__ == '__main__':
    c = Client('127.0.0.1', 8888)
    c.connect()
    print '::', c.avatar.call_remote('echo', 1, 2)




