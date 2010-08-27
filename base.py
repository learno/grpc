# -*- coding: UTF-8 -*-
from struct import pack, unpack
import gevent
from gevent.event import AsyncResult
from traceback import print_exc
from sys import maxint as MAXINT

try:
    import yajl as json
except:
    import simplejson as json

#from gevent.event import AsyncResult
#from pyamf.amf3 import decode, encode, MIN_29B_INT
#from pyamf import DecodeError

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
        raise


class BaseAvatar(Protocol):
    """"""
    #use for judge response or request
    cmp = None #lt or gt
    step = None #-1 or 1
    end = None #maxint or minint

    def __init__(self, sock):
        Protocol.__init__(self, sock)
        self.__request_id = self.step
        self.__results = {}

    def on_connection(self):
        pass

    def remote(self, name, *args, **kargs):
        """call the remote method with the synchronous mode"""
        result = self.remote_async(name, *args, **kargs)
        print 'result.get'
        result = result.get()
        if isinstance(result, Exception):
            raise result
        return result

    def remote_async(self, name, *args, **kargs):
        """call the remote method with the asynchronous mode"""
        request_id = self.__request_id
        print request_id
        if self.__request_id == self.end:
            self.__request_id = self.step
        else:
            self.__request_id += self.step

        args = (request_id, name, args, kargs)
        print args
        self._send(args)
        result = AsyncResult()
        self.__results[request_id] = result

        return result

    def _send(self, data):
        """serialize and send data"""
        self._serialize(data)
        Protocol._send(self, data)

    def _serialize(self, data):
        raise

    def _receive(self, data):
        """unserialize data and handle exception, response or request"""
        request = self._unserialize(data)
        print request

        request_id = request[0]
        if request_id is 0:
            self._handle_exception(request)

        if self.cmp(request_id, 0):
            self.__handle_response(request)
        self._handle_request(request)

    def _handle_exception(self, request):
        result_id = request[1]
        exception_args = request[2]
        result = self.__results.pop(result_id, None)
        exception = Exception(*exception_args)
        if result: result.set(exception)

    def _handle_response(self, request):
        result = self.__results.pop(request_id, None)
        value = request[1]
        if result: result.set(value)

    def _handle_request(self, request):
        name = request[1]
        args = request[2]
        kargs = request[3]
        try:
            func = getattr(self, 'remote_' + name)
            print args
            value = func(*args, **kargs)
            response = (request_id, value)
            print response

        except Exception, e:
            print u'Error:', e
            response = (0, request_id, e.args)

        self._send(response)

    def _unserialize(self, data):
        raise



class JsonAvatar(BaseAvatar):
    """
    """
    def _serialize(self, data):
        return json.dumps(data)

    def _unserialize(self, data):
        return json.loads(data)

