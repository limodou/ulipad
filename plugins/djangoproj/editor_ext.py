#   Programmer: limodou
#   E-mail:     limodou@gmail.com
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

from modules import Mixin
import wx
from modules import common
from modules.Debug import error

def other_popup_menu(editor, projectname, menus):
    if editor.languagename == 'python' and 'django' in common.getProjectName(editor.filename):
        menus.extend([(None, #parent menu id
            [
                (30, 'IDPM_DJANGO_PROJECT', tr('&Django'), wx.ITEM_NORMAL, '', ''),
                (40, '', '-', wx.ITEM_SEPARATOR, None, ''),
            ]),
            ('IDPM_DJANGO_PROJECT',
            [
                (100, 'IDPM_DJANGO_PROJECT_NEW_MODEL', tr('&New Model'), wx.ITEM_NORMAL, 'OnDjangoProjectFunc', tr('Create a new model.')),
                (110, '', '-', wx.ITEM_SEPARATOR, None, ''),
            ]),
        ])
Mixin.setPlugin('editor', 'other_popup_menu', other_popup_menu)

def OnDjangoProjectFunc(win, event):
    _id = event.GetId()
    try:
        if _id == win.IDPM_DJANGO_PROJECT_NEW_MODEL:
            OnDjangoProjectNewModel(win)
    except:
        error.traceback()
        common.showerror(win, tr("There is some wrong as executing the menu."))
Mixin.setMixin('editor', 'OnDjangoProjectFunc', OnDjangoProjectFunc)

def OnDjangoProjectNewModel(win):
    import maketext
    text = maketext.maketext(maketext.getmodel(win))
    if text:
        win.GotoPos(win.GetTextLength() - 1)
        win.EnsureCaretVisible()
        win.AddText(text)
