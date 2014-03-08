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
import os
from modules import Globals
from modules import common
from modules import meide as ui
from modules import CheckList
from tools import wrap_run

class AddDialog(wx.Dialog):
    def __init__(self, parent, title, path):
        wx.Dialog.__init__(self, parent, -1, style = wx.DEFAULT_DIALOG_STYLE, title = title, size=(400, 300))
        self.path = path
        
        self.sizer = box = ui.VBox(namebinding='widget').create(self).auto_layout()
        self.list = CheckList.CheckList(self, columns=[
                (tr("File"), 380, 'left'),
                ], style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        
        box.add(self.list, proportion=1, flag=wx.ALL|wx.EXPAND, border=5)
        self.list.on_check = self.OnCheck
        
        #add selection switch checkbox
        box.add(ui.Check3D(2, tr('Select / deselect All')), name='select').bind('check', self.OnSelect)
        
        box.add(ui.simple_buttons(), flag=wx.ALIGN_CENTER|wx.BOTTOM)
        self.btnOk.SetDefault()
        
        self.init()

    def init(self):
        def f():
            from SvnSettings import get_global_ignore
            ignore = [x[1:] for x in get_global_ignore().split()]
            
            import pysvn
            client = pysvn.Client()
            r = client.status(self.path)
            files = {}
            for node in r:
                files[node['path']] = node['is_versioned']
            if os.path.isfile(self.path) and not files.get(self.path, False):
                wx.CallAfter(self.list.addline, [os.path.basename(self.path)], flag=True)
                self.path = os.path.dirname(self.path)
            else:
                if not files.get(self.path, False):
                    wx.CallAfter(self.list.addline, ['.'], flag=True)
                _len = len(self.path)
                
                def get_path(base, path):
                    p = os.path.join(base, path)
                    for f in os.listdir(p):
                        if '.svn' == f:
                            continue
                        filename = os.path.join(p, f)
                        if os.path.isdir(filename):
                            yield filename+'/'
                            for x in get_path(base, os.path.join(path, f)):
                                yield x
                        else:
                            ext = os.path.splitext(filename)[1]
                            if ext in ignore:
                                continue
                            yield os.path.join(path, f).replace('\\', '/')
                
                for f in get_path(self.path, ''):
                    filename = os.path.join(self.path, f)
                    if not files.get(filename, False):
                          wx.CallAfter(self.list.addline, [filename[_len+1:]], flag=True)
                    
        wrap_run(f)
        
    def GetValue(self):
        files = []
        for i in range(self.list.GetItemCount()):
            if not self.list.getFlag(i):
                continue
            f = self.list.getCell(i, 0)
            if f == '.':
                f = self.path
            else:
                f = os.path.join(self.path, f)
            files.append(f)
        return files
    
    def check_state(self):
        count = {True:0, False:0}
        for i in range(self.list.GetItemCount()):
            count[self.list.getFlag(i)] += 1
        if count[True] > 0 and count[False] > 0:
            self.select.Set3StateValue(wx.CHK_UNDETERMINED)
        elif count[True] > 0 and count[False] == 0:
            self.select.Set3StateValue(wx.CHK_CHECKED)
        else:
            self.select.Set3StateValue(wx.CHK_UNCHECKED)
    
    def OnCheck(self, index, f):
        self.check_state()
    
    def OnSelect(self, event):
        value = event.GetEventObject().Get3StateValue()
        if value == wx.CHK_UNCHECKED:
            self.list.checkAll(False)
        elif value == wx.CHK_CHECKED:
            self.list.checkAll(True)

class RevertDialog(AddDialog):
    def __init__(self, title, path):
        wx.Dialog.__init__(self, Globals.mainframe, -1, style = wx.DEFAULT_DIALOG_STYLE, title = title, size=(450, 300))
        self.path = path
        
        self.sizer = box = ui.VBox(namebinding='widget').create(self).auto_layout()
        self.list = CheckList.CheckList(self, columns=[
                (tr("File"), 300, 'left'),
                (tr("Text Status"), 100, 'left'),
                ], style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        
        box.add(self.list, proportion=1, flag=wx.ALL|wx.EXPAND, border=5)
        self.list.on_check = self.OnCheck
        
        #add selection switch checkbox
        box.add(ui.Check3D(2, tr('Select / deselect All')), name='select').bind('check', self.OnSelect)
        
        box.add(ui.simple_buttons(), flag=wx.ALIGN_CENTER|wx.BOTTOM)
        self.btnOk.SetDefault()
        
        self.init()
        
    def init(self):
        def f():
            import pysvn
            client = pysvn.Client()
            r = client.status(self.path)
            if os.path.isfile(self.path):
                self.path = os.path.dirname(self.path)
            _len = len(self.path)
            for node in r:
                status = str(node['text_status'])
                if  status in ('modified', 'added', 'deleted'):
                    fname = node['path'][_len+1:]
                    if not fname:
                        fname = '.'
                    wx.CallAfter(self.list.addline, [fname, status], flag=True)
    
        wrap_run(f)
        
class CommitDialog(AddDialog):
    def __init__(self, title, path):
        wx.Dialog.__init__(self, Globals.mainframe, -1, style = wx.DEFAULT_DIALOG_STYLE, title = title, size=(600, 500))
        self.pref = Globals.pref
        self.path = path
        self.fileinfos = {}
        self.filelist = []
        
        self.sizer = box = ui.VBox(namebinding='widget').create(self).auto_layout()
        
        box1 = box.add(ui.VGroup(tr("Message")))
        box1.add(ui.Button(tr("Recent Messages"))).bind('click', self.OnHisMsg)
        box1.add(ui.MultiText, name='message')

        #add filenames list
        self.list = CheckList.CheckList(self, columns=[
                (tr("File"), 390, 'left'),
                (tr("Extension"), 70, 'left'),
                (tr("Status"), 100, 'left'),
                ], style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        
        box.add(self.list, proportion=2, flag=wx.EXPAND|wx.ALL, border=5)
        self.list.on_check = self.OnCheck
        
        box.add(
            ui.Check(True, tr('Show unversioned files')), 
            name='chkShowUnVersion').bind('check', self.OnShowUnVersion)
        box.add(
            ui.Check3D(False, tr('Select / deselect All')),
            name='select').bind('check', self.OnSelect)
        
        box.add(ui.simple_buttons(), flag=wx.ALIGN_CENTER|wx.BOTTOM)
        self.btnOk.SetDefault()
        
        box.auto_fit(0)
        
        wx.CallAfter(self.init)

    def GetValue(self):
        add_files = []
        files = []
        for i in range(self.list.GetItemCount()):
            if not self.list.getFlag(i):
                continue
            filename, flag = self.fileinfos[self.list.GetItemData(i)]
            if flag:
                files.append(filename)
            else:
                add_files.append(filename)

        #save log
        message = self.message.GetValue().strip()
        if message:
            self.pref.svn_log_history.insert(0, message)
            del self.pref.svn_log_history[30:]
            self.pref.save()
        return {'add_files':add_files, 'files':files, 
            'message':message}
    
    def init(self):
        self.filelist = []
        def f():
            import pysvn
            client = pysvn.Client()
            r = client.status(self.path, ignore=True)
            if os.path.isfile(self.path):
                self.path = os.path.dirname(self.path)
            _len = len(self.path)
            for node in r:
                status = str(node['text_status'])
                fname = node['path'][_len+1:]
                if not fname:
                    fname = '.'
                if status != 'normal':
                    self.filelist.append((node['is_versioned'], fname, node['path'],
                        status))
                
            if not self.filelist:
                wx.CallAfter(common.showmessage, tr("No files need to process."))
                return
            
            self.load_data(self.chkShowUnVersion.GetValue())
            
        wrap_run(f)
        
    def load_data(self, unversioned=True):
        color = {
            'added':'#007F05',
            'modified':wx.BLACK,
            'deleted':wx.RED,
        }
        
        self.list.DeleteAllItems()
        self.fileinfos = {}
        
        i = 0
        for flag, fname, filename, f in self.filelist:
            ext = os.path.splitext(fname)[1]
            if flag == False:
                if unversioned:
                    index = self.list.addline([fname, ext, f], False)
                    item = self.list.GetItem(index)
                    item.SetTextColour('#999999')
                    self.list.SetItem(item)
                    self.fileinfos[self.list.GetItemData(index)] = (filename, False)
            else:
                index = self.list.insertline(i, [fname, ext, f], True)
                item = self.list.GetItem(index)
                item.SetTextColour(color.get(f, wx.BLACK))
                self.list.SetItem(item)
                self.fileinfos[self.list.GetItemData(index)] = (filename, True)
                i += 1
        self.check_state()
        
    def OnHisMsg(self, event):
        dlg = wx.SingleChoiceDialog(
                self, tr('Select one log'), tr('Log History'),
                self.pref.svn_log_history, 
                wx.CHOICEDLG_STYLE
                )
        
        if dlg.ShowModal() == wx.ID_OK:
            self.message.SetValue(dlg.GetStringSelection())
        dlg.Destroy()
        
    def OnShowUnVersion(self, event):
        wx.CallAfter(self.load_data, event.IsChecked())
            
class ResultDialog(wx.Dialog):
    def __init__(self, parent, title=tr('Result')):
        wx.Dialog.__init__(self, Globals.mainframe, -1, style = wx.DEFAULT_DIALOG_STYLE, title = title, size=(600, 300))
        
        self.parent = parent
        self.sizer = box = ui.VBox(namebinding='widget').create(self).auto_layout()
        self.list = CheckList.List(self, columns=[
                (tr("Action"), 120, 'left'),
                (tr("Path"), 400, 'left'),
                ], style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        
        box.add(self.list, proportion=1, flag=wx.ALL|wx.EXPAND, border=5)
        box.add(ui.Label, name='message')
        box.add(ui.simple_buttons(), flag=wx.ALIGN_CENTER|wx.BOTTOM)
        
        box.bind('btnCancel', 'click', self.OnCancel)
        box.auto_fit(0)
        self.btnOk.Disable()
        self.btnCancel.Enable()
        
    def update_message(self, message):
        wx.CallAfter(self.message.SetLabel, message)
        
    def add(self, data):
        wx.CallAfter(self.list.addline, data)
        
    def finish(self):
        self.btnCancel.Disable()
        self.btnOk.Enable()
        
    def OnCancel(self, event):
        self.parent.cancel = True
        self.btnCancel.Disable()

class GetServerTrust(wx.Dialog):
    def __init__(self, parent, realm, info_list, may_save):
        wx.Dialog.__init__( self, parent, -1, tr('Trust server %s') % realm )

        self.sizer = sizer = ui.VBox(namebinding='widget').create(self).auto_layout()
        box = sizer.add(ui.VGroup(tr('Server Certificate')))
        box1 = box.add(ui.SimpleGrid)
        for key, value in info_list:
            box1.add(key, ui.Text(value, style=wx.TE_READONLY))
         
        sizer.add(ui.Check(may_save, tr("Always trust this server")), name='save')

        sizer.add(ui.simple_buttons(), flag=wx.ALIGN_CENTER|wx.BOTTOM)
        sizer.auto_fit(1)

        self.CentreOnParent()

    def GetValue(self):
        return self.save.GetValue()

class GetCredentials(wx.Dialog):
    def __init__(self, parent, title, username, may_save):
        wx.Dialog.__init__(self, parent, -1, title, size=(300, -1))

        self.sizer = sizer = ui.VBox(namebinding='widget').create(self).auto_layout()
        box = sizer.add(ui.VGroup(tr('Credentials')))
        box1 = box.add(ui.SimpleGrid)
        box1.add(tr('Username:'), ui.Text, name='username')
        box1.add(tr('Password:'), ui.Password, name='password')
        sizer.add(ui.Check(may_save, tr('Always uses these credentials')), name='save')
        
        sizer.add(ui.simple_buttons(), flag=wx.ALIGN_CENTER|wx.BOTTOM)
        sizer.auto_fit(1)
        
        self.CentreOnParent()

    def GetValue(self):
        return self.username.GetValue(), self.password.GetValue(), self.save.GetValue()

class LogMessage(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, title=tr('Input Log Message'), size=(300, 200))
        self.sizer = sizer = ui.VBox(namebinding='widget').create(self).auto_layout()
        sizer.add(ui.MultiText, name='text')
        
        sizer.add(ui.simple_buttons(), flag=wx.ALIGN_CENTER|wx.BOTTOM)
        sizer.auto_fit(0)
        
        self.CentreOnParent()
    
    def GetValue(self):
        return self.text.GetValue()
    
