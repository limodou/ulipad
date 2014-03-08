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
from modules import Globals
import Server
import Client
from modules import common
from modules.Debug import error
from modules import Mixin
from modules import CheckList
from wx.lib.splitter import MultiSplitterWindow
from modules import makemenu
import CommandRecord

class ConcurrentWindow(wx.Panel, Mixin.Mixin):
    __mixinname__ = 'concurrent'
    concurrent_id = 0

    def __init__(self, parent):
        self.initmixin()

        wx.Panel.__init__(self, parent, -1)

        self.mainframe = Globals.mainframe
        self.pref = self.mainframe.pref

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)

        if not self.pref.pairprog_username:
            self.pref.pairprog_username = self.pref.personal_username

        sizer1.Add(wx.StaticText(self, -1, tr("Name") + ':'), 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 2)
        self.txtName = wx.TextCtrl(self, -1, self.pref.pairprog_username, size=(100, -1))
        sizer1.Add(self.txtName, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 2)
        sizer1.Add(wx.StaticText(self, -1, tr("Host") + ':'), 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 2)
        self.txtIP = wx.TextCtrl(self, -1, self.pref.pairprog_host, size=(150, -1))
        sizer1.Add(self.txtIP, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 2)
        sizer1.Add(wx.StaticText(self, -1, tr("Port") + ':'), 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 2)
        self.txtPort = wx.SpinCtrl(self, min=1, max=65536, value=str(self.pref.pairprog_port))
        sizer1.Add(self.txtPort, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 2)
        self.btnStart = wx.Button(self, -1, tr("Start Server"))
        sizer1.Add(self.btnStart, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 2)
        self.btnConnect = wx.Button(self, -1, tr("Connect Server"))
        sizer1.Add(self.btnConnect, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 2)

        sizer.Add(sizer1, 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 2)

        self.splitter = MultiSplitterWindow(self, -1)

        userpanel = UserPanel(self.splitter)
        self.splitter.AppendWindow(userpanel, 200)
        self.userlist = userpanel.list

        filelistpanel = FileListPanel(self.splitter)
        self.splitter.AppendWindow(filelistpanel, 150)
        self.filelist = filelistpanel.list

        chatpanel = ChatPanel(self.splitter)
        self.splitter.AppendWindow(chatpanel)
        self.chat = chatpanel.chat
        self.chatroom = chatpanel.chatroom
        self.btnSend = chatpanel.btnSend
        self.btnClear = chatpanel.btnClear
        self.btnSave = chatpanel.btnSave
        self.splitter.SetMinimumPaneSize(150)
        self.splitter.SetOrientation(wx.HORIZONTAL)

        sizer.Add(self.splitter, 1, wx.EXPAND|wx.ALL, 2)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        self.btnStart.Bind(wx.EVT_BUTTON, self.OnStart)
        self.btnConnect.Bind(wx.EVT_BUTTON, self.OnConnect)
        self.btnSend.Bind(wx.EVT_BUTTON, self.OnSend)
        self.btnClear.Bind(wx.EVT_BUTTON, self.OnClear)
        self.btnSave.Bind(wx.EVT_BUTTON, self.OnSave)
        self.filelist.Bind(wx.EVT_RIGHT_DOWN, self.OnFilelistRClick)
        self.userlist.Bind(wx.EVT_RIGHT_DOWN, self.OnUserlistRClick)
        self.chat.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

        self.status = ''
        self.server = None
        self.client = None
        self.servercommands = ServerCommands(self)
        self.clientcommands = ClientCommands(self)
        self.users = {}
        self.files = {}
        self.cmdrecorder = CommandRecord.CommandRecord()
        self.filelistpopmenus = None
        self.userlistpopmenus = None


    def __get_me(self):
        return self.txtName.GetValue()

    me = property(__get_me)

    def OnStart(self, event=None):
        if not self.status:
            if not self.me or self.me == '*':
                common.showerror(self, tr("Username should not be empty or '*'"))
                self.txtName.SetFocus()
                return

            ip = self.txtIP.GetValue()
            if not ip:
                common.showerror(self, tr("Host address cannot be empty!"))
                self.txtIP.SetFocus()
                return
            port = int(self.txtPort.GetValue())
            self.pref.pairprog_host = ip
            self.pref.pairprog_port = port
            self.pref.pairprog_username = self.me
            self.pref.save()
            try:
                self.server = Server.start_server(ip, port, self.servercommands)
                if self.server:
                    self.AddUser(self.me, manager=True)
                    self.change_status('startserver')
                    self.callplugin('start', self, 'server')
            except:
                common.warn(tr("Start server error!"))
                error.traceback()
        else:
            self.server.shut_down()
            self.server = None
            self.change_status('stopserver')
            self.callplugin('stop', self, 'server')

    def OnConnect(self, event=None):
        if not self.status:
            if not self.me or self.me == '*':
                common.showerror(self, tr("Username should not be empty or '*'"))
                self.txtName.SetFocus()
                return

            ip = self.txtIP.GetValue()
            if not ip:
                common.showerror(self, tr("Host address cannot be empty!"))
                self.txtIP.SetFocus()
                return
            port = int(self.txtPort.GetValue())
            self.pref.pairprog_host = ip
            self.pref.pairprog_port = port
            self.pref.pairprog_username = self.me
            self.pref.save()
#            try:
            self.client = Client.start_client(ip, port, self.clientcommands)
            if self.client:
                self.client.call('join', self.me)

                self.change_status('connectserver')
                self.callplugin('start', self, 'client')
#            except:
#                common.warn(tr("Connect to server error!"))
#                error.traceback()
        else:
            self.client.close()
            self.client = None
            self.change_status('disconnectserver')
            self.callplugin('stop', self, 'client')

    def OnSend(self, event=None):
        message = self.chat.GetValue()
        self.chat.SetValue('')
        if message:
            self.put_message(self.me, message)
            if self.status == 'startserver':    #server
                self.server.broadcast('message', self.me, message)
            else:
                self.client.call('message', self.me, message)

    def OnClear(self, event=None):
        self.chatroom.SetReadOnly(0)
        self.chatroom.SetText('')
        self.chatroom.SetReadOnly(1)

    def OnClose(self, win):
        if self.status == 'startserver':
            self.OnStart()
        elif self.status == 'connectserver':
            self.OnConnect()

    def OnSave(self, event=None):
        filename = None
        dlg = wx.FileDialog(self, tr("Save File"), self.pref.last_dir, '', 'Text file|*.txt', wx.SAVE|wx.OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            dlg.Destroy()
        if filename:
            try:
                file(filename, 'w').write(self.chatroom.GetText().encode('utf-8'))
            except:
                common.warn(tr("There is error as saving the file"))
            else:
                common.note(tr("Finished!"))

    def OnFilelistRClick(self, event):
        pt = event.GetPosition();
        item, flags = self.filelist.HitTest(pt)
        if item > -1:
            self.filelist.Select(item)
        if self.status == 'startserver':
            popmenulist = [ (None,
                [
                    (10, 'IDPM_ADD', tr('Add Current Document'), wx.ITEM_NORMAL, 'OnAddDocument', ''),
                    (20, 'IDPM_REMOVE', tr('Remove Document'), wx.ITEM_NORMAL, 'OnRemoveDocument', ''),
                ]),
            ]
        else:
            popmenulist = [ (None,
                [
                    (10, 'IDPM_REGET', tr('Reget Document'), wx.ITEM_NORMAL, 'OnRegetDocument', ''),
                ]),
            ]

        other_menus = []
        if self.filelistpopmenus:
            self.filelistpopmenus.Destroy()
            self.filelistpopmenus = None
        self.callplugin('other_filelist_popup_menu', self, other_menus)
        import copy
        if other_menus:
            pop_menus = copy.deepcopy(popmenulist + other_menus)
        else:
            pop_menus = copy.deepcopy(popmenulist)
        self.filelistpopmenus = makemenu.makepopmenu(self, pop_menus)

        self.filelist.PopupMenu(self.filelistpopmenus)

    def OnUserlistRClick(self, event):
        pt = event.GetPosition();
        item, flags = self.userlist.HitTest(pt)
        if item > -1:
            self.userlist.Select(item)
        popmenulist = [ (None,
            [
                (10, 'IDPM_KICK', tr('Kick User'), wx.ITEM_NORMAL, 'OnKickUser', ''),
            ]),
        ]

        other_menus = []
        if self.userlistpopmenus:
            self.userlistpopmenus.Destroy()
            self.userlistpopmenus = None
        self.callplugin('other_userlist_popup_menu', self, other_menus)
        import copy
        if other_menus:
            pop_menus = copy.deepcopy(popmenulist + other_menus)
        else:
            pop_menus = copy.deepcopy(popmenulist)
        self.userlistpopmenus = makemenu.makepopmenu(self, pop_menus)

        self.filelist.PopupMenu(self.userlistpopmenus)

    def OnAddDocument(self, event):
        document = self.mainframe.editctrl.getCurDoc()
        if not self.has_document(document):
            filename = document.getShortFilename()
            index = self.filelist.addline([filename])
            ConcurrentWindow.concurrent_id += 1
            _id = ConcurrentWindow.concurrent_id
            self.filelist.SetItemData(index, _id)
            self.files[_id] = document
            self.cmdrecorder.add_document(_id, document)
            def f(self):
                self.server.broadcast('update_files', self.__get_filelist())
                self.server.broadcast('editcmd', 'openfile', (_id, filename, document.getRawText()))
                self.server.broadcast('editcmd', 'setlex', (_id, document.languagename))
                self.server.broadcast('message', '*', tr("%(user)s selects %(filename)s") % {'user':self.me, 'filename':filename})
            wx.CallAfter(f, self)

    def OnRemoveDocument(self, event=None):
        index = self.filelist.GetFirstSelected()
        if index > -1:
            filename = self.filelist.GetItem(index, 0).GetText()
            _id = self.filelist.GetItemData(index)
            del self.files[_id]
            self.filelist.DeleteItem(index)
            self.cmdrecorder.remove_document(_id)
            self.server.broadcast('forgivefile', _id)
            self.server.broadcast('message', '*', tr('%(user)s discards %(filename)s') % {'user':self.me, 'filename':filename})
        else:
            if self.filelist.GetItemCount() > 0:
                common.showerror(self, tr("You should select one item first"))
            else:
                common.showerror(self, tr("No item exists"))

    def OnRegetDocument(self, event=None):
        index = self.filelist.GetFirstSelected()
        if index > -1:
            filename = self.filelist.GetItem(index, 0).GetText()
            _id = self.filelist.GetItemData(index)
            del self.files[_id]
            self.cmdrecorder.remove_document(_id)
            self.client.call('regetfile', _id, filename)
        else:
            if self.filelist.GetItemCount() > 0:
                common.showerror(self, tr("You should select one item first"))
            else:
                common.showerror(self, tr("No item exists"))

    def OnKickUser(self, event):
        index = self.userlist.GetFirstSelected()
        if index > -1:
            m = self.userlist.GetItem(index, 0).GetText()
            username = self.userlist.GetItem(index, 1).GetText()
            if m != '*':    #not manager
                _id = self.userlist.GetItemData(index)
                user = self.users[_id]
                addr = user.addr
                username = user.name
                self.userlist.DeleteItem(index)
                del self.users[_id]
                info = tr("User [%s] has been kicked off") % username
                self.put_message('*', info)
                self.server.close_client(addr)
                self.server.broadcastexceptfor(addr, 'message', '*', info)
                self.server.broadcastexceptfor(addr, 'update_users', self.__get_userlist())
        else:
            if self.filelist.GetItemCount() > 0:
                common.showerror(self, tr("You should select one item first"))
            else:
                common.showerror(self, tr("No item exists"))

    def OnKeyDown(self, event):
        key = event.GetKeyCode()
        shift = event.ShiftDown()
        alt = event.AltDown()
        ctrl = event.ControlDown()
        if key == wx.WXK_RETURN and not shift and not alt and not ctrl:
            self.OnSend()
        elif key == wx.WXK_RETURN and shift and not alt and not ctrl:
            self.chat.WriteText('\n')
        else:
            event.Skip()

    def has_username(self, username):
        for user in self.users.values():
            if user.name == username:
                return True
        else:
            return False

    def has_document(self, document):
        return document in self.files.values()

    def get_doc_id(self, document):
        for _id, doc in self.files.items():
            if doc is document:
                return _id
        else:
            return None

    def change_status(self, status='startserver'):
        self.status = status
        if status == 'startserver':
            self.btnConnect.Enable(False)
            self.btnStart.SetLabel(tr('Stop Server'))
            self.txtName.Enable(False)
            self.txtIP.Enable(False)
            self.txtPort.Enable(False)
            self.userlist.Enable(True)
            self.filelist.Enable(True)
            self.chat.Enable(True)
            self.btnSend.Enable(True)
        elif status == 'stopserver':
            self.btnConnect.Enable(True)
            self.btnStart.SetLabel(tr('Start Server'))
            self.txtName.Enable(True)
            self.txtIP.Enable(True)
            self.txtPort.Enable(True)
            self.userlist.DeleteAllItems()
            self.filelist.DeleteAllItems()
            self.users = {}
            self.files = {}
            self.status = ''
            self.userlist.Enable(False)
            self.filelist.Enable(False)
            self.chat.Enable(False)
            self.btnSend.Enable(False)
            self.cmdrecorder.clear()
        elif status == 'connectserver':
            self.btnConnect.SetLabel(tr('Disconnect Server'))
            self.btnStart.Enable(False)
            self.txtName.Enable(False)
            self.txtIP.Enable(False)
            self.txtPort.Enable(False)
            self.userlist.Enable(False)
            self.filelist.Enable(True)
            self.chat.Enable(True)
            self.btnSend.Enable(True)
        elif status == 'disconnectserver':
            self.btnConnect.SetLabel(tr('Connect Server'))
            self.btnStart.Enable(True)
            self.status = ''
            self.userlist.DeleteAllItems()
            self.filelist.DeleteAllItems()
            self.txtName.Enable(True)
            self.txtIP.Enable(True)
            self.txtPort.Enable(True)
            self.userlist.Enable(False)
            self.filelist.Enable(False)
            self.chat.Enable(False)
            self.btnSend.Enable(False)
            self.users = {}
            self.files = {}
            self.cmdrecorder.clear()

    def put_message(self, username, message):
        self.chatroom.SetReadOnly(0)
        self.chatroom.GotoPos(self.chatroom.GetLength())
        pos = self.chatroom.GetCurrentPos()
        if username == '*': #system
            name = tr("System")
        else:
            name = username
        txt = name + ' : ' + message + '\n'
        self.chatroom.AddText(txt)
        if username == '*':
            self.chatroom.StartStyling(pos, 0xff)
            self.chatroom.SetStyling(len(txt.encode('utf-8')), 3)
        else:
            self.chatroom.StartStyling(pos, 0xff)
            length = len(name.encode('utf-8'))
            self.chatroom.SetStyling(length, 1)
            self.chatroom.StartStyling(pos + length + 3, 0xff)
            self.chatroom.SetStyling(len(message.encode('utf-8')), 2)

        self.chatroom.SetReadOnly(1)

    def get_user(self, addr):
        for k, user in self.users.items():
            if user.addr == addr:
                return user
        else:
            return None

    def __get_userlist(self):
        items = self.users.items()
        items.sort()
        userlist = []
        for index, user in items:
            userlist.append((user.name, user.manager))
        return userlist

    def __get_filelist(self):
        items = self.files.items()
        items.sort()
        filelist = []
        for index, doc in items:
            filelist.append((doc.getShortFilename(), index))
        return filelist

    def AddUser(self, username, manager=False, addr=None): #for server
        if self.has_username(username):
            self.server.sendto(addr, 'message', '*', tr('Username [%s] has also existed! Please try another') % username)
            self.server.sendto(addr, 'close')
            return

        user = User(username, manager=manager, addr=addr)
        def f(self):
            if manager:
                m = 'M'
            else:
                m = ''
            index = self.userlist.addline([m, username, ''])
            _id = self.userlist.GetItemData(index)
            self.users[_id] = user
            self.server.broadcast('update_users', self.__get_userlist())
            info = tr("User [%s] has entered the chatroom") % username
            self.put_message('*', info)
            self.server.broadcastexceptfor(addr, 'message', '*', info)
            self.server.sendto(addr, 'message', '*', 'Welcome!')
            self.server.sendto(addr, 'update_files', self.__get_filelist())
            for sid, doc in self.files.items():
                self.server.sendto(addr, 'editcmd', 'openfile', (sid, doc.getShortFilename(), doc.getRawText()))
                self.server.sendto(addr, 'editcmd', 'setlex', (sid, doc.languagename))
        wx.CallAfter(f, self)

    def UpdateUsers(self, userlist):    #for client
        """
        @param userlist: is a list of list [(username, manager)]
        @type userlist: list
        """
        def f(self):
            self.userlist.DeleteAllItems()
            for username, manager in userlist:
                if manager:
                    m = '*'
                else:
                    m = ''
                self.userlist.addline([m, username, ''])
        wx.CallAfter(f, self)

    def UpdateFiles(self, filelist):    #for client
        def f(self):
            self.filelist.DeleteAllItems()
            for filename, _id in filelist:
                index = self.filelist.addline([filename])
                self.filelist.SetItemData(index, _id)
        wx.CallAfter(f, self)

    def UserQuit(self, addr):   #for server
        for i in range(self.userlist.GetItemCount()):
            _id = self.userlist.GetItemData(i)
            user = self.users[_id]
            if user.addr == addr:   #quit
                username = user.name
                self.userlist.DeleteItem(i)
                del self.users[_id]
                info = tr("User [%s] has left the chatroom") % username
                self.put_message('*', info)
                self.server.broadcastexceptfor(addr, 'message', '*', info)
                self.server.sendto(addr, 'message', '*', 'See you next time!')
                self.server.broadcast('update_users', self.__get_userlist())
                break

    def ServerMessage(self, addr, username, message):    #for server
        def f(self):
            self.put_message(username, message)
            self.server.broadcastexceptfor(addr, 'message', username, message)
        wx.CallAfter(f, self)

    def ClientMessage(self, username, message):    #for client
        def f(self):
            self.put_message(username, message)
        wx.CallAfter(f, self)

    def ServerCommandPlay(self, addr, cmd, para):
        def f(self):
            if addr:
                self.cmdrecorder.do_command(cmd, para)
                self.server.broadcastexceptfor(addr, 'editcmd', cmd, para)
            else:
                self.server.broadcast('editcmd', cmd, para)
            user = self.get_user(addr)
            if user:
                username = user.name
            else:
                username = self.me
            self.ChangeUserAction(username, cmd)
            self.server.broadcast('activing', username, cmd)
        wx.CallAfter(f, self)

    def ClientCommandPlay(self, cmd, para):
        def f(self):
            self.cmdrecorder.do_command(cmd, para)
            if cmd == 'openfile':
                doc = self.cmdrecorder.check_document(para[0])
                self.files[para[0]] = doc
        wx.CallAfter(f, self)

    def RemoveFile(self, _id):  #for client
        def f(self):
            for i in range(self.filelist.GetItemCount()):
                s_id = self.filelist.GetItemData(i)
                if s_id == _id:
                    self.filelist.DeleteItem(i)
                    self.cmdrecorder.remove_document(_id)
        wx.CallAfter(f, self)

    def ClientClose(self):
        self.OnConnect()

    def ServerRegetFile(self, addr, _id, filename):
        self.put_message('*', tr("User [%(user)s] asks file [%(filename)s]") % {'user':self.get_user(addr).name, 'filename':filename})
        doc = self.files.get(_id, None)
        if doc:
            self.server.sendto(addr, 'editcmd', 'openfile', (_id, doc.getShortFilename(), doc.getRawText()))
            self.server.sendto(addr, 'editcmd', 'setlex', (_id, doc.languagename))
        else:
            self.server.sendto(addr, 'message', '*', tr("Can't find the file [%s]") % filename)

    def ChangeUserAction(self, username, action):
        for i in range(self.userlist.GetItemCount()):
            name = self.userlist.GetItem(i, 1).GetText()
            self.userlist.SetStringItem(i, 2, '')
            if name == username:
                self.userlist.SetStringItem(i, 2, 'active')

class ServerCommands(object):
    def __init__(self, concurrent):
        self.concurrent = concurrent

    def join(self, addr, username):
        self.concurrent.AddUser(username, addr=addr)

    def client_close(self, addr):
        self.concurrent.UserQuit(addr)

    def client_create(self, addr):
        pass

    def message(self, addr, username, message):
        self.concurrent.ServerMessage(addr, username, message)

    def editcmd(self, addr, cmd, para):
        self.concurrent.ServerCommandPlay(addr, cmd, para)

    def regetfile(self, addr, _id, filename):
        self.concurrent.ServerRegetFile(addr, _id, filename)

class ClientCommands(object):
    def __init__(self, concurrent):
        self.concurrent = concurrent

    def update_users(self, userlist):
        self.concurrent.UpdateUsers(userlist)

    def message(self, username, message):
        self.concurrent.ClientMessage(username, message)

    def editcmd(self, cmd, para):
        self.concurrent.ClientCommandPlay(cmd, para)

    def update_files(self, filelist):
        self.concurrent.UpdateFiles(filelist)

    def server_close(self):
        self.concurrent.put_message('*', tr("Server is closed"))
        self.concurrent.OnConnect()

    def forgivefile(self, _id):
        self.concurrent.RemoveFile(_id)

    def close(self):
        self.concurrent.ClientClose()

    def activing(self, username, action):
        self.concurrent.ChangeUserAction(username, action)

class User(object):
    def __init__(self, name, manager=False, addr=None, color=''):
        self.name = name
        self.color = color
        self.manager = manager
        self.addr = addr

    def isManager(self):
        return self.manager

    def __str__(self):
        return 'user=' + self.name + "manager=" + repr(self.manager) + "addr" + repr(self.addr)

class UserPanel(wx.Panel):
    def __init__(self, parent):
        self.parent = parent
        wx.Panel.__init__(self, parent, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, -1, tr("User Name")), 0, wx.ALL, 2)
        self.list = CheckList.List(self, columns=[
                        ('M', 30, 'center'),
                        (tr("User Name"), 80, 'left'),
                        (tr("Action"), 40, 'left'),
                        ], style=wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL)
        self.list.Enable(False)
        sizer.Add(self.list, 1, wx.EXPAND|wx.ALL, 2)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

class FileListPanel(wx.Panel):
    def __init__(self, parent):
        self.parent = parent
        wx.Panel.__init__(self, parent, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, -1, tr("Documents")), 0, wx.ALL, 2)
        self.list = CheckList.List(self, columns=[
                        (tr("Document Name"), 80, 'left'),
                        ], style=wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL)
        self.list.Enable(False)
        sizer.Add(self.list, 1, wx.EXPAND|wx.ALL, 2)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

class ChatPanel(wx.Panel):
    def __init__(self, parent):
        self.parent = parent
        wx.Panel.__init__(self, parent, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, -1, tr("Chat Box")), 0, wx.ALL, 2)
        self.chatroom = wx.stc.StyledTextCtrl(self, -1)
        self.chatroom.SetMarginWidth(0, 0)
        self.chatroom.SetMarginWidth(1, 0)
        self.chatroom.SetMarginWidth(2, 0)
        self.chatroom.SetReadOnly(1)
        sizer.Add(self.chatroom, 1, wx.EXPAND|wx.ALL, 2)
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer1.Add(wx.StaticText(self, -1, tr("Message") + ':'), 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 2)
        self.chat = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)
        sizer1.Add(self.chat, 1, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 2)
        self.btnSend = wx.Button(self, -1, tr("Send"))
        sizer1.Add(self.btnSend, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 2)
        self.btnClear = wx.Button(self, -1, tr("Clear"))
        sizer1.Add(self.btnClear, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 2)
        self.btnSave = wx.Button(self, -1, tr("Save"))
        sizer1.Add(self.btnSave, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 2)
        sizer.Add(sizer1, 0, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        self.chat.Enable(False)
        self.btnSend.Enable(False)

        if wx.Platform == '__WXMSW__':
            face1 = 'Arial'
            face2 = 'Times New Roman'
            face3 = 'Courier New'
            pb = 10
        else:
            face1 = 'Helvetica'
            face2 = 'Times'
            face3 = 'Courier'
            pb = 12

        self.chatroom.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, "size:%d,face:%s" % (pb, face3))
        self.chatroom.StyleClearAll()
        self.chatroom.StyleSetSpec(1, "size:%d,bold,face:%s,fore:#0000FF" % (pb, face1))  #username
        self.chatroom.StyleSetSpec(2, "face:%s,fore:#000000,size:%d" % (face1, pb))  #message
        self.chatroom.StyleSetSpec(3, "face:%s,bold,size:%d,fore:#FF0000" % (face1, pb))               #system


