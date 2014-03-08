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
#   $Id$

import wx
from modules import Mixin

def add_editor_menu(popmenulist):
    popmenulist.extend([ (None, #parent menu id
        [
            (5, 'IDPM_COPY_RUN', tr('Run In Shell') + '\tCtrl+F5', wx.ITEM_NORMAL, 'OnEditorCopyRun', ''),
        ]),
    ])
Mixin.setPlugin('editor', 'add_menu', add_editor_menu)

def editor_init(win):
    wx.EVT_UPDATE_UI(win, win.IDPM_COPY_RUN, win.OnUpdateUI)
Mixin.setPlugin('editor', 'init', editor_init)

def editor_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDPM_COPY_RUN:
        event.Enable(bool(win.hasSelection()))
Mixin.setPlugin('editor', 'on_update_ui', editor_updateui)

def OnEditorCopyRun(win, event):
    _copy_and_run(win)
Mixin.setMixin('editor', 'OnEditorCopyRun', OnEditorCopyRun)

import re
re_space = re.compile(r'^\s+')
def lstrip_multitext(text):
    lines = text.splitlines()
    m = 999999
    for line in lines:
        b = re_space.search(line)
        if b:
            m = min(len(b.group()), m)
        else:
            m = 0
            break
    return '\n'.join([x[m:] for x in lines])

def _copy_and_run(doc):
    from modules import Globals

    win = Globals.mainframe
    text = doc.GetSelectedText()
    if text:
        win.createShellWindow()
        win.panel.showPage(tr('Shell'))
        shellwin = win.panel.getPage(tr('Shell'))
        shellwin.Execute(lstrip_multitext(text))

def OnEditCopyRun(win, event):
    _copy_and_run(win.editctrl.getCurDoc())
Mixin.setMixin('mainframe', 'OnEditCopyRun', OnEditCopyRun)

def add_mainframe_menu(menulist):
    menulist.extend([
        ('IDM_EDIT',
        [
            (285, 'IDM_EDIT_COPY_RUN', tr('Run In Shell') + '\tCtrl+F5', wx.ITEM_NORMAL, 'OnEditCopyRun', tr('Copy code to shell window and run it.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDM_EDIT_COPY_RUN:
        doc = win.editctrl.getCurDoc()
        event.Enable(bool(doc.hasSelection()))
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_COPY_RUN, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

