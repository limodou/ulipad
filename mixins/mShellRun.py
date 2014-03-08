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
#   $Id: mShellRun.py 1566 2006-10-09 04:44:08Z limodou $

__doc__ = 'run external tools'

import os
import wx
from modules import Mixin
from modules import makemenu

def pref_init(pref):
    pref.shells = []
Mixin.setPlugin('preference', 'init', pref_init)

def add_mainframe_menu(menulist):
    menulist.extend([('IDM_TOOL',
        [
            (100, 'IDM_SHELL', tr('External Tools'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDM_SHELL', #parent menu id
        [
            (100, 'IDM_SHELL_MANAGE', tr('External Tools Manager...'), wx.ITEM_NORMAL, 'OnShellManage', tr('Shell command manager.')),
            (110, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (120, 'IDM_SHELL_ITEMS', tr('(Empty)'), wx.ITEM_NORMAL, 'OnShellItems', tr('Execute an shell command.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def OnShellManage(win, event):
    from ShellDialog import ShellDialog

    dlg = ShellDialog(win, win.pref)
    answer = dlg.ShowModal()
    if answer == wx.ID_OK:
        makeshellmenu(win, win.pref)
Mixin.setMixin('mainframe', 'OnShellManage', OnShellManage)

def beforeinit(win):
    win.shellmenu_ids=[win.IDM_SHELL_ITEMS]
    makeshellmenu(win, win.pref)
Mixin.setPlugin('mainframe', 'beforeinit', beforeinit)

def makeshellmenu(win, pref):
    menu = makemenu.findmenu(win.menuitems, 'IDM_SHELL')

    for id in win.shellmenu_ids:
        menu.Delete(id)

    win.shellmenu_ids = []
    if len(win.pref.shells) == 0:
        id = win.IDM_SHELL_ITEMS
        menu.Append(id, tr('(Empty)'))
        menu.Enable(id, False)
        win.shellmenu_ids=[id]
    else:
        for description, filename in win.pref.shells:
            id = wx.NewId()
            win.shellmenu_ids.append(id)
            menu.Append(id, description)
            wx.EVT_MENU(win, id, win.OnShellItems)

def OnShellItems(win, event):
    win.createMessageWindow()

    eid = event.GetId()
    index = win.shellmenu_ids.index(eid)
    command = win.pref.shells[index][1]
    command = command.replace('$path', os.path.dirname(win.document.filename))
    command = command.replace('$file', win.document.filename)
    wx.Execute(command)
Mixin.setMixin('mainframe', 'OnShellItems', OnShellItems)
