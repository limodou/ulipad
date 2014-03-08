#   Programmer: limodou
#   E-mail:     limodou@gmail.com
#
#   Copyleft 2009 limodou
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
from modules import common

def add_mainframe_menu(menulist):
    menulist.extend([
#        ('IDM_TOOL',
#        [
#            (125, 'IDM_WINDOW_CODESNIPPET', tr('Code Snippets'), wx.ITEM_NORMAL, 'OnWindowCodeSnippet', tr('Opens code snippet window.'))
#        ]),
        ('IDM_WINDOW',
        [
            (151, 'IDM_WINDOW_CODESNIPPET', tr('Code Snippets Window'), wx.ITEM_CHECK, 'OnWindowCodeSnippet', tr('Opens code snippets window.'))
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_notebook_menu(popmenulist):
    popmenulist.extend([(None,
        [
            (135, 'IDPM_CODESNIPPETWINDOW', tr('Code Snippets Window'), wx.ITEM_CHECK, 'OnCodeSnippetWindow', tr('Opens code snippet window.')),
        ]),
    ])
Mixin.setPlugin('notebook', 'add_menu', add_notebook_menu)

def add_images(images):
    images.update({
        'close': 'images/folderclose.gif',
        'open': 'images/folderopen.gif',
        'item': 'images/file.gif',
        })
Mixin.setPlugin('codesnippet', 'add_images', add_images)

def add_image(imagelist, imageids, name, image):
    if name not in ('close', 'open'):
        return

    m = [
        ('modified', common.getpngimage('images/TortoiseModified.gif')),
    ]

    for f, imgfile in m:
        bmp = common.merge_bitmaps(image, imgfile)
        index = imagelist.Add(bmp)
        imageids[name+f] = index
Mixin.setPlugin('codesnippet', 'add_image', add_image)

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (650, 'snippet'),
    ])

    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'snippet':(wx.ITEM_CHECK, 'IDM_WINDOW_CODESNIPPET', 'images/snippet.png', tr('Open Code Snippets Window'), tr('Open code snippet window.'), 'OnToolbarWindowCodeSnippet'),
    })
Mixin.setPlugin('mainframe', 'add_tool_list', add_tool_list)

_codesnippet_page_name = tr('Code Snippets')

def createCodeSnippetWindow(win):
    try:
        import xml.etree.ElementTree
    except:
        import elementtree.ElementTree

    page = win.panel.getPage(_codesnippet_page_name)
    if not page:
        from CodeSnippet import CodeSnippetWindow

        page = CodeSnippetWindow(win.panel.createNotebook('left'), win)
        win.panel.addPage('left', page, _codesnippet_page_name)
    return page
Mixin.setMixin('mainframe', 'createCodeSnippetWindow', createCodeSnippetWindow)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_WINDOW_CODESNIPPET, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDM_WINDOW_CODESNIPPET:
        page = win.panel.getPage(_codesnippet_page_name)
        event.Check(bool(page) and win.panel.LeftIsVisible)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def on_notebook_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDPM_CODESNIPPETWINDOW:
        event.Check(bool(win.panel.getPage(_codesnippet_page_name)) and win.panel.LeftIsVisible)
Mixin.setPlugin('notebook', 'on_update_ui', on_notebook_updateui)

def init(win):
    wx.EVT_UPDATE_UI(win, win.IDPM_CODESNIPPETWINDOW, win.OnUpdateUI)
Mixin.setPlugin('notebook', 'init', init)

def OnToolbarWindowCodeSnippet(win, event):
    page = win.panel.getPage(_codesnippet_page_name)
    if page:
        win.panel.closePage(_codesnippet_page_name)
    else:
        if win.createCodeSnippetWindow():
            win.panel.showPage(_codesnippet_page_name)
Mixin.setMixin('mainframe', 'OnToolbarWindowCodeSnippet', OnToolbarWindowCodeSnippet)

def OnWindowCodeSnippet(win, event):
    page = win.panel.getPage(_codesnippet_page_name)
    if page:
        win.panel.closePage(_codesnippet_page_name)
    else:
        if win.createCodeSnippetWindow():
            win.panel.showPage(_codesnippet_page_name)
Mixin.setMixin('mainframe', 'OnWindowCodeSnippet', OnWindowCodeSnippet)

def OnCodeSnippetWindow(win, event):
    page = win.mainframe.panel.getPage(_codesnippet_page_name)
    if page:
        win.mainframe.panel.closePage(_codesnippet_page_name)
    else:
        if win.mainframe.createCodeSnippetWindow():
            win.mainframe.panel.showPage(_codesnippet_page_name)
Mixin.setMixin('notebook', 'OnCodeSnippetWindow', OnCodeSnippetWindow)

def close_page(page, name):
    if name == tr('Code Snippet'):
        win = Globals.mainframe
        for pagename, panelname, notebook, page in win.panel.getPages():
            if hasattr(page, 'code_snippet') and page.code_snippet:
                ret = win.panel.closePage(page, savestatus=False)
                break
Mixin.setPlugin('notebook', 'close_page', close_page)

def on_close(win, event):
    if event.CanVeto():
        win = Globals.mainframe
        snippet = win.panel.getPage(_codesnippet_page_name)
        if snippet:
            return not snippet.canClose()
Mixin.setPlugin('mainframe', 'on_close', on_close)

def pref_init(pref):
    pref.snippet_recents = []
    pref.snippet_lastdir = ''
    pref.snippet_files = []
Mixin.setPlugin('preference', 'init', pref_init)

def createCodeSnippetEditWindow(win):
    snippet = None
    for pagename, panelname, notebook, page in win.panel.getPages():
        if hasattr(page, 'code_snippet') and page.code_snippet:
            snippet = page
            break
    if not snippet:
        from mixins.Editor import TextEditor
        snippet = TextEditor(win.panel.createNotebook('bottom'), None, 'Snippet', 'texteditor', True)
        #.document is important
        snippet.document = snippet
        snippet.cansavefileflag = False
        snippet.needcheckfile = False
        snippet.savesession = False
        snippet.code_snippet = True
        win.panel.addPage('bottom', snippet, tr('Snippet'))
    if snippet:
        win.panel.showPage(snippet)
        return snippet
Mixin.setMixin('mainframe', 'createCodeSnippetEditWindow', createCodeSnippetEditWindow)

def on_modified(win):
    if hasattr(win, 'code_snippet') and win.code_snippet:
        if not win.snippet_obj.changing:
            win.snippet_obj.update_node(win.snippet_obj.tree.GetSelection(), newcontent=win.GetText())
Mixin.setPlugin('editor', 'on_modified', on_modified)

def on_selected(win, text):
    doc = Globals.mainframe.editctrl.getCurDoc()
    doc.AddText(text)
    wx.CallAfter(doc.SetFocus)
Mixin.setPlugin('codesnippet', 'on_selected', on_selected)
