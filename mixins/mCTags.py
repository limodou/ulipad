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
#   $Id: mFormat.py 1457 2006-08-23 02:12:12Z limodou $

import os
import wx.stc
from modules import Mixin
from modules import common
from modules import dict4ini
from modules.Debug import error

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_SEARCH',
        [
            (175, 'IDM_SEARCH_GOTO_DEF', tr('Jump To The Definition')+'\tE=Ctrl+I', wx.ITEM_NORMAL, 'OnSearchJumpDef', tr('Jumps to head of line containing variable or function definition.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_editor_menu(popmenulist):
    popmenulist.extend([ (None, #parent menu id
        [
            (10, 'IDPM_GOTO_DEF', tr('Jump To The Definition')+'\tCtrl+I', wx.ITEM_NORMAL, 'OnJumpDef', tr('Jumps to definition.')),
        ]),
    ])
Mixin.setPlugin('editor', 'add_menu', add_editor_menu)

_mlist = {}
def OnSearchJumpDef(win, event):
    global _mlist
    
    word = getword(win)
    from modules import ctags
    
    flag = False
    prjfile = common.getProjectFile(win.document.getFilename())
    if prjfile:
        path = os.path.dirname(prjfile)
        ini = dict4ini.DictIni(prjfile)
        s = []
        for c in ini.ctags.values():
            c = os.path.join(path, c)
            p = os.path.dirname(c)
            try:
                s.extend(ctags.get_def(c, word, p))
            except:
                error.traceback()
        if len(s) == 1:
            d, f, m = s[0]
            win.editctrl.new(f)
            flag = jump_to_file(win, d, f, m)
        elif len(s) > 1:
            text = []
            _mlist = {}
            for i, v in enumerate(s):
                d, f, m = v
                key = str(i+1)+'|'+d+'|'+os.path.basename(f)
                text.append(key)
                _mlist[key] = (d, f, m)
            win.document.UserListShow(2, " ".join(text))
            flag = True
    if not flag:
        win.document.callplugin('on_jump_definition', win.document, word)
Mixin.setMixin('mainframe', 'OnSearchJumpDef', OnSearchJumpDef)

def on_user_list_selction(win, list_type, text):
    t = list_type
    if t == 2:  #1 is used by input assistant
        if _mlist:
            v = _mlist.get(text, None)
            if v:
                d, f, m = v
                jump_to_file(win, d, f, m)
Mixin.setPlugin('editor', 'on_user_list_selction', on_user_list_selction)

def OnJumpDef(win, event):
    win.mainframe.OnSearchJumpDef(event)
Mixin.setMixin('editor', 'OnJumpDef', OnJumpDef)

def getword(mainframe):
    doc = mainframe.document
    if doc.GetSelectedText():
        return doc.GetSelectedText()
    pos = doc.GetCurrentPos()
    start = doc.WordStartPosition(pos, True)
    end = doc.WordEndPosition(pos, True)
    if end > start:
        i = start - 1
        while i >= 0:
            if doc.getChar(i) in mainframe.getWordChars() + '.':
                start -= 1
                i -= 1
            else:
                break
        i = end
        length = doc.GetLength()
        while i < length:
            if doc.getChar(i) in mainframe.getWordChars()+ '.':
                end += 1
                i += 1
            else:
                break
    return doc.GetTextRange(start, end)

def jump_to_file(win, d, f, m):
    doc = win.editctrl.new(f)
    if doc:
        count = doc.GetLineCount()
        if m.startswith('/^') and m.endswith('$/'):
            m = m[2:-2]
        
            for i in range(count):
                line = doc.GetLine(i)
                if line.startswith(m):
                    wx.CallAfter(doc.SetFocus)
                    wx.CallAfter(doc.goto, i-1)
                    return True
        elif m.isdigit():
            wx.CallAfter(doc.SetFocus)
            wx.CallAfter(doc.GotoLine, int(m)-1)
            return True
    return False
        
        