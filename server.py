# -*- coding: UTF-8 -*-
import operator
import gevent
from gevent import socket, sleep
import json

from base import BaseAvatar

class ServerAvatar(BaseAvatar):
    cmp_func = operator.lt #lt or gt
    step = -1 #-1 or 1
    end = -100 #maxint or minint
    serialization = json

    def on_connection(self):
        print 'on_connection'
        print self.remote('echo', 'server')
        print self.remote('echo', 'next')
        print 'call end'

    def remote_echo(self, a, b):
        sleep(4)
        return a, b

    def remote_raise(self):
        raise Exception('test exception')

class Server(object):
    backlog = 500

    def __init__(self, host, port, avatar_class):
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
        self.sock.bind((host, port))
        self.avatar_class = avatar_class
        self.avatars = []

    def start(self):
        self.sock.listen(self.backlog)
        while True:
            try:
                new_sock, address = self.sock.accept()
            except KeyboardInterrupt:
                break
            avatar = self.avatar_class(new_sock)
            gevent.spawn(avatar.on_connection)
            gevent.spawn(avatar._recv)
            self.avatars.append(avatar)

if __name__ == '__main__':
    print u'start'
    s = Server('localhost', 8888, ServerAvatar)
    s.start()
    print u'end'

