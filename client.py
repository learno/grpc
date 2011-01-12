# -*- coding: UTF-8 -*-
import operator

import gevent
from gevent import socket

from base import JsonAvatar


class Avatar(JsonAvatar):
    cmp = operator.gt #lt or gt
    step = 1 #-1 or 1
    end = 100 #maxint or minint

    def remote_echo(self, a):
        return a

    def on_connection(self):
        print 'on_connection'
        try:
            print '::', c.avatar.remote('echo', 1, 2)
        except Exception, e:
            print ':E:', e

        self.sock.close()

class Client(object):
    def __init__(self, host, port, avatar_class):
        self.sock = socket.socket()
        self.address = (host, port)
        self.avatar = avatar_class(self.sock)

    def connect(self):
        print 'connect'
        self.sock.connect(self.address)
        gevent.spawn(self.avatar.on_connection)
        self.avatar._recv()

    def close(self):
        self.sock.close()


if __name__ == '__main__':
    c = Client('127.0.0.1', 8888, Avatar)
    c.connect()
    print 'end'



