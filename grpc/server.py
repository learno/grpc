# -*- coding: UTF-8 -*-
try:
    import ujson as json
except:
    import json
import operator
import sys

import gevent
from gevent.server import StreamServer

from base import BaseAvatar

class ServerAvatar(BaseAvatar):
    serialization = json

    def on_connection(self):
        print 'on_connection'
        print self.remote.echo('server')
        print self.remote.echo('next')
        print 'call end'

    def echo(self, a, b):
        print 'echo', a, b
        gevent.sleep(4)
        return a, b

    def raise_(self):
        raise Exception('test exception')

class Server(StreamServer):
    def __init__(self, listener, avatar_class, backlog=None, spawn='default', **ssl_args):
        StreamServer.__init__(self, listener, self._handle, backlog, spawn, **ssl_args)
        self.avatar_class = avatar_class
        self.avatars = []

    def _handle(self, sock, address):
        avatar = self.avatar_class(sock)
        self.avatars.append(avatar)
        gevent.spawn(avatar.on_connection)
        gevent.spawn(avatar._recv)

if __name__ == '__main__':
    print u'start'
    s = Server(('localhost', 8888), ServerAvatar)
    s.serve_forever()
    print u'end'

