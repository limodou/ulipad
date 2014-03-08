#   Programmer: Tyberius Prime
#   E-mail:     tyberius_prime@coonabibba.de
#
#   Copyleft 2006 Tyberius Prime
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

"""This plugin for UliPad enables drag&drop of files into UliPad Window (toolbar)"""

import wx
from modules import Mixin, Globals

class FileDropTarget(wx.FileDropTarget):
   """This object implements drop target functionality for files"""
   def __init__(self):
       wx.FileDropTarget.__init__(self)

   def OnDropFiles(self, x, y, filenames):
       """Load files in editor"""
       win = Globals.mainframe
       for filename in filenames:
           encoding = win.execplugin('getencoding', win, win)
           win.editctrl.new(filename, encoding)


def registerDropTargetMainFrame(mainframe):
   mainframe.SetDropTarget(FileDropTarget())

Mixin.setPlugin('mainframe', 'afterinit', registerDropTargetMainFrame)
