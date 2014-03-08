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
#   $Id: mPosition.py 1566 2006-10-09 04:44:08Z limodou $

import wx
from modules import Mixin

def on_key_up(win, event):
    if win.edittype == 'edit':
        win.mainframe.SetStatusText(tr("Line: %d") % (win.GetCurrentLine()+1), 1)
        win.mainframe.SetStatusText(tr("Column: %d") % (win.GetColumn(win.GetCurrentPos())+1), 2)
#        win.mainframe.SetStatusText(tr("Selected: %d") % len(win.GetSelectedText()), 3)
Mixin.setPlugin('editor', 'on_key_up', on_key_up)

def on_mouse_up(win, event):
    if win.edittype == 'edit':
        win.mainframe.SetStatusText(tr("Line: %d") % (win.GetCurrentLine()+1), 1)
        win.mainframe.SetStatusText(tr("Column: %d") % (win.GetColumn(win.GetCurrentPos())+1), 2)
#        win.mainframe.SetStatusText(tr("Selected: %d") % len(win.GetSelectedText()), 3)
Mixin.setPlugin('editor', 'on_mouse_up', on_mouse_up)

def on_document_enter(win, document):
    if document.edittype == 'edit':
        win.mainframe.SetStatusText(tr("Line: %d") % (document.GetCurrentLine()+1), 1)
        win.mainframe.SetStatusText(tr("Column: %d") % (document.GetColumn(document.GetCurrentPos())+1), 2)
#        win.mainframe.SetStatusText(tr("Selected: %d") % len(document.GetSelectedText()), 3)
Mixin.setPlugin('editctrl', 'on_document_enter', on_document_enter)

def on_update_ui(win, event):
    win.mainframe.SetStatusText(tr("Selected: %d") % len(win.GetSelectedText()), 3)
Mixin.setPlugin('editor', 'on_update_ui', on_update_ui)
    