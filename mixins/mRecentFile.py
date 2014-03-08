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
#   $Id: mRecentFile.py 1813 2007-01-09 01:43:13Z limodou $

import wx
import os
from modules import Mixin
from modules import common
from modules import Globals

def add_mainframe_menu(menulist):
    menulist.extend([('IDM_FILE',
        [
            (130, 'IDM_FILE_RECENTFILES', tr('Recent Files...')+'\tAlt+R', wx.ITEM_NORMAL, 'OnOpenRecentFiles', 'Shows recently opened files in a pop-up menu.'),
#            (135, 'IDM_FILE_RECENTPATHS', tr('Open Recent Paths'), wx.ITEM_NORMAL, 'OnOpenRecentPaths', 'Opens recent paths.'),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def pref_init(pref):
    pref.recent_files = []
    pref.recent_files_num = 20
#    pref.recent_paths = []
#    pref.recent_paths_num = 10
Mixin.setPlugin('preference', 'init', pref_init)

def afteropenfile(win, filename):
    if Globals.starting:
        return
    if filename:
        #deal recent files
        if filename in win.pref.recent_files:
            win.pref.recent_files.remove(filename)
        win.pref.recent_files.insert(0, filename)
        win.pref.recent_files = win.pref.recent_files[:win.pref.recent_files_num]
        win.pref.last_dir = os.path.dirname(filename)

#        #deal recent path
#        path = os.path.dirname(filename)
#        if path in win.pref.recent_paths:
#            win.pref.recent_paths.remove(path)
#        win.pref.recent_paths.insert(0, path)
#        win.pref.recent_paths = win.pref.recent_paths[:win.pref.recent_paths_num]

        #save pref
        win.pref.save()
Mixin.setPlugin('editor', 'afteropenfile', afteropenfile)
Mixin.setPlugin('editor', 'aftersavefile', afteropenfile)

def OnOpenRecentFiles(win, event=None):
    menu = wx.Menu()
    pref = win.pref
    for index, filename in enumerate(pref.recent_files):
        def OnFunc(event, index=index):
            open_recent_files(win, index)
        
        _id = wx.NewId()
        item = wx.MenuItem(menu, _id, filename, filename)
        wx.EVT_MENU(win, _id, OnFunc)
        menu.AppendItem(item)
    win.PopupMenu(menu)
Mixin.setMixin('mainframe', 'OnOpenRecentFiles', OnOpenRecentFiles)
    
def add_pref(preflist):
    preflist.extend([
        (tr('Document'), 200, 'num', 'recent_files_num', tr('Maximum number of recent files:'), None)
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

#def OnOpenRecentPaths(win, event=None):
#    menu = wx.Menu()
#    pref = win.pref
#    for index, filename in enumerate(pref.recent_paths):
#        def OnFunc(event, index=index):
#            open_recent_paths(win, index)
#        
#        _id = wx.NewId()
#        item = wx.MenuItem(menu, _id, filename, filename)
#        wx.EVT_MENU(win, _id, OnFunc)
#        menu.AppendItem(item)
#    win.PopupMenu(menu)
#Mixin.setMixin('mainframe', 'OnOpenRecentPaths', OnOpenRecentPaths)
    
def open_recent_files(win, index):
    filename = win.pref.recent_files[index]
    try:
        f = file(filename)
        f.close()
    except:
        common.showerror(win, tr("Can't open the file %s.") % filename)
        del win.pref.recent_files[index]
        win.pref.save()
        return
    win.editctrl.new(filename)

#def open_recent_paths(win, index):
#    path = win.pref.recent_paths[index]
#    if os.path.exists(path) and os.path.isdir(path):
#        dlg = wx.FileDialog(win, tr("Open"), path, "", '|'.join(win.filewildchar), wx.OPEN|wx.HIDE_READONLY|wx.MULTIPLE)
#        dlg.SetFilterIndex(win.getFilterIndex())
#        if dlg.ShowModal() == wx.ID_OK:
#            encoding = win.execplugin('getencoding', win, win)
#            for filename in dlg.GetPaths():
#                win.editctrl.new(filename, encoding)
#            dlg.Destroy()
#    else:
#        common.showerror(win, tr("Can't open the path [%s]!") % path)
#        del win.pref.recent_paths[index]
#        win.pref.save()
#        return
#
#def add_tool_list(toollist, toolbaritems):
#    toollist.extend([
#        (115, 'openpath'),
#    ])
#
#    #order, IDname, imagefile, short text, long text, func
#    toolbaritems.update({
#        'openpath':(wx.ITEM_NORMAL, 'IDM_FILE_OPEN_PATH', 'images/paths.gif', tr('open path'), tr('Open path'), 'OnFileOpenPath'),
#    })
#Mixin.setPlugin('mainframe', 'add_tool_list', add_tool_list)
#
#def OnFileOpenPath(win, event):
#    eid = event.GetId()
#    size = win.toolbar.GetToolSize()
#    pos = win.toolbar.GetToolPos(eid)
#    menu = wx.Menu()
#
#    if len(win.pref.recent_paths) == 0:
#        id = win.IDM_FILE_RECENTPATHS_ITEMS
#        menu.Append(id, tr('(empty)'))
#        menu.Enable(id, False)
#    else:
#        for i, path in enumerate(win.pref.recent_paths):
#            id = win.recentpathmenu_ids[i]
#            menu.Append(id, "%d %s" % (i+1, path))
#    win.PopupMenu(menu, (size[0]*pos, size[1]))
#    menu.Destroy()
#Mixin.setMixin('mainframe', 'OnFileOpenPath', OnFileOpenPath)
