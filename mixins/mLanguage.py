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
#   $Id: mLanguage.py 1566 2006-10-09 04:44:08Z limodou $

import wx
from modules import Mixin
from modules import makemenu
from modules import common

def add_mainframe_menu(menulist):
    menulist.extend([('IDM_TOOL',
        [
            (135, 'IDM_OPTION_LANGUAGE', tr('Language'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDM_OPTION_LANGUAGE',
        [
            (100, 'IDM_OPTION_LANGUAGE_ENGLISH', 'English', wx.ITEM_CHECK, 'OnOptionLanguageChange', 'Change langauage.'),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def beforeinit(win):
    langinifile = common.uni_work_file('lang/language.ini')
    win.language_ids = [win.IDM_OPTION_LANGUAGE_ENGLISH]
    win.language_country = ['']
    create_language_menu(win, langinifile)
Mixin.setPlugin('mainframe', 'beforeinit', beforeinit)

def create_language_menu(win, filename):
    menu = makemenu.findmenu(win.menuitems, 'IDM_OPTION_LANGUAGE')

    langs = open(filename).readlines()
    for lang in langs:
        lang = lang.strip()
        if lang == '':
            continue
        if lang[0] == '#':
            continue
        country, language = lang.strip().split(' ', 1)
        id = wx.NewId()
        win.language_ids.append(id)
        win.language_country.append(country)
        menu.Append(id, language, 'Change language', wx.ITEM_CHECK)
        wx.EVT_MENU(win, id, win.OnOptionLanguageChange)

    index = win.language_country.index(win.app.i18n.lang)
    menu.Check(win.language_ids[index], True)

def OnOptionLanguageChange(win, event):
    eid = event.GetId()
    index = win.language_ids.index(eid)
    country = win.language_country[index]
    wx.MessageDialog(win, tr("Because you changed the language, \nit will be enabled at next startup."), tr("Change language"), wx.OK).ShowModal()
    ini = common.get_config_file_obj()
    ini.language.default = country
    ini.save()

    # change menu check status
    menu = makemenu.findmenu(win.menuitems, 'IDM_OPTION_LANGUAGE')
    for id in win.language_ids:
        if id == eid:
            menu.Check(id, True)
        else:
            menu.Check(id, False)
Mixin.setMixin('mainframe', 'OnOptionLanguageChange', OnOptionLanguageChange)
