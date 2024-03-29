# -*- coding: utf-8 -*-
from struct import pack, unpack
from traceback import print_exc
from sys import maxint
import weakref

import gevent
from gevent.event import AsyncResult

class Protocol(object):
    """
    base protocol for socket

    Note: For best match with hardware and network realities, the value of bufsize should be a relatively small power of 2.
    """
    bufsize = 4096
    def __init__(self, sock):
        assert self._receive.im_class is not Protocol, Exception(
            'Must Overload _receive')
        self.sock = sock

    def _recv(self):
        buff = ''
        while True:
            if len(buff) >= 4:
                message_len = unpack('>I', buff[:4])[0]
                if len(buff) >= 4 + message_len:
                    message = buff[4:4 + message_len]
                    buff = buff[4 + message_len:]
                    try:
                        gevent.spawn(self._receive, message)
                    except:
                        print_exc()
                    finally:
                        continue

            # read message
            try:
                data = self.sock.recv(self.bufsize)
            except:
                print_exc()
                break
            # end recv
            if not data:
                break
            
            buff += data
        self.sock.close()
        self.on_disconnection()

    def _send(self, data):
        data_len = pack('>I', len(data))
        self.sock.sendall(data_len + data)

    def _receive(self, data):
        raise

    def on_connection(self):
        pass

    def on_disconnection(self):
        pass


class Remote(object):
    __slots__ = ('_avater',)
    def __init__(self, avatar):
        self._avater = weakref.proxy(avatar)

    def __getattr__(self, name):
        def func(*args, **kargs):
            result = self._avater._async_call(name, args, kargs)
            result = result.get()
            if isinstance(result, Exception):
                raise result
            return result
        func.func_name = bytes(name)
        return func


class BaseAvatar(Protocol):
    """"""
    REQUEST = 0
    RESPONSE = 1
    EXCEPTION = 2

    end = maxint
    #the serialization must has methods is dumps and loads
    serialization = None

    def __init__(self, sock):
        Protocol.__init__(self, sock)
        self._request_id = 0
        self._results = {}
        self.remote = Remote(self)

    #def remote(self, name, *args, **kargs):
        #"""call the remote method with the synchronous mode"""
        #result = self._async_call(name, args, kargs)
        #result = result.get()
        #if isinstance(result, Exception):
            #raise result
        #return result

    #def remote_async(self, name, *args, **kargs):
        #"""call the remote method with the asynchronous mode"""
        #return self._async_call(name, args, kargs)

    def _async_call(self, name, args, kargs):
        request_id = self._request_id
        #print request_id
        if self._request_id == self.end:
            self._request_id = 0
        else:
            self._request_id += 1

        args = (self.REQUEST, request_id, name, args, kargs)
        #print 'args', args
        result = AsyncResult()
        self._results[request_id] = result
        try:
            self._send(args)
        except:
            self._results.pop(request_id)
            raise
        return result

    def _send(self, data):
        """serialize and send data"""
        data = self._serialize(data)
        Protocol._send(self, data)

    def _serialize(self, data):
        """if need, overload this'"""
        return self.serialization.dumps(data)

    def _receive(self, data):
        """unserialize data and handle exception, response or request"""
        request = self._unserialize(data)
        #print 'request',request

        data_type = request[0]
        request_id = request[1]
        if data_type == self.EXCEPTION:
            exception_args = request[2]
            self._handle_exception(request_id, exception_args)
        elif data_type == self.RESPONSE:
            value = request[2]
            self._handle_response(request_id, value)
        elif data_type == self.REQUEST:
            name, args, kargs = request[2:5]
            self._handle_request(request_id, name, args, kargs)

    def _unserialize(self, data):
        """if need, overload this'"""
        return self.serialization.loads(data)

    def _handle_exception(self, request_id, exception_args):
        result = self._results.pop(request_id, None)
        if result is None:
            return
        exception = Exception(*exception_args)
        result.set(exception)

    def _handle_response(self, request_id, value):
        result = self._results.pop(request_id, None)
        if result is None:
            return
        result.set(value)

    def _handle_request(self, request_id, name, args, kargs):
        try:
            func = getattr(self, name)
            #print args
            value = func(*args, **kargs)
            response = (self.RESPONSE, request_id, value)
            #print response

        except Exception, e:
            #print u'Error:', e
            response = (self.EXCEPTION, request_id, e.args)

        self._send(response)


