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
#   $Id: mDuplicate.py 2054 2007-04-21 12:54:49Z limodou $

__doc__ = 'Duplicate char, word, line'

from modules import Mixin
import wx
from modules import Calltip

CALLTIP_DUPLICATE = 1

def pref_init(pref):
    pref.duplicate_extend_mode = False
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('Document')+'/'+tr('Edit'), 140, 'check', 'duplicate_extend_mode', tr("Use duplication extend mode and treat a dot as a normal character"), None)
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def add_editor_menu(popmenulist):
    popmenulist.extend([ (None,
        [
            (190, 'IDPM_DUPLICATE', tr('Duplication'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDPM_DUPLICATE', #parent menu id
        [
            (90, 'IDPM_DUPLICATE_MODE', tr('Duplicate Extend Mode') + '\tF10', wx.ITEM_CHECK, 'OnDuplicateMode', tr('Toggle duplication extend mode.')),
            (100, 'IDPM_DUPLICATE_CURRENT_LINE', tr('Duplicate Current Line') + '\tCtrl+J', wx.ITEM_NORMAL, 'OnDuplicateCurrentLine', tr('Duplicates current line.')),
#            (200, 'IDPM_DUPLICATE_CHAR', tr('Duplicate Previous Char') + '\tCtrl+M', wx.ITEM_NORMAL, 'OnDuplicateChar', tr('Copies a character from previous matched word')),
#            (300, 'IDPM_DUPLICATE_NEXT_CHAR', tr('Duplicate Next Char') + '\tCtrl+Shift+M', wx.ITEM_NORMAL, 'OnDuplicateNextChar', tr('Copies a character from next matched word')),
            (400, 'IDPM_DUPLICATE_WORD', tr('Duplicate Previous Word') + '\tCtrl+P', wx.ITEM_NORMAL, 'OnDuplicateWord', tr('Copies a word from previous matched line.')),
            (500, 'IDPM_DUPLICATE_NEXT_WORD', tr('Duplicate Next Word') + '\tCtrl+Shift+P', wx.ITEM_NORMAL, 'OnDuplicateNextWord', tr('Copies a word from next matched line.')),
            (600, 'IDPM_DUPLICATE_LINE', tr('Duplicate Previous Line') + '\tCtrl+L', wx.ITEM_NORMAL, 'OnDuplicateLine', tr('Copies a line from next matched line.')),
            (700, 'IDPM_DUPLICATE_NEXT_LINE', tr('Duplicate Next Line') + '\tCtrl+Shift+L', wx.ITEM_NORMAL, 'OnDuplicateNextLine', tr('Copies a line from next matched line.')),
        ]),
    ])
Mixin.setPlugin('editor', 'add_menu', add_editor_menu)

def editor_init(win):
    win.calltip = Calltip.MyCallTip(win)
    win.calltip_type = -1

    wx.EVT_UPDATE_UI(win, win.IDPM_DUPLICATE_MODE, win.OnUpdateUI)
Mixin.setPlugin('editor', 'init', editor_init)

def getWordChars(win):
    wordchars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
    if win.pref.duplicate_extend_mode:
        return wordchars + '.'
    else:
        return wordchars
Mixin.setMixin('mainframe', 'getWordChars', getWordChars)

def OnDuplicateCurrentLine(win, event):
    win.mainframe.OnEditDuplicateCurrentLine(event)
Mixin.setMixin('editor', 'OnDuplicateCurrentLine', OnDuplicateCurrentLine)

#def OnDuplicateChar(win, event):
#    win.mainframe.OnEditDuplicateChar(event)
#Mixin.setMixin('editor', 'OnDuplicateChar', OnDuplicateChar)
#
#def OnDuplicateNextChar(win, event):
#    win.mainframe.OnEditDuplicateNextChar(event)
#Mixin.setMixin('editor', 'OnDuplicateNextChar', OnDuplicateNextChar)

def OnDuplicateWord(win, event):
    win.mainframe.OnEditDuplicateWord(event)
Mixin.setMixin('editor', 'OnDuplicateWord', OnDuplicateWord)

def OnDuplicateNextWord(win, event):
    win.mainframe.OnEditDuplicateNextWord(event)
Mixin.setMixin('editor', 'OnDuplicateNextWord', OnDuplicateNextWord)

def OnDuplicateLine(win, event):
    win.mainframe.OnEditDuplicateLine(event)
Mixin.setMixin('editor', 'OnDuplicateLine', OnDuplicateLine)

def OnDuplicateNextLine(win, event):
    win.mainframe.OnEditDuplicateNextLine(event)
Mixin.setMixin('editor', 'OnDuplicateNextLine', OnDuplicateNextLine)

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_EDIT', #parent menu id
        [
            (230, 'IDM_EDIT_DUPLICATE', tr('Duplication'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDM_EDIT_DUPLICATE', #parent menu id
        [
            (90, 'IDM_EDIT_DUPLICATE_MODE', tr('Duplicate Extend Mode') + '\tF10', wx.ITEM_CHECK, 'OnEditDuplicateMode', tr('Toggle duplication extend mode.')),
            (100, 'IDM_EDIT_DUPLICATE_CURRENT_LINE', tr('Duplicate Current Line') + '\tE=Ctrl+J', wx.ITEM_NORMAL, 'OnEditDuplicateCurrentLine', tr('Duplicates current line.')),
#            (200, 'IDM_EDIT_DUPLICATE_CHAR', tr('Duplicate Previous Char') + '\tE=Ctrl+M', wx.ITEM_NORMAL, 'OnEditDuplicateChar', tr('Copies a character from previous matched word')),
#            (300, 'IDM_EDIT_DUPLICATE_NEXT_CHAR', tr('Duplicate Next Char') + '\tE=Ctrl+Shift+M', wx.ITEM_NORMAL, 'OnEditDuplicateNextChar', tr('Copies a character from next matched word')),
            (400, 'IDM_EDIT_DUPLICATE_WORD', tr('Duplicate Previous Word') + '\tE=Ctrl+P', wx.ITEM_NORMAL, 'OnEditDuplicateWord', tr('Copies a word from previous matched line.')),
            (500, 'IDM_EDIT_DUPLICATE_NEXT_WORD', tr('Duplicate Next Word') + '\tE=Ctrl+Shift+P', wx.ITEM_NORMAL, 'OnEditDuplicateNextWord', tr('Copies a word from next matched line.')),
            (600, 'IDM_EDIT_DUPLICATE_LINE', tr('Duplicate Previous Line') + '\tE=Ctrl+L', wx.ITEM_NORMAL, 'OnEditDuplicateLine', tr('Copies a line from next matched line.')),
            (700, 'IDM_EDIT_DUPLICATE_NEXT_LINE', tr('Duplicate Next Line') + '\tE=Ctrl+Shift+L', wx.ITEM_NORMAL, 'OnEditDuplicateNextLine', tr('Copies a line from next matched line.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def on_editor_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDPM_DUPLICATE_MODE:
        event.Check(win.pref.duplicate_extend_mode)
Mixin.setPlugin('editor', 'on_update_ui', on_editor_updateui)

def mainframe_init(win):
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_DUPLICATE_MODE, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'init', mainframe_init)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDM_EDIT_DUPLICATE_MODE:
        event.Check(win.pref.duplicate_extend_mode)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def OnDuplicateMode(win, event):
    win.mainframe.OnEditDuplicateMode(event)
Mixin.setMixin('editor', 'OnDuplicateMode', OnDuplicateMode)

def OnEditDuplicateMode(win, event):
    win.pref.duplicate_extend_mode = not win.pref.duplicate_extend_mode
    win.pref.save()
Mixin.setMixin('mainframe', 'OnEditDuplicateMode', OnEditDuplicateMode)

def OnEditDuplicateCurrentLine(win, event):
    line = win.document.GetCurrentLine()
    text = win.document.getLineText(line)
    pos = win.document.GetCurrentPos() - win.document.PositionFromLine(line)
    start = win.document.GetLineEndPosition(line)
    win.document.InsertText(start, win.document.getEOLChar() + text)
    win.document.GotoPos(win.document.PositionFromLine(line + 1) + pos)
Mixin.setMixin('mainframe', 'OnEditDuplicateCurrentLine', OnEditDuplicateCurrentLine)

#def OnEditDuplicateChar(win, event):
#    pos = win.document.GetCurrentPos()
#    text = win.document.getRawText()
#    word = findLeftWord(text, pos, win.getWordChars())
#    length = len(word)
#    if length > 0:
#        findstart = pos - length - 1    #-1 means skip the char before the word
#        if findstart > 0:
#            start = findPreviousWordPos(text, findstart, word, win.getWordChars())
#            if start > -1:
#                start += length
#                if text[start] in win.getWordChars():
#                    win.document.InsertText(pos, text[start])
#                    win.document.GotoPos(pos + 1)
#Mixin.setMixin('mainframe', 'OnEditDuplicateChar', OnEditDuplicateChar)

def findPreviousWordPos(text, pos, word, word_chars):
    while pos >= 0:
        if pos == 0:
            ch = ''
        else:
            ch = text[pos - 1]
        if (not ch) or (not (ch in word_chars)):
            if text.startswith(word, pos):
                return pos
        pos -= 1
    return -1

def findLeftWord(text, pos, word_chars):
    """if just left char is '.' or '(', etc. then continue to search, other case stop searching"""
    edge_chars = '.[('
    chars = []
    leftchar = text[pos - 1]
    if leftchar in edge_chars:
        chars.append(leftchar)
        pos -= 1

    while pos > 0:
        leftchar = text[pos - 1]
        if leftchar in word_chars:
            pos -= 1
            chars.append(leftchar)
        else:
            break
    chars.reverse()
    return ''.join(chars)

#def OnEditDuplicateNextChar(win, event):
#    pos = win.document.GetCurrentPos()
#    text = win.document.getRawText()
#    word = findLeftWord(text, pos, win.getWordChars())
#    length = len(word)
#    if length > 0:
#        findstart = pos         #-1 means skip the char before the word
#        if findstart > 0:
#            start = findNextWordPos(text, findstart, word, win.getWordChars())
#            if start > -1:
#                start += length
#                if text[start] in win.getWordChars():
#                    win.document.InsertText(pos, text[start])
#                    win.document.GotoPos(pos + 1)
#Mixin.setMixin('mainframe', 'OnEditDuplicateNextChar', OnEditDuplicateNextChar)

def findNextWordPos(text, pos, word, word_chars):
    length = len(text)
    while pos < length:
        if pos - 1 == 0:
            ch = ''
        else:
            ch = text[pos - 1]
        if (not ch) or (not (ch in word_chars)):
            if text.startswith(word, pos):
                return pos
        pos += 1
    return -1

def OnKeyDown(win, event):
    if win.findflag:
        key = event.GetKeyCode()
        if key in (wx.WXK_RETURN, wx.WXK_SPACE):
            win.calltip.cancel()
            win.findflag = 0
            if win.calltip_type == CALLTIP_DUPLICATE:#duplicate mode
                win.AddText(win.duplicate_match_text)
        elif key == wx.WXK_ESCAPE:
            win.calltip.cancel()
            win.findflag = 0
        elif key in ('L', 'P') and event.ControlDown():
            return False
        return True
Mixin.setPlugin('editor', 'on_key_down', OnKeyDown, Mixin.HIGH, 0)

def getMatchWordPos(text, start, word, word_chars):
    pos = start + len(word)
    length = len(text)
    while pos < length:
        if not (text[pos] in word_chars):
            return pos
        pos += 1
    return -1

def init(win):
    win.findflag = 0
Mixin.setPlugin('editor', 'init', init)

def OnEditDuplicateWord(win, event):
    duplicateMatch(win, 1)
Mixin.setMixin('mainframe', 'OnEditDuplicateWord', OnEditDuplicateWord)

def OnEditDuplicateNextWord(win, event):
    duplicateMatch(win, 2)
Mixin.setMixin('mainframe', 'OnEditDuplicateNextWord', OnEditDuplicateNextWord)

def OnEditDuplicateLine(win, event):
    duplicateMatch(win, 3)
Mixin.setMixin('mainframe', 'OnEditDuplicateLine', OnEditDuplicateLine)

def OnEditDuplicateNextLine(win, event):
    duplicateMatch(win, 4)
Mixin.setMixin('mainframe', 'OnEditDuplicateNextLine', OnEditDuplicateNextLine)

#kind =1 previous word 2 next word 3 previous line 4 next line
def duplicateMatch(win, kind):
    text = win.document.getRawText()
    length = win.document.GetLength()
    if win.document.findflag == 0:
        win.document.duplicate_pos = win.document.GetCurrentPos()
        win.document.duplicate_word = findLeftWord(text, win.document.duplicate_pos, win.getWordChars())
        win.document.duplicate_length = len(win.document.duplicate_word)
        if win.document.duplicate_length == 0:
            return
        if kind in (1, 3):
            findstart = win.document.duplicate_pos - win.document.duplicate_length - 1
        else:
            findstart = win.document.duplicate_pos + 1  #-1 means skip the char before the word
    else:
        if kind in (1, 3):
            findstart = win.document.duplicate_start - 1
        else:
            findstart = win.document.duplicate_start + win.document.duplicate_match_len
    while (kind in (1, 3) and (findstart >= 0)) or (kind in (2, 4) and (findstart < length)) :
        if kind in (1, 3):
            start = findPreviousWordPos(text, findstart, win.document.duplicate_word, win.getWordChars())
        else:
            start = findNextWordPos(text, findstart, win.document.duplicate_word, win.getWordChars())
        if start > -1:
            end = getMatchWordPos(text, start, win.document.duplicate_word, win.getWordChars())
            if end - start > win.document.duplicate_length:
                if kind in (1, 2) and win.document.findflag:
                    if win.document.duplicate_calltip == text[start:end]:
                        if kind == 1:
                            findstart = start - 1
                        else:
                            findstart = start + 1
                        continue
                win.document.findflag = 1
                win.document.duplicate_start = start
                if kind in (3, 4):
                    line = win.document.LineFromPosition(start)
                    line_end = win.document.GetLineEndPosition(line)
                    win.document.duplicate_calltip = win.document.getLineText(line).expandtabs(win.document.GetTabWidth())
                    win.document.duplicate_match_len = line_end - start - win.document.duplicate_length
                    win.document.duplicate_match_text = win.document.GetTextRange(start + win.document.duplicate_length , line_end)
                else:
                    win.document.duplicate_calltip = text[start:end]
                    win.document.duplicate_match_len = end - start - win.document.duplicate_length
                    win.document.duplicate_match_text = win.document.GetTextRange(start + win.document.duplicate_length , end)
                win.document.calltip.cancel()
                win.document.calltip_type = CALLTIP_DUPLICATE
                win.document.calltip.show(win.document.duplicate_pos, win.document.duplicate_calltip)
                return
            else:
                if kind in (1, 3):
                    findstart = start - 1
                else:
                    findstart = start + 1
        else:
            return
