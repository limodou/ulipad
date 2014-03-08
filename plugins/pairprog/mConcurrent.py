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

def afterinit(win):
    win.command_starting = False
    win.concurrentwindow = None
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def on_kill_focus(win, event):
    main = Globals.mainframe
    if main.concurrentwindow and main.concurrentwindow.has_document(win):
        return Globals.mainframe.command_starting is True
Mixin.setPlugin('editor', 'on_kill_focus', on_kill_focus)

def on_start(concurrent, side):
    win = Globals.mainframe
    win.command_starting = True
    win.concurrentwindow = concurrent
Mixin.setPlugin('concurrent', 'start', on_start)

def on_stop(concurrent, side):
    win = Globals.mainframe
    win.command_starting = False
    wx.CallAfter(win.document.SetFocus)
    wx.CallAfter(win.concurrentwindow.SetFocus)
    win.concurrentwindow = None
Mixin.setPlugin('concurrent', 'stop', on_stop)

def get_state(editor, cmd, text='', pos=None):
    win = Globals.mainframe
    concurrent = win.concurrentwindow
    if concurrent and concurrent.has_document(editor) and concurrent.cmdrecorder.enable():
        if win.command_starting:
            _id = concurrent.get_doc_id(editor)
            filename = editor.getShortFilename()
            if not pos:
                pos = editor.GetCurrentPos()
            if cmd == 'gotopos':
                if concurrent.status == 'startserver':  #for server
                    concurrent.ServerCommandPlay(None, cmd, (_id, pos))
                else:
                    concurrent.client.call('editcmd', cmd, (_id, pos))
            elif cmd == 'addtext':
                if concurrent.status == 'startserver':  #for server
                    concurrent.ServerCommandPlay(None, cmd, (_id, pos, text))
                else:
                    concurrent.client.call('editcmd', cmd, (_id, pos, text))
            elif cmd == 'deltext':
                if concurrent.status == 'startserver':  #for server
                    concurrent.ServerCommandPlay(None, cmd, (_id, pos, len(text)))
                else:
                    concurrent.client.call('editcmd', cmd, (_id, pos, len(text)))

def on_key_up(win, event):
    if win.mainframe.command_starting:
        get_state(win, 'gotopos')
Mixin.setPlugin('editor', 'on_key_up', on_key_up)

def on_mouse_up(win, event):
    if win.mainframe.command_starting:
        get_state(win, 'gotopos')
Mixin.setPlugin('editor', 'on_mouse_up', on_mouse_up)

def on_modified_text(win, event):
    if win.mainframe.command_starting:
        type = event.GetModificationType()
        pos = event.GetPosition()
        if wx.stc.STC_MOD_INSERTTEXT & type:
            get_state(win, 'addtext', event.GetText(), pos)
        elif wx.stc.STC_MOD_DELETETEXT & type:
            get_state(win, 'deltext', event.GetText(), pos)
Mixin.setPlugin('editor', 'on_modified_text', on_modified_text)

def closefile(mainframe, document, filename):
    concurrent = mainframe.concurrentwindow
    if concurrent and concurrent.has_document(document) and concurrent.cmdrecorder.enable():
        v = concurrent.cmdrecorder.find_document(document)
        if v:
            s_id, fname, doc = v
            concurrent.cmdrecorder.remove_document(s_id)
Mixin.setPlugin('mainframe', 'closefile', closefile)

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_TOOL',
        [
            (510, 'IDM_TOOL_CONCURRENT', tr('Collaborative Programming'), wx.ITEM_NORMAL, 'OnToolConcurrent', tr('Collaborative programming.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def OnToolConcurrent(win, event):
    page = win.createConcurrentWindow()
    if page:
        win.panel.showPage(page)
Mixin.setMixin('mainframe', 'OnToolConcurrent', OnToolConcurrent)

pagename = tr('Collaborative')
def createConcurrentWindow(win):
    page = win.panel.getPage(pagename)
    if not page:
        import Concurrent

        page = Concurrent.ConcurrentWindow(win.panel.createNotebook('bottom'))
        win.panel.addPage('bottom', page, pagename)
        win.concurrent = page
    return page
Mixin.setMixin('mainframe', 'createConcurrentWindow', createConcurrentWindow)

def pref_init(pref):
    pref.pairprog_host = '127.0.0.1'
    pref.pairprog_port = '55555'
    pref.pairprog_username = ''
Mixin.setPlugin('preference', 'init', pref_init)
