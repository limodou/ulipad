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
#   $Id: mToolbar.py 1896 2007-02-03 09:02:39Z limodou $

import wx
from modules import Mixin
from modules import maketoolbar

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (100, 'new'),
        (110, 'open'),
        (120, 'save'),
        (121, 'saveall'),
        (130, '|'),
        (140, 'cut'),
        (150, 'copy'),
        (160, 'paste'),
        (170, '|'),
        (180, 'undo'),
        (190, 'redo'),
        (200, '|'),
        (400, 'preference'),
        (900, '|'),
    ])

    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'new':(wx.ITEM_NORMAL, 'IDM_FILE_NEW', 'images/new.gif', tr('New Document'), tr('Creates a new document.'), 'OnFileNew'),
        'open':(wx.ITEM_NORMAL, 'IDM_FILE_OPEN', 'images/open.gif', tr('Open Document'), tr('Opens an existing document.'), 'OnFileOpen'),
        'save':(wx.ITEM_NORMAL, 'IDM_FILE_SAVE', 'images/save.gif', tr('Save Document'), tr('Saves an opened document using the same filename.'), 'OnFileSave'),
        'saveall':(wx.ITEM_NORMAL, 'IDM_FILE_SAVE_ALL', 'images/saveall.gif', tr('Save All Documents'), tr('Saves all documents.'), 'OnFileSaveAll'),
        'cut':(wx.ITEM_NORMAL, 'IDM_EDIT_CUT', 'images/cut.gif', tr('Cut'), tr('Deletes text from the document and moves it to the clipboard.'), 'DoSTCBuildIn'),
        'copy':(wx.ITEM_NORMAL, 'IDM_EDIT_COPY', 'images/copy.gif', tr('Copy'), tr('Copies text from the document to the clipboard.'), 'DoSTCBuildIn'),
        'paste':(wx.ITEM_NORMAL, 'IDM_EDIT_PASTE', 'images/paste.gif', tr('Paste'), tr('Pastes text from the clipboard into the document.'), 'DoSTCBuildIn'),
        'undo':(wx.ITEM_NORMAL, 'IDM_EDIT_UNDO', 'images/undo.gif', tr('Undo'), tr('Reverse previous editing operation.'), 'DoSTCBuildIn'),
        'redo':(wx.ITEM_NORMAL, 'IDM_EDIT_REDO', 'images/redo.gif', tr('Redo'), tr('Reverse previous undo operation.'), 'DoSTCBuildIn'),
        'preference':(wx.ITEM_NORMAL, 'wx.ID_PREFERENCES', 'images/prop.gif', tr('Preferences'), tr('Opens the Preferences window.'), 'OnOptionPreference'),
    })
Mixin.setPlugin('mainframe', 'add_tool_list', add_tool_list)

def beforeinit(win):
    maketoolbar.maketoolbar(win, win.toollist, win.toolbaritems)
Mixin.setPlugin('mainframe', 'beforeinit', beforeinit)
