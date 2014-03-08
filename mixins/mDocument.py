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
#   $Id: mDocument.py 1935 2007-02-11 00:39:59Z limodou $

import wx
import StringIO
from modules import Mixin

def add_mainframe_menu(menulist):
    menulist.extend([ (None,
        [
            (500, 'IDM_DOCUMENT', tr('Document'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDM_DOCUMENT', #parent menu id
        [
            (100, 'IDM_DOCUMENT_WORDWRAP', tr('Word Wrap'), wx.ITEM_NORMAL, 'OnDocumentWordWrap', tr('Toggles the word wrap feature of the current document.')),
            (110, 'IDM_DOCUMENT_AUTOINDENT', tr('Autoindent'), wx.ITEM_CHECK, 'OnDocumentAutoIndent', tr('Toggles the autoindent feature of the current document.')),
            (115, 'IDM_DOCUMENT_TABINDENT', tr('Switch To Space Indent'), wx.ITEM_NORMAL, 'OnDocumentTabIndent', tr('Uses tab as indent char or uses space as indent char.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_mainframe_menu_image_list(imagelist):
    imagelist.update({
        'IDM_DOCUMENT_WORDWRAP':'images/wrap.gif',
    })
Mixin.setPlugin('mainframe', 'add_menu_image_list', add_mainframe_menu_image_list)

def pref_init(pref):
    pref.autoindent = True
    pref.usetabs = False
    pref.wordwrap = False
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('Document')+'/'+tr('Edit'), 100, 'check', 'autoindent', tr('Autoindent'), None),
        (tr('Document')+'/'+tr('Edit'), 110, 'check', 'usetabs', tr('Use tabs'), None),
        (tr('Document')+'/'+tr('Edit'), 120, 'check', 'wordwrap', tr('Automatically word wrap'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def savepreference(mainframe, pref):
    for document in mainframe.editctrl.getDocuments():
        if mainframe.pref.wordwrap:
            document.SetWrapMode(wx.stc.STC_WRAP_WORD)
        else:
            document.SetWrapMode(wx.stc.STC_WRAP_NONE)
Mixin.setPlugin('prefdialog', 'savepreference', savepreference)

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (805, 'wrap'),
    ])

    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'wrap':(wx.ITEM_CHECK, 'IDM_DOCUMENT_WORDWRAP', 'images/wrap.gif', tr('Toggle Wrap Mode'), tr('Toggles the word wrap feature of the current document.'), 'OnDocumentWordWrap'),
    })
Mixin.setPlugin('mainframe', 'add_tool_list', add_tool_list)

def editor_init(win):
    win.SetUseTabs(win.mainframe.pref.usetabs)
    win.usetab = win.mainframe.pref.usetabs
    if win.pref.wordwrap:
        win.SetWrapMode(wx.stc.STC_WRAP_WORD)
    else:
        win.SetWrapMode(wx.stc.STC_WRAP_NONE)
Mixin.setPlugin('editor', 'init', editor_init)

def OnKeyDown(win, event):
    if event.GetKeyCode() == wx.WXK_RETURN:
        if win.GetSelectedText():
            win.CmdKeyExecute(wx.stc.STC_CMD_NEWLINE)
            return True
        if win.pref.autoindent:
            line = win.GetCurrentLine()
            text = win.GetTextRange(win.PositionFromLine(line), win.GetCurrentPos())
            if text.strip() == '':
                win.AddText(win.getEOLChar() + text)
                win.EnsureCaretVisible()
                return True

            n = win.GetLineIndentation(line) / win.GetTabWidth()
            win.AddText(win.getEOLChar() + win.getIndentChar() * n)
            win.EnsureCaretVisible()
            return True
        else:
            win.AddText(win.getEOLChar())
            win.EnsureCaretVisible()
            return True
Mixin.setPlugin('editor', 'on_key_down', OnKeyDown, Mixin.LOW)

def OnDocumentWordWrap(win, event):
    mode = win.document.GetWrapMode()
    if mode == wx.stc.STC_WRAP_NONE:
        win.document.SetWrapMode(wx.stc.STC_WRAP_WORD)
    else:
        win.document.SetWrapMode(wx.stc.STC_WRAP_NONE)
Mixin.setMixin('mainframe', 'OnDocumentWordWrap', OnDocumentWordWrap)

def OnDocumentAutoIndent(win, event):
    win.pref.autoindent = not win.pref.autoindent
    win.pref.save()
Mixin.setMixin('mainframe', 'OnDocumentAutoIndent', OnDocumentAutoIndent)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_DOCUMENT_WORDWRAP, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_DOCUMENT_AUTOINDENT, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_DOCUMENT_TABINDENT, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if hasattr(win, 'document') and win.document:
        if eid == win.IDM_DOCUMENT_WORDWRAP:
            if win.document.GetWrapMode:
                event.Enable(True)
                mode = win.document.GetWrapMode()
                if mode == wx.stc.STC_WRAP_NONE:
                    event.Check(False)
                else:
                    event.Check(True)
            else:
                event.Enable(False)
        elif eid == win.IDM_DOCUMENT_AUTOINDENT:
            if win.document.canedit:
                event.Enable(True)
                event.Check(win.pref.autoindent)
            else:
                event.Enable(False)
        elif eid == win.IDM_DOCUMENT_TABINDENT:
            if win.document.canedit:
                event.Enable(True)
                from modules import makemenu
                menu = makemenu.findmenu(win.menuitems, 'IDM_DOCUMENT_TABINDENT')
                if win.document.usetab:
                    menu.SetText(tr('Switch To Space Indent'))
                else:
                    menu.SetText(tr('Switch To Tab Indent'))
            else:
                event.Enable(False)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def openfiletext(win, stext):
    pos = 0
    text = stext[0]

    buf = StringIO.StringIO(text)
    while 1:
        line = buf.readline()
        if line:
            if line[0] == ' ':
                win.SetUseTabs(False)
                win.usetab = False
                return
            elif line[0] == '\t':
                win.SetUseTabs(True)
                win.usetab = True
                return
        else:
            break
    win.SetUseTabs(win.mainframe.pref.usetabs)
    win.usetab = win.mainframe.pref.usetabs
Mixin.setPlugin('editor', 'openfiletext', openfiletext)

def OnDocumentTabIndent(win, event):
    win.document.usetab = not win.document.usetab
    win.document.SetUseTabs(win.document.usetab)
Mixin.setMixin('mainframe', 'OnDocumentTabIndent', OnDocumentTabIndent)
