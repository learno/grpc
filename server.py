# -*- coding: UTF-8 -*-
import operator
import gevent
from gevent import socket

from base import JsonAvatar

class Avatar(JsonAvatar):
    cmp = operator.lt #lt或gt
    step = -1 #-1或1
    end = -100 #maxint或minint

    def remote_echo(self, a, b):
        return a, b

class RPCServer(object):
    backlog = 500

    def __init__(self, host, port):
        self.server = socket.socket()
        self.server.bind((host, port))
        self.birds = {}

    def start(self):
        self.server.listen(self.backlog)
        while True:
            try:
                new_sock, address = self.server.accept()
            except KeyboardInterrupt:
                break
            bird = Avatar(new_sock)
            gevent.spawn(bird._recv)
#            self.birds[0] = bird

if __name__ == '__main__':
    print u'start'
    s = RPCServer('localhost', 8888)
    s.start()
    print u'end'


