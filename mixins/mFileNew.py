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
#   $Id: mEditorCtrl.py 154 2005-11-07 04:48:15Z limodou $

import wx
import os
from modules import Id
from modules import Mixin
from modules import common
from modules import makemenu
from modules import Globals
from modules.wxctrl import FlatButtons

def pref_init(pref):
    pref.last_new_type = ''
Mixin.setPlugin('preference', 'init', pref_init)

def add_tool_list(toollist, toolbaritems):
    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'new':(10, create_new),
    })
Mixin.setPlugin('mainframe', 'add_tool_list', add_tool_list, Mixin.LOW)

def create_new(win, toolbar):
    _id = Id.makeid(win, 'IDM_FILE_NEW')
    btnNew = FlatButtons.FlatBitmapMenuButton(toolbar, _id, common.getpngimage('images/new.gif'))
    btnNew.SetRightClickFunc(win.OnFileNews)
    btnNew.SetToolTip(wx.ToolTip(tr('New File')))
    wx.EVT_BUTTON(btnNew, _id, win.OnFileNew)

    return btnNew

def OnFileNew(win, event):
    new_file(win)
Mixin.setMixin('mainframe', 'OnFileNew', OnFileNew)

def OnFileNews(win, event):
    eid = event.GetId()
    size = win.toolbar.GetToolSize()
    pos = win.toolbar.GetToolPos(eid)
    menu = wx.Menu()
    create_menu(win, menu)
    win.PopupMenu(menu, (size[0]*pos, size[1]))
    menu.Destroy()
Mixin.setMixin('mainframe', 'OnFileNews', OnFileNews)

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_FILE_NEWMORE',
        [
           (100, 'IDM_FILE_NEWMORE_NULL', tr('(Empty)'), wx.ITEM_NORMAL, '', ''),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def init(win):
    menu = makemenu.findmenu(win.menuitems, 'IDM_FILE_NEWMORE')
    menu.Delete(win.IDM_FILE_NEWMORE_NULL)
    create_menu(win, menu)
Mixin.setPlugin('mainframe', 'init', init)

def new_file(win, lexname=None):
    if not lexname:
        lexname = win.pref.last_new_type
    if lexname:
        lexer = win.lexers.getNamedLexer(lexname)
        text = ''
        if lexer:
            templatefile = common.getConfigPathFile('template.%s' % lexer.name)
            if os.path.exists(templatefile):
                text = file(templatefile).read()
                text = common.decode_string(text)
                import re
                eolstring = {0:'\n', 1:'\r\n', 2:'\r'}
                eol = eolstring[Globals.pref.default_eol_mode]
                text = re.sub(r'\r\n|\r|\n', eol, text)
            else:
                text = ''
        document = win.editctrl.new(defaulttext=text, language=lexer.name)
        if document:
            document.goto(document.GetTextLength())
    else:
        win.editctrl.new()

def create_menu(win, menu):
    ids = {}
    def _OnFileNew(event, win=win, ids=ids):
        lexname = ids.get(event.GetId(), '')
        new_file(win, lexname)
        win.pref.last_new_type = lexname
        win.pref.save()
    
    for name, lexname in win.filenewtypes:
        _id = wx.NewId()
        menu.AppendCheckItem(_id, "%s" % name)
        ids[_id] = lexname
        if lexname == win.pref.last_new_type:
            menu.Check(_id, True)
        wx.EVT_MENU(win, _id, _OnFileNew)
    