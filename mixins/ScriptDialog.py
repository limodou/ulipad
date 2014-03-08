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
#   $Id: ScriptDialog.py 1731 2006-11-22 03:35:50Z limodou $

import wx
import os.path
import wx.lib.dialogs
from modules import CheckList
from modules import Globals
from modules import common

class ScriptDialog(wx.Dialog):
    def __init__(self, parent, pref):
        wx.Dialog.__init__(self, parent, -1, tr('Script Manager'), size=(600, 300))
        self.parent = parent
        self.pref = pref

        box = wx.BoxSizer(wx.VERTICAL)
        self.list = CheckList.List(self, columns=[
                (tr("Description"), 150, 'left'),
                (tr("Filename"), 330, 'left'),
                (tr("Shortcut"), 80, 'center'),
                ], style=wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_EDIT_LABELS)
        
        for i, item in enumerate(pref.scripts):
            description, filename = item
            pos = description.find('\t')
            if pos > -1:
                shortcut = description[pos+1:]
                description = description[:pos]
            else:
                shortcut = ''
            self.list.addline([description, filename, shortcut])

        box.Add(self.list, 1, wx.EXPAND|wx.ALL, 5)
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        self.ID_UP = wx.NewId()
        self.ID_DOWN = wx.NewId()
        self.ID_ADD = wx.NewId()
        self.ID_EDIT = wx.NewId()
        self.ID_REMOVE = wx.NewId()
        self.btnUp = wx.Button(self, self.ID_UP, tr("Up"))
        box2.Add(self.btnUp, 0, 0, 5)
        self.btnDown = wx.Button(self, self.ID_DOWN, tr("Down"))
        box2.Add(self.btnDown, 0, 0, 5)
        self.btnAdd = wx.Button(self, self.ID_ADD, tr("Add"))
        box2.Add(self.btnAdd, 0, 0, 5)
        self.btnEdit = wx.Button(self, self.ID_EDIT, tr("Edit"))
        box2.Add(self.btnEdit, 0, 0, 5)
        self.btnRemove = wx.Button(self, self.ID_REMOVE, tr("Remove"))
        box2.Add(self.btnRemove, 0, 0, 5)
        self.btnOK = wx.Button(self, wx.ID_OK, tr("OK"))
        self.btnOK.SetDefault()
        box2.Add(self.btnOK, 0, 0, 5)
        self.btnCancel = wx.Button(self, wx.ID_CANCEL, tr("Cancel"))
        box2.Add(self.btnCancel, 0, 0, 5)
        box.Add(box2, 0, wx.ALIGN_CENTER|wx.ALL, 5)

        wx.EVT_BUTTON(self.btnUp, self.ID_UP, self.OnUp)
        wx.EVT_BUTTON(self.btnDown, self.ID_DOWN, self.OnDown)
        wx.EVT_BUTTON(self.btnAdd, self.ID_ADD, self.OnAdd)
        wx.EVT_BUTTON(self.btnEdit, self.ID_EDIT, self.OnEdit)
        wx.EVT_BUTTON(self.btnRemove, self.ID_REMOVE, self.OnRemove)
        wx.EVT_BUTTON(self.btnOK, wx.ID_OK, self.OnOK)
        wx.EVT_LIST_ITEM_ACTIVATED(self.list, self.list.GetId(), self.OnEdit)
        wx.EVT_UPDATE_UI(self.btnEdit, self.ID_EDIT, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self.btnUp, self.ID_UP, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self.btnDown, self.ID_DOWN, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self.btnRemove, self.ID_REMOVE, self.OnUpdateUI)

        self.SetSizer(box)
        self.SetAutoLayout(True)

    def OnEdit(self, event):
        i = self.list.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        value = dict(zip(['description', 'filename', 'shortcut'],
            self.list.getline(i)))
        dlg = AddScriptDialog(self, value=value)
        value = None
        try:
            if dlg.ShowModal() == wx.ID_OK:
                value = dlg.GetValue()
            else:
                return
        finally:
            dlg.Destroy()
        
        self.list.updateline(i, [value['description'], value['filename'],
            value['shortcut']])
        self.pref.last_script_dir = os.path.dirname(value['filename'])
        self.pref.save()
        if value['description'] == 'Change the description':
            self.list.EditLabel(i)
        
    def OnUp(self, event):
        item = self.list.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        self.list.exchangeline(item, item - 1)

    def OnDown(self, event):
        item = self.list.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        self.list.exchangeline(item, item + 1)

    def OnRemove(self, event):
        lastitem = -1
        item = self.list.GetNextItem(lastitem, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        while item > -1:
            dlg = wx.MessageDialog(self, tr("Do you realy want to delete current item [%s]?") % self.list.getCell(item), tr("Deleting Script"), wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
            answer = dlg.ShowModal()
            dlg.Destroy()
            if answer == wx.ID_YES:
                self.list.delline(item)
            elif answer == wx.ID_NO:
                lastitem = item
            else:
                return
            item = self.list.GetNextItem(lastitem, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)

    def OnAdd(self, event):
        dlg = AddScriptDialog(self)
        value = None
        try:
            if dlg.ShowModal() == wx.ID_OK:
                value = dlg.GetValue()
            else:
                return
        finally:
            dlg.Destroy()

        i = self.list.addline([value['description'], value['filename'],
            value['shortcut']])
        self.pref.last_script_dir = os.path.dirname(value['filename'])
        self.pref.save()
        if value['description'] == 'Change the description':
            self.list.EditLabel(i)

    def OnOK(self, event):
        scripts = []
        for description, filename, shortcut in self.list.GetValue():
            scripts.append((description+'\t'+shortcut, filename))
            if (description == '') or (description == 'Change the description'):
                common.showerror(self, tr("The description must not be empty or ") + '"Change the description"' +
                         tr('.\nPlease change them first!'))
                return
        self.pref.scripts = scripts[:]
        self.pref.save()
        event.Skip()

    def OnUpdateUI(self, event):
        _id = event.GetId()
        count = self.list.GetSelectedItemCount()
        if _id in (self.ID_UP, self.ID_DOWN, self.ID_REMOVE, self.ID_EDIT):
            event.Enable(count>0)

class AddScriptDialog(wx.Dialog):
    def __init__(self, parent, value=None, size=(400, 150)):
        wx.Dialog.__init__(self, parent, -1, style = wx.DEFAULT_DIALOG_STYLE, title = tr('Add Script'), size=size)

        box = wx.BoxSizer(wx.VERTICAL)
        gbs = wx.GridBagSizer(5, 5)
        
        self.filename = wx.TextCtrl(self, -1, '')
        gbs.Add(wx.StaticText(self, -1, tr('Script File')), (0, 0), flag=wx.ALIGN_CENTER_VERTICAL, border=2)
        
        box1 = wx.BoxSizer(wx.HORIZONTAL)
        box1.Add(self.filename, 1, wx.EXPAND)
        self.ID_BROWSER = wx.NewId()
        self.btnBrowser = wx.Button(self, self.ID_BROWSER, '...', size=(22, 22))
        box1.Add(self.btnBrowser, 0, wx.LEFT, 5)
        gbs.Add(box1, (0, 1), flag=wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, border=2)
        
        self.text = wx.TextCtrl(self, -1, '')
        gbs.Add(wx.StaticText(self, -1, tr('Description')), (1, 0), flag=wx.ALIGN_CENTER_VERTICAL, border=2)
        gbs.Add(self.text, (1, 1), flag=wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, border=2)
        
        shortcuts = []
        for i in range(0, 10):
            shortcuts.append('Ctrl+%d' % i)
        self.shortcut = wx.ComboBox(self, -1, '', choices = shortcuts, style = wx.CB_DROPDOWN|wx.CB_READONLY )
        gbs.Add(wx.StaticText(self, -1, tr('Choice Shortcut')), (2, 0), flag=wx.ALIGN_CENTER_VERTICAL, border=2)
        gbs.Add(self.shortcut, (2, 1), flag=wx.ALIGN_CENTER_VERTICAL, border=2)
        
        box.Add(gbs, 1, wx.EXPAND|wx.ALL, 5)
        gbs.AddGrowableCol(1)
        
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        btnOK = wx.Button(self, wx.ID_OK, tr("OK"))
        btnOK.SetDefault()
        box2.Add(btnOK, 0, wx.ALIGN_RIGHT|wx.RIGHT, 5)
        btnCancel = wx.Button(self, wx.ID_CANCEL, tr("Cancel"))
        box2.Add(btnCancel, 0, wx.ALIGN_LEFT|wx.LEFT, 5)
        box.Add(box2, 0, wx.ALIGN_CENTER|wx.BOTTOM, 5)

        wx.EVT_BUTTON(self.btnBrowser, self.ID_BROWSER, self.OnBrowser)
        
        if value:
            self.text.SetValue(value['description'])
            self.filename.SetValue(value['filename'])
            self.shortcut.SetValue(value['shortcut'])
        
        self.SetSizer(box)
        self.SetAutoLayout(True)
        
        self.Centre()

    def GetValue(self):
        v = {}
        v['description'] = self.text.GetValue()
        v['filename'] = self.filename.GetValue()
        v['shortcut'] = self.shortcut.GetValue()
        return v

    def OnBrowser(self, event):
        filename = ''
        dlg = wx.FileDialog(self, tr("Select Script File"), Globals.pref.last_script_dir, 
            "", tr("Python file (*.py)|*.py"), wx.OPEN)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
                self.filename.SetValue(filename)
                
                def guess_name(text):
                    import re
                    import os
                    
                    r = re.compile('(?i)#\s*(?:caption|name)\s*[:=](.*)$', re.M)
                    b = r.search(text)
                    name = ''
                    if b:
                        name = b.group(1).strip()
                    if not name:
                        name = os.path.splitext(os.path.basename(filename))[0]
                    if not name:
                        name = 'Change the description'
                    return name
                        
                from modules import common
                from modules import unicodetext
                from modules.Debug import error
                
                try:
                    s, encoding = unicodetext.unicodetext(file(filename).read())
                    name = guess_name(s)
                except unicodetext.UnicodeError:
                    common.showerror(self, tr("Unicode convert error"))
                    error.traceback()
                    return
                except:
                    common.showerror(self, tr("Can't open the file %s.") % filename)
                    error.traceback()
                    return
                self.text.SetValue(name)
        finally:
            dlg.Destroy()
        
    