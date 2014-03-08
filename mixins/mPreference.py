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
#   $Id: mPreference.py 1757 2006-12-14 01:20:35Z limodou $

import wx
from modules import Mixin

def add_mainframe_menu(menulist):
    menulist.extend([
        ('IDM_EDIT',
        [
            (300, '-', '', wx.ITEM_SEPARATOR, '', ''),
            (310, 'wx.ID_PREFERENCES', tr('Preferences...'), wx.ITEM_NORMAL, 'OnOptionPreference', tr('Opens the Preferences window.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def beforegui(win):
    import Preference
    from modules import Globals

    win.pref = Preference.Preference()
    win.pref.load()
    win.pref.printValues()
    Globals.pref = win.pref
Mixin.setPlugin('app', 'beforegui', beforegui, Mixin.HIGH)

def OnOptionPreference(win, event):
    import PrefDialog

    dlg = PrefDialog.PrefDialog(win)
    dlg.ShowModal()
Mixin.setMixin('mainframe', 'OnOptionPreference', OnOptionPreference)

def add_pref_page(pages_order):
    pages_order.update({
        tr('General'):100,
        tr('Document'):110,
    }
    )
Mixin.setPlugin('preference', 'add_pref_page', add_pref_page)
