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
#   $Id: MyPanel.py 1852 2007-01-25 01:50:35Z limodou $
#
#   This file's code is mostly copy from DrPython. Thanks to Daniel Pozmanter

import wx
from modules import Mixin
from modules import meide as ui

def create_document_area(win):
    win.mainframe.documentarea = DocumentArea(win.top)
Mixin.setPlugin('mainsubframe', 'init', create_document_area)

class DocumentArea(wx.Panel, Mixin.Mixin):
    
    __mixinname__ = 'documentarea'
    
    def __init__(self, parent):
        self.initmixin()
        
        wx.Panel.__init__(self, parent, -1)
        
        self.sizer = ui.VBox(0).create(self).auto_layout()
        obj = self.execplugin('init', self)
        self.sizer.add(obj, proportion=1, flag=wx.EXPAND)
        
