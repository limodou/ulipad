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
#   $Id: BlogManageWindow.py 42 2005-09-28 05:19:21Z limodou $

from modules import Mixin
from modules import i18n
from modules import Resource
from modules import makemenu
from modules.Debug import error
import xmlrpclib
import wx
import os
import glob
import types
from modules import common
from modules.meteor.Tree import Tree

class BlogManageWindow(wx.Panel, Mixin.Mixin):

    __mixinname__ = 'blogmanagewindow'
    popmenulist = []
    imagelist = {}

    def __init__(self, parent, mainframe):
        self.initmixin()
        self.parent = parent
        self.mainframe = mainframe
        self.pref = self.mainframe.pref
        wx.Panel.__init__(self, parent, -1)

        self.box = wx.BoxSizer(wx.VERTICAL)

        self.box1 = wx.BoxSizer(wx.HORIZONTAL)

        obj = wx.StaticText(self, -1, tr('Account:'))
        self.box1.Add(obj, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 2)
        self.ID_SITELIST = wx.NewId()
        self.cmbSite= wx.ComboBox(self, self.ID_SITELIST, "", choices=self.mainframe.pref.blog_sites, size=(100, 20), style=wx.CB_READONLY)
        self.box1.Add(self.cmbSite, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 2)

        #manage
        self.ID_MANAGE = wx.NewId()
        self.btnManage = wx.Button(self, self.ID_MANAGE, tr('Manage'), size=(50, -1))
        self.box1.Add(self.btnManage, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 2)

        #new button
        self.ID_NEW= wx.NewId()
        self.btnNew = wx.Button(self, self.ID_NEW, tr('New'), size=(40, -1))
        self.box1.Add(self.btnNew, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 2)

        #delete button
        self.ID_DELETE= wx.NewId()
        self.btnDelete = wx.Button(self, self.ID_DELETE, tr('Del'), size=(40, -1))
        self.box1.Add(self.btnDelete, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 2)

        #get last post
        self.ID_GETPOSTS = wx.NewId()
        self.btnGetposts = wx.Button(self, self.ID_GETPOSTS, tr('Get Post'), size=(65, -1))
        self.box1.Add(self.btnGetposts, 0, wx.ALIGN_CENTER_VERTICAL)

        #get posts more
        self.ID_GETPOSTSMORE = wx.NewId()
        self.btnGetpostsMore = wx.Button(self, self.ID_GETPOSTSMORE, tr('>'), size=(15, -1))
        self.box1.Add(self.btnGetpostsMore, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 2)

        #get posts more
        self.ID_CACHE = wx.NewId()
        self.btnCache = wx.Button(self, self.ID_CACHE, tr('Cache'), size=(40, -1))
        self.box1.Add(self.btnCache, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 2)

        self.box.Add(self.box1, 0, wx.ALL|wx.EXPAND, 2)

        self.list = wx.ListCtrl(self, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.box.Add(self.list, 1, wx.EXPAND)

        self.SetSizer(self.box)
        self.SetAutoLayout(True)

        self.load()
        self.data = []
        self.initlist()

        wx.EVT_UPDATE_UI(self.btnDelete, self.ID_DELETE, self.OnUpdateUI)
        wx.EVT_BUTTON(self.btnManage, self.ID_MANAGE, self.OnManage)
        wx.EVT_BUTTON(self.btnNew, self.ID_NEW, self.OnNew)
        wx.EVT_BUTTON(self.btnDelete, self.ID_DELETE, self.OnDelete)
        wx.EVT_BUTTON(self.btnGetposts, self.ID_GETPOSTS, self.OnGetPosts)
        wx.EVT_BUTTON(self.btnGetpostsMore, self.ID_GETPOSTSMORE, self.OnGetPostsMore)
        wx.EVT_BUTTON(self.btnCache, self.ID_CACHE, self.OnCache)
        wx.EVT_LIST_ITEM_ACTIVATED(self.list, self.list.GetId(), self.OnEntryEntered)
        wx.EVT_COMBOBOX(self.cmbSite, self.ID_SITELIST, self.OnSiteChanged)

        if self.popmenulist:
            self.popmenu = makemenu.makepopmenu(self, self.popmenulist, self.imagelist)
            wx.EVT_LIST_ITEM_RIGHT_CLICK(self.list, self.list.GetId(), self.OnRClick)
            wx.EVT_RIGHT_UP(self.list, self.OnRClick)

        self.callplugin('init', self)

    def canClose(self):
        return True

    def OnUpdateUI(self, event):
        eid = event.GetId()
        if eid == self.ID_DELETE:
            index = self.list.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            event.Enable(index > -1)

    def OnManage(self, event):
        filename = i18n.makefilename(self.mainframe.blog_resfile, self.mainframe.app.i18n.lang)
        dlg = Resource.loadfromresfile(filename, self.mainframe, BlogSiteManageDialog, 'BlogSiteManageDialog', self.mainframe)
        dlg.ShowModal()
        self.load()

    def OnRClick(self, event):
        self.list.PopupMenu(self.popmenu, event.GetPosition())

    def OnSiteChanged(self, event):
        self.pref.last_blog_site = self.cmbSite.GetSelection()
        self.pref.save()
        self.load()

    def OnNew(self, event):
        self.new()

    def OnGetPosts(self, event):
        self.getposts()

    def OnGetPostsMore(self, event):
        from modules import Entry

        dlg = Entry.MyTextEntry(self, tr("Get Recent Posts"), tr("Enter the number from the lastest one:"), '1')
        answer = dlg.ShowModal()
        if answer == wx.ID_OK:
            try:
                number = int(dlg.GetValue())
                self.getposts(number)
            except:
                return

    def getposts(self, number=1, postid=''):
        common.setmessage(self.mainframe, tr('Getting entries...'))
        site = self.pref.blog_sites_info[self.pref.blog_sites[self.cmbSite.GetSelection()]]
        try:
            server = xmlrpclib.ServerProxy(site['url'])
            if not postid:
                result = server.metaWeblog.getRecentPosts('', site['user'], site['password'], number)
            else:
                result = [server.metaWeblog.getPost(postid, site['user'], site['password'])]
            self.list.DeleteAllItems()
            self.data = []
            for i, entry in enumerate(result):
                tree = Tree()
                data = {}
                data['title'] = entry['title']
                data['dateCreated'] = getDateTime(entry['dateCreated'])
                data['guid'] = entry.get('guid', '')
                data['postid'] = entry.get('postid', '')
                data['permalink'] = entry['permaLink']
                data['description'] = entry['description']
                data['author'] = entry.get('author', '')
                data['categories'] = entry['categories']
                if not data['postid']:
                    pos = data['guid'].rfind('#')
                    data['postid'] = data['guid']


                tree['entry'] = data
                path = self.getpath(site['datapath'], site['name'])
                if path:
                    filename = os.path.join(path, data['dateCreated']+'.xml')
                    file(filename, 'wb').write(tree.write_to_xml())

                    categories = self.mapCategories(data['categories'])

                    #write list
                    self.data.append(filename)
                    self.list.InsertStringItem(i , ','.join(categories))
                    self.list.SetStringItem(i, 1, data['title'])
                    self.list.SetStringItem(i, 2, formatDate(data['dateCreated']))
                    self.list.SetStringItem(i, 3, data['postid'])

        except Exception, msg:
            error.traceback()
            common.showerror(self.mainframe, msg)
        common.setmessage(self.mainframe, tr('Done'))

    def getpath(self, path, accountname):
        if not path:
            path = os.path.join(self.mainframe.app.workpath, accountname)

        if os.path.exists(path):
            return path
        else:
            dlg = wx.MessageDialog(self.mainframe, tr('The path %s is not exists. \nDo you want to create it?') % path, tr("Check Path"), wx.YES_NO | wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_YES:
                os.makedirs(path)
                return path
            else:
                return False

    def load(self):
        self.cmbSite.Clear()

        if self.pref.last_blog_site >= len(self.pref.blog_sites):
            self.pref.last_blog_site = 0
            self.pref.save()

        if len(self.pref.blog_sites) > 0:
            for name in self.pref.blog_sites:
                self.cmbSite.Append(name)
            self.cmbSite.SetSelection(self.pref.last_blog_site)
            site = self.pref.blog_sites_info[self.pref.blog_sites[self.pref.last_blog_site]]

            self.cmbSite.Enable(True)
        else:
            self.cmbSite.Enable(False)

    def initlist(self):
        self.list.InsertColumn(0, tr("Category"), width=80)
        self.list.InsertColumn(1, tr("Title"), width=300)
        self.list.InsertColumn(2, tr("Date"), width=110)
        self.list.InsertColumn(3, tr("PostId"), width=100)

    def OnCache(self, event):
        site = self.pref.blog_sites_info[self.pref.blog_sites[self.cmbSite.GetSelection()]]
        self.list.DeleteAllItems()
        self.data = []
        path = self.getpath(site['datapath'], site['name'])
        if path:
            files = glob.glob(os.path.join(path, '*.xml'))
            files.reverse()
            for i, f in enumerate(files):
                tree = Tree()
                tree.read_from_xml(file(f).read())
                data = tree['entry']
                self.data.append(f)
                categories = self.mapCategories(data['categories'])
                self.list.InsertStringItem(i , ','.join(categories))
                self.list.SetStringItem(i, 1, data['title'])
                self.list.SetStringItem(i, 2, formatDate(data['dateCreated']))
                self.list.SetStringItem(i, 3, data['postid'])

    def mapCategories(self, categories):
        site = self.pref.blog_sites_info[self.pref.blog_sites[self.cmbSite.GetSelection()]]
        s = []
        if not isinstance(categories, types.ListType):
            categories = [categories]
        cats = site.get('categories', [])
        for c in categories:
            for i in cats:
                if c == i['title']:
                    s.append(i['description'])
                    break
            else:
                s.append(c)
        return s

    def OnEntryEntered(self, event):
        index = self.list.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        filename = self.data[index]
        self.mainframe.editctrl.newPage(filename, documenttype='blogpanel')

    def new(self):
        self.mainframe.editctrl.newPage('', documenttype='blogpanel')

    def OnDelete(self, event):
        self.delete()

    def delete(self, postid=''):
        if not postid:
            index = self.list.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            if index == -1:
                common.showmessage(self.mainframe, tr('You should select on entry first!'))
                return
            filename = self.data[index]
            tree = Tree()
            tree.read_from_xml(file(filename).read())
            data = tree['entry']

            postid = data['postid']

        common.setmessage(self.mainframe, tr('Deleting entry...'))
        site = self.pref.blog_sites_info[self.pref.blog_sites[self.cmbSite.GetSelection()]]
        try:
            server = xmlrpclib.ServerProxy(site['url'])
            result = server.blogger.deletePost('', postid, site['user'], site['password'], False)
            if result:
                common.showmessage(self.mainframe, tr('Delete is successful!'))
                self.list.DeleteItem(index)
            else:
                common.showerror(self.mainframe, tr('Delete error!'))

        except Exception, msg:
            error.traceback()
            common.showerror(self.mainframe, msg)
        common.setmessage(self.mainframe, tr('Done'))

class BlogSiteManageDialog(wx.Dialog):
    def __init__(self, *args, **kwargs):
        wx.Dialog.__init__(self, *args, **kwargs)

    def init(self, mainframe):
        self.mainframe = mainframe
        self.pref = self.mainframe.pref
        self.obj_ID_CLOSE.SetId(wx.ID_CANCEL)

        self.lastindex = self.pref.last_blog_site
        self.categories = {}
        self.load()

        wx.EVT_UPDATE_UI(self.obj_ID_DELETE, self.ID_DELETE, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self.obj_ID_UPDATE, self.ID_UPDATE, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self.obj_ID_ADD, self.ID_ADD, self.OnUpdateUI)
        wx.EVT_CLOSE(self, self.OnClose)
        wx.EVT_BUTTON(self.obj_ID_CLOSE, wx.ID_CANCEL, self.OnClose)
        wx.EVT_BUTTON(self.obj_ID_ADD, self.ID_ADD, self.OnAdd)
        wx.EVT_BUTTON(self.obj_ID_UPDATE, self.ID_UPDATE, self.OnUpdate)
        wx.EVT_BUTTON(self.obj_ID_DELETE, self.ID_DELETE, self.OnDelete)
        wx.EVT_BUTTON(self.obj_ID_BROWSE, self.ID_BROWSE, self.OnBrowse)
        wx.EVT_LISTBOX(self.obj_ID_SITE, self.obj_ID_SITE.GetId(), self.OnSiteSelected)

    def OnUpdateUI(self, event):
        eid = event.GetId()
        selected = len(self.obj_ID_SITE.GetSelections()) > 0
        if eid == self.ID_DELETE:
            event.Enable(selected)
        elif eid == self.ID_UPDATE:
            event.Enable(selected and len(self.obj_ID_NAME.GetValue()) > 0 and len(self.obj_ID_URL.GetValue()) > 0)
        elif eid == self.ID_ADD:
            event.Enable(len(self.obj_ID_NAME.GetValue()) > 0 and len(self.obj_ID_URL.GetValue()) > 0)

    def OnClose(self, event):
        self.Destroy()

    def OnAdd(self, event):
        if not self.login():
            return
        site = self.getSite()
        if site['name'] in self.pref.blog_sites:
            wx.MessageDialog(self, tr("The site name is duplicated! Try another."), tr("Add Blog Site"), wx.OK | wx.ICON_INFORMATION).ShowModal()
        else:
            self.pref.blog_sites.append(site['name'])
            self.pref.blog_sites_info[site['name']] = site
            self.pref.save()
            self.lastindex = len(self.pref.blog_sites) - 1
            self.load()

    def login(self):
        try:
            server = xmlrpclib.ServerProxy(self.obj_ID_URL.GetValue())
            result = server.metaWeblog.getCategories('', self.obj_ID_USER.GetValue(), self.obj_ID_PASSWORD.GetValue())
            if result:
                self.categories = result
                common.showmessage(self.mainframe, tr('Login is successful!'))
            else:
                self.categories = {}
                common.showerror(self.maiframe, tr('Login is faild!'))
            return True
        except Exception, msg:
            error.traceback()
            common.showerror(self.mainframe, msg)
            return False

    def OnSiteSelected(self, event):
        self.lastindex = event.GetSelection()
        self.setSite(self.lastindex)

    def OnUpdate(self, event):
        if self.obj_ID_NAME.GetValue() in self.pref.blog_sites:
            if not self.login():
                return
            site = self.getSite()
            self.pref.blog_sites_info[site['name']] = site
            self.pref.save()
            self.load()
        else:
            self.OnAdd(event)

    def OnDelete(self, event):
        index = self.obj_ID_SITE.GetSelection()
        name = self.obj_ID_SITE.GetString(index)
        self.obj_ID_SITE.Delete(index)
        self.pref.blog_sites.remove(name)
        del self.pref.blog_sites_info[name]
        self.pref.save()
        self.load()

    def OnBrowse(self, event):
        dlg = wx.DirDialog(self, tr('Choose a directory'))
        answer = dlg.ShowModal()
        if answer == wx.ID_OK:
            path = dlg.GetPath()
            self.obj_ID_DATAPATH.SetValue(path)

    def load(self):
        self.obj_ID_SITE.Clear()
        self.obj_ID_SITE.InsertItems(self.pref.blog_sites, 0)
        if self.lastindex >= len(self.pref.blog_sites):
            self.lastindex = len(self.pref.blog_sites) - 1
        if len(self.pref.blog_sites) > 0:
            self.obj_ID_SITE.SetSelection(self.lastindex)
            self.setSite(self.lastindex)
        else:
            self.setSite(-1)

    def getSite(self):
        site = {}
        site['name'] = self.obj_ID_NAME.GetValue()
        site['user'] = self.obj_ID_USER.GetValue()
        site['password'] = self.obj_ID_PASSWORD.GetValue()
        site['url'] = self.obj_ID_URL.GetValue()
        site['utf-8'] = self.obj_ID_UTF_8.GetValue()
        site['datapath'] = self.obj_ID_DATAPATH.GetValue()
        site['categories'] = self.categories

        return site

    def setSite(self, index):
        if index > -1:
            site = self.pref.blog_sites_info[self.pref.blog_sites[index]]
            self.obj_ID_NAME.SetValue(site['name'])
            self.obj_ID_USER.SetValue(site['user'])
            self.obj_ID_PASSWORD.SetValue(site['password'])
            self.obj_ID_URL.SetValue(site['url'])
            self.obj_ID_UTF_8.SetValue(site['utf-8'])
            self.obj_ID_DATAPATH.SetValue(site.get('datapath', ''))
            self.categories = site.get('categories', {})
        else:
            self.obj_ID_NAME.SetValue('')
            self.obj_ID_USER.SetValue('')
            self.obj_ID_PASSWORD.SetValue('')
            self.obj_ID_URL.SetValue('')
            self.obj_ID_UTF_8.SetValue(True)
            self.obj_ID_DATAPATH.SetValue('')
            self.categories = {}

def getDateTime(d):
    a = str(d)
    if '-' in a:
        b = a[0:4]+'_'+a[5:7]+'_'+a[8:10]+'_'+a[11:19]
    else:
        b = a[0:4]+'_'+a[4:6]+'_'+a[6:8]+'_'+a[9:17]
    return b.replace(':', '_')

def formatDate(d):
    year, mon, day, h, m, s = d.split('_')
    return "%s/%s/%s %s:%s" % (year, mon, day, h, m)
