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
#   $Id$

from modules import Mixin
import LexerBase
from modules import Globals

def add_pref(preflist):
    names = LexerBase.color_theme.keys()
    names.sort()
    preflist.extend([
        (tr('General'), 131, 'choice', 'default_color_theme', tr('Default color theme:'), names),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def pref_init(pref):
    pref.default_color_theme = 'Blue'
Mixin.setPlugin('preference', 'init', pref_init)

def set_default_style(lexer):
    lexer.set_color_theme(Globals.pref.default_color_theme)
Mixin.setPlugin('lexerbase', 'set_default_style', set_default_style)

def savepreferencevalues(values):
    mainframe = Globals.mainframe
    pref = Globals.pref
    if values['default_color_theme'] != pref.default_color_theme:
        mainframe.lexers.reset()
        for document in mainframe.editctrl.getDocuments():
            for lexer in mainframe.lexers.items():
                if document.languagename == lexer.name:
                    lexer.colourize(document, force=True)
                    break
Mixin.setPlugin('prefdialog', 'savepreferencevalues', savepreferencevalues)
