# -*- coding: UTF-8 -*-
import operator

import gevent
from gevent import socket

from base import JsonAvatar


class Avatar(JsonAvatar):
    cmp = operator.gt #lt或gt
    step = 1 #-1或1
    end = 100 #maxint或minint

    def remote_echo(self, a):
        return a

    def on_connection(self):
        print 'on_connection'

class Client(object):
    def __init__(self, host, port):
        self.sock = socket.socket()
        self.address = (host, port)
        self.avatar = Avatar(self.sock)

    def connect(self):
        print 'connect'
        self.sock.connect(self.address)
        gevent.spawn(self.avatar.on_connection)
        gevent.spawn(self.avatar._recv)

    def close(self):
        self.sock.close()


if __name__ == '__main__':
    c = Client('127.0.0.1', 8888)
    c.connect()
    print '::', c.avatar.call_remote('echo', 1, 2)
    gevent.sleep(10)




