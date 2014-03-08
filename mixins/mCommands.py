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
import Commands

_impact_mode = False
buf = []

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_TOOL', #parent menu id
        [
            (137, 'IDM_TOOL_SEARCHCMDS', tr('Commands'), wx.ITEM_NORMAL, '', ''),
        ]),
        ('IDM_TOOL_SEARCHCMDS',
        [
            (100, 'IDM_TOOL_SEARCHCMDS_SEARCH', tr('Searching...') +'\tCtrl+K', wx.ITEM_NORMAL, 'OnToolSearchCMDS', tr('Searches commands.')),
            (110, 'IDM_TOOL_SEARCHCMDS_IMPACT_MODE', tr('Switch Impact Mode') +'\tCtrl+Shift+K', wx.ITEM_CHECK, 'OnToolSearchCMDSImpactMode', tr('Switches commands searching impact mode.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def mainframe_init(win):
    win.command_mode = False
Mixin.setPlugin('mainframe', 'init', mainframe_init)

#def on_set_focus(win, event):
#    win.on_focus = True
#Mixin.setPlugin('editor', 'on_set_focus', on_set_focus)

def on_kill_focus(win, event):
    return Globals.mainframe.command_mode is True
Mixin.setPlugin('editor', 'on_kill_focus', on_kill_focus)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_TOOL_SEARCHCMDS_IMPACT_MODE, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if hasattr(win, 'document') and win.document:
        if eid == win.IDM_TOOL_SEARCHCMDS_IMPACT_MODE:
            event.Check(win.pref.commands_impact)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def showinfo(text):
    win = Globals.mainframe.statusbar
    win.show_panel('Command: '+text, color='#AAFFAA', font=wx.Font(10, wx.TELETYPE, wx.NORMAL, wx.BOLD, True))
    
def OnToolSearchCMDS(win, event):
    global _impact_mode
    if not win.pref.commands_impact:
        from mixins import SearchWin
        s = SearchWin.SearchWin(win, tr("Search Commands"))
        s.Show()
    else:
        _impact_mode = True
        showinfo('')
Mixin.setMixin('mainframe', 'OnToolSearchCMDS', OnToolSearchCMDS)

def OnToolSearchCMDSImpactMode(win, event):
    win.pref.commands_impact = not win.pref.commands_impact
    win.pref.save()
Mixin.setMixin('mainframe', 'OnToolSearchCMDSImpactMode', OnToolSearchCMDSImpactMode)
    
def pref_init(pref):
    pref.commands_impact = False
    pref.commands_autoclose = True
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('Commands'), 100, 'check', 'commands_impact', tr('Enable commands search impact mode'), None),
        (tr('Commands'), 110, 'check', 'commands_autoclose', tr('Close commands search window after command executed'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def on_first_char(win, event):
    global _impact_mode, buf
    if _impact_mode:
        key = event.GetKeyCode()
        if key < 127:
            buf.append(chr(key))
            showinfo(' '.join(buf))
            Mixin.reload_obj(Commands)
            commandar = Commands.getinstance()    
            s = commandar.impact_search(''.join(buf))
            if len(s) == 1:     #find a cmd
                showinfo(' '.join(buf + ['('+s[0][0]+')']))
                cmd_id = s[0][-1]
                commandar.run(cmd_id)
                buf = []
            elif len(s) == 0:
                buf = []
        return True
Mixin.setPlugin('editor', 'on_first_char', on_first_char)

def on_first_keydown(win, event):
    global _impact_mode
    if _impact_mode:
        key = event.GetKeyCode()
        if key in (wx.WXK_ESCAPE, wx.WXK_RETURN):
            _impact_mode = False
            Globals.mainframe.statusbar.hide_panel()
            return True
        else:
            return False
# recovery the old version
#    key = event.GetKeyCode()
#    if key in (wx.WXK_ESCAPE, ):
#        if  win.on_focus:
#            if win.AutoCompActive():
#                win.AutoCompCancel()
#                return
#            if win.calltip.active:
#                win.calltip.cancel()
#                return 
#            if  not _impact_mode:
#                _impact_mode = True
#                showinfo("vim mode begin")
#                return True
#        _impact_mode = False
#        Globals.mainframe.statusbar.hide_panel()
#        return True
#    else:
#        return False
Mixin.setPlugin('editor', 'on_first_keydown', on_first_keydown)
