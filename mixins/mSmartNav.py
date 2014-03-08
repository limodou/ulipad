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
import os
from modules import Mixin
from modules.wxctrl import FlatButtons
from modules import common
from modules import Id
from modules import Globals

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_SEARCH',
        [
            (176, 'IDM_SEARCH_SMART_NAV', tr('Smart Navigation'), wx.ITEM_NORMAL, '', ''),
        ]),
        ('IDM_SEARCH_SMART_NAV',
            [
                (100, 'IDM_SEARCH_NAV_PREV', tr('Go To Previous File'), wx.ITEM_NORMAL, 'OnSmartNavPrev', tr('Goes to previous file.')),
                (110, 'IDM_SEARCH_NAV_NEXT', tr('Go To Next File'), wx.ITEM_NORMAL, 'OnSmartNavNext', tr('Goes to next file.')),
                (120, 'IDM_SEARCH_NAV_CLEAR', tr('Clear Filenames'), wx.ITEM_NORMAL, 'OnSmartNavClear', tr('Clears buffered filenames.')),
            ]),
        
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (235, 'smartprev'),
        (236, 'smartnext'),
    ])

    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'smartprev':(10, create_prev),
        'smartnext':(10, create_next),
    })
Mixin.setPlugin('mainframe', 'add_tool_list', add_tool_list)

def create_prev(win, toolbar):
    ID_PREV = Id.makeid(win, 'IDM_SEARCH_NAV_PREV')
    btnPrev = FlatButtons.FlatBitmapMenuButton(toolbar, ID_PREV, common.getpngimage('images/nav_left.gif'))
    btnPrev.SetRightClickFunc(win.OnSmartNavPrevFiles)
    btnPrev.SetToolTip(wx.ToolTip(tr('Previous File')))
    wx.EVT_BUTTON(btnPrev, ID_PREV, win.OnSmartNavPrev)
    wx.EVT_UPDATE_UI(win, win.IDM_SEARCH_NAV_PREV, win.OnUpdateUI)

    return btnPrev

def create_next(win, toolbar):
    ID_NEXT = Id.makeid(win, 'IDM_SEARCH_NAV_NEXT')
    btnNext = FlatButtons.FlatBitmapMenuButton(toolbar, ID_NEXT, common.getpngimage('images/nav_right.gif'))
    btnNext.SetRightClickFunc(win.OnSmartNavNextFiles)
    btnNext.SetToolTip(wx.ToolTip(tr('Next File')))
    wx.EVT_BUTTON(btnNext, ID_NEXT, win.OnSmartNavNext)
    wx.EVT_UPDATE_UI(win, win.IDM_SEARCH_NAV_NEXT, win.OnUpdateUI)

    return btnNext

#def afterinit(win):
#    pos = 'replace'
#    k = -1
#    for i, t in enumerate(win.toollist):
#        if t[1] == pos:
#            k = i + 1
#            break
#    toolbar = win.toolbar
#    ID_PREV = Id.makeid(win, 'IDM_SEARCH_NAV_PREV')
#    btnPrev = FlatButtons.FlatBitmapMenuButton(toolbar, ID_PREV, common.getpngimage('images/nav_left.gif'))
#    btnPrev.SetRightClickFunc(win.OnSmartNavPrevFiles)
#    if k > -1:
#        toolbar.InsertControl(k, btnPrev)
#    else:
#        toolbar.AddControl(btnPrev)
#
#    ID_NEXT = Id.makeid(win, 'IDM_SEARCH_NAV_NEXT')
#    btnNext = FlatButtons.FlatBitmapMenuButton(toolbar, ID_NEXT, common.getpngimage('images/nav_right.gif'))
#    btnNext.SetRightClickFunc(win.OnSmartNavNextFiles)
#    if k > -1:
#        toolbar.InsertControl(k+1, btnNext)
#    else:
#        toolbar.AddControl(btnNext)
#    
#    toolbar.Realize()
#    
#    wx.EVT_UPDATE_UI(win, win.IDM_SEARCH_NAV_PREV, win.OnUpdateUI)
#    wx.EVT_UPDATE_UI(win, win.IDM_SEARCH_NAV_NEXT, win.OnUpdateUI)
#    wx.EVT_BUTTON(btnPrev, ID_PREV, win.OnSmartNavPrev)
#    wx.EVT_BUTTON(btnNext, ID_NEXT, win.OnSmartNavNext)
#Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def GotoSmartNavIndex(index):
    pref = Globals.mainframe.pref
    pref.smart_nav_cur = index
    pref.save()
    if pref.smart_nav_cur < 0 or not pref.smart_nav_files:
        return
    state = pref.smart_nav_files[pref.smart_nav_cur]
    doc = Globals.mainframe.editctrl.new_with_state(state)
    if not doc:
        del pref.smart_nav_files[pref.smart_nav_cur]
    
def OnSmartNavPrev(win, event=None):
    pref = Globals.mainframe.pref
    pref.smart_nav_cur -= 1
    GotoSmartNavIndex(pref.smart_nav_cur)
Mixin.setMixin('mainframe', 'OnSmartNavPrev', OnSmartNavPrev)
    
def OnSmartNavNext(win, event=None):
    pref = Globals.mainframe.pref
    pref.smart_nav_cur += 1
    GotoSmartNavIndex(pref.smart_nav_cur)
Mixin.setMixin('mainframe', 'OnSmartNavNext', OnSmartNavNext)

def OnSmartNavClear(win, event=None):
    pref = Globals.mainframe.pref
    pref.smart_nav_cur = -1
    pref.smart_nav_files = []
    pref.save()
Mixin.setMixin('mainframe', 'OnSmartNavClear', OnSmartNavClear)

def OnSmartNavPrevFiles(win, btn):
    menu = wx.Menu()
    pref = win.pref
    for i in range(pref.smart_nav_cur-1, -1, -1)[:10]:
        v = pref.smart_nav_files[i]
        filename, state, bookmarks = v
        def OnFunc(event, index=i):
            GotoSmartNavIndex(index)
        
        _id = wx.NewId()
        item = wx.MenuItem(menu, _id, os.path.basename(filename), filename)
        wx.EVT_MENU(win, _id, OnFunc)
        menu.AppendItem(item)
    btn.PopupMenu(menu)
Mixin.setMixin('mainframe', 'OnSmartNavPrevFiles', OnSmartNavPrevFiles)
   
def OnSmartNavNextFiles(win, btn):
    menu = wx.Menu()
    pref = win.pref
    for i in range(pref.smart_nav_cur+1, len(pref.smart_nav_files))[:10]:
        v = pref.smart_nav_files[i]
        filename, state, bookmarks = v
        def OnFunc(event, index=i):
            GotoSmartNavIndex(index)
        
        _id = wx.NewId()
        item = wx.MenuItem(menu, _id, os.path.basename(filename), filename)
        wx.EVT_MENU(win, _id, OnFunc)
        menu.AppendItem(item)
    btn.PopupMenu(menu)
Mixin.setMixin('mainframe', 'OnSmartNavNextFiles', OnSmartNavNextFiles)

def on_update_ui(win, event):
    pref = win.pref
    eid = event.GetId()
    if eid == win.IDM_SEARCH_NAV_PREV:
        event.Enable(len(pref.smart_nav_files) > 0 and pref.smart_nav_cur > 0)
    elif eid == win.IDM_SEARCH_NAV_NEXT:
        event.Enable(len(pref.smart_nav_files) > 0 and pref.smart_nav_cur < len(pref.smart_nav_files) - 1)
Mixin.setPlugin('mainframe', 'on_update_ui', on_update_ui)

def pref_init(pref):
    pref.smart_nav_files  = []
    pref.smart_nav_cur = -1
Mixin.setPlugin('preference', 'init', pref_init)

def get_state(editor):
    pref = editor.pref
    filename, state, bookmarks = v = editor.get_full_state()
    if not filename: return #so the filename should not be empty

    if not pref.smart_nav_files or pref.smart_nav_files[pref.smart_nav_cur][0] != filename:   #add new file
        pref.smart_nav_files = pref.smart_nav_files[:pref.smart_nav_cur+1]    #remove the next files
        pref.smart_nav_files.append(v)
        del pref.smart_nav_files[:-20]
        pref.smart_nav_cur = len(pref.smart_nav_files) - 1
        pref.save()
    else:   #equal current nav file, so just update the value
        pref.smart_nav_files[pref.smart_nav_cur] = v
        pref.save()
    
def on_key_up(win, event):
    get_state(win)
Mixin.setPlugin('editor', 'on_key_up', on_key_up)

def on_mouse_up(win, event):
    get_state(win)
Mixin.setPlugin('editor', 'on_mouse_up', on_mouse_up)

def on_document_enter(win, document):
    if document.documenttype == 'texteditor' and not Globals.starting:
        get_state(document)
Mixin.setPlugin('editctrl', 'on_document_enter', on_document_enter)
