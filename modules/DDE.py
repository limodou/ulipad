#   Programmer: limodou
#   E-mail:     limodou@gmail.com
#
#   Copyleft 2009 limodou
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
from modules import common

HOST = '127.0.0.1'
PORT = 50000

class DDEServer(asyncore.dispatcher):
    def __init__(self, host=HOST, port=PORT):
        asyncore.dispatcher.__init__(self)
        self.clients = []
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(2)

    def handle_accept(self):
        client = Receiver(self, self.accept())
        self.clients.append(client)
        
class Receiver(asynchat.async_chat):
    def __init__(self, server, (conn, addr)):
        self.addr = addr
        asynchat.async_chat.__init__ (self, conn)
        self.set_terminator('\r\n\r\n')
        self.server = server
        self.buffer = []

    def collect_incoming_data(self, data):
        self.buffer.append(data)
        
    def found_terminator(self):
        files  = ''.join(self.buffer)
        
        import wx
        import Globals
        wx.CallAfter(Globals.app.frame.openfiles, unicode(files, 'utf-8').splitlines())
        
    def handle_close (self):
        if self.server.clients.count(self) > 0:
            self.server.clients.remove(self)
        self.close()
    
server = None
def run(host=HOST, port=PORT):
    global server
    
    server = DDEServer(host, port)
    from modules import Casing
    d = Casing.Casing(asyncore.loop, 1)
    d.start_thread()
    return server

def stop():
    if server:
        server.close()
        
def senddata(data, host=HOST, port=PORT):
    try:
        sendSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sendSock.connect((host, port))
        if isinstance(data, str):
            data = unicode(data, common.defaultfilesystemencoding)
        data = data.encode('utf-8')
        sendSock.send(data+'\r\n\r\n')
        sendSock.close()
        return True
    except:
        return False

if __name__ == '__main__':
    import sys
    if sys.argv[1] == 'server':
        DDEServer()
        asyncore.loop()
    else:
        senddata('a.text')
