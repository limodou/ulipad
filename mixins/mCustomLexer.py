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
#   $Id: mFormat.py 1457 2006-08-23 02:12:12Z limodou $

import wx.stc
from modules import Mixin

def editor_init(win):
    wx.stc.EVT_STC_STYLENEEDED(win, win.GetId(), win.OnStyleNeeded)
#    wx.EVT_PAINT(win, win.OnStyleNeeded)
Mixin.setPlugin('editor', 'init', editor_init)

def OnStyleNeeded(win, event):
    lexer = getattr(win, 'lexer', None)
    if lexer:
        if lexer.syntaxtype == wx.stc.STC_LEX_CONTAINER:
            lexer.styleneeded(win, event.GetPosition())
Mixin.setMixin('editor', 'OnStyleNeeded', OnStyleNeeded)