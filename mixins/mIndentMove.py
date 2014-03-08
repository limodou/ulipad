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

def pref_init(pref):
    pref.document_move_next_indent_selection = True
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('Document')+'/'+tr('Edit'), 170, 'check', 'document_move_next_indent_selection', tr('Always select from start of line when moving down to next matching indent'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def on_key_down(editor, event):
    ctrl = event.ControlDown()
    shift = event.ShiftDown()
    alt = event.AltDown()
    
    if not shift and not ctrl and alt:
        if event.GetKeyCode() == wx.WXK_LEFT:
            editor.move_parent_indent()
            return True
        elif event.GetKeyCode() == wx.WXK_UP:
            editor.move_prev_indent()
            return True
        elif event.GetKeyCode() == wx.WXK_DOWN:
            editor.move_next_indent()
            return True
        elif event.GetKeyCode() == wx.WXK_RIGHT:
            editor.move_child_indent()
            return True
Mixin.setPlugin('editor', 'on_key_down', on_key_down)

def move_parent_indent(editor):
    line = editor.GetCurrentLine()
    indent = editor.GetLineIndentation(line)
    line -= 1
    comment_chars = editor.get_document_comment_chars()
    while line > -1:
        line_text = editor.GetLine(line)
        text = line_text.strip()
        if text and not line_text.startswith(comment_chars):
            i = editor.GetLineIndentation(line)
            editor.GotoLine(line)
            if i < indent:
                editor.GotoLine(line)
                break
        
        line -= 1
Mixin.setMixin('editor', 'move_parent_indent', move_parent_indent)

def move_prev_indent(editor):
    line = editor.GetCurrentLine()
    indent = editor.GetLineIndentation(line)
    line -= 1
    comment_chars = editor.get_document_comment_chars()
    while line > -1:
        line_text = editor.GetLine(line)
        text = line_text.strip()
        if text and not line_text.startswith(comment_chars):
            i = editor.GetLineIndentation(line)
            if i <= indent:
                editor.GotoLine(line)
                break
#            elif i < indent:
#                break
        
        line -= 1
Mixin.setMixin('editor', 'move_prev_indent', move_prev_indent)

def move_next_indent(editor):
    line = editor.GetCurrentLine()
    if editor.GetSelectionStart() < editor.GetCurrentPos():
        startpos = editor.GetSelectionStart()
    else:
        startpos = editor.FindColumn(line, 0)
    indent = editor.GetLineIndentation(line)
    line += 1
    comment_chars = editor.get_document_comment_chars()
    while line < editor.GetLineCount():
        line_text = editor.GetLine(line)
        text = line_text.strip()
        if text and not line_text.startswith(comment_chars):
            i = editor.GetLineIndentation(line)
            if i <= indent:
                editor.GotoLine(line)
                if Globals.pref.document_move_next_indent_selection:
                    editor.SetSelectionStart(startpos)
                    editor.SetSelectionEnd(editor.GetCurrentPos())
                return
#            elif i < indent:
#                break
        
        line += 1
    
    if editor.GetCurrentLine() < editor.GetLineCount() - 1:
        editor.goto(line-1)
        if Globals.pref.document_move_next_indent_selection:
            editor.SetSelectionStart(startpos)
            editor.SetSelectionEnd(editor.GetCurrentPos())
    else:
        editor.GotoPos(editor.GetTextLength())
        if Globals.pref.document_move_next_indent_selection:
            editor.SetSelectionStart(startpos)
            editor.SetSelectionEnd(editor.GetTextLength())
Mixin.setMixin('editor', 'move_next_indent', move_next_indent)

def move_child_indent(editor):
    line = editor.GetCurrentLine()
    indent = editor.GetLineIndentation(line)
    line += 1
    comment_chars = editor.get_document_comment_chars()
    while line < editor.GetLineCount():
        line_text = editor.GetLine(line)
        text = line_text.strip()
        if text and not line_text.startswith(comment_chars):
            i = editor.GetLineIndentation(line)
            if i > indent:
                editor.GotoLine(line)
                break
            else:
                break
        
        line += 1
Mixin.setMixin('editor', 'move_child_indent', move_child_indent)
