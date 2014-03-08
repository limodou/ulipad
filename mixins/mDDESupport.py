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
#   $Id: mDDESupport.py 1863 2007-01-26 12:08:14Z limodou $

__doc__ = 'simulate DDE support'

import sys
from modules import DDE
from modules import Mixin
from modules import common

def app_init(app, filenames):
#    print 'ddeflag', app.ddeflag
    if app.ddeflag:
        x = common.get_config_file_obj()
        port = x.server.get('port', 50009)
        if DDE.senddata('\r\n'.join(filenames), port=port):
            print """Found previous instance of UliPad and the files will be 
opened in it, current instance will be quit. If you have not 
seen the UliPad started, please change the DDE support port at 
config.ini with :

    [server]
    port=50001 #or other port number

If it's alreay exit, contact ulipad author to get help."""
            sys.exit(0)
        else:
            DDE.run(port=port)
Mixin.setPlugin('app', 'dde', app_init, Mixin.HIGH, 0)

def afterclosewindow(win):
    if win.app.ddeflag:
        DDE.stop()
Mixin.setPlugin('mainframe', 'afterclosewindow', afterclosewindow)

def openfiles(win, files):
    if files:
        doc = None
        firstdoc = None
        for filename in files:
            doc = win.editctrl.new(filename, delay=True)
            if not firstdoc:
                firstdoc = doc
        win.Show()
        win.Raise()
        if firstdoc:
            win.editctrl.switch(firstdoc)
Mixin.setMixin('mainframe', 'openfiles', openfiles)
