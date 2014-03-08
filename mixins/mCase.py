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
#   $Id: mCase.py 1874 2007-01-29 00:47:08Z limodou $

__doc__ = 'uppercase and lowercase processing'

import wx
from modules import Mixin

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_EDIT',
        [
            (260, 'IDM_EDIT_CASE', tr('Case'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDM_EDIT_CASE',
        [
            (100, 'IDM_EDIT_CASE_UPPER_CASE', tr('Uppercase') + '\tE=Ctrl+U', wx.ITEM_NORMAL, 'OnEditCaseUpperCase', tr('Changes the selected text to upper case.')),
            (200, 'IDM_EDIT_CASE_LOWER_CASE', tr('Lowercase') + '\tE=Ctrl+Shift+U', wx.ITEM_NORMAL, 'OnEditCaseLowerCase', tr('Changes the selected text to lower case.')),
            (300, 'IDM_EDIT_CASE_INVERT_CASE', tr('Invert Case'), wx.ITEM_NORMAL, 'OnEditCaseInvertCase', tr('Inverts the case of the selected text.')),
            (400, 'IDM_EDIT_CASE_CAPITALIZE', tr('Capitalize'), wx.ITEM_NORMAL, 'OnEditCaseCapitalize', tr('Capitalizes all words of the selected text.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_editor_menu(popmenulist):
    popmenulist.extend([ (None, #parent menu id
        [
            (230, 'IDPM_CASE', tr('Case'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDPM_CASE',
        [
            (100, 'IDPM_CASE_UPPER_CASE', tr('Uppercase') + '\tCtrl+U', wx.ITEM_NORMAL, 'OnCaseUpperCase', tr('Changes the selected text to upper case.')),
            (200, 'IDPM_CASE_LOWER_CASE', tr('Lowercase') + '\tCtrl+Shift+U', wx.ITEM_NORMAL, 'OnCaseLowerCase', tr('Changes the selected text to lower case.')),
            (300, 'IDPM_CASE_INVERT_CASE', tr('Invert Case'), wx.ITEM_NORMAL, 'OnCaseInvertCase', tr('Inverts the case of the selected text.')),
            (400, 'IDPM_CASE_CAPITALIZE', tr('Capitalize'), wx.ITEM_NORMAL, 'OnCaseCapitalize', tr('Capitalizes all words of the selected text.')),
        ]),
    ])
Mixin.setPlugin('editor', 'add_menu', add_editor_menu)

def OnEditCaseUpperCase(win, event):
    text = win.document.GetSelectedText()
    if len(text) > 0:
        text = text.upper()
        win.document.BeginUndoAction()
        win.document.ReplaceSelection(text)
        win.document.EndUndoAction()
Mixin.setMixin('mainframe', 'OnEditCaseUpperCase', OnEditCaseUpperCase)

def OnEditCaseLowerCase(win, event):
    text = win.document.GetSelectedText()
    if len(text) > 0:
        text = text.lower()
        win.document.BeginUndoAction()
        win.document.ReplaceSelection(text)
        win.document.EndUndoAction()
Mixin.setMixin('mainframe', 'OnEditCaseLowerCase', OnEditCaseLowerCase)

def OnEditCaseInvertCase(win, event):
    text = win.document.GetSelectedText()
    if len(text) > 0:
        text = text.swapcase()
        win.document.BeginUndoAction()
        win.document.ReplaceSelection(text)
        win.document.EndUndoAction()
Mixin.setMixin('mainframe', 'OnEditCaseInvertCase', OnEditCaseInvertCase)

def OnEditCaseCapitalize(win, event):
    text = win.document.GetSelectedText()
    if len(text) > 0:
        s=[]
        word = False
        for ch in text:
            if 'a' <= ch.lower() <= 'z':
                if word == False:
                    ch = ch.upper()
                    word = True
            else:
                if word == True:
                    word = False
            s.append(ch)
        text = ''.join(s)
        win.document.BeginUndoAction()
        win.document.ReplaceSelection(text)
        win.document.EndUndoAction()
Mixin.setMixin('mainframe', 'OnEditCaseCapitalize', OnEditCaseCapitalize)

def OnCaseUpperCase(win, event):
    event.SetId(win.mainframe.IDM_EDIT_CASE_UPPER_CASE)
    OnEditCaseUpperCase(win.mainframe, event)
Mixin.setMixin('editor', 'OnCaseUpperCase', OnCaseUpperCase)

def OnCaseLowerCase(win, event):
    event.SetId(win.mainframe.IDM_EDIT_CASE_LOWER_CASE)
    OnEditCaseLowerCase(win.mainframe, event)
Mixin.setMixin('editor', 'OnCaseLowerCase', OnCaseLowerCase)

def OnCaseInvertCase(win, event):
    event.SetId(win.mainframe.IDM_EDIT_CASE_INVERT_CASE)
    OnEditCaseInvertCase(win.mainframe, event)
Mixin.setMixin('editor', 'OnCaseInvertCase', OnCaseInvertCase)

def OnCaseCapitalize(win, event):
    event.SetId(win.mainframe.IDM_EDIT_CASE_CAPITALIZE)
    OnEditCaseCapitalize(win.mainframe, event)
Mixin.setMixin('editor', 'OnCaseCapitalize', OnCaseCapitalize)

def mainframe_init(win):
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_CASE_CAPITALIZE, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'init', mainframe_init)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDM_EDIT_CASE_CAPITALIZE:
        event.Enable(win.document.GetSelectedText and len(win.document.GetSelectedText()) > 0)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def editor_init(win):
    wx.EVT_UPDATE_UI(win, win.IDPM_CASE_CAPITALIZE, win.OnUpdateUI)
Mixin.setPlugin('editor', 'init', editor_init)

def on_editor_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDPM_CASE_CAPITALIZE:
        event.Enable(len(win.GetSelectedText()) > 0)
Mixin.setPlugin('editor', 'on_update_ui', on_editor_updateui)
