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
from modules import common

pagename = tr("Spell Check")
def createSpellCheckWindow(win):
    if not win.panel.getPage(pagename):
        import SpellCheck
        
        page = SpellCheck.SpellCheck(win.panel.createNotebook('bottom'))
        win.panel.addPage('bottom', page, pagename)
    return pagename
Mixin.setMixin('mainframe', 'createSpellCheckWindow', createSpellCheckWindow)

def add_mainframe_menu(menulist):
    menulist.extend([('IDM_TOOL', #parent menu id
        [
            (160, 'IDM_TOOL_SPELLCHECK', tr('Spell Check') + '\tF7', wx.ITEM_NORMAL, 'OnToolSpellCheck', tr('Spell check for current document.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def OnToolSpellCheck(win, event):
    try:
        from enchant.checker import SpellChecker
    except:
        common.showerror(win, tr('You should install PyEnchant module first.\n Or there are something wrong as import the module'))
        return
    p = win.createSpellCheckWindow()
    win.panel.showPage(p)
Mixin.setMixin('mainframe', 'OnToolSpellCheck', OnToolSpellCheck)

def pref_init(pref):
    pref.default_spellcheck_dict = ''
Mixin.setPlugin('preference', 'init', pref_init)
