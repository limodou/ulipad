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
from EasyUtils import *
import EasyBasicElements
from EasyGlobal import element_classes

class EasyElements(object):
    def __init__(self, elements, values={}, factor=1):
        self.elements = elements
        self.items = {}
        self.values = values
        self.factor = factor

    def addItems(self, sizer):
        number = len(self.elements)
        if not number:
            return
        if self.values:
            elements = self.getNewElements(self.values)
        else:
            elements = self.elements

        self.gbs = wx.GridBagSizer(2, 2)

        for i, item in enumerate(elements):
            enabledflag = None
            size = (-1, -1)
            if isinstance(item[0], bool):
                enabledflag = item[0]
                item = item[1:]
            if isinstance(item[-1], tuple):
                size = item[-1]
                item = item[:-1]
            kind, name, value, message, extern = item
            self.addItem(i, kind, name, value, message, extern, size, enabledflag)

        sizer.Add(self.gbs, self.factor, wx.EXPAND|wx.ALL, 2)
        self.gbs.AddGrowableCol(2)

    def getNewElements(self, values):
        new_elements = []
        for i, e in enumerate(self.elements):
            value = values.get(e[1], None)
            if value is not None:
                e = list(e)
                e[2] = value
                new_elements.append(tuple(e))
            else:
                new_elements.append(e)
        return new_elements

    def addItem(self, i, kind, name, value, message, extern, size, enabledflag):
        flag = wx.LEFT|wx.RIGHT
        try:
            klass = element_classes[kind]
        except:
            raise EasyException, "Can't support this type [%s]" % kind
        obj = klass(self, value, message, extern, size, enabledflag)
        self.items[name] = obj
        if enabledflag is not None:
            check = EnableFlagBox(self, obj)
            check.SetValue(enabledflag)
            obj.setEnabled(enabledflag)
            self.gbs.Add(check, (i, 0), flag=wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, border=4)

        if not obj.isLarge():
            self.gbs.Add(wx.StaticText(self, -1, message), (i, 1), flag=wx.ALIGN_CENTER_VERTICAL, border=2)
            self.gbs.Add(obj.getContainer(), (i, 2), flag=obj.getAlignFlag(flag), border=2)
        else:
            self.gbs.Add(obj.getContainer(), (i, 1), (1, 2), flag=wx.EXPAND|wx.TOP|wx.BOTTOM, border=2)
            self.gbs.AddGrowableRow(i)

    def getValues(self):
        values = {}
        for key, obj in self.items.items():
            if not obj.getEnabledFlag() or obj.getEnabled():
                values[key] = obj.getValue()
        return values

class EnableFlagBox(wx.CheckBox):
    def __init__(self, parent, target):
        wx.CheckBox.__init__(self, parent, -1)
        self.parent = parent
        self.target = target
        target.checkbox = self
        wx.EVT_CHECKBOX(self, self.GetId(), self.OnCheck)

    def OnCheck(self, event):
        self.target.setEnabled(self.GetValue())
