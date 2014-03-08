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
#   $Id: mIcon.py 1457 2006-08-23 02:12:12Z limodou $

import wx
from modules import Mixin
from modules import common

def init(win):
    icon = wx.EmptyIcon()
    iconfile = common.uni_work_file('ulipad.ico')
#    icon.LoadFile(iconfile, wx.BITMAP_TYPE_ICO)
    bmp = common.getpngimage(iconfile)
#    win.SetIcon(icon.CopyFromBitmap(bmp))
    win.SetIcon(wx.Icon(iconfile, wx.BITMAP_TYPE_ICO))
Mixin.setPlugin('mainframe', 'init', init)
