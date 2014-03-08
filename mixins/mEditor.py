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
#   $Id: mEditor.py 1631 2006-10-21 06:22:54Z limodou $

from modules import Mixin
import wx
from modules import Globals

def add_panel_list(panellist):
    from TextPanel import TextPanel
    panellist['texteditor'] = TextPanel
Mixin.setPlugin('editctrl', 'add_panel_list', add_panel_list)

def on_first_keydown(win, event):
    key = event.GetKeyCode()
    alt = event.AltDown()
    shift = event.ShiftDown()
    ctrl = event.ControlDown()
    if ctrl and key == wx.WXK_TAB:
        if not shift:
            win.editctrl.Navigation(True)
            wx.CallAfter(Globals.mainframe.editctrl.getCurDoc().SetFocus)
        else:
            win.editctrl.Navigation(False)
            wx.CallAfter(Globals.mainframe.editctrl.getCurDoc().SetFocus)
Mixin.setPlugin('editor', 'on_first_keydown', on_first_keydown)

def on_modified_routin(win):
    win.mainframe.auto_onmodified.put(win)
Mixin.setPlugin('editor', 'on_modified_routin', on_modified_routin)

def on_modified(win):
    if win.edittype == 'edit':
        if not win.isModified():
            win.SetSavePoint()
        if win.editctrl:
            wx.CallAfter(win.editctrl.showTitle, win)
            wx.CallAfter(win.editctrl.showPageTitle, win)
Mixin.setPlugin('editor', 'on_modified', on_modified)

from modules import Globals
from modules.Debug import error
from modules import AsyncAction
class OnModified(AsyncAction.AsyncAction):
    def do_action(self, obj):
        win = Globals.mainframe
        if not self.empty:
            return
        try:
            if not obj: return
            wx.CallAfter(obj.callplugin, 'on_modified', obj)
            return True
        except:
            error.traceback()

def main_init(win):
    win.auto_onmodified = OnModified(.5)
    win.auto_onmodified.start()
Mixin.setPlugin('mainframe', 'init', main_init)

def on_close(win, event):
    win.auto_onmodified.join()
Mixin.setPlugin('mainframe','on_close', on_close)
