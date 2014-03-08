#       Programmer:     limodou
#       E-mail:         limodou@gmail.com
#
#       Copyleft 2006 limodou
#
#       Distributed under the terms of the GPL (GNU Public License)
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
#       $Id: wxPythonDocument.py 42 2005-09-28 05:19:21Z limodou $

__doc__ = 'Plugin: Show wxPython doc'

from modules import Mixin
import wx
import os
import os.path
import sys

menulist = [ ('IDM_HELP', #parent menu id
        [
                (106, 'IDM_HELP_WXPYTHONDOC', tr('wxPython Document'), wx.ITEM_NORMAL, 'OnHelpWxPythonDoc', tr('Show wxPython document.')),
        ]),
]
Mixin.setMixin('mainframe', 'menulist', menulist)

def OnHelpWxPythonDoc(win, event):
    os.startfile(os.path.join(sys.prefix, 'Lib/site-packages/wx/docs', 'wx.chm'))
Mixin.setMixin('mainframe', 'OnHelpWxPythonDoc', OnHelpWxPythonDoc)
