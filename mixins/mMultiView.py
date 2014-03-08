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
#   $Id$

import wx
from modules import Mixin
from modules import Globals

def add_editor_menu(popmenulist):
    popmenulist.extend([ (None,
        [
            (200, 'IDPM_MULTIVIEWWINDOW', tr('Open Multiview Window'), wx.ITEM_NORMAL, 'OnMultiViewWindow', tr('Opens the multiview window.')),
        ]),
    ])
Mixin.setPlugin('notebook', 'add_menu', add_editor_menu)

def createMultiViewWindow(win, side, document):
    dispname = document.getShortFilename()
    filename = document.filename

    obj = None
    for pagename, panelname, notebook, page in win.panel.getPages():
        if is_multiview(page, document):
            obj = page
            break
    if not obj:
        if hasattr(document, 'GetDocPointer'):
            from mixins import Editor
            
            page = Editor.TextEditor(win.panel.createNotebook(side), None, filename, document.documenttype, multiview=True)
            page.SetDocPointer(document.GetDocPointer())
            page.document = document    #save document object
            document.lexer.colourize(page, True)
            win.panel.addPage(side, page, dispname)
            win.panel.setImageIndex(page, 'document')
            return page
    else:
        return obj
Mixin.setMixin('mainframe', 'createMultiViewWindow', createMultiViewWindow)

def OnMultiViewWindow(win, event):
    side = win.getSide()
    dispname = win.mainframe.createMultiViewWindow(side, Globals.mainframe.editctrl.getCurDoc())
    if dispname:
        win.panel.showPage(dispname)
Mixin.setMixin('notebook', 'OnMultiViewWindow', OnMultiViewWindow)

def closefile(win, document, filename):
    for pagename, panelname, notebook, page in Globals.mainframe.panel.getPages():
        if is_multiview(page, document):
            Globals.mainframe.panel.closePage(page)
Mixin.setPlugin('mainframe', 'closefile', closefile)

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_WINDOW',
        [
            (220, 'IDM_WINDOW_MULTIVIEWWINDOW', tr('Open Multiview Window'), wx.ITEM_NORMAL, 'OnWindowMultiView', tr('Opens the multiview window.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def OnWindowMultiView(win, event):
    dispname = win.createMultiViewWindow('bottom', Globals.mainframe.document)
    if dispname:
        win.panel.showPage(dispname)
Mixin.setMixin('mainframe', 'OnWindowMultiView', OnWindowMultiView)

def setfilename(document, filename):
    for pagename, panelname, notebook, page in Globals.mainframe.panel.getPages():
        if is_multiview(page, document):
            title = document.getShortFilename()
            Globals.mainframe.panel.setName(page, title)
Mixin.setPlugin('editor', 'setfilename', setfilename)
    
def other_popup_menu(editctrl, document, menus):
    if document.documenttype == 'texteditor':
        menus.extend([ (None,
            [
                (600, '', '-', wx.ITEM_SEPARATOR, None, ''),
                (700, 'IDPM_MULTIVIEW_LEFT', tr('Open MultiView In Left Pane'), wx.ITEM_NORMAL, 'OnOpenViewLeft', tr('Opens the multiview of current document in left pane.')),
                (800, 'IDPM_MULTIVIEW_BOTTOM', tr('Open MultiView In Bottom Pane'), wx.ITEM_NORMAL, 'OnOpenViewBottom', tr('Opens the multiview of current document in bottom pane.')),
            ]),
        ])
Mixin.setPlugin('editctrl', 'other_popup_menu', other_popup_menu)

def OnOpenViewLeft(win, event):
    dispname = win.mainframe.createMultiViewWindow('left', Globals.mainframe.editctrl.getCurDoc())
    if dispname:
        win.mainframe.panel.showPage(dispname)
Mixin.setMixin('editctrl', 'OnOpenViewLeft', OnOpenViewLeft)

def OnOpenViewBottom(win, event):
    dispname = win.mainframe.createMultiViewWindow('bottom', Globals.mainframe.editctrl.getCurDoc())
    if dispname:
        win.mainframe.panel.showPage(dispname)
Mixin.setMixin('editctrl', 'OnOpenViewBottom', OnOpenViewBottom)

def is_multiview(page, document):
    if (hasattr(page, 'multiview') and page.multiview and 
            hasattr(page, 'document') and page.document is document):
        return True
    else:
        return False
