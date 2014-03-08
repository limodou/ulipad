#   Programmer:     limodou
#   E-mail:         limodou@gmail.com
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

from modules import Mixin
import wx
import os
from modules import common

menulist = [('IDM_PYTHON', #parent menu id
                [
                        (160, 'IDM_PYTHON_DEBUG', tr('Debug In WinPdb'), wx.ITEM_NORMAL, 'OnPythonDebug', tr('Debug the current program in WinPdb.')),
                ]),
]
Mixin.setMixin('pythonfiletype', 'menulist', menulist)

toollist = [
        (2130, 'debug'),
]
Mixin.setMixin('pythonfiletype', 'toollist', toollist)

#order, IDname, imagefile, short text, long text, func
toolbaritems = {
        'debug':(wx.ITEM_NORMAL, 'IDM_PYTHON_DEBUG', 'images/debug.png', tr('Debug'), tr('Debug the current program in WinPdb.'), 'OnPythonDebug'),
}
Mixin.setMixin('pythonfiletype', 'toolbaritems', toolbaritems)

def OnPythonDebug(win, event):
    interpreters = dict(win.pref.python_interpreter)
    interpreter = interpreters.get(win.pref.default_interpreter, '')
    if not interpreter:
        common.showerror(win, tr("You didn't setup python interpreter, \nplease setup it first in Preference dialog"))
        return
    try:
        import wx
    except:
        common.showerror(win, tr("You should install wxPython package to run the Debugger."))
        return

    cmd = os.path.normpath('"%s" "%s/packages/winpdb/winpdb.py" -t -c "%s" "%s"' % (interpreter, win.app.workpath, win.document.filename, win.document.args))
    wx.Execute(cmd)
Mixin.setMixin('mainframe', 'OnPythonDebug', OnPythonDebug)
