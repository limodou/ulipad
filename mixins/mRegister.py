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
#   $Id: mRegister.py 1633 2006-10-21 08:31:55Z limodou $

import wx
import os
import sys
from modules import Mixin
from modules.Debug import error
from modules import common


if wx.Platform == '__WXMSW__':
    import _winreg

    def add_mainframe_menu(menulist):
        menulist.extend([ ('IDM_TOOL',
            [
                (890, '-', '', wx.ITEM_SEPARATOR, '', ''),
                (900, 'IDM_TOOL_REGISTER', tr('Register To Windows Explorer'), wx.ITEM_NORMAL, 'OnToolRegister', tr('Registers UliPad to the context menu of Windows Explorer.')),
                (910, 'IDM_TOOL_UNREGISTER', tr('Unregister From Windows Explorer'), wx.ITEM_NORMAL, 'OnToolUnRegister', tr('Unregisters UliPad from the context menu of Windows Explorer.')),
            ]),
        ])
    Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

    def OnToolRegister(win, event):
        try:
            key = _winreg.OpenKey(_winreg.HKEY_CLASSES_ROOT, '*', _winreg.KEY_ALL_ACCESS)
            filename = os.path.basename(sys.argv[0])
            f, ext = os.path.splitext(filename)
            if ext == '.exe':
                command = '"%s" "%%L"' % os.path.normpath(common.uni_work_file(filename))
            else:
                path = os.path.normpath(common.uni_work_file('%s.pyw' % f))
                execute = sys.executable.replace('python.exe', 'pythonw.exe')
                command = '"%s" "%s" "%%L"' % (execute, path)
            _winreg.SetValue(key, 'shell\\UliPad\\command', _winreg.REG_SZ, common.encode_string(command, common.defaultfilesystemencoding))
            common.note(tr('Done'))
        except:
            error.traceback()
            wx.MessageDialog(win, tr('Registering UliPad to the context menu of Windows Explorer failed.'), tr("Error"), wx.OK | wx.ICON_EXCLAMATION).ShowModal()
    Mixin.setMixin('mainframe', 'OnToolRegister', OnToolRegister)

    def OnToolUnRegister(win, event):
        try:
            key = _winreg.OpenKey(_winreg.HKEY_CLASSES_ROOT, '*\\shell', _winreg.KEY_ALL_ACCESS)
            _winreg.DeleteKey(key, 'UliPad\\command')
            _winreg.DeleteKey(key, 'UliPad')
            common.note(tr('Successful!'))
        except:
            error.traceback()
            wx.MessageDialog(win, tr('Unregistering UliPad from the context menu of Windows Explorer failed.'), tr("Error"), wx.OK | wx.ICON_EXCLAMATION).ShowModal()
    Mixin.setMixin('mainframe', 'OnToolUnRegister', OnToolUnRegister)
