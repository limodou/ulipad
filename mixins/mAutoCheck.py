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
#   $Id: mAutoCheck.py 2000 2007-02-25 01:47:53Z limodou $

__doc__ = 'Auto check if the file is modified'

import wx
import os
#import time
from modules import Mixin
#from modules import AsyncAction
from modules import Globals

def add_pref(preflist):
    preflist.extend([
        (tr('Document')+'/'+tr('Back-End'), 110, 'check', 'auto_check', tr('Autocheck if opened documents were modified by others'), None),
        (tr('Document')+'/'+tr('Back-End'), 120, 'check', 'auto_check_confirm', tr('Confirm file reload'), None)
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def pref_init(pref):
    pref.auto_check  = True
    pref.auto_check_confirm = True
#    pref.auto_check_interval = 3    #second
Mixin.setPlugin('preference', 'init', pref_init)
#
#class Autocheck(AsyncAction.AsyncAction):
#    def do_action(self, obj):
#        if not self.empty:
#            return
#        try:
#            win = Globals.mainframe
#            _check(win)
#        except:
#            pass
#
#def main_init(win):
#    win.auto_check_files = Autocheck(1)
#    win.auto_check_files.start()
#    win.auto_last_checkpoint = 0
#Mixin.setPlugin('mainframe', 'init', main_init)
#
#def on_idle(win):
#    if not win.auto_last_checkpoint:
#        win.auto_last_checkpoint = time.time()
#    else:
#        if time.time() - win.auto_last_checkpoint > win.pref.auto_check_interval:
#            win.auto_check_files.put(True)
#            win.auto_last_checkpoint = time.time()
#Mixin.setPlugin('mainframe', 'on_idle', on_idle)

def on_set_focus(win, event):
    _check(Globals.mainframe)
Mixin.setPlugin('editor', 'on_set_focus', on_set_focus)
    
def _check(win):
    if win.pref.auto_check:
        for document in win.editctrl.getDocuments():
            if win.closeflag: return
            if document.filename and document.edittype == 'edit' and document.opened and hasattr(document, 'saving'):
                if os.path.exists(document.filename) and not checkFilename(win, document) and win.editctrl.filetimes.has_key(document.filename):
                    if not document.saving and getModifyTime(document.filename) > win.editctrl.filetimes[document.filename]:
                        def fn():
                            answer = wx.ID_NO
                            if win.pref.auto_check_confirm:
                                dlg = wx.MessageDialog(win, tr("Another application has modified [%s].\nDo you want to reopen it?") % document.filename, tr("Check"), wx.YES_NO | wx.ICON_QUESTION)
                                answer = dlg.ShowModal()
                            if answer == wx.ID_YES or not win.pref.auto_check_confirm:
                                state = document.save_state()
                                document.openfile(document.filename)
                                document.editctrl.switch(document)
                                document.restore_state(state)
                        wx.CallAfter(fn)
                        win.editctrl.filetimes[document.filename] = getModifyTime(document.filename)
                        return

def editctrl_init(win):
    win.filetimes = {}
Mixin.setPlugin('editctrl', 'init', editctrl_init)

def afteropenfile(win, filename):
    if filename and win.edittype == 'edit':
        win.editctrl.filetimes[filename] = getModifyTime(filename)
Mixin.setPlugin('editor', 'afteropenfile', afteropenfile)

def aftersavefile(win, filename):
    if win.edittype == 'edit':
        win.editctrl.filetimes[filename] = getModifyTime(filename)
Mixin.setPlugin('editor', 'aftersavefile', aftersavefile)

def closefile(win, document, filename):
    if filename and document.edittype == 'edit':
        if win.editctrl.filetimes.has_key(filename):
            del win.editctrl.filetimes[filename]
Mixin.setPlugin('mainframe', 'closefile', closefile)

def getModifyTime(filename):
    try:
        ftime = os.path.getmtime(filename)
    except:
        ftime = 0
    return ftime

def checkFilename(win, document):
    if not document.needcheck():
        return True
    if not os.path.exists(document.filename) and win.editctrl.filetimes[document.filename] != 'NO':
        dlg = wx.MessageDialog(win, tr("The file %s has been removed by others.\nDo you want to save it?") % document.filename, tr("Check"), wx.YES_NO | wx.ICON_QUESTION)
        answer = dlg.ShowModal()
        if answer == wx.ID_YES:
            document.savefile(document.filename, document.locale)
            document.editctrl.switch(document)
            win.editctrl.filetimes[document.filename] = getModifyTime(document.filename)
        else:
            win.editctrl.filetimes[document.filename] = 'NO'
        return True
    else:
        return False
