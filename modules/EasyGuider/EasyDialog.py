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
from EasyElements import EasyElements

class EasyDialog(wx.Dialog, EasyElements):
    def __init__(self, parent, title, elements, values={}):
        self.title = title
        self.values = values

        wx.Dialog.__init__(self, parent, -1, title, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        EasyElements.__init__(self, elements, self.values)

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.addItems(sizer)

        box1 = wx.BoxSizer(wx.HORIZONTAL)

        self.btnok = wx.Button(self, wx.ID_OK, 'OK')
        self.btnok.SetDefault()
        box1.Add(self.btnok, 0, wx.ALL, 2)
        self.btncancel = wx.Button(self, wx.ID_CANCEL, 'Cancel')
        box1.Add(self.btncancel, 0, wx.ALL, 2)

        sizer.Add(box1, 0, wx.ALIGN_CENTER | wx.ALL, 2)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)

        self.Centre()

    def GetValue(self):
        return self.getValues()
