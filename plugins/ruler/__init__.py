#   Programmer:     limodou
#   E-mail:         limodou@gmail.com
#  
#   Copyleft 2006 limodou
#  
#   Distributed under the terms of the GPL (GNU Public License)
#  
#   NewEdit is free software; you can redistribute it and/or modify
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
#   Update by Claudio Grondi 2006/08/14 :
#   added menu shortcut Alt+R - switches the ruler on/off
#   added on_key_down()       - BUT ... column indicator is still not in sync with cursor ...
   
import wx
from modules import Mixin
import unicodedata

def new_control(editor, win, sizer):
    from RulerCtrl import RulerCtrl

    ruler = RulerCtrl(win, offset=cal_offset(editor), show=editor.ruler_show)
    editor.ruler = ruler
    sizer.Add(ruler, 0, wx.EXPAND)
Mixin.setPlugin('textpanel', 'new_control', new_control)

def cal_offset(win):
    return sum(map(win.GetMarginWidth, range(3))) + win.GetMarginLeft()

def cal_column(win):
    text, pos = win.GetCurLine()
    pos = win.GetColumn(win.GetCurrentPos())
    s = 0
    for ch in text[:pos]:
        if unicodedata.east_asian_width(ch) != 'Na':
            s += 2
        else:
            s += 1
    return s

def on_char(win, event):
    if win.edittype == 'edit' and hasattr(win, 'ruler'):
        char = event.GetKeyCode()
        win.ruler.setoffset(cal_offset(win))
        col = cal_column(win)
        if (31 <char < 127) or char > wx.WXK_PAGEDOWN:
            if char < 127:
                col += 1
            else:
                if unicodedata.east_asian_width(unichr(char)) != 'Na':
                    col += 2
                else:
                    col += 1
        win.ruler.position(col)
Mixin.setPlugin('editor', 'on_char', on_char, nice=5)

def on_mouse_down(win, event):
    if win.edittype == 'edit' and hasattr(win, 'ruler'):
        win.ruler.setoffset(cal_offset(win))
        win.ruler.position(cal_column(win))
Mixin.setPlugin('editor', 'on_mouse_down', on_mouse_down)

def on_key_down(win, event):
    if win.edittype == 'edit' and hasattr(win, 'ruler'):
        win.ruler.setoffset(cal_offset(win))
        win.ruler.position(cal_column(win))
Mixin.setPlugin('editor', 'on_key_down', on_key_down, nice=5)

def on_key_up(win, event):
    if win.edittype == 'edit' and hasattr(win, 'ruler'):
        win.ruler.setoffset(cal_offset(win))
        win.ruler.position(cal_column(win))
Mixin.setPlugin('editor', 'on_key_up', on_key_up)

def on_mouse_up(win, event):
    if win.edittype == 'edit' and hasattr(win, 'ruler'):
        win.ruler.setoffset(cal_offset(win))
        win.ruler.position(cal_column(win))
Mixin.setPlugin('editor', 'on_mouse_up', on_mouse_up)

def on_document_enter(win, document):
    if document.edittype == 'edit' and hasattr(document, 'ruler'):
        document.ruler.setoffset(cal_offset(document))
        document.ruler.position(cal_column(document))
Mixin.setPlugin('editctrl', 'on_document_enter', on_document_enter)

def add_mainframe_menu(menulist):
    menulist.extend([
        ('IDM_VIEW', #parent menu id
        [
            (200, '-', '', wx.ITEM_SEPARATOR, '', ''),
            (210, 'IDM_VIEW_RULER', tr('Show/Hide Ruler'), wx.ITEM_CHECK, 'OnViewRuler', tr('Shows or hides ruler')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def editor_init(win):
    win.ruler_show = False
Mixin.setPlugin('editor', 'init', editor_init)

def on_update_ui(win, event):
    eid = event.GetId()
    if eid == win.IDM_VIEW_RULER:
        if hasattr(win, 'document'):
            if hasattr(win.document, 'ruler') and not win.document.multiview:
                event.Enable(True)
                event.Check(win.document.ruler_show)
                return
        event.Enable(False)
Mixin.setPlugin('mainframe', 'on_update_ui', on_update_ui)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_VIEW_RULER, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def OnViewRuler(win, event):
    if hasattr(win, 'document') and hasattr(win.document, 'ruler'):
        win.document.ruler_show = not win.document.ruler_show
        if hasattr(win.document, 'lexer'):
            win.document.ruler.setfont(win.document.lexer.font)
            a = win.document.lexer.getSyntaxItems()['linenumber']
            win.document.ruler.setbgcolor(a.style.back)
        win.document.ruler.show(win.document.ruler_show)
        win.document.ruler.position(cal_column(win.document))
Mixin.setMixin('mainframe', 'OnViewRuler', OnViewRuler)

#def on_zoom(win, event):
#    factor = win.GetZoom()
#    if hasattr(win, 'lexer'):
#        font = win.lexer.font
#        newfont = wx.Font(font.GetPointSize()+factor, wx.TELETYPE, wx.NORMAL, wx.NORMAL, True)
#        win.ruler.setfont(newfont)
#Mixin.setPlugin('editor', 'on_zoom', on_zoom)
