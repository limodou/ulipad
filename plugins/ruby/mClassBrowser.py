#   Programmer: limodou
#   E-mail:     limodou@gmail.com
#
#   Copyleft 2006 limodou
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
from modules import Mixin

def init(pref):
    pref.ruby_classbrowser_show = False
    pref.ruby_classbrowser_refresh_as_save = True
Mixin.setPlugin('preference', 'init', init)

preflist = [
    ('Ruby', 100, 'check', 'ruby_classbrowser_show', tr('Show class browser window as open ruby source file'), None),
    ('Ruby', 105, 'check', 'ruby_classbrowser_refresh_as_save', tr('Refresh class browser window as saved ruby source file'), None),
]
Mixin.setMixin('preference', 'preflist', preflist)

menulist = [('IDM_RUBY', #parent menu id
        [
            (100, 'IDM_RUBY_CLASSBROWSER', tr('Class Browser'), wx.ITEM_CHECK, 'OnRubyClassBrowser', tr('Show ruby class browser window')),
            (110, 'IDM_RUBY_CLASSBROWSER_REFRESH', tr('Class Browser Refresh'), wx.ITEM_NORMAL, 'OnRubyClassBrowserRefresh', tr('Refresh ruby class browser window')),
        ]),
]
Mixin.setMixin('rubyfiletype', 'menulist', menulist)

def init(win):
    win.class_browser = False
    win.init_class_browser = False
Mixin.setPlugin('editor', 'init', init)

def OnRubyClassBrowser(win, event):
    win.document.class_browser = not win.document.class_browser
    win.document.panel.showWindow('LEFT', win.document.class_browser)
    if win.document.panel.LeftIsVisible:
        if win.document.init_class_browser == False:
            win.document.init_class_browser = True
            win.document.outlinebrowser.show()
Mixin.setMixin('mainframe', 'OnRubyClassBrowser', OnRubyClassBrowser)

def aftersavefile(win, filename):
    if (win.edittype == 'edit'
        and win.languagename == 'ruby'
        and win.pref.ruby_classbrowser_refresh_as_save
        and win.init_class_browser):
        win.outlinebrowser.show()
Mixin.setPlugin('editor', 'aftersavefile', aftersavefile)

def OnRubyClassBrowserRefresh(win, event):
    win.document.outlinebrowser.show()
Mixin.setMixin('mainframe', 'OnRubyClassBrowserRefresh', OnRubyClassBrowserRefresh)

def OnRubyUpdateUI(win, event):
    eid = event.GetId()
    if eid == win.IDM_RUBY_CLASSBROWSER:
        event.Check(win.document.panel.LeftIsVisible and getattr(win.document, 'init_class_browser', False) and not win.document.multiview)
Mixin.setMixin('mainframe', 'OnRubyUpdateUI', OnRubyUpdateUI)

def on_enter(mainframe, document):
    wx.EVT_UPDATE_UI(mainframe, mainframe.IDM_RUBY_CLASSBROWSER, mainframe.OnRubyUpdateUI)
    if mainframe.pref.ruby_classbrowser_show and document.init_class_browser == False:
        document.class_browser = not document.class_browser
        document.panel.showWindow('LEFT', document.class_browser)
        if document.panel.LeftIsVisible:
            if document.init_class_browser == False:
                document.init_class_browser = True
                document.outlinebrowser.show()
Mixin.setPlugin('rubyfiletype', 'on_enter', on_enter)

def on_leave(mainframe, filename, languagename):
    mainframe.Disconnect(mainframe.IDM_RUBY_CLASSBROWSER, -1, wx.wxEVT_UPDATE_UI)
Mixin.setPlugin('rubyfiletype', 'on_leave', on_leave)

def add_images(images):
    s = [
        ('CLASS_OPEN', 'images/minus.gif'),
        ('CLASS_CLOSE', 'images/plus.gif'),
        ('METHOD', 'images/method.gif'),
        ('MODULE', 'images/module.gif'),
        ]
    images.extend(s)
Mixin.setPlugin('outlinebrowser', 'add_images', add_images)

def parsetext(win, editor):
    if editor.edittype == 'edit' and editor.languagename == 'ruby':
        import RbParse as Parser
        nodes = Parser.parseString(editor.GetText())

        imports = nodes['import']
        for i, v in enumerate(imports):
            info, lineno = v
            win.replacenode(None, i, info, win.get_image_id('MODULE'), None, {'data':lineno}, win.get_image_id('MODULE'))
        functions = nodes['function'].values()
        functions.sort()
        for i, v in enumerate(functions):
            info, lineno = v
            win.replacenode(None, i, info, win.get_image_id('METHOD'), None,  {'data':lineno}, win.get_image_id('METHOD'))
        classes = nodes['class'].values()
        classes.sort()
        for i, c in enumerate(classes):
            _id, node = win.replacenode(None, i, c.info, win.get_image_id('CLASS_CLOSE'), win.get_image_id('CLASS_OPEN'), {'data':c.lineno},
                win.get_image_id('CLASS_CLOSE'))
            functions = c.methods.values()
            functions.sort()
            for j, v in enumerate(functions):
                info, lineno = v
                win.replacenode(node, j, info, win.get_image_id('METHOD'), None,  {'data':lineno}, win.get_image_id('METHOD'))
            win.tree.Expand(node)
Mixin.setPlugin('outlinebrowser', 'parsetext', parsetext)

toollist = [
    (2000, 'classbrowser'),
    (2010, 'classbrowserrefresh'),
    (2050, '|'),
]
Mixin.setMixin('rubyfiletype', 'toollist', toollist)

#order, IDname, imagefile, short text, long text, func
toolbaritems = {
    'classbrowser':(wx.ITEM_CHECK, 'IDM_RUBY_CLASSBROWSER', 'images/classbrowser.gif', tr('class browser'), tr('Class browser'), 'OnRubyClassBrowser'),
    'classbrowserrefresh':(wx.ITEM_NORMAL, 'IDM_RUBY_CLASSBROWSER_REFRESH', 'images/classbrowserrefresh.gif', tr('class browser refresh'), tr('Class browser refresh'), 'OnRubyClassBrowserRefresh'),
}
Mixin.setMixin('rubyfiletype', 'toolbaritems', toolbaritems)
