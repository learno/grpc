# -*- coding: UTF-8 -*-
from struct import pack, unpack
from traceback import print_exc

import gevent
from gevent.event import AsyncResult

class Protocol(object):
    """
    base protocol for socket

    Note: For best match with hardware and network realities, the value of bufsize should be a relatively small power of 2.
    """
    bufsize = 4096
    def __init__(self, sock):
        self.sock = sock

    def _recv(self):
        #print '_recv'

        buff = []
        body_len = None
        buff_len = 0
        data = ''
        while True:
            #print 'loop'
            #handle segment data
            if not data:
                try:
                    data = self.sock.recv(self.bufsize)
                except:
                    print_exc()
                    break

                if not data:
                    #print 'break'
                    break

            #print 'repr:', repr(data)#
            #new segment
            if body_len is None:
                body_len = unpack('>I', data[:4])[0]
                data = data[4:]

            buff.append(data)
            buff_len += len(data)

            #print 'buff_len, body_len', buff_len, body_len#
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
            except:
                print_exc()
                #print e
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
    cmp_func = None #lt or gt
    step = None #-1 or 1
    end = None #maxint or -manint

    #the serialization must has methods is dumps and loads
    serialization = None

    def __init__(self, sock):
        Protocol.__init__(self, sock)
        self._request_id = self.step
        self._results = {}

    def on_connection(self):
        pass

    def remote(self, name, *args, **kargs):
        """call the remote method with the synchronous mode"""
        result = self._async_call(name, args, kargs)
        result = result.get()
        if isinstance(result, Exception):
            raise result
        return result

    def remote_async(self, name, *args, **kargs):
        """call the remote method with the asynchronous mode"""
        return self._async_call(name, args, kargs)

    def _async_call(self, name, args, kargs):
        request_id = self._request_id
        #print request_id
        if self._request_id == self.end:
            self._request_id = self.step
        else:
            self._request_id += self.step

        args = (request_id, name, args, kargs)
        #print 'args', args
        self._send(args)
        result = AsyncResult()
        self._results[request_id] = result

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

        request_id = request[0]
        if request_id is 0:
            self._handle_exception(request)
        elif self.cmp_func(request_id, 0):
            self._handle_response(request)
        else:
            self._handle_request(request)

    def _unserialize(self, data):
        """if need, overload this'"""
        return self.serialization.loads(data)

    def _handle_exception(self, request):
        result_id, exception_args = request[1:3]
        result = self._results.pop(result_id, None)
        if result is None:
            return
        exception = Exception(*exception_args)
        result.set(exception)

    def _handle_response(self, request):
        request_id = request[0]
        result = self._results.pop(request_id, None)
        if result is None:
            return
        value = request[1]
        result.set(value)

    def _handle_request(self, request):
        request_id, name, args, kargs = request[0:4]
        try:
            func = getattr(self, 'remote_' + name)
            #print args
            value = func(*args, **kargs)
            response = (request_id, value)
            #print response

        except Exception, e:
            #print u'Error:', e
            response = (0, request_id, e.args)

        self._send(response)


