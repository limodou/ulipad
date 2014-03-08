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
#   $Id: mSyntaxPref.py 1457 2006-08-23 02:12:12Z limodou $

__doc__ = 'syntax preference'

import wx
from modules import common
from modules import Mixin

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_DOCUMENT',
        [
            (150, 'IDM_DOCUMENT_SYNTAX_PREFERENCE', tr('Syntax Preference...'), wx.ITEM_NORMAL, 'OnDocumentSyntaxPreference', tr('Syntax highlight preference setup.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def OnSyntax(win, event):
    from modules import Globals
    Globals.mainframe.OnDocumentSyntaxPreference(None)
Mixin.setMixin('prefdialog', 'OnSyntax', OnSyntax)

def add_pref(preflist):
    preflist.extend([
        (tr('Document'), 160, 'button', 'document_syntax', tr('Setup document syntax highlight'), 'OnSyntax'),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)


def OnDocumentSyntaxPreference(win, event):
    from modules import i18n
    from modules import Resource
    import SyntaxDialog

    syntax_resfile = common.uni_work_file('resources/syntaxdialog.xrc')
    filename = i18n.makefilename(syntax_resfile, win.app.i18n.lang)
    if hasattr(win.document, 'languagename'):
        name = win.document.languagename
    else:
        name = ''
    Resource.loadfromresfile(filename, win, SyntaxDialog.SyntaxDialog, 'SyntaxDialog', win, win.lexers, name).ShowModal()
Mixin.setMixin('mainframe', 'OnDocumentSyntaxPreference', OnDocumentSyntaxPreference)
