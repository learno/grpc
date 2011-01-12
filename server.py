# -*- coding: UTF-8 -*-
import operator
import gevent
from gevent import socket

from base import JsonAvatar

class Avatar(JsonAvatar):
    cmp = operator.lt #lt or gt
    step = -1 #-1 or 1
    end = -100 #maxint or minint
    def __init__(self, sock):
        JsonAvatar.__init__(self, sock)

    def on_connection(self):
        print 'on_connection'
        print self.remote('echo', 'server')
        print self.remote('echo', 'next')


    def remote_echo(self, a, b):
        c
        return a, b

class RPCServer(object):
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
    s = RPCServer('localhost', 8888, Avatar)
    s.start()
    print u'end'

