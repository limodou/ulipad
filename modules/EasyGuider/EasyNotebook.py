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
import EasyPage

class EasyNotebook(wx.Dialog):
    def __init__(self, parent, title="", pagesinfo=[], values={}):
        wx.Dialog.__init__(self, parent, -1, title=title, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.title = title
        self.pages = []
        self.pagesinfo = pagesinfo
        self.values = values

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        self.notebook = wx.Notebook(self, -1)
        self.sizer.Add(self.notebook, 1, wx.EXPAND, 2)

        line = wx.StaticLine(self, -1)
        self.sizer.Add(line, 0, wx.EXPAND, 2)

        box = wx.BoxSizer(wx.HORIZONTAL)
        self.okbtn = wx.Button(self, wx.ID_OK, 'OK')
        self.okbtn.SetDefault()
        box.Add(self.okbtn, 0, wx.ALL, 2)
        self.cancelbtn = wx.Button(self, wx.ID_CANCEL, 'Cancel')
        box.Add(self.cancelbtn, 0, wx.ALL, 2)

        self.sizer.Add(box, 0, wx.ALIGN_CENTER, 2)

        self.installPages()
        self.SetAutoLayout(True)

        self.sizer.Fit(self)

    def installPages(self):
        for i, page in enumerate(self.pagesinfo):
            if isinstance(page, EasyPage.EasyPage):
                self.pages.append(page)
                self.notebook.AddPage(p, page.title)
            else:
                p = EasyPage.EasyPage(self.notebook, title=page.get("title", ""), description=page.get("description", ""),
                    elements=page.get("elements", []), theme=page.get("theme", 'simple'), values=self.values)
                self.pages.append(p)
                self.notebook.AddPage(p, page.get("title", "Page%d" % i))

    def GetValue(self):
        values = {}
        for page in self.pages:
            values.update(page.getValues())
        return values
