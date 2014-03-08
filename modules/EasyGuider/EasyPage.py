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

import wx
import EasyElements

class EasyPage(wx.Panel, EasyElements.EasyElements):
    def __init__(self, parent, title="", description="", elements=[], theme='simple', values={}):
        wx.Panel.__init__(self, parent, -1)
        EasyElements.EasyElements.__init__(self, elements, values)

        self.title = title
        self.description = description

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        func_name = 'makePageTitle_' + theme
        getattr(self, func_name, self.makePageTitle_classic)()

        self.addItems(self.sizer)
        self.SetAutoLayout(True)
        self.sizer.Fit(self)

    def makePageTitle_simple(self):
        if self.description:
            box = wx.StaticBox(self, -1, label = self.title)
            bsizer = wx.StaticBoxSizer(box, wx.VERTICAL)
            t = wx.StaticText(self, -1, self.description)
            bsizer.Add(t, 0, wx.EXPAND|wx.ALL, 5)
            self.sizer.Add(bsizer, 0, wx.EXPAND|wx.ALL, 5)

    def makePageTitle_classic(self):
        if self.title:
            title = wx.StaticText(self, -1, self.title)
            title.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
            self.sizer.Add(title, 0, wx.EXPAND|wx.ALL, 5)
        if self.description:
            description = wx.StaticText(self, -1, self.description)
            self.sizer.Add(description, 0, wx.EXPAND|wx.ALL, 5)
        if self.title or self.description:
            self.sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND|wx.ALL, 5)
