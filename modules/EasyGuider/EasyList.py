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
import wx.lib.mixins.listctrl as listmix
from EasyUtils import *

class AutoWidthListCtrl(wx.ListView,listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, style=wx.LC_REPORT, size=wx.DefaultSize):
        wx.ListView.__init__(self, parent, -1, style=style, size=size)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

class EasyList(wx.Panel):
    def __init__(self, parent, datas=[], values=[], style=wx.LC_REPORT, size=wx.DefaultSize, flag='edit'):
        wx.Panel.__init__(self, parent)

        if flag == 'edit':
            self.columns = datas['columns']
            self.elements = datas['elements']
        else:
            self.columns = datas['columns']
            self.elements = []

        self.cols, self.cols_key = self.setColsId(self.elements)
        self.values = copy.deepcopy(values)
        self.parent = parent
        self.style = style
        self.size = size
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)
        self.list = self.createlist(self.columns)
        self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnEdit)
        self.sizer.Add(self.list, 1, wx.EXPAND|wx.ALL, 2)
        self.SetValue(self.values)

        if flag == 'edit':
            self.button_names = ['add', 'ins', 'del', 'edit', 'up', 'down']
            self.buttons = {}
            sizer1 = wx.BoxSizer(wx.VERTICAL)
            for btn in self.button_names:
                self.addButton(sizer1, btn)
            self.sizer.Add(sizer1)
        self.SetAutoLayout(True)

    def SetValue(self, values):
        self.list.DeleteAllItems()
        self.values = values
        for i, v in enumerate(self.values):
            self.addRowValue(v)

    def setColsId(self, elements):
        cols = {}
        keys = []
        for i, v in enumerate(elements):
            kind, prefname, prefvalue, message, extern = v
            cols[prefname] = i
            keys.append(prefname)
        return cols, keys

    def getColIdValue(self, values, id):
        return values[self.cols_key[id]]

    def addButton(self, sizer, btn):
        item = EMPTY_CLASS()
        self.buttons[btn] = item
        item.id = wx.NewId()
        item.func_name = 'On' + btn.capitalize()
        obj = wx.Button(self, item.id, btn.capitalize(), size=(40, 22))
        item.obj = obj
        sizer.Add(obj, 0, wx.ALL, 1)
        obj.Bind(wx.EVT_BUTTON, self.OnCommand)
        if btn not in ('add'):
            obj.Bind(wx.EVT_UPDATE_UI, self.OnUpdateUI)

    def OnCommand(self, event):
        for key, obj in self.buttons.items():
            if obj.id == event.GetId():
                if hasattr(self, obj.func_name):
                    func = getattr(self, obj.func_name)
                    func(event)
                    return

    def OnUpdateUI(self, event):
        event.Enable(self.list.GetFirstSelected() > -1)

    def OnAdd(self, event):
        from EasyDialog import EasyDialog
        dlg = EasyDialog(self, 'Add', self.elements)
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
            self.values.append(values)
            index = self.addRowValue(values)
            self.setSelection(index)

    def OnIns(self, event):
        from EasyDialog import EasyDialog
        dlg = EasyDialog(self, 'Insert', self.elements)
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
            self.values.insert(self.getSelection(), values)
            index = self.addRowValue(values, self.getSelection())
            self.setSelection(index)

    def OnDel(self, event):
        index = i = self.list.GetFirstSelected()
        while i > -1:
            self.list.DeleteItem(i)
            del self.values[i]
            i = self.list.GetNextSelected(i + 1)
        if index < self.list.GetItemCount():
            self.setSelection(index)
        elif index > 0:
            self.setSelection(index - 1)

    def OnEdit(self, event):
        from EasyDialog import EasyDialog
        index = self.list.GetFirstSelected()
        dlg = EasyDialog(self, 'Edit', self.elements, self.getRowValue(index))
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
            self.values[index] = values
            self.setRowValue(index, values)

    def OnUp(self, event):
        index = self.list.GetFirstSelected()
        if index > 0:
            values = self.getRowValue(index)
            self.list.DeleteItem(index)
            self.addRowValue(values, index - 1)
            self.setSelection(index - 1)
            self.values[index - 1], self.values[index] = self.values[index], self.values[index - 1]

    def OnDown(self, event):
        index = self.list.GetFirstSelected()
        if index < self.list.GetItemCount() - 1:
            values = self.getRowValue(index)
            self.list.DeleteItem(index)
            self.addRowValue(values, index + 1)
            self.setSelection(index + 1)
            self.values[index + 1], self.values[index] = self.values[index], self.values[index + 1]

    def createlist(self, columns):
        self.columns_num = len(columns)
        list = AutoWidthListCtrl(self, style=self.style, size=self.size)

        for i, v in enumerate(columns):
            info = wx.ListItem()
            info.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_FORMAT

            name, length, align = v

            if align == 'left':
                info.m_format = wx.LIST_FORMAT_LEFT
            elif align == 'center':
                info.m_format = wx.LIST_FORMAT_CENTER
            else:
                info.m_format = wx.LIST_FORMAT_RIGHT
            info.m_text = name
            list.InsertColumnInfo(i, info)
            list.SetColumnWidth(i, length)

        return list

    def GetValue(self):
        return self.values

    def str(self, s):
        if isinstance(s, (int, float, long)) :
            return "%s" % str(s)
        else:
            return s

    def getSelection(self):
        return self.list.GetFirstSelected()

    def setSelection(self, index):
        n = self.list.GetFirstSelected()
        while n > -1:
            self.list.SetItemState(n, 0, wx.LIST_STATE_SELECTED)
            n = self.list.GetNextSelected(n + 1)
        self.list.Select(index)
        self.list.EnsureVisible(index)

    def getRowValue(self, index):
        return self.values[index]

    def getRowText(self, index, col):
        if index >= 0:
            return self.list.GetItem(index, col).GetText()
        else:
            return ''

    def getSelRowText(self, col):
        return self.getRowText(self.list.GetFirstSelected(), col)

    def setRowValue(self, index, values):
        for j in range(len(self.cols_key)):
            value = self.getColIdValue(values, j)
            if isinstance(value, bool):
                value = ['N', 'Y'][value]
            if isinstance(value, (list, tuple, dict)):
                value = '<...>'
            self.list.SetStringItem(index, j, self.str(value))

    def addRowValue(self, values, index=-1):
        if index == -1:
            pos = sys.maxint
        else:
            pos = index
        index = self.list.InsertStringItem(pos, self.str(self.getColIdValue(values, 0)))
        for j in range(1, len(self.cols_key)):
            value = self.getColIdValue(values, j)
            if isinstance(value, bool):
                value = ['N', 'Y'][value]
            if isinstance(value, (list, tuple, dict)):
                value = '<...>'
            self.list.SetStringItem(index, j, self.str(value))
        return index
