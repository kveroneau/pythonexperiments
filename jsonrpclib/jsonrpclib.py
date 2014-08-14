#
# JSON-RPC CLIENT LIBRARY inspired by the standard library xmlrpclib
#
# an JSON-RPC client interface for Python.
#
import urllib, json, socket

class _Method(object):
    # some magic to bind an JSON-RPC method to an RPC server.
    # supports "nested" methods (e.g. examples.getStateName)
    def __init__(self, send, name):
        self.__send = send
        self.__name = name
    def __getattr__(self, name):
        return _Method(self.__send, "%s.%s" % (self.__name, name))
    def __call__(self, **kwargs):
        return self.__send(self.__name, kwargs)

class ServerProxy(object):
    def __init__(self, uri):
        protocol, uri = urllib.splittype(uri)
        if protocol not in ('socket',):
            raise IOError, 'unsupported JSON-RPC protocol'
        self.__host, self.__handler = urllib.splithost(uri)
        self.__id = 0
    def __request(self, method, params):
        s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        s.connect(urllib.splitnport(self.__host, 80))
        self.__id +=1
        data = {"jsonrpc": "2.0", "method": method, "id":self.__id}
        if params != {}:
            data.update({'params':params})
        s.send(json.dumps(data))
        resp = json.loads(s.recv(512))
        s.close()
        return resp['result']
    def __repr__(self):
        return '<ServerProxy for %s%s>' % (self.__host, self.__handler)
    __str__ = __repr__
    def __getattr__(self, name):
        return _Method(self.__request, name)
