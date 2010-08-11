# -*- coding: UTF-8 -*-
import operator

from gevent import socket

from base import BaseAvatar

class Avatar(BaseAvatar):
    cmp = operator.lt #lt或gt
    step = -1 #-1或1
    end = -100 #maxint或minint
    def __init__(self, sock):
        BaseAvatar.__init__(self, sock)

#        print self.call_remote('echo', 'luo')
#        print 'sdfds'



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
#            self.birds[0] = bird

if __name__ == '__main__':
    print u'start'
    s = RPCServer('localhost', 8888)
    s.start()
    print u'end'


