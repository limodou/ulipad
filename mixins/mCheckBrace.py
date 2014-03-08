#       Programmer:     limodou
#       E-mail:         limodou@gmail.com
#
#       Copyleft 2006 limodou
#
#       Distributed under the terms of the GPL (GNU Public License)
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
#       $Id: mCheckBrace.py 1621 2006-10-18 06:07:01Z limodou $

from modules import Mixin

def on_editor_updateui(win, event):
    # check for matching braces
    braceAtCaret = -1
    braceOpposite = -1
    charBefore = None
    caretPos = win.GetCurrentPos()
    if caretPos > 0:
        charBefore = win.GetCharAt(caretPos - 1)
        styleBefore = win.GetStyleAt(caretPos - 1)

    # check before
    if charBefore and chr(charBefore) in "[]{}()": # and styleBefore == wx.stc.STC_P_OPERATOR:
        braceAtCaret = caretPos - 1

    # check after
    if braceAtCaret < 0:
        charAfter = win.GetCharAt(caretPos)
        styleAfter = win.GetStyleAt(caretPos)
        if charAfter and chr(charAfter) in "[]{}()": # and styleAfter == wx.stc.STC_P_OPERATOR:
            braceAtCaret = caretPos

    if braceAtCaret >= 0:
        braceOpposite = win.BraceMatch(braceAtCaret)

    if braceAtCaret != -1  and braceOpposite == -1:
        win.BraceBadLight(braceAtCaret)
    else:
        win.BraceHighlight(braceAtCaret, braceOpposite)
Mixin.setPlugin('editor', 'on_update_ui', on_editor_updateui)
