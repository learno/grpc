# -*- coding: UTF-8 -*-
try:
    import ujson as json
except:
    import json
import operator
import sys

import gevent
from gevent import socket

from base import BaseAvatar

class ClientAvatar(BaseAvatar):
    cmp_func = operator.gt #lt or gt
    step = 1 #-1 or 1
    end = sys.maxint #maxint or -maxint
    serialization = json

    def echo(self, a):
        return a

    def on_connection(self):
        print 'on_connection'
        print client.avatar.remote.echo(1, 2)
        #result = client.avatar.remote_async('echo', 1, 2)
        try:
            print client.avatar.remote.raise_()
        except Exception, e:
            print 'Error', e
        #print result.get()
        print 'call end'

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
    client = Client('127.0.0.1', 8888, ClientAvatar)
    client.connect()
    print 'end'



