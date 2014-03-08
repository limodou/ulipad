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

class ConCurrentClient(asynchat.async_chat):
    def __init__(self, host='127.0.0.1', port=5555):
        asynchat.async_chat.__init__(self)
        self.bindobj = None
        self.buffer = []
        self.state = 'length'
        self.set_terminator(8)
        self.create_socket (socket.AF_INET, socket.SOCK_STREAM)
        self.connect ((host, port))

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
    
    def handle_close (self):
        self.close()
        self._call_func('server_close')
        
    def _call_func(self, func, *args, **kwargs):
        if self.bindobj and hasattr(self.bindobj, func):
            f = getattr(self.bindobj, func)
            r = f(*args, **kwargs)
            return r

    def call_obj_func(self, info):
        func, p = CommandParse.parse_call(info)
        self._call_func(func, *p['tuple'], **p['dict'])
        
    def call(self, func, *args, **kwargs):
        s = CommandParse.call_dumps(func, *args, **kwargs)
        self.push(s)

    def bindobject(self, obj):
        self.bindobj = obj
    
def start_client(host, port, bindobj):
    client = ConCurrentClient(host, port)
    client.bindobject(bindobj)
    from modules import Casing
    d = Casing.Casing(asyncore.loop, 1)
    d.start_thread()
    return client

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print 'Usage: %s <server-host> <server-port>' % sys.argv[0]
    else:
        ps = ConCurrentClient(sys.argv[1], int(sys.argv[2]))
        ps.call("hello", 'limodou')
        ps.call("close")
        asyncore.loop()

