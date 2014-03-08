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

import wx
from modules import Mixin
import editor_ext
import dirbrowser_ext
import DjangoTMPLexer

def add_lexer(lexer):
    lexer.extend([
        (DjangoTMPLexer.DjangoTmpLexer.metaname, 'Django Template|*.dmp',
            wx.stc.STC_LEX_CONTAINER, 'djangotmp.stx', DjangoTMPLexer.DjangoTmpLexer),
    ])
Mixin.setPlugin('lexerfactory', 'add_lexer', add_lexer)

def add_new_files(new_files):
    new_files.extend([
        ('Django Template', DjangoTMPLexer.DjangoTmpLexer.metaname),
    ])
Mixin.setPlugin('mainframe', 'add_new_files', add_new_files)

