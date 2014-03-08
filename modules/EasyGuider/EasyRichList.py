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
import sys
import copy
from EasyUtils import *
from EasyElements import EasyElements

class EasyRichList(wx.Panel, EasyElements):
    def __init__(self, parent, datas=[], values=[], size=wx.DefaultSize):
        wx.Panel.__init__(self, parent, size=size)
        self._values = copy.deepcopy(values)

        self.elements = datas['elements']
        if not datas.has_key('key'):    #not key attribute then use the first column
            self.keyname = self.elements[0][1]
        else:
            self.keyname = datas['key']
        EasyElements.__init__(self, self.elements, factor=3)

#        self.cols, self.cols_key = self.setColsId(self.elements)
        self.parent = parent
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)

        #add list
        self.list = self.createlist()
        self.list.Bind(wx.EVT_LISTBOX, self.OnSelect)
        self.sizer.Add(self.list, 1, wx.EXPAND|wx.ALL, 2)
        self.SetValue(self._values)

        #add buttons
        self.button_names = ['add', 'ins', 'del', 'up', 'down', 'save']
        self.buttons = {}
        box = wx.BoxSizer(wx.VERTICAL)
        for btn in self.button_names:
            self.addButton(box, btn)
        self.sizer.Add(box)

        #add sub controls
        self.addItems(self.sizer)

        self.SetAutoLayout(True)

    def SetValue(self, values):
        self.list.Clear()
        for i, v in enumerate(self._values):
            self.addRowValue(v)

    def addButton(self, sizer, btn):
        item = EMPTY_CLASS()
        self.buttons[btn] = item
        item.id = wx.NewId()
        item.func_name = 'On' + btn.capitalize()
        obj = wx.Button(self, item.id, btn.capitalize(), size=(40, 22))
        item.obj = obj
        sizer.Add(obj, 0, wx.ALL, 1)
        obj.Bind(wx.EVT_BUTTON, self.OnCommand)
        if btn not in ('add', 'ins', 'save'):
            obj.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI)

    def OnSelect(self, event):
        values = self._values[event.GetSelection()]
        for k, obj in self.items.items():
            v = values.get(k, None)
            obj.setValue(v)
            if obj.checkbox:
                obj.checkbox.SetValue(v is not None)
                obj.setEnabled(v is not None)

    def OnCommand(self, event):
        for key, obj in self.buttons.items():
            if obj.id == event.GetId():
                if hasattr(self, obj.func_name):
                    func = getattr(self, obj.func_name)
                    func(event)
                    return

    def OnUpdateUI(self, event):
        event.Enable(self.getSelection() > -1)

    def OnAdd(self, event):
        from EasyDialog import EasyDialog
        dlg = EasyDialog(self, 'Add', self.elements)
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
            self._values.append(values)
            index = self.addRowValue(values)
            self.setSelection(index)

    def OnIns(self, event):
        from EasyDialog import EasyDialog
        dlg = EasyDialog(self, 'Insert', self.elements)
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
            self._values.insert(self.getSelection(), values)
            index = self.addRowValue(values, self.getSelection())
            self.setSelection(index)

    def OnDel(self, event):
        index = i = self.getSelection()
        self.list.Delete(index)
        del self._values[i]

    def OnSave(self, event):
        values = self.getValues()
        index = self.getSelection()
        self._values[index] = values
        self.setRowValue(index, values)

    def OnUp(self, event):
        index = self.getSelection()
        if index > 0:
            values = self.getRowValue(index)
            self.list.Delete(index)
            self.addRowValue(values, index - 1)
            self.setSelection(index - 1)
            self._values[index - 1], self._values[index] = self._values[index], self._values[index - 1]

    def OnDown(self, event):
        index = self.getSelection()
        if index < self.list.GetCount() - 1:
            values = self.getRowValue(index)
            self.list.Delete(index)
            self.addRowValue(values, index + 1)
            self.setSelection(index + 1)
            self._values[index + 1], self._values[index] = self._values[index], self._values[index + 1]

    def createlist(self):
        list = wx.ListBox(self, -1, size=(80, 20), style=wx.LB_SINGLE)

        return list

    def GetValue(self):
        return self._values

    def str(self, s):
        if isinstance(s, (int, float, long)) :
            return "%s" % str(s)
        else:
            return s

    def getSelection(self):
        return self.list.GetSelection()

    def setSelection(self, index):
        n = self.getSelection()
        self.list.Select(index)

    def getRowValue(self, index):
        return self._values[index]

    def setRowValue(self, index, values):
        self.list.SetString(index, values.get(self.keyname))

    def addRowValue(self, values, index=-1):
        value = str_object(values.get(self.keyname))
        if index == -1: #add
            self.list.Append(value)
        else:
            self.list.Insert(value, index)
        return index
