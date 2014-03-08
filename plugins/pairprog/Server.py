#   Programmer: limodou
#   E-mail:     limodou@gmail.com
#
#   Copyleft 2006 limodou
#
#   Distributed under the terms of the GPL (GNU Public License)
#
#   UliPad is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#   $Id$

import asynchat
import asyncore
import socket
from CommandParse import CommandParse

class ConCurrentServer(asyncore.dispatcher):
    def __init__ (self, host='127.0.0.1', port=5555):
        asyncore.dispatcher.__init__(self)
        self.bindobj = None
        self.clients = []
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accept(self):
        client = Receiver(self, self.accept())
        self.clients.append(client)
        
    def shut_down(self):
        for c in self.clients:
            c.close()
        self.close()
        self.clients = []
        
    def close_client(self, addr):
        for i, c in enumerate(self.clients):
            if c.addr == addr:
                c.close()
                self.clients.remove(c)
                break
        
    def bindobject(self, obj):
        self.bindobj = obj
        
    def broadcast(self, func, *args, **kwargs):
        for c in self.clients:
            c.call(func, *args, **kwargs)
            
    def broadcastexceptfor(self, addr, func, *args, **kwargs):
        for c in self.clients:
            if c.addr != addr:
                print 'exceptfor', addr, func, args, kwargs
                c.call(func, *args, **kwargs)
                
    def sendto(self, addr, func, *args, **kwargs):
        for c in self.clients:
            if c.addr == addr:
                c.call(func, *args, **kwargs)

# Command format
#  <xxxxxxxx>commandname\t<pickled parameter>
#  <xxxxxxxx> is the length of pickled parameter + '\t' + commandname
#  <pickled parameter> is a dict, should be {'tuple':tuple parameter, 'dict':dict parameter}
class Receiver(asynchat.async_chat):
    def __init__ (self, server, (conn, addr)):
        self.addr = addr
        asynchat.async_chat.__init__ (self, conn)
        self.set_terminator (8)
        self.server = server
        self.buffer = []
        self.state = 'length'
        self._call_func('client_create')

    def collect_incoming_data (self, data):
        self.buffer.append(data)
        
    def found_terminator (self):
        data = ''.join(self.buffer)
        self.buffer = []
        if self.state == 'length':
            length = int(data)
            self.set_terminator(length)
            self.state = 'call'
        elif self.state == 'call':
            self.set_terminator(8)
            self.state = 'length'
            self.call_obj_func(data)
            
    def _call_func(self, func, *args, **kwargs):
        if self.server.bindobj and hasattr(self.server.bindobj, func):
            f = getattr(self.server.bindobj, func)
            r = f(self.addr, *args, **kwargs)
            return r

    def handle_close (self):
        if self.server.clients.count(self) > 0:
            self.server.clients.remove(self)
        self.close()
        self._call_func('client_close')
        
    def call_obj_func(self, info):
        func, p = CommandParse.parse_call(info)
        self._call_func(func, *p['tuple'], **p['dict'])
    
    def call(self, func, *args, **kwargs):
        s = CommandParse.call_dumps(func, *args, **kwargs)
        self.push(s)
        
def start_server(host, port, bindobj):
    server = ConCurrentServer(host, port)
    server.bindobject(bindobj)
    from modules import Casing
    d = Casing.Casing(asyncore.loop, 1)
    d.start_thread()
    return server

if __name__ == '__main__':
    class TestObj(object):
        def __init__(self, server):
            self.server = server
            
        def hello(self, addr, name):
            print 'TestObj', 'hello', addr, name
            
        def close(self, addr):
            self.server.shut_down()
            
        def client_close(self, addr):
            print 'client_close', addr
            
        def client_create(self, addr):
            print 'client_create'
            
    import sys
    if len(sys.argv) < 3:
        print 'Usage: %s <server-host> <server-port>' % sys.argv[0]
    else:
        ps = ConCurrentServer(sys.argv[1], int(sys.argv[2]))
        obj = TestObj(ps)
        ps.bindobject(obj)
        asyncore.loop()
