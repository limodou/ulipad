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
#
#   $Id$

import wx
import re, os
from modules import Globals
from modules import common
from modules import CheckList

class BatchRename(wx.Panel):
    def __init__(self, parent):
        self.parent = parent
        wx.Panel.__init__(self, parent, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.fileinfos = {}
        
        #add filenames ctrl
        self.filenames = CheckList.CheckList(self, columns=[
                (tr("Directory"), 200, 'left'),
                (tr("Source Filenames"), 350, 'left'),
                (tr("Results"), 300, 'left'),
                ], style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        
        sizer.Add(self.filenames, 1, wx.ALL|wx.EXPAND, 2)
        
        box1 = wx.BoxSizer(wx.HORIZONTAL)
        self.ID_ADDFILES = wx.NewId()
        self.addfile = wx.Button(self, self.ID_ADDFILES, tr("Add Files"))
        box1.Add(self.addfile, 0, wx.ALL, 2)
        
        self.ID_REMOVEFILES = wx.NewId()
        self.removefile = wx.Button(self, self.ID_REMOVEFILES, tr("Remove Files"))
        box1.Add(self.removefile, 0, wx.ALL, 2)
        
        self.ID_CLEAR = wx.NewId()
        self.clear = wx.Button(self, self.ID_CLEAR, tr("Clear Results"))
        box1.Add(self.clear, 0, wx.ALL, 2)

        self.chk_all = wx.CheckBox(self, -1, tr("Select All"))
        box1.Add(self.chk_all, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)

        self.chk_select = wx.CheckBox(self, -1, tr("Select"))
        box1.Add(self.chk_select, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)

        self.chk_remainsufix = wx.CheckBox(self, -1, tr('Skip filename suffix'))
        self.chk_remainsufix.SetValue(True)
        box1.Add(self.chk_remainsufix, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)

        box1.AddStretchSpacer()

        self.ID_APPLY = wx.NewId()
        self.apply = wx.Button(self, self.ID_APPLY, tr("Apply"))
        box1.Add(self.apply, 0, wx.ALL|wx.ALIGN_RIGHT, 2)

        sizer.Add(box1, 0, wx.EXPAND)
        
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        box2.Add(wx.StaticText(self, -1, tr("Template") + ':'), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)
        self.text = wx.TextCtrl(self, -1, "", size=(150, -1))
        box2.Add(self.text, 1, wx.ALL|wx.EXPAND, 2)

        box2.Add(wx.StaticText(self, -1, tr("Start Num") + ':'), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)
        self.startnum = wx.SpinCtrl(self, -1, "1", size=(40, -1), min=1, max=100, initial=1)
        box2.Add(self.startnum, 0, wx.ALL, 2)

        self.ID_CREATE = wx.NewId()
        self.create = wx.Button(self, self.ID_CREATE, tr("Create"))
        box2.Add(self.create, 0, wx.ALL, 2)

        sizer.Add(box2, 0, wx.EXPAND)
        
        box3 = wx.BoxSizer(wx.HORIZONTAL)
        box3.Add(wx.StaticText(self, -1, tr("Current Result") + ':'), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)
        self.result = wx.TextCtrl(self, -1, "", size=(150, -1))
        box3.Add(self.result, 1, wx.ALL|wx.EXPAND, 2)
        
        self.ID_UPDATE = wx.NewId()
        self.update = wx.Button(self, self.ID_UPDATE, tr("Update"))
        box3.Add(self.update, 0, wx.ALL, 2)
        
        sizer.Add(box3, 0, wx.EXPAND)
        
        box4 = wx.StaticBoxSizer(wx.StaticBox(self, -1, tr("Group Mode")), wx.HORIZONTAL)
        box4.Add(wx.StaticText(self, -1, tr("Find") + ':'), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)
        self.find = wx.TextCtrl(self, -1, "", size=(150, -1))
        box4.Add(self.find, 1, wx.ALL|wx.EXPAND, 2)
        
        box4.Add(wx.StaticText(self, -1, tr("Replace") + ':'), 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)
        self.replace_text = wx.TextCtrl(self, -1, "", size=(150, -1))
        box4.Add(self.replace_text, 1, wx.ALL|wx.EXPAND, 2)
        
        self.chk_regular = wx.CheckBox(self, -1, tr('Regular Mode'))
        self.chk_regular.SetValue(False)
        box4.Add(self.chk_regular, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)

        self.chk_cursor = wx.CheckBox(self, -1, tr('Start from cursor'))
        self.chk_cursor.SetValue(False)
        self.chk_cursor.SetToolTip(wx.ToolTip(tr('If you set this, the process will begin from \nthe cursor position of "Current Result" field')))
        box4.Add(self.chk_cursor, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)

        self.ID_DELETE = wx.NewId()
        self.delete = wx.Button(self, self.ID_DELETE, tr("Delete"))
        box4.Add(self.delete, 0, wx.ALL, 2)
        
        self.ID_REPLACE = wx.NewId()
        self.replace = wx.Button(self, self.ID_REPLACE, tr("Replace"))
        box4.Add(self.replace, 0, wx.ALL, 2)

        self.ID_INSERT = wx.NewId()
        self.insert = wx.Button(self, self.ID_INSERT, tr("Insert"))
        box4.Add(self.insert, 0, wx.ALL, 2)
        
        sizer.Add(box4, 0, wx.EXPAND|wx.ALL, 2)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        
        #bind event
        wx.EVT_BUTTON(self.addfile, self.ID_ADDFILES, self.OnAddFiles)
        wx.EVT_BUTTON(self.removefile, self.ID_REMOVEFILES, self.OnRemoveFiles)
        wx.EVT_BUTTON(self.clear, self.ID_CLEAR, self.OnClear)
        wx.EVT_BUTTON(self.create, self.ID_CREATE, self.OnCreate)
        wx.EVT_BUTTON(self.apply, self.ID_APPLY, self.OnApply)
        wx.EVT_BUTTON(self.update, self.ID_UPDATE, self.OnUpdate)
        wx.EVT_BUTTON(self.delete, self.ID_DELETE, self.OnDelete)
        wx.EVT_BUTTON(self.insert, self.ID_INSERT, self.OnInsert)
        wx.EVT_BUTTON(self.replace, self.ID_REPLACE, self.OnReplace)
        wx.EVT_CHECKBOX(self.chk_all, self.chk_all.GetId(), self.OnAll)
        wx.EVT_CHECKBOX(self.chk_select, self.chk_select.GetId(), self.OnSelect)
        wx.EVT_LIST_ITEM_ACTIVATED(self.filenames, self.filenames.GetId(), self.OnEnterItem)
        wx.EVT_LIST_ITEM_SELECTED(self.filenames, self.filenames.GetId(), self.OnSelectItem)
        wx.EVT_UPDATE_UI(self.removefile, self.ID_REMOVEFILES, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self.chk_select, self.chk_select.GetId(), self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self.update, self.ID_UPDATE, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self.result, self.result.GetId(), self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self.find, self.find.GetId(), self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self.replace_text, self.replace_text.GetId(), self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self.delete, self.ID_DELETE, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self.replace, self.ID_REPLACE, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self.insert, self.ID_INSERT, self.OnUpdateUI)

    def OnAddFiles(self, event):
        dlg = wx.FileDialog(self, tr("Open"), Globals.pref.last_batchrenamefilenames_path, "", '*.*', wx.OPEN|wx.HIDE_READONLY|wx.MULTIPLE)
        files = []
        if dlg.ShowModal() == wx.ID_OK:
            files = dlg.GetPaths()
        dlg.Destroy()
        for i in range(self.filenames.GetItemCount()-1, -1, -1):
            self.filenames.delline(i)
        self.fileinfos = {}
        _cmp = lambda x,y: cmp(x.lower(), y.lower())
        for f in sorted(files, _cmp):
            path = os.path.dirname(f)
            filename = os.path.basename(f)
            if self.chk_remainsufix.GetValue():
                filename = os.path.splitext(filename)[0]
            i = self.filenames.addline([path, filename, filename], True)
            self.fileinfos[self.filenames.GetItemData(i)] = f
        if files:
            Globals.pref.last_batchrenamefilenames_path = os.path.dirname(files[0])
            Globals.pref.save()
            
    def OnRemoveFiles(self, event):
        for i in range(self.filenames.GetItemCount()-1, -1, -1):
            if self.filenames.getFlag(i):
                del self.fileinfos[self.filenames.GetItemData(i)]
                self.filenames.delline(i)
                
    def OnSelect(self, event):
        i = self.filenames.GetFirstSelected()
        while i>-1:
            self.filenames.setFlag(i, self.chk_select.GetValue())
            i = self.filenames.GetNextSelected(i)
            
    def OnClear(self, event):
        for i in range(self.filenames.GetItemCount()):
            if not self.filenames.getFlag(i):
                continue
            self.filenames.setCell(i, 2, '')
            
    def OnUpdateUI(self, event):
        eid = event.GetId()
        if eid in [self.ID_REMOVEFILES, self.ID_CREATE, self.chk_select.GetId(),
                self.ID_APPLY, self.ID_UPDATE, self.result.GetId(),
                self.find.GetId(), self.ID_DELETE, self.replace_text.GetId(),
                self.ID_INSERT, self.ID_REPLACE]:
            event.Enable(self.filenames.GetSelectedItemCount()>0)
            
    def OnEnterItem(self, event):
        i = event.GetIndex()
        self.text.SetValue(self.filenames.getCell(i, 1))
        
    def OnSelectItem(self, event):
        i = event.GetIndex()
        self.result.ChangeValue(self.filenames.getCell(i, 2))
        
    def OnAll(self, event):
        f = self.chk_all.GetValue()
        self.filenames.checkAll(f)
            
    def OnCreate(self, event):
        find = self.text.GetValue()
        b = re.search(r'\?+', find)
        p = pt = ''
        if b:
            p = b.group()
        start = self.startnum.GetValue()
        p_len = len(p)
        for i in range(self.filenames.GetItemCount()):
            if not self.filenames.getFlag(i):
                continue
            if not find:
                f = self.filenames.getCell(i, 1)
            else:
                if p:
                    f = find.replace(p, str(start).zfill(p_len))
                else:
                    f = find
            self.filenames.setCell(i, 2, f)
            start = start + 1
        self._select()
        
    def OnApply(self, event):
        dlg = wx.MessageDialog(self, tr("Do you want to apply these changes?\nThese changes will not be undo."), tr("Confirm"), wx.OK | wx.CANCEL | wx.ICON_INFORMATION)
        ret = dlg.ShowModal()
        dlg.Destroy()
        if ret == wx.ID_CANCEL:
            return
        
        for i in range(self.filenames.GetItemCount()-1, -1, -1):
            if not self.filenames.getFlag(i):
                continue
            filename = self.fileinfos[self.filenames.GetItemData(i)]
            path = os.path.dirname(filename)
            if self.chk_remainsufix.GetValue():
                ext = os.path.splitext(filename)[1]
            else:
                ext = ''
            f = self.filenames.getCell(i, 2)
            if f:
                newf = os.path.join(path, f+ext)
                try:
                    os.rename(filename, newf)
                    self.filenames.delline(i)
                except Exception, e:
                    common.showerror(self, str(e))
                    self.filenames.setFlag(i, False)
            else:
                self.filenames.setFlag(i, False)
        
    def OnUpdate(self, event):
        i = self.filenames.GetFirstSelected()
        if i>-1:
            self.filenames.setCell(i, 2, self.result.GetValue())
            
    def _get_find(self):
        if self.chk_regular.GetValue():
            p = self.find.GetValue()
        else:
            p = re.escape(self.find.GetValue())
        return p
        
    def OnDelete(self, event):
        pos = self._get_insert_pos()
        try:
            b = re.compile(self._get_find(), re.DOTALL)
        except Exception, e:
            common.showerror(self, str(e))
            return
        for i in range(self.filenames.GetItemCount()):
            if not self.filenames.getFlag(i):
                continue
            f = self.filenames.getCell(i, 2)
            f = f[:pos] + b.sub('', f[pos:], 1)
            self.filenames.setCell(i, 2, f)
        self._select()
    
    def OnInsert(self, event):
        pos = self._get_insert_pos()
        for i in range(self.filenames.GetItemCount()):
            if not self.filenames.getFlag(i):
                continue
            f = self.filenames.GetItem(i, 2).GetText()
            f = f[:pos] + self.find.GetValue() + f[pos:]
            self.filenames.setCell(i, 2, f)
        self._select()
        
    def OnReplace(self, event):
        pos = self._get_insert_pos()
        try:
            b = re.compile(self._get_find(), re.DOTALL)
        except Exception, e:
            common.showerror(self, str(e))
            return
        for i in range(self.filenames.GetItemCount()):
            if not self.filenames.getFlag(i):
                continue
            f = self.filenames.getCell(i, 2)
            f = f[:pos] + b.sub(self.replace_text.GetValue(), f[pos:], 1)
            self.filenames.setCell(i, 2, f)
        self._select()
        
    def _get_insert_pos(self):
        if self.chk_cursor.GetValue():
            pos = self.result.GetInsertionPoint()
        else:
            pos = 0
        return pos
    
    def _select(self):
        index = self.filenames.GetFirstSelected()
        if index > -1:
            self.filenames.Select(index, False)
            self.filenames.Select(index, True)
        