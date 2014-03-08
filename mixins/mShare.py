#   Programmer: limodou
#   E-mail:     limodou@gmail.coms
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

def add_mainframe_menu(menulist):
    menulist.extend([
        ('IDM_WINDOW',
        [
            (200, 'IDM_WINDOW_SHARE', tr('Resource Shares Window'), wx.ITEM_CHECK, 'OnWindowShare', tr('Opens resource shares window.'))
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_notebook_menu(popmenulist):
    popmenulist.extend([(None,
        [
            (180, 'IDPM_SHAREWINDOW', tr('Resource Shares Window'), wx.ITEM_CHECK, 'OnShareWindow', tr('Opens resource shares window.')),
        ]),
    ])
Mixin.setPlugin('notebook', 'add_menu', add_notebook_menu)

def afterinit(win):
    win.share_imagelist = {
        'close':'images/folderclose.gif',
        'open':'images/folderopen.gif',
        'item':'images/file.gif',
    }
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

#toollist = [
#   (550, 'dirbrowser'),
#]
#Mixin.setMixin('mainframe', 'toollist', toollist)
#
##order, IDname, imagefile, short text, long text, func
#toolbaritems = {
#   'dirbrowser':(wx.ITEM_NORMAL, 'IDM_WINDOW_DIRBROWSER', images.getWizardBitmap(), tr('dir browser'), tr('Opens directory browser window.'), 'OnWindowDirBrowser'),
#}
#Mixin.setMixin('mainframe', 'toolbaritems', toolbaritems)

_resshare_pagename = tr('Resource Shares')

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDM_WINDOW_SHARE:
        event.Check(bool(win.panel.getPage(_resshare_pagename)) and win.panel.LeftIsVisible)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_WINDOW_SHARE, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def on_notebook_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDPM_SHAREWINDOW:
        event.Check(bool(win.panel.getPage(_resshare_pagename)) and win.panel.LeftIsVisible)
Mixin.setPlugin('notebook', 'on_update_ui', on_notebook_updateui)

def init(win):
    wx.EVT_UPDATE_UI(win, win.IDPM_SHAREWINDOW, win.OnUpdateUI)
Mixin.setPlugin('notebook', 'init', init)

def createShareWindow(win):
    if not win.panel.getPage(_resshare_pagename):
        from ShareWindow import ShareWindow

        page = ShareWindow(win.panel.createNotebook('left'), win)
        win.panel.addPage('left', page, _resshare_pagename)
Mixin.setMixin('mainframe', 'createShareWindow', createShareWindow)

def OnWindowShare(win, event):
    if not win.panel.getPage(_resshare_pagename):
        win.createShareWindow()
        win.panel.showPage(_resshare_pagename)
    else:
        win.panel.closePage(_resshare_pagename)
Mixin.setMixin('mainframe', 'OnWindowShare', OnWindowShare)

def OnShareWindow(win, event):
    if not win.panel.getPage(_resshare_pagename):
        win.mainframe.createShareWindow()
        win.panel.showPage(_resshare_pagename)
    else:
        win.panel.closePage(_resshare_pagename)
Mixin.setMixin('notebook', 'OnShareWindow', OnShareWindow)

def close_page(page, name):
    if name == _resshare_pagename:
        page.OnCloseWin()
Mixin.setPlugin('notebook', 'close_page', close_page)
