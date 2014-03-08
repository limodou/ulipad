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

import  wx
import  wx.wizard as wiz
import EasyElements

class EasyWizardPage(wiz.PyWizardPage, EasyElements.EasyElements):
    def __init__(self, parent, title="", description="", elements=[], bitmap=wx.NullBitmap, theme='simple', values={}):
        wiz.PyWizardPage.__init__(self, parent)
        EasyElements.EasyElements.__init__(self, elements, values)
        self.next = self.prev = None

        self.title = title
        if bitmap and isinstance(bitmap, (str, unicode)):
            self.bitmap = wx.Image(bitmap).ConvertToBitmap()
        else:
            self.bitmap = bitmap
        self.description = description

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        func_name = 'makePageTitle_' + theme
        getattr(self, func_name, self.makePageTitle_classic)()

        self.addItems(self.sizer)
        self.SetAutoLayout(True)

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

    def SetNext(self, next):
        self.next = next

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        return self.next

    def GetPrev(self):
        return self.prev

    def GetBitmap(self):
        return self.bitmap

class EasyWizard:
    def __init__(self, parent, title="", pagesinfo=[], values={}, bitmap=wx.NullBitmap):
        self.title = title
        self.pages = []
        self.pagesinfo = pagesinfo
        self.values = values
        if bitmap and isinstance(bitmap, (str, unicode)):
            self.bitmap = wx.Image(bitmap).ConvertToBitmap()
        else:
            self.bitmap = bitmap
        self.wizard = wiz.Wizard(parent, -1, title=title, bitmap=self.bitmap, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)

        self.installPages()
        self.wizard.FitToPage(self.page1)

    def installPages(self):
        for page in self.pagesinfo:
            if isinstance(page, EasyWizardPage):
                self.pages.append(page)
            else:
                p = EasyWizardPage(self.wizard, title=page.get("title", ""), description=page.get("description", ""),
                    elements=page.get("elements", []), bitmap=page.get("bitmap", wx.NullBitmap), theme=page.get("theme", 'simple'), values=self.values)
                self.pages.append(p)

        self.page1 = self.pages[0]

        last_page = len(self.pages) - 1
        for i, page in enumerate(self.pages):
            if i != 0:
                page.SetPrev(self.pages[i-1])
            if i != last_page:
                page.SetNext(self.pages[i+1])


    def GetValue(self):
        values = {}
        for page in self.pages:
            values.update(page.getValues())
        return values

    def ShowModal(self):
        ret = self.wizard.RunWizard(self.page1)
        if ret:
            return wx.ID_OK
        else:
            return wx.ID_CANCEL

    def Destroy(self):
        if self.wizard:
            self.wizard.Destroy()
