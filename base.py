# -*- coding: UTF-8 -*-
from struct import pack, unpack
import gevent
from gevent.event import AsyncResult
from traceback import print_exc
from sys import maxint as MAXINT


#from gevent.event import AsyncResult
#from pyamf.amf3 import decode, encode, MIN_29B_INT
#from pyamf import DecodeError
import simplejson as json

#import operator

class Protocol(object):
    """
    """
    bufferSize = 1024
    def __init__(self, sock):
        self.sock = sock

    def _recv(self):
        print '_recv'

        buff = []
        body_len = None
        buff_len = 0
        data = ''
        while True:
            print 'loop'
            #handle segment data
            if not data:
                try:
                    data = self.sock.recv(self.bufferSize)
                except Exception, e:
                    print_exc()
                    print e
                    break

                if not data:
                    print 'break'
                    break

            print 'repr:', repr(data)#
            #new segment
            if body_len is None:
                body_len = unpack('>I', data[:4])[0]
                data = data[4:]

            buff.append(data)
            buff_len += len(data)

            print 'buff_len, body_len', buff_len, body_len#
            #not enough
            if buff_len < body_len:
                data = ''
                continue

            data = ''.join(buff)
            del buff[:]
            buff_len = 0
            body = data[:body_len]
            #rest data
            data = data[body_len:]
            body_len = None


            try:
                gevent.spawn(self._receive, body)
            except Exception, e:
                print_exc()
                print e
                continue

        self.sock.close()

    def _send(self, data):
        data_len = pack('>I', len(data))
        self.sock.sendall(data_len + data)

    def _receive(self, _):
        pass


class JsonAvatar(Protocol):
    """
    """
    #use for judge response or request
    cmp = None #lt或gt
    step = None #-1或1
    end = None #maxint或minint
    def __init__(self, sock):
        Protocol.__init__(self, sock)
        self.__request_id = self.step
        self.__results = {}



    def call_remote(self, name, *args):
        request_id = self.__request_id
        print request_id
        if self.__request_id == self.end:
            self.__request_id = self.step
        else:
            self.__request_id += self.step

        args = (request_id, name) + args
        print args
        self._send(args)
        result = AsyncResult()
        self.__results[request_id] = result
        print 'result.get'
        return result.get()

    def _receive(self, data):
        """unserialize data"""
        request = json.loads(data)
        print request

        request_id = request[0]
        if self.cmp(request_id, 0):
            #receive response
            result = self.__results.pop(request_id, None)
            result.set(request[1])
            return

        #handle request
        name, args = request[1], request[2:]
        try:
            func = getattr(self, 'remote_' + name)
            print args
            result = func(*args)
            response = (request_id, result)
            print response

            self._send(response)
        except Exception, e:
            print u'Error:', e

    def _send(self, data):
        """serialize and send data"""
        data = json.dumps(data)
        Protocol._send(self, data)
