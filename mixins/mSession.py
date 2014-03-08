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
#   $Id: mSession.py 1892 2007-02-02 05:19:37Z limodou $

import os
import wx
from modules import Mixin
from modules.Debug import error
from modules import common
from modules import Globals
from modules import makemenu

def pref_init(pref):
    pref.load_session = True
    pref.sessions = []
    pref.last_tab_index = -1
    pref.screen_lines = 0
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('Document') + '/' + tr('Startup'), 150, 'check', 'load_session', tr('Load files of last session at startup'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def save_session(win):
    if Globals.starting: return
    win.pref.sessions, win.pref.last_tab_index = [], -1
    if win.pref.load_session:
        win.pref.sessions, win.pref.last_tab_index = gather_status()
    win.pref.save()

def afterclosewindow(win):
    save_session(win)
Mixin.setPlugin('mainframe', 'afterclosewindow', afterclosewindow)

def afterclosefile(win, *args):
    save_session(win)
Mixin.setPlugin('editctrl', 'afterclosefile', afterclosefile)

def afternewfile(win, *args):
    save_session(win.mainframe)
Mixin.setPlugin('editctrl', 'afternewfile', afternewfile)

def gather_status():
    sessions = []
    last_tab_index = -1
    win = Globals.mainframe
    for document in win.editctrl.getDocuments():
        if document.documenttype != 'texteditor':
            continue
        if document.filename and document.savesession:
            sessions.append(document.get_full_state())
    last_tab_index = win.editctrl.GetSelection()
    return sessions, last_tab_index
    
def openPage(win):
    n = 0
    if win.mainframe.pref.load_session and not win.mainframe.app.skipsessionfile:
        for v in win.mainframe.pref.sessions:
            if len(v) == 4:
                filename, row, col, bookmarks = v
                state = row
            else:
                filename, state, bookmarks = v
            document = win.new(filename, delay=True)
            if document:
                n += 1
        index = win.mainframe.pref.last_tab_index
        if index < 0:
            index = 0
        elif index >= len(win.getDocuments()):
            index = len(win.getDocuments()) -1
        if index > -1 and index < len(win.getDocuments()):
            wx.CallAfter(win.switch, win.getDoc(index), delay=False)
    return n > 0
Mixin.setPlugin('editctrl', 'openpage', openPage)

#add session manager
def pref_init(pref):
    pref.recent_sessions = []
    pref.last_session_dir = ''
Mixin.setPlugin('preference', 'init', pref_init)

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_FILE', #parent menu id
        [
            (202, 'IDM_FILE_SESSION_OPEN', tr('Open Session...'), wx.ITEM_NORMAL, 'OnFileSessionOpen', tr('Opens an existing session file.')),
            (203, 'IDM_FILE_SESSION_SAVE', tr('Save Session...'), wx.ITEM_NORMAL, 'OnFileSessionSave', tr('Saves opened documents to a session file.')),
            (204, 'IDM_FILE_SESSION_RECENT', tr('Open Recent Session'), wx.ITEM_NORMAL, '', ''),
            (205, '', '-', wx.ITEM_SEPARATOR, None, ''),
        ]),
        ('IDM_FILE_SESSION_RECENT',
        [
            (100, 'IDM_FILE_SESSION_RECENT_ITEMS', tr('(Empty)'), wx.ITEM_NORMAL, '', tr('There is no recent session.')),
        ]),
        
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

from modules.EasyGuider import obj2ini

def OnFileSessionOpen(win, event=None, filename=None):
    if not filename:
        dlg = wx.FileDialog(win, tr("Choose A Session File"), win.pref.last_session_dir, "", 'UliPad Session File (*.ses)|*.ses', wx.OPEN|wx.HIDE_READONLY)
        filename = None
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
        dlg.Destroy()
    if filename:
        try:
            get_recent_session_file(win, filename)
            d = obj2ini.load(filename)
            sessions, last_file = d['sessions'], d['last_file']
            win.pref.sessions.extend(sessions)
            for v in sessions:
                win.editctrl.new(v[0], delay=True)
            for document in win.editctrl.getDocuments():
                if document.documenttype == 'texteditor' and document.filename == last_file:
                    wx.CallAfter(win.editctrl.switch, document, delay=False)
        except:
            error.traceback()
            common.warn(tr('There was something wrong with loading the session file.'))
Mixin.setMixin('mainframe', 'OnFileSessionOpen', OnFileSessionOpen)

def OnFileSessionSave(win, event=None):
    dlg = wx.FileDialog(win, tr("Save To Session File"), win.pref.last_session_dir, "", 'UliPad Session File (*.ses)|*.ses', wx.SAVE|wx.OVERWRITE_PROMPT)
    filename = None
    if dlg.ShowModal() == wx.ID_OK:
        filename = dlg.GetPath()
    dlg.Destroy()
    if filename:
        try:
            get_recent_session_file(win, filename)
            sessions, last_index = gather_status()
            last_file = win.editctrl.getDoc(last_index).filename
            obj2ini.dump({'sessions':sessions, 'last_file':last_file}, filename)
        except:
            error.traceback()
            common.warn(tr('There was something wrong with saving the session file.'))
Mixin.setMixin('mainframe', 'OnFileSessionSave', OnFileSessionSave)

def afterinit(win):
    win.recentsession_ids = [win.IDM_FILE_SESSION_RECENT_ITEMS]
    create_recent_session_menu(win)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def create_recent_session_menu(win):
    menu = makemenu.findmenu(win.menuitems, 'IDM_FILE_SESSION_RECENT')

    for id in win.recentsession_ids:
        menu.Delete(id)

    win.recentsession_ids = []
    if len(win.pref.recent_sessions) == 0:
        id = win.IDM_FILE_SESSION_RECENT_ITEMS
        menu.Append(id, tr('(Empty)'))
        menu.Enable(id, False)
        win.recentsession_ids = [id]
    else:
        for i, filename in enumerate(win.pref.recent_sessions):
            id = wx.NewId()
            win.recentsession_ids.append(id)
            menu.Append(id, "%d %s" % (i+1, filename))
            wx.EVT_MENU(win, id, win.OnOpenRecentSession)

def OnOpenRecentSession(win, event):
    eid = event.GetId()
    index = win.recentsession_ids.index(eid)
    filename = win.pref.recent_sessions[index]
    try:
        f = file(filename)
        f.close()
    except:
        common.showerror(win, tr("Can't open the file %s.") % filename)
        del win.pref.recent_sessions[index]
        win.pref.save()
        create_recent_session_menu(win)
        return
    win.OnFileSessionOpen(filename=filename)
Mixin.setMixin('mainframe', 'OnOpenRecentSession', OnOpenRecentSession)

def get_recent_session_file(win, filename):
    if filename:
        #deal recent files
        if filename in win.pref.recent_sessions:
            win.pref.recent_sessions.remove(filename)
        win.pref.recent_sessions.insert(0, filename)
        win.pref.recent_sessions = win.pref.recent_sessions[:10]
        win.pref.last_session_dir = os.path.dirname(filename)

        #save pref
        win.pref.save()

        #create menus
        create_recent_session_menu(win)
