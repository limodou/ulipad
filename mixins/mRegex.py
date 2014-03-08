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

regex_pagename = tr("Regex")
def createRegexWindow(win):
    if not win.panel.getPage(regex_pagename):
        from mixins import RegexWindow
        
        page = RegexWindow.RegexWindow(win.panel.createNotebook('bottom'))
        win.panel.addPage('bottom', page, regex_pagename)
    return regex_pagename
Mixin.setMixin('mainframe', 'createRegexWindow', createRegexWindow)

def add_mainframe_menu(menulist):
    menulist.extend([('IDM_TOOL', #parent menu id
        [
            (170, 'IDM_TOOL_REGEX', tr('Live Regular Expression'), wx.ITEM_NORMAL, 'OnToolRegex', tr('Live regular expression searching.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def OnToolRegex(win, event):
    p = win.createRegexWindow()
    win.panel.showPage(p)
Mixin.setMixin('mainframe', 'OnToolRegex', OnToolRegex)
