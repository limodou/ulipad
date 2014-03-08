#   Programmer:     limodou
#   E-mail:         limodou@gmail.com
#  
#   Copyleft 2008 limodou
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
from modules import Globals
from modules import meide as ui
from modules import Mixin

class WrapTextDialog(wx.Dialog):
    def __init__(self, title=tr('Wrap Text'), values=None):
        wx.Dialog.__init__(self, Globals.mainframe, -1, style = wx.DEFAULT_DIALOG_STYLE, title = title, size=(600, 300))
        
        self.sizer = box = ui.VBox(namebinding='widget').create(self).auto_layout()
        grid = box.add(ui.SimpleGrid)
        grid.add(tr('Width'), ui.Int(75), name='width')
        grid.add(tr('Indent'), ui.Text(''), name='indent')
        grid.add(tr('First Line Indent'), ui.Text(''), name='firstindent')
        grid.add(tr('Skip Beginning Characters'), ui.Text(''), name='skipchar')
        grid.add(tr('Remove Tailing Characters'), ui.Text(''), name='remove_tailingchar')
        grid.add(tr('Add Tailing Characters'), ui.Text(''), name='add_tailingchar')
        box.add(ui.simple_buttons(), flag=wx.ALIGN_CENTER|wx.BOTTOM)
        
        box.auto_fit(2)
        
        if values:
            box.SetValue(values)
        
    def GetValue(self):
        return self.sizer.GetValue()
    
def add_mainframe_menu(menulist):
    menulist.extend([
        ('IDM_EDIT_FORMAT',
        [
            (126, 'IDM_EDIT_FORMAT_WRAP', tr('Wrap Text...')+'\tCtrl+Shift+T', wx.ITEM_NORMAL, 'OnEditFormatWrap', tr('Wraps selected text.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_editor_menu(popmenulist):
    popmenulist.extend([
        ('IDPM_FORMAT',
        [
            (126, 'IDPM_FORMAT_WRAP', tr('Wrap Text...')+'\tE=Ctrl+Shift+T', wx.ITEM_NORMAL, 'OnFormatWrap', tr('Wraps selected text.')),
        ]),
    ])
Mixin.setPlugin('editor', 'add_menu', add_editor_menu)

def OnEditFormatWrap(win, event):
    OnFormatWrap(win.document, event)
Mixin.setMixin('mainframe', 'OnEditFormatWrap', OnEditFormatWrap)

def pref_init(pref):
    pref.wrap_width = 75
    pref.wrap_indent = ''
    pref.wrap_firstindent = ''
    pref.wrap_skipchar = ''
    pref.wrap_remove_tailingchar = ''
    pref.wrap_add_tailingchar = ''
Mixin.setPlugin('preference', 'init', pref_init)

def OnFormatWrap(win, event):
    pref = Globals.pref
    v = {'width':pref.wrap_width, 'indent':pref.wrap_indent,
        'firstindent':pref.wrap_firstindent, 'skipchar':pref.wrap_skipchar,
        'remove_tailingchar':pref.wrap_remove_tailingchar,
        'add_tailingchar':pref.wrap_add_tailingchar}
    dlg = WrapTextDialog(values=v)
    value = None
    if dlg.ShowModal() == wx.ID_OK:
        value = dlg.GetValue()
        pref.wrap_width = value['width']
        pref.wrap_indent = value['indent']
        pref.wrap_firstindent = value['firstindent']
        pref.wrap_skipchar = value['skipchar']
        pref.wrap_remove_tailingchar = value['remove_tailingchar']
        pref.wrap_add_tailingchar = value['add_tailingchar']
        pref.save()
    dlg.Destroy()
    if value:
        text = win.GetSelectedText()
        from modules.wraptext import wraptext
        text = wraptext(text, value['width'], cr=win.getEOLChar(), 
            indent=value['indent'], firstindent=value['firstindent'],
            skipchar=value['skipchar'], remove_tailingchar=value['remove_tailingchar'],
            add_tailingchar=value['add_tailingchar'])
        start, end = win.GetSelection()
        win.SetTargetStart(start)
        win.SetTargetEnd(end)
        win.ReplaceTarget(text)
Mixin.setMixin('editor', 'OnFormatWrap', OnFormatWrap)

def mainframe_init(win):
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_FORMAT_WRAP, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'init', mainframe_init)

def editor_init(win):
    wx.EVT_UPDATE_UI(win, win.IDPM_FORMAT_WRAP, win.OnUpdateUI)
Mixin.setPlugin('editor', 'init', editor_init)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDM_EDIT_FORMAT_WRAP:
        event.Enable(win.document and win.document.GetSelectedText and len(win.document.GetSelectedText()) > 0)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def on_editor_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDPM_FORMAT_WRAP:
        event.Enable(len(win.GetSelectedText()) > 0)
Mixin.setPlugin('editor', 'on_update_ui', on_editor_updateui)
