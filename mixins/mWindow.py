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
#   $Id: mWindow.py 1839 2007-01-19 12:15:56Z limodou $

import wx
from modules import Mixin
from modules import Globals

def add_mainframe_menu(menulist):
    menulist.extend([(None,
        [
            (890, 'IDM_WINDOW', tr('Windows'), wx.ITEM_NORMAL, '', ''),
        ]),
        ('IDM_WINDOW',
        [
            (100, 'IDM_WINDOW_LEFT', tr('Left Window')+'\tAlt+Z', wx.ITEM_CHECK, 'OnWindowLeft', tr('Shows the left pane.')),
            (110, 'IDM_WINDOW_BOTTOM', tr('Bottom Window')+'\tAlt+X', wx.ITEM_CHECK, 'OnWindowBottom', tr('Shows the bottom pane.')),
            (120, '-', '', wx.ITEM_SEPARATOR, '', ''),
            (130, 'IDM_WINDOW_SHELL', tr('Shell Window'), wx.ITEM_CHECK, 'OnWindowShell', tr('Shows the Shell pane.')),
            (140, 'IDM_WINDOW_MESSAGE', tr('Messages Window'), wx.ITEM_CHECK, 'OnWindowMessage', tr('Shows the Messages pane.')),
        ]),
        ('IDM_EDIT',
        [
            (280, '-', '', wx.ITEM_SEPARATOR, '', ''),
            (290, 'IDM_EDIT_CLEARSHELL', tr('Clear Shell Contents') + '\tCtrl+Alt+R', wx.ITEM_NORMAL, 'OnEditClearShell', tr('Clears the contents of the shell.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)


def OnWindowLeft(win, event):
    flag = not win.panel.LeftIsVisible

#    if flag:
#        win.createSnippetWindow()
#
    win.panel.showWindow('left', flag)
Mixin.setMixin('mainframe', 'OnWindowLeft', OnWindowLeft)

def OnWindowBottom(win, event):
    flag = not win.panel.BottomIsVisible
#    if flag:
#        if not win.panel.bottombook or win.panel.bottombook.GetPageCount() == 0:
#            win.createShellWindow()
    
    win.panel.showWindow('bottom', flag)
    if flag:
        if not win.panel.bottombook or win.panel.bottombook.GetPageCount() == 0:
            win.panel.showPage(_shell_page_name)
Mixin.setMixin('mainframe', 'OnWindowBottom', OnWindowBottom)

_shell_page_name = tr('Shell')
_message_page_name = tr('Messages')
def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDM_WINDOW_LEFT:
        event.Check(win.panel.LeftIsVisible)
    elif eid == win.IDM_WINDOW_BOTTOM:
        event.Check(win.panel.BottomIsVisible)
    elif eid == win.IDM_WINDOW_SHELL:
        event.Check(bool(win.panel.getPage(_shell_page_name)))
    elif eid == win.IDM_WINDOW_MESSAGE:
        event.Check(bool(win.panel.getPage(_message_page_name)))
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_WINDOW_LEFT, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_WINDOW_BOTTOM, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_WINDOW_SHELL, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_WINDOW_MESSAGE, win.OnUpdateUI)
    win.messagewindow = None
    win.shellwindow = None
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def on_notebook_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDPM_SHELLWINDOW:
        event.Check(bool(Globals.mainframe.panel.getPage(_shell_page_name)) and win.panel.BottomIsVisible)
    if eid == win.IDPM_MESSAGEWINDOW:
        event.Check(bool(Globals.mainframe.panel.getPage(_message_page_name)) and win.panel.BottomIsVisible)
Mixin.setPlugin('notebook', 'on_update_ui', on_notebook_updateui)

def init(win):
    wx.EVT_UPDATE_UI(win, win.IDPM_SHELLWINDOW, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDPM_MESSAGEWINDOW, win.OnUpdateUI)
Mixin.setPlugin('notebook', 'init', init)

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (450, 'left'),
        (500, 'bottom'),
        (510, 'shell'),
    ])

    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'left':(wx.ITEM_CHECK, 'IDM_WINDOW_LEFT', 'images/left.gif', tr('Toggle Left Pane'), tr('Shows or hides the left pane.'), 'OnWindowLeft'),
        'bottom':(wx.ITEM_CHECK, 'IDM_WINDOW_BOTTOM', 'images/bottom.gif', tr('Toggle Bottom Pane'), tr('Shows or hides the bottom pane.'), 'OnWindowBottom'),
        'shell':(wx.ITEM_CHECK, 'IDM_WINDOW_SHELL', 'images/shell.gif', tr('Toggle Shell Pane'), tr('Shows or hides the Shell pane.'), 'OnWindowShell'),
    })
Mixin.setPlugin('mainframe', 'add_tool_list', add_tool_list)

def createShellWindow(win):
    side = Globals.pref.shell_window_side
    if not win.panel.getPage(_shell_page_name):
        from ShellWindow import ShellWindow

        page = ShellWindow(win.panel.createNotebook(side), win)
        win.panel.addPage(side, page, _shell_page_name)
    win.shellwindow = win.panel.getPage(_shell_page_name)
Mixin.setMixin('mainframe', 'createShellWindow', createShellWindow)

def createMessageWindow(win):
    if not win.panel.getPage(_message_page_name):
        from MessageWindow import MessageWindow

        page = MessageWindow(win.panel.createNotebook('bottom'), win)
        win.panel.addPage('bottom', page, _message_page_name)
    win.messagewindow = win.panel.getPage(_message_page_name)
Mixin.setMixin('mainframe', 'createMessageWindow', createMessageWindow)

def OnWindowShell(win, event):
    if not win.panel.getPage(_shell_page_name):
        win.createShellWindow()
        win.panel.showPage(_shell_page_name)
    else:
        win.panel.closePage(_shell_page_name)
Mixin.setMixin('mainframe', 'OnWindowShell', OnWindowShell)

def OnWindowMessage(win, event):
    if not win.panel.getPage(_message_page_name):
        win.createMessageWindow()
        win.panel.showPage(_message_page_name)
    else:
        win.panel.closePage(_message_page_name)
Mixin.setMixin('mainframe', 'OnWindowMessage', OnWindowMessage)

def add_editor_menu(popmenulist):
    popmenulist.extend([ (None,
        [
            (120, 'IDPM_SHELLWINDOW', tr('Shell Pane'), wx.ITEM_CHECK, 'OnShellWindow', tr('Shows the Shell pane.')),
            (130, 'IDPM_MESSAGEWINDOW', tr('Messages Pane'), wx.ITEM_CHECK, 'OnMessageWindow', tr('Shows the Messages pane.')),
        ]),
    ])
Mixin.setPlugin('notebook', 'add_menu', add_editor_menu)

def OnShellWindow(win, event):
    if not win.panel.getPage(_shell_page_name):
        win.mainframe.createShellWindow()
        win.panel.showPage(_shell_page_name)
    else:
        win.panel.closePage(_shell_page_name)
Mixin.setMixin('notebook', 'OnShellWindow', OnShellWindow)

def OnMessageWindow(win, event):
    if not win.panel.getPage(_message_page_name):
        win.mainframe.createMessageWindow()
        win.panel.showPage(_message_page_name)
    else:
        win.panel.closePage(_message_page_name)
Mixin.setMixin('notebook', 'OnMessageWindow', OnMessageWindow)

def OnEditClearShell(win, event):
    shellwin = win.panel.getPage(_shell_page_name)
    if shellwin:
        shellwin.clear()
        shellwin.prompt()
Mixin.setMixin('mainframe', 'OnEditClearShell', OnEditClearShell)

#add open shell window on side bar support
def add_pref(preflist):
    preflist.extend([
        (tr('Python'), 180, 'choice', 'shell_window_side', tr('Placement of the Shell pane is:'), 
            [('Left', 'left'), ('Bottom', 'bottom')])
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def pref_init(pref):
    pref.shell_window_side = 'bottom'
Mixin.setPlugin('preference', 'init', pref_init)
