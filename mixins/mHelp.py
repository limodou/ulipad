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
#   $Id: mHelp.py 1731 2006-11-22 03:35:50Z limodou $

import os
import wx
from modules import Mixin
from modules import Version
from modules import common
from modules.HyperLinksCtrl import HyperLinkCtrl, EVT_HYPERLINK_LEFT
from modules import Globals
from modules import meide as ui

homepage = 'http://code.google.com/p/ulipad/'
blog = 'http://www.donews.net/limodou'
email = 'limodou@gmail.com'
ulispot = 'http://ulipad.appspot.com'
author = 'Limodou'
maillist = 'http://groups.google.com/group/ulipad'

class AboutDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, size = (400, 340), style = wx.DEFAULT_DIALOG_STYLE, title = tr('About'))

#        self.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False))
#
        box = ui.VBox(padding=6, namebinding='widget').create(self).auto_layout()
        box.add(ui.Label(tr('UliPad %s') % Version.version), name='version', flag=wx.ALIGN_CENTER|wx.ALL)
        font = self.version.GetFont()
        font.SetPointSize(20)
        self.version.SetFont(font)
        box.add(ui.Label(tr('Author: %s (%s)') % (author, email)))
        box.add(ui.Label(tr('If you have any questions, please contact me.')))

        self.ID_HOMEPAGE = wx.NewId()
        self.homepage = HyperLinkCtrl(self, self.ID_HOMEPAGE, "The UliPad project homepage", URL=homepage)
        box.add(self.homepage).bind(EVT_HYPERLINK_LEFT, self.OnLink)

        self.ID_MAILLIST = wx.NewId()
        self.maillist = HyperLinkCtrl(self, self.ID_MAILLIST, "The UliPad maillist", URL=maillist)
        box.add(self.maillist).bind(EVT_HYPERLINK_LEFT, self.OnLink)

        self.ID_ULISPOT = wx.NewId()
        self.ulispot = HyperLinkCtrl(self, self.ID_ULISPOT, "The UliPad Snippets Site", URL=ulispot)
        box.add(self.ulispot).bind(EVT_HYPERLINK_LEFT, self.OnLink)

        self.ID_BLOG = wx.NewId()
        self.blog = HyperLinkCtrl(self, self.ID_BLOG, "My Blog", URL=blog)
        box.add(self.blog)

        self.ID_EMAIL = wx.NewId()
        self.email = HyperLinkCtrl(self, self.ID_EMAIL, "Contact me", URL='mailto:'+email)
        box.add(self.email)

        box.add(ui.Button(tr("OK"), id=wx.ID_OK), name='btnOk', flag=wx.ALIGN_RIGHT|wx.ALL, border=10)
        self.btnOk.SetDefault()

        box.auto_fit(2)

    def OnLink(self, event):
        eid = event.GetId()
        mainframe = Globals.mainframe
        if eid == self.ID_HOMEPAGE:
            mainframe.OnHelpProject(event)
        elif eid == self.ID_MAILLIST:
            mainframe.OnHelpMaillist(event)
        elif eid == self.ID_ULISPOT:
            mainframe.OnHelpUlispot(event)
        elif eid == self.ID_BLOG:
            mainframe.OnHelpMyBlog(event)
        elif eid == self.ID_EMAIL:
            mainframe.OnHelpEmail(event)

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_HELP', #parent menu id
        [
            (100, 'wx.ID_HELP', tr('UliPad Help Document') + '\tF1', wx.ITEM_NORMAL, 'OnHelpIndex', tr('UliPad help document.')),
            (200, '-', '', wx.ITEM_SEPARATOR, '', ''),
            (210, 'wx.ID_HOME', tr('Visit Project Homepage'), wx.ITEM_NORMAL, 'OnHelpProject', tr('Visit Project Homepage: %s.') % homepage),
            (220, 'IDM_HELP_MAILLIST', tr('Visit Mail List'), wx.ITEM_NORMAL, 'OnHelpMaillist', tr('Visit Project Mail List: %s.') % maillist),
            (230, 'IDM_HELP_MYBLOG', tr('Visit My Blog'), wx.ITEM_NORMAL, 'OnHelpMyBlog', tr('Visit My blog: %s.') % blog),
            (240, 'IDM_HELP_ULISPOT', tr('Visit UliPad Snippets Site'), wx.ITEM_NORMAL, 'OnHelpUlispot', tr('Visit UliPad snippets site: %s.') % ulispot),
            (250, 'IDM_HELP_EMAIL', tr('Contact Me'), wx.ITEM_NORMAL, 'OnHelpEmail', tr('Send email to me mailto:%s.') % email),
            (900, 'wx.ID_ABOUT', tr('About...'), wx.ITEM_NORMAL, 'OnHelpAbout', tr('About this program.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def OnHelpIndex(win, event):
    lang = 'en'
    if Globals.app.i18n.lang:
        lang = Globals.app.i18n.lang
    filename = common.get_app_filename(win, 'doc/%s/index.htm' % lang)
    if not os.path.exists(filename):
        filename = common.get_app_filename(win, 'doc/%s/index.htm' % 'en')
    common.webopen(filename)
Mixin.setMixin('mainframe', 'OnHelpIndex', OnHelpIndex)

def OnHelpAbout(win, event):
    AboutDialog(win).ShowModal()
Mixin.setMixin('mainframe', 'OnHelpAbout', OnHelpAbout)

def OnHelpProject(win, event):
    common.webopen(homepage)
Mixin.setMixin('mainframe', 'OnHelpProject', OnHelpProject)

def OnHelpMaillist(win, event):
    common.webopen(maillist)
Mixin.setMixin('mainframe', 'OnHelpMaillist', OnHelpMaillist)

def OnHelpEmail(win, event):
    common.webopen('mailto:%s' % email)
Mixin.setMixin('mainframe', 'OnHelpEmail', OnHelpEmail)

def OnHelpMyBlog(win, event):
    common.webopen(blog)
Mixin.setMixin('mainframe', 'OnHelpMyBlog', OnHelpMyBlog)

def OnHelpUlispot(win, event):
    common.webopen(ulispot)
Mixin.setMixin('mainframe', 'OnHelpUlispot', OnHelpUlispot)
