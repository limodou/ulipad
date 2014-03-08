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
#   $Id$

import wx
import sys
from modules import Globals
from modules import CheckList
import Commands

class SearchWin(wx.Dialog):
    def __init__(self, parent, title=''):
        if hasattr(Globals.pref, 'searchwin_pos') and hasattr(Globals.pref, 'searchwin_size'):
            searchwin_pos = Globals.pref.searchwin_pos
            searchwin_size = Globals.pref.searchwin_size
            wx.Dialog.__init__(self, parent, -1, title, searchwin_pos, searchwin_size, style=wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE)
        else:
            wx.Dialog.__init__(self, parent, -1, title, size=(600, 400), style=wx.RESIZE_BORDER|wx.DEFAULT_DIALOG_STYLE)
            self.Center()
            
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, tr("Search for:"))
        sizer1.Add(label, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)
        self.text = wx.TextCtrl(self, -1, "", style=wx.TE_PROCESS_ENTER)
        self.impact_check = wx.CheckBox(self, -1, tr("Impact Mode"))
        self.autoclose_check = wx.CheckBox(self, -1, tr("Auto Close"))
        sizer1.Add(self.text, 1, wx.ALL, 2)
        sizer1.Add(self.impact_check, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)
        sizer1.Add(self.autoclose_check, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)
        
        self.list = CheckList.List(self, columns=[
                (tr("Function"), 300, 'left'),
                (tr("ShortCuts"), 120, 'left'),
                (tr("Impact"), 80, 'left'),
                ], style=wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL)
        self.commandar = Commands.getinstance()    
        self.cmdbuf = {}
        self.load(self.commandar.search(''))
        
        sizer.Add(sizer1, 0, wx.EXPAND)
        sizer.Add(self.list, 1, wx.EXPAND, 2)
        
        btnCancel = wx.Button(self, wx.ID_CANCEL, tr("Cancel"))
        sizer.Add(btnCancel, 0, wx.ALIGN_CENTER, 2)
        
        wx.EVT_CLOSE(self, self.OnClose)
        wx.EVT_SIZE(self, self.OnSize)
        wx.EVT_BUTTON(self, wx.ID_CANCEL, self.OnClose)
        wx.EVT_TEXT(self.text, self.text.GetId(), self.OnChange)
        wx.EVT_KEY_DOWN(self.text, self.OnKeyDown)
        wx.EVT_LIST_ITEM_ACTIVATED(self.list, self.list.GetId(), self.OnEnter)
        wx.EVT_CHECKBOX(self.impact_check, self.impact_check.GetId(), self.OnCheckImpact)
        wx.EVT_CHECKBOX(self.autoclose_check, self.autoclose_check.GetId(), self.OnCheckAutoClose)
        
        self.impact_check.SetValue(Globals.pref.commands_impact)
        self.autoclose_check.SetValue(Globals.pref.commands_autoclose)
        
        Globals.mainframe.command_mode = True
        
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

    def load(self, commands):
        self.cmdbuf = {}
        self.list.Freeze()
        self.list.DeleteAllItems()
        for i, v in enumerate(commands):
            index = self.list.InsertStringItem(sys.maxint, v[0])
            self.list.SetStringItem(index, 1, v[1])
            self.list.SetStringItem(index, 2, v[2])
            self.cmdbuf[i] = v[3]
            self.list.SetItemData(index, i)
        if self.list.GetItemCount() > 0:
            self.list.Select(0)
        self.list.Thaw()
    
    def getdata(self):
        s = []
        for i, v in enumerate(Globals.commands):
            s.append((v[0], v[1].get('shortcut', ''), i))
        return s
        
    def save_status(self):
        Globals.pref.searchwin_pos = self.GetPosition()
        Globals.pref.searchwin_size = self.GetSize()
        Globals.pref.save()
        
    def OnClose(self, event):
        Globals.mainframe.command_mode = False
        self.save_status()
        self.Destroy()

    def OnSize(self, event):
        self.save_status()
        event.Skip()
        
    def OnChange(self, event):
        text = self.text.GetValue()
        if not Globals.pref.commands_impact:
            self.load(self.commandar.search(text))
        else:
            s = self.commandar.impact_search(text)
            self.load(s)
            if len(s) == 1:     #find a cmd
                self.OnEnter(None)

    def OnKeyDown(self, event):
        key = event.GetKeyCode()
        if key == wx.WXK_RETURN:
            self.OnEnter(None)
            return
        if key == wx.WXK_DOWN:
            if self.list.GetItemCount() > 0:
                i = self.list.GetFirstSelected()
                if i == -1:
                    i = 0
                elif i == self.list.GetItemCount() - 1:
                    i = 0
                else:
                    i += 1
                self.list.Select(i, True)
            return
        if key == wx.WXK_UP:
            if self.list.GetItemCount() > 0:
                i = self.list.GetFirstSelected()
                if i == -1:
                    i = self.list.GetItemCount() - 1
                elif i == 0:
                    i = self.list.GetItemCount() - 1
                else:
                    i -= 1
                self.list.Select(i, True)
            return
        event.Skip()
        
    def OnEnter(self, event):
        i = self.list.GetFirstSelected()
        if i > -1:
            index = self.list.GetItemData(i)
            cmd_id = self.cmdbuf[index]
            self.commandar.run(cmd_id)
            if self.text.GetValue():
                self.text.Clear()
            if Globals.pref.commands_autoclose:
                self.Close()
                
    def OnCheckImpact(self, event):
        Globals.pref.commands_impact = event.IsChecked()
        Globals.pref.save()
        
    def OnCheckAutoClose(self, event):
        Globals.pref.commands_autoclose = event.IsChecked()
        Globals.pref.save()
        