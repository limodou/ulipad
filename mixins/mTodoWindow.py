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

def add_mainframe_menu(menulist):
    menulist.extend([('IDM_WINDOW', #parent menu id
        [
            (210, 'IDM_WINDOW_TODO', tr('TODO Window')+u'\tCtrl+T', wx.ITEM_CHECK, 'OnWindowTODO', tr('Opens the TODO window.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_notebook_menu(popmenulist):
    popmenulist.extend([ (None,
        [
            (190, 'IDPM_TODOWINDOW', tr('TODO Window'), wx.ITEM_CHECK, 'OnNTodoWindow', tr('Opens the TODO window.')),
        ]),
    ])
Mixin.setPlugin('notebook', 'add_menu', add_notebook_menu)

def pref_init(pref):
    pref.auto_todo = True
    pref.todo_column1 = 80
    pref.todo_column2 = 50
    pref.todo_column3 = 90
    pref.todo_column4 = 300
    pref.todo_column5 = 200
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('Document'), 180, 'check', 'auto_todo', tr('Autoshow TODO window when a file with a TODO tag is opened'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

_todo_pagename = tr('TODO')

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDM_WINDOW_TODO:
        event.Check(bool(win.panel.getPage(_todo_pagename)) and win.panel.BottomIsVisible)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_WINDOW_TODO, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def on_notebook_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDPM_TODOWINDOW:
        event.Check(bool(win.panel.getPage(_todo_pagename)) and win.panel.BottomIsVisible)
Mixin.setPlugin('notebook', 'on_update_ui', on_notebook_updateui)

def init(win):
    wx.EVT_UPDATE_UI(win, win.IDPM_TODOWINDOW, win.OnUpdateUI)
Mixin.setPlugin('notebook', 'init', init)

def createtodowindow(win):
    if not win.panel.getPage(_todo_pagename):
        from TodoWindow import TodoWindow

        page = TodoWindow(win.panel.createNotebook('bottom'), win)
        win.panel.addPage('bottom', page, _todo_pagename)
    win.todowindow = win.panel.getPage(_todo_pagename)
Mixin.setMixin('mainframe', 'createtodowindow', createtodowindow)

def OnWindowTODO(win, event):
    if not win.panel.getPage(_todo_pagename):
        win.createtodowindow()
        win.panel.showPage(_todo_pagename)
        win.todowindow.show(win.document)
    else:
        win.panel.closePage(_todo_pagename)
Mixin.setMixin('mainframe', 'OnWindowTODO', OnWindowTODO)

def OnNTodoWindow(win, event):
    if not win.panel.getPage(_todo_pagename):
        win.mainframe.createtodowindow()
        win.panel.showPage(_todo_pagename)
        win.mainframe.todowindow.show(win.mainframe.document)
    else:
        win.panel.closePage(_todo_pagename)
Mixin.setMixin('notebook', 'OnNTodoWindow', OnNTodoWindow)

def aftersavefile(win, filename):
    def f():
        todo = win.mainframe.panel.getPage(_todo_pagename)
        if todo:
            data = read_todos(win)
            if data:
                win.mainframe.todowindow.show(win, data)
                return
        else:
            if win.pref.auto_todo and win.todo_show_status:
                data = read_todos(win)
                if data:
                    win.mainframe.createtodowindow()
                    win.mainframe.panel.showPage(_todo_pagename)
                    win.mainframe.todowindow.show(win, data)
                    return
        win.mainframe.panel.closePage(_todo_pagename, savestatus=False)
    wx.CallAfter(f)
Mixin.setPlugin('editor', 'aftersavefile', aftersavefile)

def on_document_enter(win, editor):
    if win.pref.auto_todo:
        if editor.todo_show_status:
            data = read_todos(win.document)
            if data:
                win.mainframe.createtodowindow()
                win.mainframe.panel.showPage(_todo_pagename)
                win.mainframe.todowindow.show(win.document, data)
                return
    else:
        todo = win.mainframe.panel.getPage(_todo_pagename)
        if todo:
            data = read_todos(win.document)
            if data:
                win.mainframe.todowindow.show(win.document, data)
                return
    win.mainframe.panel.closePage(_todo_pagename, savestatus=False)
Mixin.setPlugin('editctrl', 'on_document_enter', on_document_enter)

def editor_init(editor):
    editor.todo_show_status = True
Mixin.setPlugin('editor', 'init', editor_init)

def on_show(todowin):
    todowin.editor.todo_show_status = True
Mixin.setPlugin('todowindow', 'show', on_show)

def on_close(todowin, savestatus=True):
    if savestatus:
        todowin.editor.todo_show_status = False
Mixin.setPlugin('todowindow', 'close', on_close)

def read_todos(editor):
    from mixins.TodoWindow import read_todos as read
    
    return read(editor)