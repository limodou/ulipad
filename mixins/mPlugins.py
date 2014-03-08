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
#   $Id: mPlugins.py 1457 2006-08-23 02:12:12Z limodou $

__doc__ = 'Plugins manage'

import wx
from modules import Mixin
from modules import common

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_TOOL',
        [
            (130, 'IDM_TOOL_PLUGINS_MANAGE', tr('Plugins Manager...'), wx.ITEM_NORMAL, 'OnDocumentPluginsManage', 'Manages plugins.'),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def OnDocumentPluginsManage(win, event):
    from PluginDialog import PluginDialog

    dlg = PluginDialog(win)
    answer = dlg.ShowModal()
    dlg.Destroy()
Mixin.setMixin('mainframe', 'OnDocumentPluginsManage', OnDocumentPluginsManage)

def afterinit(win):
    win.plugin_imagelist = {
        'uncheck':  'images/uncheck.gif',
        'check':    'images/check.gif',
    }
    win.plugin_initfile = common.get_app_filename(win, 'plugins/__init__.py')
Mixin.setPlugin('mainframe', 'afterinit', afterinit)
