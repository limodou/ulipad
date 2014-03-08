#   Programmer: limodou
#   E-mail:     limodou@gmail.com
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
#   $Id: FtpClass.py 2018 2007-03-16 03:14:55Z limodou $

__doc__ = 'ftp class'

import wx
from modules.Debug import error
from ftplib import FTP
#from ftp import FTP
import os.path
from modules.Mixin import Mixin
from modules import makemenu
from modules.Entry import MyTextEntry
import socket
from modules import ftplistparse
from modules import common
from modules import meide as ui
from modules import Globals

FTP_LINUX = 0
FTP_UNIX = 1

class Ftp(wx.Panel, Mixin):

    __mixinname__ = 'ftpclass'
    popmenulist = []
    imagelist = {}

    def __init__(self, parent, mainframe):
        self.initmixin()
        self.parent = parent
        self.mainframe = mainframe
        self.pref = self.mainframe.pref
        wx.Panel.__init__(self, parent, -1)

        self.alive = False
        self.running = False

        self.box = box = ui.VBox(namebinding='widget').create(self).auto_layout()
        box1 = box.add(ui.HBox)
        box1.add(ui.Label(tr('Sites:')))
        box1.add(ui.ComboBox("", self.mainframe.pref.ftp_sites), name='cmbSite').bind(wx.EVT_COMBOBOX, self.OnSiteChanged)
        box1.add(ui.Label(tr('Username:')))
        box1.add(ui.Text('', size=(100, -1)), name = 'txtUser')
        box1.add(ui.Label(tr('Password:')))
        box1.add(ui.Password('', size=(100, -1)), name = 'txtPassword')
        box1.add(ui.Button(tr('Connect')), name='btnConnect').bind('click', self.OnConnect)
        box1.add(ui.Button(tr('Disconnect')),name='btnDisconnect').bind('click', self.OnDisconnect)
    
        box.add(ui.List(columns=[
                (tr("Name"), 500, 'left'),
                (tr("Size"), 80, 'right'),
                (tr("Format"), 80, 'left'),
                ], style=wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL), name='list')

        box2 = box.add(ui.HBox)
        box2.add(ui.Label(tr('Encoding:')))
        box2.add(ui.ComboBox("Default", ['Default', 'UTF-8', 'Custom'], size=(100, -1)), name='txtEncoding')
        box2.add(ui.Label(tr('Remote path:')))
        box2.add(ui.ComboBox("", self.mainframe.pref.remote_paths), name='txtPath')
        box2.add(ui.Button(tr('Refresh')), name='btnRefresh').bind('click', self.OnRefresh)
        box2.add(ui.Button(tr('Set FTP site...')), name='btnSite').bind('click', self.OnSite)

        self.load()
        self.initlist()
        
        box.bind('btnConnect', wx.EVT_UPDATE_UI, self.OnUpdateUI)
        box.bind('btnDisconnect', wx.EVT_UPDATE_UI, self.OnUpdateUI)
        box.bind('btnRefresh', wx.EVT_UPDATE_UI, self.OnUpdateUI)
        box.bind('btnSite', wx.EVT_UPDATE_UI, self.OnUpdateUI)
        box.bind('list', wx.EVT_LIST_ITEM_ACTIVATED, self.OnEnter)

        #@add_menu menulist
        self.callplugin_once('add_menu', Ftp.popmenulist)
        #make popup menu
        if self.popmenulist:
            self.popmenu = makemenu.makepopmenu(self, self.popmenulist, self.imagelist)
            wx.EVT_LIST_ITEM_RIGHT_CLICK(self.list, self.list.GetId(), self.OnRClick)
            wx.EVT_RIGHT_UP(self.list, self.OnRClick)

    def canClose(self):
        self.mainframe.ftp = None
        return True

    def OnUpdateUI(self, event):
        eid = event.GetId()
        if eid == self.btnConnect.GetId():
            event.Enable(bool(not self.cmbSite.IsEmpty() and not self.alive and not self.running))
        elif eid == self.btnDisconnect.GetId():
            event.Enable(self.alive or self.running)
        elif eid == self.btnSite.GetId():
            event.Enable(not self.alive and not self.running)
        elif eid == self.btnRefresh.GetId():
            event.Enable(self.alive and not self.running)

    def OnSite(self, event):
        dlg = FtpManageDialog()
        dlg.ShowModal()
        self.load()

    def OnSiteChanged(self, event):
        self.pref.last_ftp_site = self.cmbSite.GetSelection()
        self.pref.save()
        self.load()

    def OnConnect(self, event):
        def connect(self):
            self.running = True

            site = self.pref.sites_info[self.pref.ftp_sites[self.cmbSite.GetSelection()]]
            self.ftp = FTP()

            #connect
            try:
                common.setmessage(self.mainframe, tr('Connecting to %s (%s:%s)...') % (site['name'],site['ip'], site['port']))
                self.ftp.connect(site['ip'], site['port'])
                flag, user, password = self.getuserpassword(self.cmbSite.GetSelection(), self.txtUser.GetValue(), self.txtPassword.GetValue())
                if not flag:
                    common.setmessage(self.mainframe, tr('Connection canceled'))
                    self.ftp = None
                    self.alive = False
                    self.running = False
                    return
                common.setmessage(self.mainframe, tr('Logging in...'))
                self.ftp.login(user, password)
            except socket.error, msg:
                error.traceback()
                common.showerror(self, msg[1])
                self.ftp = None
                self.running = False
                return
            except Exception, msg:
                error.traceback()
                common.showerror(self, msg)
                self.ftp = None
                self.running = False
                return

            try:
                self.ftp.set_pasv(site['pasv'])
            except Exception, msg:
                error.traceback()
                common.showerror(self, msg)

            self.getcurrentpath()
            self.refresh(self.getpath(self.txtPath.GetValue()))
            self.alive = True
            self.running = False

        #thread.start_new_thread(connect, (self,))
        connect(self)

    def OnDisconnect(self, event):
        def disconnect(self):
            try:
                if self.ftp and self.alive:
                    if self.running:
                        self.ftp.abort()
                    self.ftp.quit()
            except Exception, msg:
                error.traceback()
                common.showerror(self, msg)

            self.alive = False
            self.running = False
            self.ftp = None
            common.setmessage(self.mainframe, tr('Disconnected'))
            self.list.DeleteAllItems()

        #thread.start_new_thread(disconnect, (self,))
        disconnect(self)

    def OnEnter(self, event):
        common.setmessage(self.mainframe, tr('Retrieving the file...'))
        index = self.list.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        data = self.list.GetItemData(index)
        if data == 0:   #is directory
            self.refresh(self.getpath(self.list.GetItemText(index)))
        elif data == 2: #is parent denote
            self.refresh('..')
        elif data == 1: #is a file
            filename = "ftp(%d):%s" % (self.cmbSite.GetSelection(), self.getpath(os.path.join(self.curpath, self.list.GetItemText(index))))
            encoding = self.txtEncoding.GetValue()
            if encoding == 'Custom':
                dlg = MyTextEntry(self, tr("Encoding Input"), tr('Input an encoding:'), '')
                answer = dlg.ShowModal()
                if answer == wx.ID_OK:
                    encoding = dlg.GetValue()
            if encoding == 'Default':
                encoding = ''
            self.mainframe.editctrl.new(filename, encoding)

    def OnRefresh(self, event):
        common.setmessage(self.mainframe, tr('Refreshing the current path...'))
        self.refresh()
        text = self.txtPath.GetValue()
        if text in self.pref.remote_paths:
            self.pref.remote_paths.remove(text)
            self.pref.remote_paths.insert(0, text)
        else:
            self.pref.remote_paths.insert(0, text)
        while len(self.pref.remote_paths) > self.pref.max_number:
            del self.pref.remote_paths[-1]

        self.pref.save()

        self.txtPath.Clear()
        for s in self.pref.remote_paths:
            self.txtPath.Append(s)

        self.txtPath.SetValue(text)
        self.txtPath.SetMark(0, len(text))

    def OnRClick(self, event):
        if self.alive:
            self.list.PopupMenu(self.popmenu, event.GetPosition())

    def load(self):
        self.cmbSite.Clear()

        if self.pref.last_ftp_site >= len(self.pref.ftp_sites):
            self.pref.last_ftp_site = 0
            self.pref.save()

        if len(self.pref.ftp_sites) > 0:
            for name in self.pref.ftp_sites:
                self.cmbSite.Append(name)
            self.cmbSite.SetSelection(self.pref.last_ftp_site)
            site = self.pref.sites_info[self.pref.ftp_sites[self.pref.last_ftp_site]]
            self.txtUser.SetValue(site['user'])
            self.txtPassword.SetValue(site['password'])
            self.txtPath.SetValue(site['path'])

            self.txtUser.Enable(True)
            self.txtPassword.Enable(True)
            self.txtPath.Enable(True)
            self.cmbSite.Enable(True)
            self.btnRefresh.Enable(True)
            self.txtEncoding.Enable(True)
        else:
            self.txtUser.SetValue('')
            self.txtPassword.SetValue('')
            self.txtPath.SetValue('')
            self.txtEncoding.SetValue('Default')
            self.txtUser.Enable(False)
            self.txtPassword.Enable(False)
            self.txtPath.Enable(False)
            self.cmbSite.Enable(False)
            self.btnRefresh.Enable(False)
            self.txtEncoding.Enable(False)

    def getuserpassword(self, siteno, user=None, password=None):
        site = self.pref.sites_info[self.pref.ftp_sites[siteno]]
        if user is None:
            user = site['user']
        if password is None:
            password = site['password']

        if not user or not password:
            dlg = UserDialog(self, site['name'], user, password)
            answer = dlg.ShowModal()
            v = None
            if answer == wx.ID_OK:
                v = dlg.GetValue()
                user, password = v['txtUser'], v['txtPassword']
            dlg.Destroy()
            if v:
                return True, user, password
            else:
                return False, '', ''
        else:
            return True, user, password

    def refresh(self, path=''):
        if not path:
            path = self.txtPath.GetValue()
        try:
            common.setmessage(self.mainframe, tr('Changing the current directory...'))
            self.ftp.cwd(common.encode_string(path))
            self.data = []
            self.ftp.retrlines('LIST', self.receivedData)
            self.curpath = common.decode_string(self.ftp.pwd())
            self.txtPath.SetValue(self.curpath)
            self.loadFile(self.data)
        except Exception, msg:
            common.showerror(self, msg)
            error.traceback()
            return

        return True

    def initlist(self):
        #create imagelist
        imagelist = self.mainframe.ftp_imagelist
        _imagel = wx.ImageList(16, 16)
        _imagel.Add(common.getpngimage(imagelist['close']))
        _imagel.Add(common.getpngimage(imagelist['document']))
        _imagel.Add(common.getpngimage(imagelist['parentfold']))
        self.images = _imagel

        self.list.SetImageList(self.images, wx.IMAGE_LIST_SMALL)

    def receivedData(self, data):
        self.data.append(data)

    def loadFile(self, lines, type=FTP_LINUX, filter=None):
        self.list.DeleteAllItems()
        if self.curpath != '/':
            self.list.InsertImageStringItem(0, tr('Parent folder'), 2)
            self.list.SetItemData(0, 2)
            flag = 1
        else:
            flag = 0

        dirs, files = ftplistparse.ftplistparse(lines, Unicode=True, callback=filter)

        items = dirs + files
        for i, line in enumerate(items):
            filename, size, dir, image = line
            self.list.InsertImageStringItem(i + flag, filename, image)
            self.list.SetStringItem(i + flag, 1, str(size))
            self.list.SetStringItem(i + flag, 2, dir)
            self.list.SetItemData(i + flag, image)

    def getcurrentpath(self):
        #current path
        try:
            self.curpath = common.encode_string(self.ftp.pwd())
        except Exception, msg:
            common.showerror(self, msg)
            error.traceback()
            self.curpath = ''

    def getpath(self, path):
        return path.replace('\\', '/')

    def newfile(self):
        filename = ''
        dlg = MyTextEntry(self, tr("Filename Input"), tr('Input a new filename:'), '')
        answer = dlg.ShowModal()
        if answer == wx.ID_OK:
            filename = dlg.GetValue()
            if not filename:
                return
            #check if the new name has existed
            index = self.list.FindItem(-1, filename)
            if index > -1:
                common.showerror(self, tr('The filename already exists.\nPlease input another one.'))
                return
            from StringIO import StringIO
            f = StringIO('')
            try:
                self.ftp.storbinary('STOR %s' % common.decode_string(filename), f)
            except Exception, msg:
                error.traceback()
                common.showerror(self, msg)
                return

            if self.refresh(self.curpath):
                index = self.list.FindItem(-1, filename)
                self.list.SetItemState(index, wx.LIST_STATE_SELECTED, wx.LIST_MASK_STATE)

    def newdir(self):
        dirname = ''
        dlg = MyTextEntry(self, tr("Directory Input"), tr('Input a new directory:'), '')
        answer = dlg.ShowModal()
        if answer == wx.ID_OK:
            dirname = dlg.GetValue()
            if not dirname:
                return
            #check if the new name has existed
            index = self.list.FindItem(-1, dirname)
            if index > -1:
                common.showerror(self, tr('The directory already exists.\nPlease input another one.'))
                return
            try:
                self.ftp.mkd(common.decode_string(dirname))
            except Exception, msg:
                error.traceback()
                common.showerror(self, msg)
                return

            if self.refresh(self.curpath):
                index = self.list.FindItem(-1, dirname)
                self.list.SetItemState(index, wx.LIST_STATE_SELECTED, wx.LIST_MASK_STATE)

    def delete(self):
        index = self.list.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        if index >= 0:
            flag = self.list.GetItemData(index)
            if flag == 2:
                return
            pathname = self.list.GetItemText(index)
            dlg = wx.MessageDialog(self, tr("Do you want to delete %s?") % pathname, tr("Delete"), wx.YES_NO | wx.ICON_QUESTION)
            answer = dlg.ShowModal()
            if answer == wx.ID_YES:
                if flag == 0:   #dir
                    try:
                        self.ftp.rmd(common.decode_string(pathname))
                    except Exception, msg:
                        error.traceback()
                        common.showerror(self, msg)
                        return
                elif flag == 1: #file
                    try:
                        self.ftp.delete(common.decode_string(pathname))
                    except Exception, msg:
                        error.traceback()
                        common.showerror(self, msg)
                        return
                self.refresh(self.curpath)

    def rename(self):
        index = self.list.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        if index >= 0:
            pathname = self.list.GetItemText(index)
            dlg = MyTextEntry(self, tr("Name Input"), tr('Input a new name:'), '')
            answer = dlg.ShowModal()
            if answer == wx.ID_OK:
                newpath = dlg.GetValue()
                if not newpath:
                    return
                flag = self.list.GetItemData(index)
                if flag != 2:   #dir
                    try:
                        self.ftp.rename(common.decode_string(pathname), common.decode_string(newpath))
                    except Exception, msg:
                        error.traceback()
                        common.showerror(self, msg)
                        return
                if self.refresh(self.curpath):
                    index = self.list.FindItem(-1, newpath)
                    self.list.SetItemState(index, wx.LIST_STATE_SELECTED, wx.LIST_MASK_STATE)

    def upload(self):
        dlg = UploadFileEntry(self)
        answer = dlg.ShowModal()
        if answer == wx.ID_OK:
            filename, newfile, bin = dlg.GetValue()
            if not filename:
                common.showerror(self, tr("The filename can't be empty."))
                return
            if not newfile:
                newfile = os.path.basename(filename)
            #check if the new name has existed
            index = self.list.FindItem(-1, newfile)
            if index > -1:
                dlg = wx.MessageDialog(self, tr("The filename already exists. Do you want to overwrite it?"), tr("Upload File"), wx.YES_NO | wx.ICON_QUESTION)
                answer = dlg.ShowModal()
                if answer == wx.ID_NO:
                    return

            common.setmessage(self.mainframe, tr('Uploading the file...'))
#           if not self.setBin(bin):
#               return
            from StringIO import StringIO
            try:
                if bin:
                    f = StringIO(file(filename, 'rb').read())
                    self.ftp.storbinary('STOR %s' % common.decode_string(newfile), f)
                else:
                    f = StringIO(file(filename, 'r').read())
                    self.ftp.storlines('STOR %s' % common.decode_string(newfile), f)
            except Exception, msg:
                error.traceback()
                common.showerror(self, msg)
                return

            self.setBin(True)
            if self.refresh(self.curpath):
                index = self.list.FindItem(-1, newfile)
                self.list.SetItemState(index, wx.LIST_STATE_SELECTED, wx.LIST_MASK_STATE)
            common.setmessage(self.mainframe, tr('Uploading finished'))

    def download(self):
        index = self.list.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        if index >= 0:
            flag = self.list.GetItemData(index)
            if flag == 2:
                return
            filename = self.list.GetItemText(index)
            dlg = DownloadFileEntry(self, filename)
            answer = dlg.ShowModal()
            if answer == wx.ID_OK:
                newfile, bin = dlg.GetValue()
                if not newfile:
                    common.showerror(self, tr("The filename can't be empty."))
                    return
            else:
                return

            common.setmessage(self.mainframe, tr('Downloading the file...'))
            try:
                try:
                    if bin:
                        f = file(newfile, 'wb')
                        def getdata(d, f=f):
                            f.write(d)
                        self.ftp.retrbinary("RETR %s" % common.decode_string(filename), getdata)
                    else:
                        f = file(newfile, 'w')
                        def getdata(d, f=f):
                            f.write(d+"\n")
                        self.ftp.retrlines("RETR %s" % common.decode_string(filename), getdata)
                except Exception, msg:
                    error.traceback()
                    common.showerror(self, msg)
                    return
            finally:
                f.close()
            common.setmessage(self.mainframe, tr('Downloading finished'))

    def setBin(self, bin):
        try:
            if bin:
                self.ftp.voidcmd('TYPE I')
            else:
                self.ftp.voidcmd('TYPE A')
        except Exception, msg:
            common.showerror(self, msg)
            return False
        return True

def getuserpassword(mainframe, siteno):
    site = mainframe.pref.sites_info[mainframe.pref.ftp_sites[siteno]]
    user = site['user']
    password = site['password']

    if not user or not password:
        dlg = UserDialog(mainframe, site['name'], user, password)
        answer = dlg.ShowModal()
        v = None
        if answer == wx.ID_OK:
            v = dlg.GetValue()
            user, password = v['txtUser'], v['txtPassword']
        dlg.Destroy()
        if v:
            return True, user, password
        else:
            return False, '', ''
    else:
        return True, user, password

def readfile(mainframe, filename, siteno, user=None, password=None):
    if siteno >= len(mainframe.pref.ftp_sites):
        common.showerror(mainframe, tr("Can't find the FTP site."))
        return

    site = mainframe.pref.sites_info[mainframe.pref.ftp_sites[siteno]]
    if not user:
        user = site['user']
    if not password:
        password = site['password']

    flag, user, password = getuserpassword(mainframe, siteno)
    if not flag:
        common.setmessage(mainframe, tr('Connection canceled'))
        return

    ftp = FTP()
    try:
        ftp.connect(site['ip'], site['port'])
        ftp.login(user, password)
        ftp.set_pasv(site['pasv'])
        data = []
        def getdata(d, data=data):
            data.append(d)
        ftp.retrbinary("RETR %s" % common.decode_string(filename), getdata)
        ftp.quit()
        ftp.close()
        text = ''.join(data)
        return text
    except Exception, msg:
        error.traceback()
        common.showerror(mainframe, msg)

def writefile(mainframe, filename, siteno, text, user=None, password=None):
    if siteno >= len(mainframe.pref.ftp_sites):
        common.showerror(mainframe, tr("Can't find the FTP site."))
        return

    site = mainframe.pref.sites_info[mainframe.pref.ftp_sites[siteno]]
    if not user:
        user = site['user']
    if not password:
        password = site['password']

    flag, user, password = getuserpassword(mainframe, siteno)
    if not flag:
        common.setmessage(mainframe, tr('Connection canceled'))
        return

    ftp = FTP()
    #connect
    try:
        ftp.connect(site['ip'], site['port'])
        ftp.login(user, password)
        ftp.set_pasv(site['pasv'])
        import StringIO
        f = StringIO.StringIO(text)
        ftp.storbinary("STOR %s" % common.decode_string(filename), f)
        ftp.quit()
        ftp.close()
        return True
    except Exception, msg:
        error.traceback()
        common.showerror(mainframe, msg)

class FtpManageDialog(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(self, Globals.mainframe, -1, title=tr('FTP Site Manager'), size=(400, 300))
        self.init()

    def init(self):
        mainframe = Globals.mainframe
        self.pref = Globals.pref

        self.sizer = box = ui.Grid(growablecol=1, namebinding='widget').create(self).auto_layout()
        box1 = box.add((0, 0), ui.VBox)
        box1.add(ui.Label(tr('FTP sites:')))
        box1.add(ui.ListBox, name='listbox').bind(wx.EVT_LISTBOX, self.OnFtpSelected)
        box1.add(ui.Check(True, tr('Passive FTP')), name='chkPass')
        box2 = box.add((0, 1), ui.SimpleGrid)
        box2.add(tr('Site name:'), ui.Text, name='txtName')
        box2.add(tr('Host IP:'), ui.Text, name='txtHost')
        box2.add(tr('Port:'), ui.IntSpin(21, min=0, max=65535), name='txtPort')
        box2.add(tr('Username:'), ui.Text, name='txtUsername')
        box2.add(tr('Password:'), ui.Password, name='txtPassword')
        box2.add(tr('Remote path:'), ui.Text, name='txtPath')
        box3 = box.add((0, 2), ui.VBox)
        box3.add(ui.Button(tr('Add')), name='btnAdd').bind('click', self.OnAdd)
        box3.add(ui.Button(tr('Delete')), name='btnDelete').bind('click', self.OnDelete)
        box3.add(ui.Button(tr('Update')), name='btnUpdate').bind('click', self.OnUpdate)
        box3.add(ui.Button(tr('Close'), id=wx.ID_CANCEL, name='btnClose')).bind(wx.EVT_CLOSE, self.OnClose).bind('click', self.OnClose)
        
        self.lastindex = self.pref.last_ftp_site
        self.load()

        box.bind('btnDelete', wx.EVT_UPDATE_UI, self.OnUpdateUI)
        box.bind('btnUpdate', wx.EVT_UPDATE_UI, self.OnUpdateUI)
        box.bind('btnAdd', wx.EVT_UPDATE_UI, self.OnUpdateUI)
        
        box.auto_fit(2)
        
    def OnUpdateUI(self, event):
        eid = event.GetId()
        selected = len(self.listbox.GetSelections()) > 0
        if eid == self.btnDelete.GetId():
            event.Enable(selected)
        elif eid == self.btnUpdate.GetId():
            event.Enable(selected and len(self.txtName.GetValue()) > 0 and len(self.txtHost.GetValue()) > 0)
        elif eid == self.btnAdd.GetId():
            event.Enable(len(self.txtName.GetValue()) > 0 and len(self.txtHost.GetValue()) > 0)

    def OnClose(self, event):
        self.Destroy()

    def OnAdd(self, event):
        site = self.getSite()
        if site['name'] in self.pref.ftp_sites:
            wx.MessageDialog(self, tr("The FTP site already exists. Choose a different name."), tr("Error"), wx.OK | wx.ICON_EXCLAMATION).ShowModal()
        else:
            self.pref.ftp_sites.append(site['name'])
            self.pref.sites_info[site['name']] = site
            self.pref.save()
            self.lastindex = len(self.pref.ftp_sites) - 1
            self.load()

    def OnFtpSelected(self, event):
        self.lastindex = event.GetSelection()
        self.setSite(self.lastindex)

    def OnUpdate(self, event):
        site = self.getSite()
        if site['name'] in self.pref.ftp_sites:
            self.pref.sites_info[site['name']] = site
            self.pref.save()
            self.load()
        else:
            self.OnAdd(event)

    def OnDelete(self, event):
        index = self.listbox.GetSelection()
        name = self.listbox.GetString(index)
        self.listbox.Delete(index)
        self.pref.ftp_sites.remove(name)
        del self.pref.sites_info[name]
        self.pref.save()
        self.load()

    def load(self):
        self.listbox.Clear()
        self.listbox.InsertItems(self.pref.ftp_sites, 0)
        if self.lastindex >= len(self.pref.ftp_sites):
            self.lastindex = len(self.pref.ftp_sites) - 1
        if len(self.pref.ftp_sites) > 0:
            self.listbox.SetSelection(self.lastindex)
            self.setSite(self.lastindex)
        else:
            self.setSite(-1)

    def getSite(self):
        site = {}
        site['name'] = self.txtName.GetValue()
        site['ip'] = self.txtHost.GetValue()
        site['port'] = self.txtPort.GetValue()
        site['user'] = self.txtUsername.GetValue()
        site['password'] = self.txtPassword.GetValue()
        site['path'] = self.txtPath.GetValue()
        site['pasv'] = self.chkPass.GetValue()

        return site

    def setSite(self, index):
        if index > -1:
            site = self.pref.sites_info[self.pref.ftp_sites[index]]
            self.txtName.SetValue(site['name'])
            self.txtHost.SetValue(site['ip'])
            self.txtPort.SetValue(site['port'])
            self.txtUsername.SetValue(site['user'])
            self.txtPassword.SetValue(site['password'])
            self.txtPath.SetValue(site['path'])
            self.chkPass.SetValue(site['pasv'])
        else:
            self.txtName.SetValue('')
            self.txtHost.SetValue('')
            self.txtPort.SetValue(21)
            self.txtUsername.SetValue('')
            self.txtPassword.SetValue('')
            self.txtPath.SetValue('')
            self.chkPass.SetValue(True)


class UserDialog(wx.Dialog):
    def __init__(self, parent, ftpname, user, password):
        wx.Dialog.__init__(self, parent, -1, style = wx.DEFAULT_DIALOG_STYLE, title = tr("FTP site: %s") % ftpname,size=(200, 50))

        self.sizer = box = ui.SimpleGrid(namebinding='widget').create(self).auto_layout()
        box.add(tr('Username:'), ui.Text(user), name='txtUser')
        box.add(tr('Password:'), ui.Password(password), name='txtPassword')

        box.add('', ui.simple_buttons(), flag=wx.ALIGN_CENTER|wx.BOTTOM, span=True)
        self.btnOk.SetDefault()
        
        box.auto_fit(2)
        
        box.bind('btnOk', wx.EVT_UPDATE_UI, self.OnUpdateUI)

    def GetValue(self):
        return self.sizer.GetValue()

    def OnUpdateUI(self, event):
        eid = event.GetId()
        if eid == self.btnOk.GetId():
            event.Enable(len(self.txtUser.GetValue()) > 0)

class UploadFileEntry(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, style = wx.DEFAULT_DIALOG_STYLE, title = tr('File Upload Client'))

        box = wx.BoxSizer(wx.VERTICAL)
        t = wx.StaticText(self, -1, label=tr('Upload a file:'))
        box.Add(t, 0, wx.ALIGN_LEFT|wx.ALL, 3)
        box1 = wx.BoxSizer(wx.HORIZONTAL)
        self.text = wx.TextCtrl(self, -1, '', size=(200, 20))
        self.text.SetSelection(-1, -1)
        box1.Add(self.text, 1, wx.EXPAND|wx.ALL, 3)
        self.ID_BROWSER = wx.NewId()
        self.btnBrowser = wx.Button(self, self.ID_BROWSER, tr("Browser"), size=(50, -1))
        box1.Add(self.btnBrowser, 0, wx.ALL, 3)
        box.Add(box1, 1, wx.EXPAND, 5)

        t = wx.StaticText(self, -1, label=tr('New filename:'))
        box.Add(t, 0, wx.ALIGN_LEFT|wx.ALL, 3)
        self.txtNew = wx.TextCtrl(self, -1, '', size=(200, 20))
        box.Add(self.txtNew, 0, wx.ALIGN_LEFT|wx.ALL, 3)

        self.chkBin = wx.CheckBox(self, -1, tr('Use binary transfer mode'))
        box.Add(self.chkBin, 0, wx.LEFT|wx.BOTTOM, 5)
        self.chkBin.SetValue(True)

        box2 = wx.BoxSizer(wx.HORIZONTAL)
        btnOK = wx.Button(self, wx.ID_OK, tr("OK"), size=(60, -1))
        btnOK.SetDefault()
        box2.Add(btnOK, 0, wx.ALIGN_RIGHT|wx.RIGHT, 5)
        btnCancel = wx.Button(self, wx.ID_CANCEL, tr("Cancel"), size=(60, -1))
        box2.Add(btnCancel, 0, wx.ALIGN_LEFT|wx.LEFT, 5)
        box.Add(box2, 0, wx.ALIGN_CENTER|wx.BOTTOM, 5)

        wx.EVT_BUTTON(self.btnBrowser, self.ID_BROWSER, self.OnBrowser)

        self.SetSizer(box)
        self.SetAutoLayout(True)
        box.Fit(self)

    def GetValue(self):
        return self.text.GetValue(), self.txtNew.GetValue(), self.chkBin.GetValue()

    def OnBrowser(self, event):
        dlg = wx.FileDialog(self, tr("File List"), "", "", tr("All Files (*.*)|*.*"), wx.OPEN|wx.HIDE_READONLY)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            self.text.SetValue(filename)
            if not self.txtNew.GetValue():
                self.txtNew.SetValue(os.path.basename(filename))

class DownloadFileEntry(wx.Dialog):
    def __init__(self, parent, filename=''):
        wx.Dialog.__init__(self, parent, -1, style = wx.DEFAULT_DIALOG_STYLE, title = tr('File Download Client'))

        self.filename = filename

        box = wx.BoxSizer(wx.VERTICAL)
        t = wx.StaticText(self, -1, label=tr('Download a file:'))
        box.Add(t, 0, wx.ALIGN_LEFT|wx.ALL, 3)
        box1 = wx.BoxSizer(wx.HORIZONTAL)
        self.text = wx.TextCtrl(self, -1, self.filename, size=(200, 20))
        self.text.SetSelection(-1, -1)
        box1.Add(self.text, 1, wx.ALIGN_LEFT|wx.ALL, 3)
        self.ID_BROWSER = wx.NewId()
        self.btnBrowser = wx.Button(self, self.ID_BROWSER, tr("Browser"), size=(50, -1))
        box1.Add(self.btnBrowser, 0, wx.ALL, 3)
        box.Add(box1, 1, wx.EXPAND, 5)

        self.chkBin = wx.CheckBox(self, -1, tr('Use binary transfer mode'))
        box.Add(self.chkBin, 0, wx.ALL, 5)
        self.chkBin.SetValue(True)

        box2 = wx.BoxSizer(wx.HORIZONTAL)
        btnOK = wx.Button(self, wx.ID_OK, tr("OK"), size=(60, -1))
        btnOK.SetDefault()
        box2.Add(btnOK, 0, wx.ALIGN_RIGHT|wx.RIGHT, 5)
        btnCancel = wx.Button(self, wx.ID_CANCEL, tr("Cancel"), size=(60, -1))
        box2.Add(btnCancel, 0, wx.ALIGN_LEFT|wx.LEFT, 5)
        box.Add(box2, 0, wx.ALIGN_CENTER|wx.BOTTOM, 5)

        wx.EVT_BUTTON(self.btnBrowser, self.ID_BROWSER, self.OnBrowser)

        self.SetSizer(box)
        self.SetAutoLayout(True)
        box.Fit(self)

    def GetValue(self):
        return self.text.GetValue(), self.chkBin.GetValue()

    def OnBrowser(self, event):
        dlg = wx.FileDialog(self, tr("File List"), "", self.filename, tr("All Files (*.*)|*.*"), wx.SAVE|wx.HIDE_READONLY)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            self.text.SetValue(filename)
