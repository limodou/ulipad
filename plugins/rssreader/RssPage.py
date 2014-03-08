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
import tempfile
import RssDb
import wx.lib.pubsub as pubsub
import images
import os.path
import threading
from modules import dict4ini
from modules import Casing
from modules import Mixin
from modules import CheckList
from mixins import HtmlPage
from mixins import DocumentBase
from modules.meteor import Template
from modules import Globals

class RssPage(wx.SplitterWindow, DocumentBase.DocumentBase, Mixin.Mixin):

    __mixinname__ = 'rsspage'

    def __init__(self, parent, mainframe, filename, documenttype):
        self.initmixin()

        wx.SplitterWindow.__init__(self, parent, -1, style = wx.SP_LIVE_UPDATE )
        DocumentBase.DocumentBase.__init__(self, parent, filename, documenttype)
        self.parent = parent
        self.mainframe = mainframe
        self.pref = mainframe.pref

        self.datas = RssDataPage(self, self.mainframe)

        self.view = HtmlPage.HtmlPage(self, mainframe, filename, documenttype)

        self.SetMinimumPaneSize(50)
        self.SplitHorizontally(self.datas, self.view, 250)

        self.publisher = pubsub.Publisher()
        self.publisher.subscribe(self.OnChangeHtml, 'change_html')

        self.data = []
        self.guids = {}

    def canClose(self):
        return True

    def openfile(self, filename='', encoding='', delay=None, *args, **kwargs):
        rssid = filename[6:]
        rssid = int(rssid)

        d = Casing.Casing(self.load_from_db, rssid)
        d += Casing.Casing(self.datas.set_guids, self.guids)
        d += Casing.Casing(self.datas.load, self.getdata)
        d += Casing.Casing(self.show_unread, rssid)
        d.start_thread()

        self.filename = filename
        self.locale = encoding
        self.opened = True

    def isMe(self, filename, documenttype='rssview'):
        if filename.startswith('rss://'):
            return True

    def load_from_db(self, rssid):
        RssDb.init(Globals.rss_dbfile)
        from modules.Debug import error
        error.info('load_from_db'+str(rssid))
        self.data = []
        feed = RssDb.Feed.get(rssid)
        for i, data in enumerate(RssDb.Data.get_posts(feed.id)):
            self.data.append(([data.title, data.pubDate.strftime("%Y-%m-%d %H:%M:%S")], data.read))
            self.guids[i] = data.guid
        self.title = feed.title
        editctrl = Globals.mainframe.editctrl
        wx.CallAfter(editctrl.showPageTitle, self)
        wx.CallAfter(editctrl.showTitle, self)

    def show_unread(self, rssid):
        t = Template()
        t.load(os.path.join(Globals.workpath, 'plugins/rssreader/unread_message.py'), 'python')

        RssDb.init(Globals.rss_dbfile)

        feed = RssDb.Feed.get(rssid)
        data = RssDb.Data.select(RssDb.and_(RssDb.Data.c.feed_id==rssid, RssDb.Data.c.read==False), order_by=[RssDb.desc(RssDb.Data.c.pubDate)])
        x = dict4ini.DictIni()
        x.html.chanel_title = feed.title
        x.html.chanel_url = feed.link
        x.html.chanel_image_url = feed.imagelink
        x.html.newsletter = []
        for i in data:
            v = dict4ini.DictIni()
            v.title = i.title
            v.link = i.link
            v.description = i.description
            v.date = i.pubDate.strftime("%Y-%m-%d %H:%M:%S")
            v.comments = i.comments
            v.comments_gif = ('file:///' + os.path.join(Globals.workpath, 'plugins/rssreader/comments.png').replace(':', '|')).replace('\\', '/')
            x.html.newsletter.append(v)

        text = t.value('html', x.dict(), encoding='utf-8')
        filename = os.path.join(tempfile.gettempdir(), 'rssreader.html')
        file(filename, 'w').write(text)

        self.publisher.sendMessage('change_html', filename)

    def getdata(self):
        for i in self.data:
            yield i

    def OnChangeHtml(self, message):
        self.view.openfile(message.data)

class RssDataPage(wx.Panel, Mixin.Mixin):

    __mixinname__ = 'rssdatapage'

    def __init__(self, parent, mainframe):
        self.initmixin()

        self.parent = parent

        wx.Panel.__init__(self, parent, -1)

        self.publisher = pubsub.Publisher()

        box = wx.BoxSizer(wx.VERTICAL)
        self.list = CheckList.CheckList(self, columns=[
            (tr("Subject"), 400, 'left'),
            (tr("Date"), 120, 'left'),
            ], check_image=images.getCheckBitmap(), uncheck_image=images.getUncheckBitmap(),
            style=wx.LC_REPORT | wx.SUNKEN_BORDER)

        self.list.on_check = self.OnCheck

        box.Add(self.list, 1, wx.EXPAND|wx.ALL)
        self.SetSizer(box)
        self.SetAutoLayout(True)

        wx.EVT_LIST_ITEM_SELECTED(self.list, self.list.GetId(), self.OnChanged)

    def load(self, getdata):
        self.list.Freeze()
        self.list.DeleteAllItems()
        self.list.load(getdata)
        self.list.Thaw()

    def OnCheck(self, index, checkflag):
        RssDb.init(Globals.rss_dbfile)

        data = RssDb.Data.get_by(guid=self.guids[index])
        data.read = checkflag
        data.save()
        self.list.setFlag(index, checkflag)

        self.publisher.sendMessage('rss_unread_changed', {'rssid':data.feed_id, 'flag':checkflag})

    def set_guids(self, guids):
        self.guids = guids

    def OnChanged(self, event):
        t = Template()
        t.load(os.path.join(Globals.workpath, 'plugins/rssreader/single_message.txt'), 'text')

        RssDb.init(Globals.rss_dbfile)

        item = event.GetIndex()
        index = self.list.GetItemData(item)
        data = RssDb.Data.get_by(guid=self.guids[index])
        v = {}
        v["title"] = data.title
        v["link"] = data.link
        v["description"] = data.description
        v["date"] = data.pubDate.strftime("%Y-%m-%d %H:%M:%S")
        v["comments"] = data.comments
        v["comments_gif"] = ('file:///' + os.path.join(Globals.workpath, 'plugins/rssreader/comments.png').replace(':', '|')).replace('\\', '/')

        text = t.value('text', v, encoding='utf-8')
        filename = os.path.join(tempfile.gettempdir(), 'rssreader.html')
        file(filename, 'w').write(text)

        self.publisher.sendMessage('change_html', filename)

        #cal read status
        def check_and_update(self=self, index=item):
            if self.list.GetFirstSelected() == index:
                wx.CallAfter(self.OnCheck, index, True)
        t = threading.Timer(Globals.mainframe.pref.rss_read_time, check_and_update)
        t.start()
