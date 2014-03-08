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
#   $Id: mHtmlFileType.py 1624 2006-10-19 02:27:11Z limodou $

__doc__ = 'Html syntax highlitght process'

import wx
from modules import Mixin
import FiletypeBase
from modules import Globals

class HtmlFiletype(FiletypeBase.FiletypeBase):

    __mixinname__ = 'htmlfiletype'
    menulist = [ (None,
        [
            (890, 'IDM_HTML', 'HTML', wx.ITEM_NORMAL, None, ''),
        ]),
    ]
    toollist = []               #your should not use supperclass's var
    toolbaritems= {}

def add_filetypes(filetypes):
    filetypes.extend([('html', HtmlFiletype)])
Mixin.setPlugin('changefiletype', 'add_filetypes', add_filetypes)

def add_html_menu(menulist):
    menulist.extend([('IDM_HTML', #parent menu id
            [
                (100, 'IDM_HTML_BROWSER_LEFT', tr('View HTML Content In Left Pane'), wx.ITEM_NORMAL, 'OnHtmlBrowserInLeft', tr('Views html content in left pane.')),
                (110, 'IDM_HTML_BROWSER_BOTTOM', tr('View HTML Content In Bottom Pane'), wx.ITEM_NORMAL, 'OnHtmlBrowserInBottom', tr('Views html content in bottom pane.')),
            ]),
    ])
Mixin.setPlugin('htmlfiletype', 'add_menu', add_html_menu)

def OnHtmlBrowserInLeft(win, event):
    dispname = win.createHtmlViewWindow('left', Globals.mainframe.editctrl.getCurDoc())
    if dispname:
        win.panel.showPage(dispname)
Mixin.setMixin('mainframe', 'OnHtmlBrowserInLeft', OnHtmlBrowserInLeft)

def OnHtmlBrowserInBottom(win, event):
    dispname = win.createHtmlViewWindow('bottom', Globals.mainframe.editctrl.getCurDoc())
    if dispname:
        win.panel.showPage(dispname)
Mixin.setMixin('mainframe', 'OnHtmlBrowserInBottom', OnHtmlBrowserInBottom)

def createHtmlViewWindow(win, side, document):
    dispname = document.getShortFilename()
    obj = None
    for pagename, panelname, notebook, page in win.panel.getPages():
        if is_htmlview(page, document):
            obj = page
            break
    
    if not obj:
        if win.document.documenttype == 'texteditor':
            from mixins import HtmlPage
            page = HtmlPage.HtmlImpactView(win.panel.createNotebook(side), document.getRawText())
            page.document = win.document    #save document object
            page.htmlview = True
            win.panel.addPage(side, page, dispname)
            win.panel.setImageIndex(page, 'html')
            return page
    else:
        obj.load(document.getRawText())
        return obj
Mixin.setMixin('mainframe', 'createHtmlViewWindow', createHtmlViewWindow)

#add menu to editctrl
def other_popup_menu(editctrl, document, menus):
    if document.documenttype == 'texteditor' and document.languagename == 'html':
        menus.extend([ (None,
            [
                (920, 'IDPM_HTML_VIEW_LEFT', tr('View Html Content in Left Pane'), wx.ITEM_NORMAL, 'OnHtmlHtmlViewLeft', tr('Views html content in left pane.')),
                (930, 'IDPM_HTML_VIEW_BOTTOM', tr('View Html Content in Bottom Pane'), wx.ITEM_NORMAL, 'OnHtmlHtmlViewBottom', tr('Views html content in bottom pane.')),
            ]),
        ])
Mixin.setPlugin('editctrl', 'other_popup_menu', other_popup_menu)

def OnHtmlHtmlViewLeft(win, event=None):
    win.mainframe.OnHtmlBrowserInLeft(None)
Mixin.setMixin('editctrl', 'OnHtmlHtmlViewLeft', OnHtmlHtmlViewLeft)

def OnHtmlHtmlViewBottom(win, event=None):
    win.mainframe.OnHtmlBrowserInBottom(None)
Mixin.setMixin('editctrl', 'OnHtmlHtmlViewBottom', OnHtmlHtmlViewBottom)

#common functions
def setfilename(document, filename):
    for pagename, panelname, notebook, page in Globals.mainframe.panel.getPages():
        if is_htmlview(page, document):
            title = document.getShortFilename()
            Globals.mainframe.panel.setName(page, title)
Mixin.setPlugin('editor', 'setfilename', setfilename)

def closefile(win, document, filename):
    for pagename, panelname, notebook, page in Globals.mainframe.panel.getPages():
        if is_htmlview(page, document):
            Globals.mainframe.panel.closePage(page)
Mixin.setPlugin('mainframe', 'closefile', closefile)

def is_htmlview(page, document):
    if hasattr(page, 'htmlview') and page.htmlview and page.document is document:
        return True
    else:
        return False