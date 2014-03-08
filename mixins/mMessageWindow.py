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

import wx
from modules import Mixin
from modules import Globals

def other_popup_menu(win, menus):
    menus.extend([(None, #parent menu id
        [
            (190, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (200, 'IDPM_GOTO', tr('Goto error line'), wx.ITEM_NORMAL, 'OnGoto', tr('Goto the line that occurs the error.')),
        ]),
    ])
Mixin.setPlugin('messagewindow', 'other_popup_menu', other_popup_menu)

def OnGoto(win, event):
    line = win.GetCurLine()
    ret = win.execplugin('goto_error_line', win, *line)
    if ret:
        filename, lineno = ret
        Globals.mainframe.editctrl.new(filename)
        wx.CallAfter(Globals.mainframe.document.goto, int(lineno))
Mixin.setMixin('messagewindow', 'OnGoto', OnGoto)

def messagewindow_init(win):
    wx.EVT_LEFT_DCLICK(win, win.OnGoto)
Mixin.setPlugin('messagewindow', 'init', messagewindow_init)

def pref_init(pref):
    pref.clear_message = True
    pref.message_wrap = False
    pref.message_setfocus_back = False
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('General'), 170, 'check', 'clear_message', tr('Autoclear messages window content at program run'), None),
        (tr('General'), 180, 'check', 'message_setfocus_back', tr('Set focus back to document window after program run'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def add_mainframe_menu(menulist):
    menulist.extend([
        ('IDM_EDIT',
        [
            (291, 'IDM_EDIT_CLEARMESSAGE', tr('Clear Messages Window') + '\tShift+F5', wx.ITEM_NORMAL, 'OnEditClearMessage', tr('Clears content of messages window.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def OnEditClearMessage(win, event):
    if hasattr(win, 'messagewindow') and win.messagewindow:
        win.messagewindow.OnClear(None)
Mixin.setMixin('mainframe', 'OnEditClearMessage', OnEditClearMessage)

def start_run(win, messagewindow):
    if win.pref.clear_message:
        messagewindow.SetText('')
Mixin.setPlugin('mainframe', 'start_run', start_run)
    