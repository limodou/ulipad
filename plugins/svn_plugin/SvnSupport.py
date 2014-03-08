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
#   Update:
#   2008/08/25
#       * Support Chinese filename, and auto adaptate the utf-8 encoding and local
#         locale
#       * When exporting, can test if the direction directory is already existed
#       * Add refreshing current folder functionality after the svn command finished
#   2008/08/27
#       * Add show unversioned files checkbox
#       * Add select / deselect all checkbox, support 3Dstates

import wx
import os
from modules import Globals
from modules import common
from modules import meide as ui
from Dialogs import (AddDialog, RevertDialog, CommitDialog, 
    ResultDialog, GetServerTrust, GetCredentials, LogMessage)
from tools import wrap_run, CallFunctionOnMainThread

#export functions
################################################################
def do(dirwin, command, *args):
    callbacks = {
        'update': dirwin.OnRefresh,
        'commit':dirwin.OnRefresh,
        'add':dirwin.OnRefresh,
        'rename':dirwin.OnRefresh,
        'delete':dirwin.OnRefresh,
        'revert':dirwin.OnRefresh,
        'status':dirwin.OnRefresh,
    }

    proxy = Command(dirwin, *args)
    func = getattr(proxy, command, None)
    if func:
        func(callbacks.get(command, None))
    else:
        common.showerror(tr("Don't support [%s] command!") % command)

class Command(object):
    def __init__(self, dirwin, *args):
        try:
            import pysvn
            client = pysvn.Client()
        except:
            common.showerror(dirwin, tr('You should install pysvn module first.\nYou can get it from http://pysvn.tigris.org/'))
            return
        
        self.svn = pysvn
        self.dirwin = dirwin
        self.args = args
        self.pref = Globals.pref
        self.path = args[0]
        self.result = None
        self.cancel = False
        
    def _begin(self):
        self.cancel = False
        if self.result:
            self.result.Destory()
            self.result = None
        
    def export(self, callback=None):
        self._begin()
        dirwin = self.dirwin
        url = self.path
        path = get_path(dirwin.pref.version_control_export_path)
        self.pref.version_control_export_path = path
        self.pref.save()
        if not path:
            return
        export_path = os.path.join(path, os.path.basename(url))
        if os.path.exists(export_path):
            dlg = wx.MessageDialog(dirwin, tr("The directory [%s] is existed, \ndo you want to overwrite it?") % export_path, 
                tr("Export"), wx.YES_NO|wx.ICON_QUESTION)
            answer = dlg.ShowModal()
            dlg.Destroy()
            if answer != wx.ID_YES:
                return
            force = True
        else:
            force = False
            
        def callback():
            common.showmessage(tr('Export completed!'))
            
        def f():
            client = self.get_client([])
            client.export(url, export_path, force)
            
        wrap_run(f, callback)
            
    def checkout(self, callback=None):
        self._begin()
        dlg = CheckoutDialog()
        value = None
        if dlg.ShowModal() == wx.ID_OK:
            value = dlg.GetValue()
        dlg.Destroy()
        if not value: return
    
        if value['revision']:
            r = value['revision']
        else:
            r = self.svn.Revision(self.svn.opt_revision_kind.head )
    
        self.result = ResultDialog(self)
        self.result.Show()

        def f():
            client = self.get_client()
            client.checkout(value['url'], value['dir'], revision=r)
            if self.result:
                self.result.finish()
                
        wrap_run(f, callback, result=self.result)
            
    def list(self, callback=None):
        self._begin()
        def f():
            client = self.get_client()
            r = client.list(self.path)
            s = []
            fmt = "%(path)-60s %(last_author)-20s %(size)-10s"
            s.append(fmt % {'path':'Filename', 'last_author':'Last Author', 'size':'Size'})
            for node, flag in r:
                t = fmt % node
                s.append(t)
            wx.CallAfter(show_in_message_win, '\n'.join(s))
        wrap_run(f, callback)
        
    def status(self, callback=None):
        self._begin()
        def f():
            client = self.get_client()
            r = client.status(self.path, ignore=True)
            s = []
            fmt = "%(path)-60s %(text_status)-20s"
            s.append(fmt % {'path':'Filename', 'text_status':'Status'})
            for node in r:
                t = fmt % node
                s.append(t)
            wx.CallAfter(show_in_message_win, '\n'.join(s))
        wrap_run(f, callback)
        
    def log(self, callback):
        self._begin()
        def f():
            import time
            
            client = self.get_client()
            r = client.log(self.path)
            s = []
            fmt = ("%(message)s\n" + '-'*70 + 
                "\nr%(revision)d | %(author)s | %(date)s\n")
            for node in r:
                node['revision'] = node['revision'].number
                node['date'] = time.strftime("%Y-%m-%d %H:%M:%S", 
                    time.localtime(node['date']))
                if not node['author']:
                    node['author'] = tr('<No Author>')
                t = fmt % node
                s.append(t)
            wx.CallAfter(show_in_message_win, '\n'.join(s))
        wrap_run(f, callback)
        
    def diff(self, callback):
        self._begin()
        def f():
            client = self.get_client([])
            r = client.diff(wx.StandardPaths.Get().GetTempDir(), self.path)
            wx.CallAfter(show_in_message_win, r)
        wrap_run(f, callback)
        
    def add(self, callback):
        self._begin()
        dlg = AddDialog(Globals.mainframe, tr('Add'), self.path)
        values = []
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
        dlg.Destroy()
        
        if values:
            self.result = ResultDialog(self)
            self.result.Show()

            def f():
                client = self.get_client()
                client.add(values, False)
                if self.result:
                    self.result.finish()
            wrap_run(f, callback, result=self.result)
            
    def revert(self, callback):
        self._begin()
        dlg = RevertDialog(tr('Revert'), self.path)
        values = []
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
        dlg.Destroy()
        
        if values:
            self.result = ResultDialog(self)
            self.result.Show()

            def f():
                client = self.get_client()
                client.revert(values, False)
                if self.result:
                    self.result.finish()
            wrap_run(f, callback, result=self.result)
            
    def rename(self, callback):
        self._begin()
        dir = os.path.dirname(self.path)
        dlg = wx.TextEntryDialog(Globals.mainframe, tr('New name'),
            tr('Rename'), os.path.basename(self.path))
        newname = ''
        if dlg.ShowModal() == wx.ID_OK:
            newname = os.path.join(dir, dlg.GetValue())
        dlg.Destroy()
        if newname:
            def f():
                client = self.get_client([])
                client.move(self.path, os.path.join(dir, newname))
            wrap_run(f, callback)
            
    def delete(self, callback):
        self._begin()
        def f():
            client = self.get_client([])
            client.remove(self.path)
        wrap_run(f, callback)
        
    def update(self, callback):
        self._begin()
        
        self.result = ResultDialog(self)
        self.result.Show()

        def f():
            client = self.get_client()
            client.update(self.path)
            if self.result:
                self.result.finish()
                
        wrap_run(f, callback, result=self.result)
    
    def commit(self, callback):
        self._begin()
        dlg = CommitDialog(tr('Commit'), self.path)
        values = None
        if dlg.ShowModal() == wx.ID_OK:
            values =  dlg.GetValue()
        dlg.Destroy()
        
        if values and values['add_files'] + values['files']:
            self.result = ResultDialog(self)
            self.result.Show()

            def f():
                client = self.get_client()
                if values['add_files']:
                    client.add(values['add_files'], False)
                client.checkin(values['add_files'] + values['files'], values['message'])
                client.update('.', False)
                if self.result:
                    self.result.finish()
            wrap_run(f, callback, result=self.result)
            
    def get_client(self, flag=['notify', 'get_log_message', 'get_login', 'ssl_server_trust_prompt', 'cancel']):
        client = self.svn.Client()
        if 'notify' in flag:
            client.callback_notify  = self.cbk_update
        if 'get_log_message' in flag:
            client.callback_get_log_message = CallFunctionOnMainThread(self.cbk_get_log_message)
        if 'get_login' in flag:
            client.callback_get_login = CallFunctionOnMainThread(self.cbk_get_login)
        if 'ssl_server_trust_prompt' in flag:
            client.callback_ssl_server_trust_prompt = CallFunctionOnMainThread(self.cbk_ssl_server_trust_prompt)
        if 'cancel' in flag:
            client.callback_cancel = self.cbk_cancel
        return client
        
    def cbk_update(self, event):
        if event['error']:
            self.result.add([tr('error'), event['error']])
        else:
            action = str(event['action'])
            if action.startswith('update_'):
                action = action[7:]
            elif action.startswith('commit_'):
                action = action[7:]
                
            if action == 'update':
                return
            elif action == 'completed':
                action = 'completed'
                path = 'At version %d' % event['revision'].number
            else:
                path = event['path']
            self.result.add([action, common.decode_string(path, 'utf8')])
            
    def cbk_ssl_server_trust_prompt(self, trust_data):
        realm = trust_data['realm']
        
        info_list = []
        info_list.append(('Hostname', trust_data['hostname']))
        info_list.append(('Valid From', trust_data['valid_from']))
        info_list.append(('Valid Until', trust_data['valid_until']))
        info_list.append(('Issuer Name', trust_data['issuer_dname']))
        info_list.append(('Finger Print', trust_data['finger_print']))
        
        dlg = GetServerTrust(Globals.mainframe, realm, info_list, True)
        save = False
        trust = False
        if dlg.ShowModal() == wx.ID_OK:
            save = dlg.GetValue()
            trust = True
        dlg.Destroy()
        
        return trust, trust_data['failures'], save
    
    def cbk_get_login(self, realm, username, save):
        dlg = GetCredentials(Globals.mainframe, realm, username, True)
        save = False
        username = ''
        password = ''
        ret = False
        if dlg.ShowModal() == wx.ID_OK:
            username, password, save = dlg.GetValue()
            ret = True
        dlg.Destroy()
        return ret, username.encode('utf-8'), password.encode('utf-8'), save

    def cbk_get_log_message(self):
        dlg = LogMessage(Globals.mainframe)
        message = ''
        if dlg.ShowModal() == wx.ID_OK:
            message = dlg.GetValue()
        dlg.Destroy()
        if message:
            return True, message.encode('utf-8')
        return False, ''
    
    def cbk_cancel(self):
        return self.cancel
        
#common functions
################################################################
def show_in_message_win(text, clear=True, goto_end=False):
    win = Globals.mainframe
    win.createMessageWindow()
    win.panel.showPage(tr('Messages'))
    ro = win.messagewindow.GetReadOnly()
    win.messagewindow.SetReadOnly(0)
    if clear:
        win.messagewindow.SetText('')
    win.messagewindow.AddText(text)
    if goto_end:
        win.messagewindow.GotoPos(win.messagewindow.GetTextLength())
    else:
        win.messagewindow.GotoPos(0)
    win.messagewindow.SetReadOnly(ro)
    
def get_entries(path):
    import pysvn
    client = pysvn.Client()
    entries = {}
    for line in client.status(path, False, ignore=True):
        entries[os.path.basename(line['path'])] = str(line['text_status'])
    return entries

#dialogs
################################################################
def get_path(path=''):
    if not path:
        path = os.getcwd()
    dlg = wx.DirDialog(Globals.mainframe, tr("Select directory:"), defaultPath=path, style=wx.DD_NEW_DIR_BUTTON)
    if dlg.ShowModal() == wx.ID_OK:
        dir = dlg.GetPath()
        dlg.Destroy()
        return dir
    
def is_versioned(path):
    try:
        import pysvn
    except:
        return False
    client = pysvn.Client()
    r = client.status(path, False)
    if len(r) > 0:
        return r[0]['is_versioned']
    else:
        return False

class CheckoutDialog(wx.Dialog):
    def __init__(self, title=tr('Checkout'), size=(450, -1)):
        wx.Dialog.__init__(self, Globals.mainframe, -1, title=title, size=size)
        
        self.pref = Globals.pref
        self.sizer = sizer = ui.VBox(namebinding='widget').create(self).auto_layout()
        box = sizer.add(ui.VGroup(tr('Repository')))
        box.add(ui.Label(tr('URL of repository:')))
        box.add(ui.ComboBox('', self.pref.svn_urls), name='url')
        box.add(ui.Label(tr('Checkout Directory')))
        box.add(ui.Dir(self.pref.svn_checkout_folder), name='dir')
        
        box = sizer.add(ui.VGroup(tr('Revision')))
        box1 = box.add(ui.HBox)
        box1.add(ui.Check(False, tr('Revision'), name='chk_revision')).bind('check', self.OnCheck)
        box1.add(ui.Text('', size=(80, -1)), name='revision').get_widget().Disable()
        
        sizer.add(ui.simple_buttons(), flag=wx.ALIGN_CENTER|wx.BOTTOM)
        sizer.bind('btnOk', 'click', self.OnOk)
        self.btnOk.SetDefault()
        
        sizer.auto_fit(1)
        
    def OnCheck(self, event):
        self.revision.Enable()
        
    def GetValue(self):
        return self.sizer.GetValue()
    
    def OnOk(self, event):
        url = self.url.GetValue()
        if url:
            try:
                self.pref.svn_urls.remove(url)
            except:
                pass
            self.pref.svn_urls.insert(0, url)
            del self.pref.svn_urls[30:]
            self.pref.save()
        path = self.dir.GetValue()
        if path:
            self.pref.svn_checkout_folder = path
            self.pref.save()
        event.Skip()


