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
#   $Id: mScript.py 1566 2006-10-09 04:44:08Z limodou $

import wx
import sys
from modules import Mixin
from modules import makemenu

def pref_init(pref):
    pref.scripts = []
    pref.last_script_dir = ''
Mixin.setPlugin('preference', 'init', pref_init)

def add_mainframe_menu(menulist):
    menulist.extend([('IDM_TOOL',
        [
            (50, 'IDM_SCRIPT', tr('Scripts'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDM_SCRIPT', #parent menu id
        [
            (100, 'IDM_SCRIPT_MANAGE', tr('Scripts Manager...'), wx.ITEM_NORMAL, 'OnScriptManage', tr('Script manager.')),
            (110, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (120, 'IDM_SCRIPT_ITEMS', tr('(Empty)'), wx.ITEM_NORMAL, 'OnScriptItems', tr('Executes an script.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def OnScriptManage(win, event):
    from ScriptDialog import ScriptDialog

    dlg = ScriptDialog(win, win.pref)
    answer = dlg.ShowModal()
    if answer == wx.ID_OK:
        makescriptmenu(win, win.pref)
Mixin.setMixin('mainframe', 'OnScriptManage', OnScriptManage)

def beforeinit(win):
    win.old_script_accel = {}
    win.scriptmenu_ids=[win.IDM_SCRIPT_ITEMS]
    makescriptmenu(win, win.pref)
Mixin.setPlugin('mainframe', 'beforeinit', beforeinit)

def makescriptmenu(win, pref):
    menu = makemenu.findmenu(win.menuitems, 'IDM_SCRIPT')

    for id in win.scriptmenu_ids:
        menu.Delete(id)

    win.scriptmenu_ids = []
    if len(win.pref.scripts) == 0:
        id = win.IDM_SCRIPT_ITEMS
        menu.Append(id, tr('(Empty)'))
        menu.Enable(id, False)
        win.scriptmenu_ids=[id]
    else:
        accel = {}
        for description, filename in win.pref.scripts:
            id = wx.NewId()
            win.scriptmenu_ids.append(id)
            menu.Append(id, description)
            pos = description.find('\t')
            if pos > -1:
                key = description[pos+1:]
                accel[id] = (key, '')
            wx.EVT_MENU(win, id, win.OnScriptItems)
        if win.old_script_accel:
            win.removeAccel(win.old_script_accel)
        win.old_script_accel = accel
        if accel:
            win.insertAccel(accel)

def OnScriptItems(win, event):
    import wx.lib.dialogs
    import traceback
    from modules import common

    eid = event.GetId()
    index = win.scriptmenu_ids.index(eid)
    filename = win.pref.scripts[index][1]

    try:
        scripttext = open(common.encode_path(filename), 'rU').read()
    except:
        common.showerror(win, tr("Can't open the file %s.") % filename)
        return

    try:
        code = compile((scripttext + '\n'), common.encode_path(filename), 'exec')
    except:
        d = wx.lib.dialogs.ScrolledMessageDialog(win, (tr("Error compiling script.\n\nTraceback:\n\n") +
            ''.join(traceback.format_exception(*sys.exc_info()))), tr("Error"), wx.DefaultPosition, wx.Size(400,300))
        d.ShowModal()
        d.Destroy()
        return

    try:
        namespace = locals()
        exec code in namespace
    except:
        d = wx.lib.dialogs.ScrolledMessageDialog(win, (tr("Error running script.\n\nTraceback:\n\n") +
            ''.join(traceback.format_exception(*sys.exc_info()))), tr("Error"), wx.DefaultPosition, wx.Size(400,300))
        d.ShowModal()
        d.Destroy()
        return
Mixin.setMixin('mainframe', 'OnScriptItems', OnScriptItems)
