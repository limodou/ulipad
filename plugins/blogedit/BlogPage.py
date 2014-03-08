#       Programmer:     limodou
#       E-mail:         limodou@gmail.com
#
#       Copyleft 2006 limodou
#
#       Distributed under the terms of the GPL (GNU Public License)
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
#       $Id: BlogPage.py 42 2005-09-28 05:19:21Z limodou $

from modules import Mixin
import wx
from mixins import DocumentBase
from mixins.Editor import TextEditor
from modules import i18n
from modules import Resource
import wx.lib.dialogs as Dialogs
from BlogManageWindow import *

class BlogPage(wx.Panel, DocumentBase.DocumentBase, Mixin.Mixin):

    __mixinname__ = 'blogpage'

    def __init__(self, parent, mainframe, filename, documenttype, **kwargs):
        self.initmixin()

        wx.Panel.__init__(self, parent, -1)
        DocumentBase.DocumentBase.__init__(self, parent, filename, documenttype, **kwargs)
        self.mainframe = mainframe
        self.pref = mainframe.pref

        self.siteindex = self.pref.last_blog_site
        if len(self.pref.blog_sites) > 0:
            site = self.pref.blog_sites_info[self.pref.blog_sites[self.siteindex]]
        else:
            site = {}
        self.categoryindex = site.get('last_category', 0)
        self.dateCreated = ''
        self.postid = ''

        box = wx.BoxSizer(wx.VERTICAL)

        box1 = wx.BoxSizer(wx.HORIZONTAL)

        #title
        obj = wx.StaticText(self, -1, tr('Title:'))
        box1.Add(obj, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 2)
        self.txtTitle = wx.TextCtrl(self, -1, "", size=(-1, 20))
        box1.Add(self.txtTitle, 1, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 2)

        #categories
        obj = wx.StaticText(self, -1, tr('Category:'))
        box1.Add(obj, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 2)
        self.ID_CATELIST = wx.NewId()
        self.cmbCategory = wx.ComboBox(self, self.ID_CATELIST, "", choices=[], size=(120, 20), style=wx.CB_READONLY)
        box1.Add(self.cmbCategory, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 2)

        #send button
        self.ID_SEND = wx.NewId()
        self.btnSend = wx.Button(self, self.ID_SEND, tr('Send'), size=(40, -1))
        box1.Add(self.btnSend, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 2)

        #site button
        self.ID_SITE = wx.NewId()
        self.btnSite = wx.Button(self, self.ID_SITE, tr('Site'), size=(40, -1))
        box1.Add(self.btnSite, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 2)

        #info button
        self.ID_INFO = wx.NewId()
        self.btnInfo = wx.Button(self, self.ID_INFO, tr('Info'), size=(40, -1))
        box1.Add(self.btnInfo, 0, wx.ALIGN_CENTER_VERTICAL, 2)

        box.Add(box1, 0, wx.TOP|wx.BOTTOM|wx.EXPAND, 2)

        #editor
        self.editor = TextEditor(self, self.mainframe.editctrl, self.filename, self.documenttype)

        box.Add(self.editor, 1, wx.ALL|wx.EXPAND, 0)

        self.load()

        self.SetSizer(box)
        self.SetAutoLayout(True)

        wx.EVT_BUTTON(self.btnSend, self.ID_SEND, self.OnSend)
        wx.EVT_BUTTON(self.btnSite, self.ID_SITE, self.OnSite)
        wx.EVT_BUTTON(self.btnInfo, self.ID_INFO, self.OnInfo)
        wx.EVT_UPDATE_UI(self.cmbCategory, self.ID_CATELIST, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self.btnSend, self.ID_SEND, self.OnUpdateUI)

        self.opened = True

    def openfile(self, filename='', encoding='', delay=None, *args, **kwargs):
        #check if the blog accounts is empty
        if len(self.pref.blog_sites) == 0:
            wx.MessageDialog(self, tr("Your blog account is empty! \nPlease config it first."), tr("Blog Window"), wx.OK | wx.ICON_INFORMATION).ShowModal()

        if filename:
            self.loadFromFile(filename)
        else:
            self.title = tr('New Post')

    def savefile(self, filename, encoding):
        self.editor.savefile(filename, encoding)

    def load(self):
        self.cmbCategory.Clear()

        if len(self.pref.blog_sites) > 0 and self.siteindex >= len(self.pref.blog_sites):
            self.siteindex = 0

        if len(self.pref.blog_sites) > 0:
            name = self.pref.blog_sites[self.siteindex]
            site = self.pref.blog_sites_info[name]

            if self.categoryindex >= len(site['categories']):
                self.categoryindex = 0

            categories = []
            for c in site['categories']:
                self.cmbCategory.Append(c['description'])
            self.cmbCategory.SetSelection(self.categoryindex)

    def OnSite(self, event):
        self.ids = {}
        menu = wx.Menu()

        self.IDPM_SITEMANAGE = wx.NewId()
        menu.Append(self.IDPM_SITEMANAGE, tr("Site Manage"))
        menu.AppendSeparator()
        wx.EVT_MENU(self, self.IDPM_SITEMANAGE, self.OnSiteManage)

        for i, name in enumerate(self.pref.blog_sites):
            site = self.pref.blog_sites_info[name]
            id = wx.NewId()
            self.ids[id] = i
            item = menu.AppendCheckItem(id, name)
            if i == self.siteindex:
                item.Check(True)
            else:
                item.Check(False)
            wx.EVT_MENU(self, id, self.OnSiteItem)
        self.PopupMenu(menu, self.btnSite.GetPosition() + (0, self.btnSite.GetSize()[1]))
        menu.Destroy()

    def OnSiteItem(self, event):
        eid = event.GetId()

        self.siteindex = self.ids.get(eid, 0)
        self.load()

    def OnSiteManage(self, event):
        filename = i18n.makefilename(self.mainframe.blog_resfile, self.mainframe.app.i18n.lang)
        dlg = Resource.loadfromresfile(filename, self.mainframe, BlogSiteManageDialog, 'BlogSiteManageDialog', self.mainframe)
        dlg.ShowModal()
        self.load()

    def OnInfo(self, event):
        struct = self.getPost()
        struct['categories'] = struct['categories'][0]
        msg = tr("""Title      : %(title)s
Categories : [%(categories)s]
DateCreated: %(dateCreated)s
PostId     : %(postid)s
Account    : %(account)s
Xmlrpcurl  : %(xmlrpcurl)s
        """) % struct
        dlg = Dialogs.ScrolledMessageDialog(self, msg, tr("Blog Information"))
        dlg.ShowModal()

    def getPost(self):
        if len(self.pref.blog_sites) > 0:
            site = self.pref.blog_sites_info[self.pref.blog_sites[self.siteindex]]
        else:
            site = {}
        struct = {}
        struct['user'] = site.get('user', '')
        struct['password'] = site.get('password', '')
        struct['account'] = site.get('name', '')
        struct['xmlrpcurl'] = site.get('url', '')
        struct['description'] = self.editor.GetText()
        if site.get('utf-8', False):
            struct['description'] = struct['description'].encode('utf-8')
        else:
            struct['descrpition'] = struct['description'].encode(self.editor.locale)

        index = self.cmbCategory.GetSelection()
        if len(site.get('categories', [])) > 0:
            struct['categories'] = [site['categories'][index]['title']]
        else:
            struct['categories'] = ['']
        if self.dateCreated:
            struct['dateCreated'] = self.dateCreated
        else:
            struct['dateCreated'] = xmlrpclib.DateTime()
        struct['title'] = self.txtTitle.GetValue()
        struct['postid'] = self.postid

        return struct

    def OnSend(self, event):
        self.post()

    def post(self):
        if len(self.pref.blog_sites) == 0:
            wx.MessageDialog(self, tr("Your blog account is empty! \nPlease config it first."), tr("Blog Window"), wx.OK | wx.ICON_INFORMATION).ShowModal()
            return
        setmessage(self.mainframe, tr('Posting entry...'))
        struct = self.getPost()
        try:
            server = xmlrpclib.ServerProxy(struct['xmlrpcurl'])
            if struct['postid']:
                result = server.metaWeblog.editPost(struct['postid'], struct['user'], struct['password'], struct, True)
                if result:
                    showmessage(self.mainframe, tr('Modify is successful!'))
                    self.title = struct['title']
                    self.mainframe.editctrl.switch(self)
                else:
                    showerror(self.mainframe, tr('Modify error!'))
            else:
                result = server.metaWeblog.newPost('', struct['user'], struct['password'], struct, True)
                if result:
                    showmessage(self.mainframe, tr('Post is successful! Id=%s') % result)
                    self.postid = result
                    self.title = struct['title']
                    self.mainframe.editctrl.switch(self)

                    #save last category index
                    site = self.pref.blog_sites_info[self.pref.blog_sites[self.siteindex]]
                    site['last_category'] = self.cmbCategory.GetSelection()
                    self.pref.save()
                else:
                    showerror(self.mainframe, tr('Post error!'))
        except Exception, msg:
            error.traceback()
            showerror(self.mainframe, msg)
        setmessage(self.mainframe, tr('Done'))

    def OnUpdateUI(self, event):
        eid = event.GetId()
        if eid == self.ID_CATELIST:
            event.Enable(not self.postid)
        elif eid == self.ID_SEND:
            event.Enable(len(self.txtTitle.GetValue()) > 0)

    def loadFromFile(self, filename):
        tree = Tree()
        tree.read_from_xml(file(filename).read())
        data = tree['entry']
        self.txtTitle.SetValue(data['title'])
        self.title = data['title']
        categories = data['categories']
        if not isinstance(categories, types.ListType):
            categories = [categories]

        self.postid = data['postid']
        self.dateCreated = data['dateCreated']

        site = self.pref.blog_sites_info[self.pref.blog_sites[self.siteindex]]
        for c in site['categories']:
            if c['title'] == categories[0]:
                category_desc = c['description']
                break
        else:
            showerror(self.mainframe, tr('The category [%s] is not existed!') % categories[0])
            raise Exception

        i = self.cmbCategory.FindString(category_desc)
        if i > -1:
            self.cmbCategory.SetSelection(i)

        self.editor.SetText(data['description'])
        self.editor.EmptyUndoBuffer()
        self.editor.SetSavePoint()

    def __getattr__(self, name):
        return getattr(self.editor, name)
