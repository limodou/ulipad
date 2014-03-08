#   Programmer:     limodou
#   E-mail:         limodou@gmail.com
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
#   $Id: DosPrompt.py,v 1.1 2005/07/31 09:08:14 limodou Exp $

__doc__ = 'Dos Prompt'

from modules import Mixin
import wx
import os.path
from modules import common
from mixins import MessageWindow
import DosPrompt
import images

menulist = [ ('IDM_WINDOW',
        [
                (180, 'IDM_WINDOW_DOS', tr('Open Dos Prompt Window'), wx.ITEM_NORMAL, 'OnWindowDos', tr('Opens dos prompt window.')),
        ]),
]
Mixin.setMixin('mainframe', 'menulist', menulist)

popmenulist = [ (None,
        [
                (150, 'IDPM_DOSWINDOW', tr('Open Dos Prompt Window'), wx.ITEM_NORMAL, 'OnDosWindow', tr('Opens dos prompt window.')),
        ]),
]
Mixin.setMixin('notebook', 'popmenulist', popmenulist)

class DosPromptWindow(MessageWindow.MessageWindow):
    __mixinname__ = 'dospromptwindow'

    popmenulist = [(None, #parent menu id
        [
            (100, 'IDPM_UNDO', tr('Undo') + '\tCtrl+Z', wx.ITEM_NORMAL, 'OnPopupEdit', tr('Reverse previous editing operation')),
            (110, 'IDPM_REDO', tr('Redo') + '\tCtrl+Y', wx.ITEM_NORMAL, 'OnPopupEdit', tr('Reverse previous undo operation')),
            (120, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (130, 'IDPM_CUT', tr('Cut') + '\tCtrl+X', wx.ITEM_NORMAL, 'OnPopupEdit', tr('Deletes text from the document and moves it to the clipboard')),
            (140, 'IDPM_COPY', tr('Copy') + '\tCtrl+C', wx.ITEM_NORMAL, 'OnPopupEdit', tr('Copies text from the document to the clipboard')),
            (150, 'IDPM_PASTE', tr('Paste') + '\tCtrl+V', wx.ITEM_NORMAL, 'OnPopupEdit', tr('Pastes text from the clipboard into the document')),
            (160, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (170, 'IDPM_SELECTALL', tr('Select All') + '\tCtrl+A', wx.ITEM_NORMAL, 'OnPopupEdit', tr('Selects all text.')),
            (175, 'IDPM_CLEAR', tr('Clear') + '\tShift+F5', wx.ITEM_NORMAL, 'OnClear', tr('Clear all the text.')),
        ]),
    ]
    
    def __init__(self, parent, mainframe):
        MessageWindow.MessageWindow.__init__(self, parent, mainframe)

    def OnClear(self, event):
        self.SetText('')
        self.writeposition = self.GetLength()
        self.editpoint = self.GetLength()
        
    def OnUpdateUI(self, event):
        eid = event.GetId()
        if eid == self.IDPM_CUT:
            event.Enable(not self.GetReadOnly() and bool(self.GetSelectedText()))
        elif eid == self.IDPM_COPY:
            event.Enable(bool(self.GetSelectedText()))
        elif eid == self.IDPM_PASTE:
            event.Enable(not self.GetReadOnly() and bool(self.CanPaste()))
        elif eid == self.IDPM_UNDO:
            event.Enable(bool(self.CanUndo()))
        elif eid == self.IDPM_REDO:
            event.Enable(bool(self.CanRedo()))
        
def createDosWindow(win):
    page = win.panel.getPage('Dos')
    if not page:
        page = DosPromptWindow(win.panel.createNotebook('bottom'), win)
        win.panel.addPage('bottom', page, 'Dos')
    win.dosprompt = page
Mixin.setMixin('mainframe', 'createDosWindow', createDosWindow)

def OnWindowDos(win, event):
    path = os.getcwd()
    path = common.decode_string(path)
    dlg = wx.DirDialog(win, tr('Choose a directory'), path)
    answer = dlg.ShowModal()
    if answer == wx.ID_OK:
        path = dlg.GetPath()
        win.createDosWindow()
        win.panel.showPage('Dos')
        win.RunDosCommand('cmd.exe /k "cd %s"' % path)
Mixin.setMixin('mainframe', 'OnWindowDos', OnWindowDos)

def OnDosWindow(win, event):
    win.mainframe.OnWindowDos(event)
Mixin.setMixin('notebook', 'OnDosWindow', OnDosWindow)

toollist = [
        (1000, 'dos'),
]
Mixin.setMixin('mainframe', 'toollist', toollist)

#order, IDname, imagefile, short text, long text, func
toolbaritems = {
        'dos':(wx.ITEM_NORMAL, 'IDM_WINDOW_DOS', images.getDosBitmap(), tr('open dos prompt window'), tr('Open dos prompt window.'), 'OnWindowDos'),
}
Mixin.setMixin('mainframe', 'toolbaritems', toolbaritems)
