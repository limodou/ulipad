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

import wx
from modules import Mixin
from mixins import FiletypeBase

class FortranFiletype(FiletypeBase.FiletypeBase):

    __mixinname__ = 'fortranfiletype'
    menulist = [ (None,
        [
            (890, 'IDM_FORTRAN', 'Fortran', wx.ITEM_NORMAL, None, ''),
        ]),
    ]
    toollist = []               #your should not use supperclass's var
    toolbaritems= {}

def add_filetypes(filetypes):
    filetypes.extend([('fortran', FortranFiletype)])
Mixin.setPlugin('changefiletype', 'add_filetypes', add_filetypes)

def add_html_menu(menulist):
    menulist.extend([('IDM_FORTRAN', #parent menu id
            [
                (100, 'IDM_FORTRAN_TEST', tr('This is a test menu'), wx.ITEM_NORMAL, 'OnFortranTest', tr('This is a test.')),
            ]),
    ])
Mixin.setPlugin('fortranfiletype', 'add_menu', add_html_menu)

def OnFortranTest(win, event):
    print 'fortran menu test'
Mixin.setMixin('mainframe', 'OnFortranTest', OnFortranTest)

