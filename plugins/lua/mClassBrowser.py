#   Programmer: zhangchunlin
#   E-mail:     zhangchunlin@gmail.com
#
#   Copyleft 2010 zhangchunlin
#
#   Distributed under the terms of the GPL (GNU Public License)
#
#   NewEdit is free software; you can redistribute it and/or modify
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
import os.path
from modules import Mixin
from modules import Globals

def init(pref):
    pref.lua_classbrowser_show = False
    pref.lua_classbrowser_refresh_as_save = True
Mixin.setPlugin('preference', 'init', init)

preflist = [
    ('Lua', 100, 'check', 'lua_classbrowser_show', tr('Show class browser window as open lua source file'), None),
    ('Lua', 105, 'check', 'lua_classbrowser_show', tr('Refresh class browser window as saved lua source file'), None),
]
Mixin.setMixin('preference', 'preflist', preflist)

menulist = [('IDM_LUA', #parent menu id
        [
            (100, 'IDM_LUA_CLASSBROWSER', tr('Class Browser'), wx.ITEM_CHECK, 'OnLuaClassBrowser', tr('Show lua class browser window')),
            (110, 'IDM_LUA_CLASSBROWSER_REFRESH', tr('Class Browser Refresh'), wx.ITEM_NORMAL, 'OnLuaClassBrowserRefresh', tr('Refresh lua class browser window')),
        ]),
]
Mixin.setMixin('luafiletype', 'menulist', menulist)

def init(win):
    win.class_browser = False
    win.init_class_browser = False
Mixin.setPlugin('editor', 'init', init)

def OnLuaClassBrowser(win, event):
    win.document.class_browser = not win.document.class_browser
    win.document.panel.showWindow(win.pref.python_classbrowser_show_side, win.document.class_browser)
    if win.document.init_class_browser == False:
        win.document.init_class_browser = True
        win.document.outlinebrowser.show()
Mixin.setMixin('mainframe', 'OnLuaClassBrowser', OnLuaClassBrowser)

def aftersavefile(win, filename):
    if (win.edittype == 'edit'
        and win.languagename == 'lua'
        and win.pref.lua_classbrowser_refresh_as_save
        and win.init_class_browser):
        win.outlinebrowser.show()
Mixin.setPlugin('editor', 'aftersavefile', aftersavefile)

def OnLuaClassBrowserRefresh(win, event):
    win.document.outlinebrowser.show()
Mixin.setMixin('mainframe', 'OnLuaClassBrowserRefresh', OnLuaClassBrowserRefresh)

def OnLuaUpdateUI(win, event):
    eid = event.GetId()
    if eid == win.IDM_LUA_CLASSBROWSER:
        event.Check(win.document.panel.LeftIsVisible and getattr(win.document, 'init_class_browser', False) and not win.document.multiview)
Mixin.setMixin('mainframe', 'OnLuaUpdateUI', OnLuaUpdateUI)

def on_enter(mainframe, document):
    wx.EVT_UPDATE_UI(mainframe, mainframe.IDM_LUA_CLASSBROWSER, mainframe.OnLuaUpdateUI)
    if mainframe.pref.lua_classbrowser_show and document.init_class_browser == False:
        document.class_browser = not document.class_browser
        document.panel.showWindow(win.pref.python_classbrowser_show_side, document.class_browser)
        if document.panel.LeftIsVisible:
            if document.init_class_browser == False:
                document.init_class_browser = True
                document.outlinebrowser.show()
Mixin.setPlugin('luafiletype', 'on_enter', on_enter)

def on_leave(mainframe, filename, languagename):
    mainframe.Disconnect(mainframe.IDM_LUA_CLASSBROWSER, -1, wx.wxEVT_UPDATE_UI)
Mixin.setPlugin('luafiletype', 'on_leave', on_leave)

def add_images(images):
    s = [
        ('CLASS_OPEN', 'images/minus.gif'),
        ('CLASS_CLOSE', 'images/plus.gif'),
        ('METHOD', 'images/method.gif'),
        ('MODULE', 'images/module.gif'),
        ('VAR','images/vars.gif'),
        ]
    images.extend(s)
Mixin.setPlugin('outlinebrowser', 'add_images', add_images)

def parsetext(win, editor):
    if editor.edittype == 'edit' and editor.languagename == 'lua':
        import LuaParse as Parser
        nodes = Parser.parseString(editor.GetText())

        for type, info, lineno in nodes:
            win.addnode(None,None, info, win.get_image_id(type), None,  {'data':lineno})

Mixin.setPlugin('outlinebrowser', 'parsetext', parsetext)

toollist = [
    (2000, 'classbrowser'),
    (2010, 'classbrowserrefresh'),
    (2050, '|'),
]
Mixin.setMixin('luafiletype', 'toollist', toollist)

#order, IDname, imagefile, short text, long text, func
toolbaritems = {
    'classbrowser':(wx.ITEM_CHECK, 'IDM_LUA_CLASSBROWSER', 'images/classbrowser.gif', tr('class browser'), tr('Class browser'), 'OnLuaClassBrowser'),
    'classbrowserrefresh':(wx.ITEM_NORMAL, 'IDM_LUA_CLASSBROWSER_REFRESH', 'images/classbrowserrefresh.gif', tr('class browser refresh'), tr('Class browser refresh'), 'OnLuaClassBrowserRefresh'),
}
Mixin.setMixin('luafiletype', 'toolbaritems', toolbaritems)
