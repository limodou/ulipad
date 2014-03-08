#   Programmer: limodou
#   E-mail:     limodou@gmail.com
#
#   Copyleft 2006 limodou
#
#   Distributed under the terms of the GPL (GNU Public License)
#
#   NewEdit is free software; you can redistribute it and/or modify
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
#   $Id: ShellWindow.py 536 2006-01-23 03:44:21Z limodou $

import wx
import os
from modules import Globals

class DjangoShell(wx.Frame):
    def __init__(self, parent, path, style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT):
        if not hasattr(Globals.mainframe.pref, 'django_shell_pos'):
            pos = wx.DefaultPosition
        else:
            pos = Globals.mainframe.pref.django_shell_pos
        if not hasattr(Globals.mainframe.pref, 'django_shell_size'):
            size = wx.DefaultSize
        else:
            size = Globals.mainframe.pref.django_shell_size
        wx.Frame.__init__(self, parent, -1, 'Django Shell - [%s]' % path,
            pos, size, style)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.path = path

        from mixins import ShellWindow
        self.shell = ShellWindow.ShellWindow(self, Globals.mainframe)
        self.shell.push('import sys')
        self.shell.push('sys.path.insert(0, %s)' % path)
        self.shell.push('import os')
        self.shell.push('os.environ["DJANGO_MODULE_SETTINGS"] = %s.settings' % os.path.basename(path))
        self.shell.clear()
        self.shell.prompt()
        sizer.Add(self.shell, 1, wx.EXPAND)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        wx.EVT_CLOSE(self, self.OnClose)

    def OnClose(self, event):
        Globals.mainframe.pref.django_shell_pos = self.GetPosition()
        Globals.mainframe.pref.django_shell_size = self.GetSize()
        Globals.mainframe.pref.save()
        self.Destroy()
