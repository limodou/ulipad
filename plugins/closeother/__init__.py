#   Programmer: weizi
#   E-mail:     weizi@163.com
#
#   Copyleft 2006 weizi
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
from modules import Globals

menulist = [ ('IDM_FILE', #parent menu id
    [
        (151, 'IDM_FILE_CLOSE_OTHER', tr('Close Other'), wx.ITEM_NORMAL, 'OnFileCloseOther', tr('Closes other document windows')),
    ]),
]
Mixin.setMixin('mainframe', 'menulist', menulist)

def add_editctrl_menu(popmenulist):
    popmenulist.extend([ (None,
        [
            (115, 'IDPM_CLOSE_OTHER', tr('Close Other'), wx.ITEM_NORMAL, 'OnEditCtrlCloseOther', tr('Closes other document windows')),
        ]),
    ])
Mixin.setPlugin('editctrl', 'add_menu', add_editctrl_menu)

def OnFileCloseOther(win, event):
    i = len(win.editctrl.getDocuments()) - 1
    temp = win.document
    while i > -1:
        document = win.editctrl.getDoc(i)
        if (not document == temp) and (not document.opened):
            win.editctrl.skip_closing = True
            win.editctrl.skip_page_change = True
            win.editctrl.DeletePage(i)
        i -= 1

    k = len(win.editctrl.getDocuments())-1
    while k > -1:
        document = win.editctrl.getDoc(k)
        if not document == temp:
            r = win.CloseFile(document)
            if r == wx.ID_CANCEL:
                break
        k = k-1
    if win.editctrl.GetPageCount() == 0:
        win.editctrl.new()
Mixin.setMixin('mainframe', 'OnFileCloseOther', OnFileCloseOther)
def OnEditCtrlCloseOther(win, event):
    win.mainframe.OnFileCloseOther(event)
Mixin.setMixin('editctrl', 'OnEditCtrlCloseOther', OnEditCtrlCloseOther)
