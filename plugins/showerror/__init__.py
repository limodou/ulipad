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
#   $Id$

import wx
import os.path
from modules import Mixin

menulist = [ ('IDM_HELP', #parent menu id
    [
        (103, 'IDM_HELP_SHOWERROR', tr('Show error.log'), wx.ITEM_NORMAL, 'OnHelpShowError', tr('Show error.log file content.')),
        (104, 'IDM_HELP_SHOWDEBUG', tr('Show debug.log'), wx.ITEM_NORMAL, 'OnHelpShowDebug', tr('Show debug.log file content.')),
    ]),
]
Mixin.setMixin('mainframe', 'menulist', menulist)

#def add_editctrl_menu(popmenulist):
#    popmenulist.extend([ (None,
#        [
#            (610, 'IDPM_SHOWERROR', tr('Show error.log'), wx.ITEM_NORMAL, 'OnEditCtrlHelpShowError', tr('Saves an opened document using the same filename')),
#            (620, 'IDPM_SHOWDEBUG', tr('Show debug.log'), wx.ITEM_NORMAL, 'OnEditCtrlHelpShowDebug', tr('Show debug.log file content.')),
#        ]),
#    ])
#Mixin.setPlugin('editctrl', 'add_menu', add_editctrl_menu)
#
def OnHelpShowError(win, event):
    win.editctrl.new(os.path.join(win.userpath, 'error.txt'))
Mixin.setMixin('mainframe', 'OnHelpShowError', OnHelpShowError)

def OnHelpShowDebug(win, event):
    win.editctrl.new(os.path.join(win.userpath, 'debug.txt'))
Mixin.setMixin('mainframe', 'OnHelpShowDebug', OnHelpShowDebug)

#def OnEditCtrlHelpShowError(win, event):
#    win.new(os.path.join(Globals.userpath, 'error.txt'))
#Mixin.setMixin('editctrl', 'OnEditCtrlHelpShowError', OnEditCtrlHelpShowError)
#
#def OnEditCtrlHelpShowDebug(win, event):
#    win.new(os.path.join(Globals.userpath, 'debug.txt'))
#Mixin.setMixin('editctrl', 'OnEditCtrlHelpShowDebug', OnEditCtrlHelpShowDebug)
