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
#   $Id: mModuleInfo.py 1566 2006-10-09 04:44:08Z limodou $

import wx
from modules import Mixin

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_HELP', #parent menu id
        [
            (102, 'IDM_HELP_MODULES', tr('Extended Modules Info'), wx.ITEM_NORMAL, 'OnHelpModules', tr('Extended modules infomation.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def OnHelpModules(win, event):
    from ModulesInfo import show_modules_info
    show_modules_info(win)
Mixin.setMixin('mainframe', 'OnHelpModules', OnHelpModules)
