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
#   $Id: mSearchInFiles.py 1837 2007-01-19 10:24:10Z limodou $

import wx
import os.path
import sys
from modules import Mixin

def add_mainframe_menu(menulist):
    menulist.extend([
        ('IDM_SEARCH', #parent menu id
        [
            (145, 'IDM_SEARCH_FIND_IN_FILES', tr('Find In Files...')+'\tCtrl+Shift+F4', wx.ITEM_NORMAL, 'OnSearchFindInFiles', tr('Find text in files.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def createFindInFilesWindow(win):
    findinfiles_pagename = tr('Find in Files')
    if not win.panel.getPage(findinfiles_pagename):
        from FindInFiles import FindInFiles

        page = FindInFiles(win.panel.createNotebook('bottom'), win)
        win.panel.addPage('bottom', page, findinfiles_pagename)
    return findinfiles_pagename
Mixin.setMixin('mainframe', 'createFindInFilesWindow', createFindInFilesWindow)

def OnSearchFindInFiles(win, event):
    p = win.createFindInFilesWindow()
    win.panel.showPage(p)
Mixin.setMixin('mainframe', 'OnSearchFindInFiles', OnSearchFindInFiles)

def pref_init(pref):
    pref.searchinfile_searchlist = []
    pref.searchinfile_dirlist = []
    pref.searchinfile_extlist = []
    pref.searchinfile_case = False
    pref.searchinfile_subdir = True
    pref.searchinfile_regular = False
    pref.searchinfile_onlyfilename = False
    pref.searchinfile_defaultpath = os.path.dirname(sys.argv[0])
Mixin.setPlugin('preference', 'init', pref_init)
