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
#   $Id: InterpreterDialog.py 1731 2006-11-22 03:35:50Z limodou $

import wx
from modules import Entry
from modules import common
from modules import meide as ui
from modules import Globals

class InterpreterDialog(wx.Dialog):
    def __init__(self, parent, pref):
        wx.Dialog.__init__(self, parent, -1, tr('Interpreter Setup'))
        self.parent = parent
        self.pref = pref

        box = wx.BoxSizer(wx.VERTICAL)
        self.list = wx.ListCtrl(self, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_EDIT_LABELS)
        self.list.InsertColumn(0, tr("Description"))
        self.list.InsertColumn(1, tr("Interpreter path"))
        self.list.SetColumnWidth(0, 150)
        self.list.SetColumnWidth(1, 330)
        for i, item in enumerate(pref.python_interpreter):
            description, path = item
            self.list.InsertStringItem(i, description)
            self.list.SetStringItem(i, 1, path)

        box.Add(self.list, 1, wx.EXPAND|wx.ALL, 5)
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        self.ID_ADD = wx.NewId()
        self.ID_REMOVE = wx.NewId()
        self.ID_MODIFY = wx.NewId()
        self.btnAdd = wx.Button(self, self.ID_ADD, tr("Add"))
        box2.Add(self.btnAdd, 0, 0, 5)
        self.btnModify = wx.Button(self, self.ID_MODIFY, tr("Modify"))
        box2.Add(self.btnModify, 0, 0, 5)
        self.btnRemove = wx.Button(self, self.ID_REMOVE, tr("Remove"))
        box2.Add(self.btnRemove, 0, 0, 5)
        self.btnOK = wx.Button(self, wx.ID_OK, tr("OK"))
        self.btnOK.SetDefault()
        box2.Add(self.btnOK, 0, 0, 5)
        self.btnCancel = wx.Button(self, wx.ID_CANCEL, tr("Cancel"))
        box2.Add(self.btnCancel, 0, 0, 5)
        box.Add(box2, 0, wx.ALIGN_CENTER|wx.ALL, 5)

        wx.EVT_BUTTON(self.btnAdd, self.ID_ADD, self.OnAdd)
        wx.EVT_BUTTON(self.btnModify, self.ID_MODIFY, self.OnModify)
        wx.EVT_BUTTON(self.btnRemove, self.ID_REMOVE, self.OnRemove)
        wx.EVT_BUTTON(self.btnOK, wx.ID_OK, self.OnOK)
        wx.EVT_LIST_ITEM_SELECTED(self.list, self.list.GetId(), self.OnItemSelected)
        wx.EVT_LIST_ITEM_DESELECTED(self.list, self.list.GetId(), self.OnItemDeselected)

        self.OnItemDeselected(None)

        self.SetSizer(box)
        self.SetAutoLayout(True)

    def getItemText(self, item):
        return self.list.GetItemText(item), self.list.GetItem(item, 1).GetText()

    def OnRemove(self, event):
        lastitem = -1
        item = self.list.GetNextItem(lastitem, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        while item > -1:
            if self.getItemText(item)[0] == tr('default'):
                common.showmessage(self, tr("You can't delete the default interpreter!"))
                return
            dlg = wx.MessageDialog(self, tr("Do you realy want to delete current item [%s]?") % self.getItemText(item)[0],
                    tr("Deleting Interpreter"), wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
            answer = dlg.ShowModal()
            if answer == wx.ID_YES:
                self.list.DeleteItem(item)
            elif answer == wx.ID_NO:
                lastitem = item
            else:
                return
            item = self.list.GetNextItem(lastitem, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)

    def OnAdd(self, event):
        dlg = Entry.MyFileEntry(self, tr("Interpreter Path"),
                tr("Enter the interpreter path"), '')
        answer = dlg.ShowModal()
        if answer == wx.ID_OK:
            path = dlg.GetValue()
            if len(path) > 0:
                i = self.list.GetItemCount()
                self.list.InsertStringItem(i, 'Change the description')
                self.list.SetStringItem(i, 1, path)
                self.list.EditLabel(i)

    def OnModify(self, event):
        if self.list.GetSelectedItemCount() > 1:
            dlg = wx.MessageDialog(self, tr("You can select only one item"), tr("Modify Interpreter Path"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            return
        item = self.list.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        dlg = Entry.MyFileEntry(self, tr("Interpreter Path"), tr("Enter the interpreter path"), self.getItemText(item)[1])
        answer = dlg.ShowModal()
        if answer == wx.ID_OK:
            path = dlg.GetValue()
            if len(path) > 0:
                self.list.SetStringItem(item, 1, path)

    def OnOK(self, event):
        interpreters = []
        for i in range(self.list.GetItemCount()):
            description, path = self.getItemText(i)
            interpreters.append((description, path))
            if (description == '') or (description == 'Change the description'):
                dlg = wx.MessageDialog(self, tr("The description must not be empty or ") + '"Change the description"' +
                         tr('.\nPlease change them first!'), tr("Saving Interpreter Setting"), wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                return
        else:
            self.pref.python_interpreter = interpreters[:]
            self.pref.save()
            event.Skip()

    def OnItemSelected(self, event):
        self.btnRemove.Enable(True)
        self.btnModify.Enable(True)

    def OnItemDeselected(self, event):
        self.btnRemove.Enable(False)
        self.btnModify.Enable(False)

class PythonArgsDialog(wx.Dialog):
    def __init__(self, parent, title, defaultvalue, defaultchkvalue):
        wx.Dialog.__init__(self, parent, -1, style = wx.DEFAULT_DIALOG_STYLE, title = title)
        
        self.pref = Globals.pref
        
        self.sizer = sizer = ui.VBox(namebinding='widget').create(self).auto_layout()
        box = sizer.add(ui.VGroup(tr('Python interpreter')))
        h = box.add(ui.HBox())
        h.add(ui.Label(tr('Select:')))
        
        interpreters = dict(self.pref.python_interpreter)
        default_interpreter = self.pref.default_interpreter
        if not default_interpreter in interpreters:
            default_interpreter = self.pref.python_interpreter[0][0]
        
        h.add(ui.SingleChoice(default_interpreter, sorted(interpreters.keys())), name='interpreter').bind(wx.EVT_COMBOBOX, self.OnChanged)
        h.add(ui.Label(tr('Parameters:')))
        h.add(ui.Text(self.pref.python_default_paramters.get(default_interpreter, '')), name='parameter')
        
        h = self.sizer.add(ui.HBox())
        h.add(ui.Label(tr('Parameters of script:')))
        h.add(ui.Text(defaultvalue), name='command_line').tooltip("$file will be replaced with the filename of the current document\n"
            "$path will be replaced with the filename's directory of the current document")
        self.sizer.add(ui.Check(defaultchkvalue, tr('Redirect input and output')), name='redirect')
        self.sizer.add(ui.Check(self.pref.python_show_args, tr('Show the Select Arguments dialog at Python program run')), name='show_args')
        
        sizer.add(ui.simple_buttons(), flag=wx.ALIGN_CENTER|wx.BOTTOM)
        self.sizer.bind('btnOk', 'click', self.OnOK)
        self.btnOk.SetDefault()
        
        sizer.auto_fit(1)
        
    def GetValue(self):
        return self.sizer.GetValue()
    
    def OnOK(self, event):
        self.pref.default_interpreter = self.interpreter.GetValue()
        self.pref.python_default_paramters[self.pref.default_interpreter] = self.parameter.GetValue()
        self.pref.python_show_args = self.show_args.GetValue()
        self.pref.save()
        event.Skip()

    def OnChanged(self, event):
        self.parameter.SetValue(self.pref.python_default_paramters.get(self.interpreter.GetValue(), ''))