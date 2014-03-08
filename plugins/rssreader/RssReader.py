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

import os.path
import wx
import wx.lib.pubsub as pubsub
import feedparser
import RssDb
import datetime
from modules import Casing
from modules.Debug import error
from modules import Globals
import re

r = re.compile(r'<\?xml.*encoding="(.*?)"\s*\?>')

class RssReader:
    def __init__(self, parent):
        self.parent = parent
        self.sharewin = parent
        self.pref = parent.pref
        self.categories = {}
        self.cate_items = {}
        self.feeds = {}
        self.publisher = pubsub.Publisher()
        self.publisher.subscribe(self.OnUnreadChanged, 'rss_unread_changed')

        self.casings = {}

        #check rss reader data dir
        self.rootpath = path = os.path.join(Globals.userpath, 'rssreader')
        if not os.path.exists(path):
            os.mkdir(path)
        self.iconpath = path = os.path.join(Globals.userpath, 'rssreader/FavIcons')
        if not os.path.exists(path):
            os.mkdir(path)

        for f in os.listdir(self.iconpath):
            imagefile = os.path.join(self.iconpath, f)
            name = os.path.splitext(f)[0]
            nolog = wx.LogNull()
            ok = wx.Image(imagefile, wx.BITMAP_TYPE_ANY).Ok()
            del nolog
            if not ok:
                continue
            self.sharewin.add_image(name, imagefile)

        Globals.rss_data_path = self.rootpath
        Globals.rss_dbfile = os.path.join(self.rootpath, Globals.mainframe.pref.rss_dbfile)

        for name in ['RSS_ROOT_IMAGE', 'RSS_CATEGORY_IMAGE', 'RSS_FEED_IMAGE', 'RSS_RUN1',
                'RSS_RUN2', 'RSS_RUN3', 'RSS_ERROR']:
            setattr(self, name, self.sharewin.get_image_id(name))

    def get_item_image_index(self, item):
        node = self.sharewin.get_node(item)
        return self.get_image_index(node)

    def get_image_index(self, data, imagetype=wx.TreeItemIcon_Normal):
        if data.get('type', '') == 'rss':
            if data.get('level', '') == 'root':
                return self.RSS_ROOT_IMAGE
            elif data.get('level', '') == 'category':
                return self.RSS_CATEGORY_IMAGE
            elif data.get('level', '') == 'feed':
                homeurl = data['data'].get('homeurl', '')
                return self.get_feed_image(homeurl)
        return -1

    def delete(self, node):
        if node.get('type', '') == 'rss':
            if node.get('level', '') == 'root':
                return True
            elif node.get('level', '') == 'category':
                cate_id = node['data']['id']
                RssDb.init(Globals.rss_dbfile)
                RssDb.Category.delete_id(cate_id)
                self.del_category_ids(cate_id)
                return True
            elif node.get('level', '') == 'feed':
                RssDb.init(Globals.rss_dbfile)
                rssid = node['data']['id']
                feed = RssDb.Feed.get(rssid)
                cate_id = feed.category_id
                RssDb.Feed.delete_id(rssid)
                self.del_feed_ids(cate_id, rssid)
                return True

    def fresh_feed(self, item):
        d = self.casings.get(item, None)
        if d and d.isactive():
            return
        d = self.get_casting(item)
        d += Casing.Casing(self.update_content, item=item)
        d.start_sync_thread()

    def stop_category(self, item):
        node = self.sharewin.get_node(item)
        cate_id = node['data']['id']
        for i in self.cate_items[cate_id]:
            c = self.feeds[i]
            self.stop_feed(c)

    def stop_feed(self, item):
        d = self.casings.get(item, None)
        if d and d.isactive():
            d.stop_thread()
        wx.CallAfter(self.sharewin.tree.SetItemImage, item, self.get_item_image_index(item))

    def get_casting(self, item):
        text = Casing.new_obj()
        text.text = ''
        node = self.sharewin.get_node(item)
        rssid = node['data']['id']
        feedurl = str(node['data']['url'])
        d = Casing.Casing(self.get_feed, feedurl=feedurl, text=text)
        d += Casing.Casing(self.parse_content, rssid=rssid, text=text)
        d += Casing.Casing(self.update_feed_read, item=item)
        d.onexception(self.on_exception, item)
        d.onprocess(self.on_process, item=item)
        d.onsuccess(self.on_success, item)
        self.casings[item] = d
        return d

    def get_feed(self, syncvar, feedurl, text):
        text.text = self.get_feed_text(feedurl)

    def get_feed_text(self, feedurl):
        feedurl = str(feedurl)
        import pycurl
        c = pycurl.Curl()
        c.setopt(pycurl.URL, feedurl)
        import StringIO
        b = StringIO.StringIO()
        c.setopt(pycurl.WRITEFUNCTION, b.write)
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.setopt(pycurl.MAXREDIRS, 5)
        c.setopt(pycurl.CONNECTTIMEOUT, 30)
        if self.pref.use_proxy:
            c.setopt(pycurl.PROXY, str(self.pref.proxy))
            c.setopt(pycurl.PROXYUSERPWD, '%s:%s' % (str(self.pref.proxy_user), str(self.pref.proxy_password)))
        c.perform()
        return b.getvalue()

    def parse_content(self, syncvar, rssid, text):
        if text.text:
            self.feed(rssid, text.text)

    def update_feed_read(self, syncvar, item):
        node = self.sharewin.get_node(item)
        wx.CallAfter(self.refresh_feed_unread, node['data']['id'])

    def update_content(self, syncvar, item):
        node = self.parent.get_node(item)
        editctrl = self.parent.mainframe.editctrl
        rssid = u"rss://" + str(node['data']['id'])
        for d in editctrl.getDocuments():
            if d.isMe(rssid, 'rssview'):
                wx.CallAfter(editctrl.switch, d)
                wx.CallAfter(d.openfile, rssid)
        else:
            wx.CallAfter(editctrl.new, rssid, documenttype='rssview')


    def on_process(self, syncvar, item):
        tree = self.sharewin.tree
        if not hasattr(item, '_imageindex'):
            item._imageindex = self.RSS_RUN1
        wx.CallAfter(tree.SetItemImage, item, item._imageindex)
        if item._imageindex == self.RSS_RUN1:
            item._imageindex = self.RSS_RUN2
        elif item._imageindex == self.RSS_RUN2:
            item._imageindex = self.RSS_RUN3
        else:
            item._imageindex = self.RSS_RUN1

    def on_exception(self, item):
        error.traceback()
        wx.CallAfter(self.sharewin.tree.SetItemImage, item, self.RSS_ERROR)

    def on_success(self, item):
        wx.CallAfter(self.sharewin.tree.SetItemImage, item, self.get_item_image_index(item))
        item._imageindex = self.RSS_RUN1

    def OnUnreadChanged(self, message):
        rssid = message.data['rssid']
        self.refresh_feed_unread(rssid)

    def OnSharewinClose(self):
        self.publisher.unsubscribe(self.OnUnreadChanged, 'rss_unread_changed')

    def refresh_feed_unread(self, rssid):
        RssDb.init(Globals.rss_dbfile)

        feed = RssDb.Feed.get(rssid)
        number = RssDb.Data.un_read_count(rssid)
        if number:
            caption = u"(%d)%s" % (number, feed.title)
        else:
            caption = feed.title
        item = self.feeds[rssid]
        node = self.sharewin.get_node(item)
        node['caption'] = caption

        self.sharewin.tree.SetItemText(item, caption)
        if number:
            self.sharewin.tree.SetItemBold(item, True)
        else:
            self.sharewin.tree.SetItemBold(item, False)

    def feed(self, rssid, text):
        RssDb.init(Globals.rss_dbfile)

#        b = r.match(text)
#        if b:
#            text = text[b.end():]
#            encoding = b.groups()[0]
#            if encoding.lower() == 'gb2312':
#                encoding = 'gbk'
#            text = unicode(text, encoding).encode('utf-8')
        d = feedparser.parse(text)
        new = 0
        RssDb.objectstore.begin()
        feed = RssDb.Feed.get(rssid)
        for i in d.entries:
            if not i.has_key('modified_parsed'):
                date = datetime.datetime.now()
            else:
                date = datetime.datetime(*i.modified_parsed[:-2])
            if not i.has_key('comments'):
                i.comments = ''
            if not i.has_key('guid'):
                i.guid = i.link
            data = RssDb.Data.get_by(feed_id=rssid, guid=i.guid)
            if data:
                if i.title!= data.title or i.description!=data.description:
                    data.title = i.title
                    data.description=i.description
                    data.pubDate=date
                    data.read=False
                    new += 1
            else:
                data = RssDb.Data(guid=i.guid, title=i.title, comments=i.comments,
                    description=i.description, link=i.link, pubDate=date, read=False, feed_id=rssid)
                new += 1
        RssDb.objectstore.commit()
        if Globals.mainframe.pref.rss_auto_dig:
            self.parse_feed(feed, d.feed)

    def startup(self, item):
        sharewin = self.parent
        RssDb.init(Globals.rss_dbfile)
        categories = RssDb.Category.select()
        sharewin.tree.Freeze()
        for i in categories:
            data = {'type':'rss', 'level':'category', 'caption':i.title, 'data':{'save':False, 'id':i.id}}
            root = sharewin.addnode(item, data=data)
            self.add_category_ids(i.id, root)
            for f in RssDb.Feed.select(RssDb.Feed.c.category_id==i.id, order_by=[RssDb.Feed.c.title]):
                number = RssDb.Data.un_read_count(f.id)
                if number:
                    caption = u"(%d)%s" % (number, f.title)
                else:
                    caption = f.title
                data = {'type':'rss', 'level':'feed', 'caption':caption, 'data':{'url':f.link, 'homeurl':f.homelink, 'save':False, 'id':f.id}}
                obj = sharewin.addnode(root, data=data)
                self.add_feed_ids(i.id, f.id, obj)
                if number:
                    sharewin.tree.SetItemBold(obj, True)
            sharewin.tree.Expand(root)
        sharewin.tree.Thaw()
        if categories:
            wx.CallAfter(sharewin.tree.Expand, item)
            if Globals.mainframe.pref.rss_start:
                mc = Casing.MultiCasing()
                for item in self.feeds.values():
                    d = self.get_casting(item)
                    mc.append(d)
                mc.start_sync_thread()

    def add_category_ids(self, cate_id, obj):
        self.categories[cate_id] = obj
        self.cate_items[cate_id] = []

    def add_feed_ids(self, cate_id, feed_id, obj):
        self.cate_items[cate_id].append(feed_id)
        self.feeds[feed_id] = obj

    def del_category_ids(self, cate_id):
        del self.cate_items[cate_id]
        del self.categories[cate_id]

    def del_feed_ids(self, cate_id, feed_id):
        self.cate_items[cate_id].remove(feed_id)
        del self.feeds[feed_id]

    def fresh_category(self, item):
        node = self.sharewin.get_node(item)
        cate_id = node['data']['id']
        mc = Casing.MultiCasing()
        for i in self.cate_items[cate_id]:
            d = self.get_casting(self.feeds[i])
            mc.append(d)
        mc.start_sync_thread()

    def set_all_read(self, item):
        node = self.sharewin.get_node(item)
        rssid = node['data']['id']
        RssDb.init(Globals.rss_dbfile)

        RssDb.Data.set_read(rssid)

        self.refresh_feed_unread(rssid)

    def change_feed(self, item):
        data = self.sharewin.get_node(item)
        wx.CallAfter(self.sharewin.tree.SetItemImage, item, self.get_item_image_index(item))
        from modules.Debug import error
        error.info(data)
        if data:
            if data.get('type', '') == 'rss' and data.get('level', '') == 'feed':
                editctrl = self.sharewin.parent.mainframe.editctrl
                rssid = u"rss://" + str(data['data']['id'])
                for d in editctrl.getDocuments():
                    if d.isMe(rssid, 'rssview'):
                        wx.CallAfter(editctrl.switch, d)
                        wx.CallAfter(d.openfile, rssid)
                else:
                    wx.CallAfter(editctrl.new, rssid, documenttype='rssview')

    def delete_all_posts(self, item):
        node = self.sharewin.get_node(item)
        rssid = node['data']['id']
        RssDb.init(Globals.rss_dbfile)

        RssDb.Data.delete_posts(rssid)

    def import_opml(self, filename):
        RssDb.init(Globals.rss_dbfile)

        import OPML
        opml = OPML.parse(filename)
        for o in opml.outlines:
            c = RssDb.Category.get_by(title=o['title'])
            if not c:
                c = RssDb.Category(o['title'])
                c.commit()
            for i in o.children:
                f = RssDb.Feed.get_by(category_id=c.id, link=i['xmlUrl'])
                if f:
                    f.title = i['title']
                    f.homelink = i.get('htmlUrl', '')
                    f.description = i.get('description', '')
                    f.commit()
                else:
                    c.feeds.append(RssDb.Feed(title=i['title'], link=i['xmlUrl'], homelink=i.get('htmlUrl', ''), imagelink='', description=i.get('description', '')))
        RssDb.objectstore.commit()
        item, node = self.sharewin.get_cur_node()
        self.sharewin.reset_cur_item()

    def export_opml(self, filename):
        RssDb.init(Globals.rss_dbfile)

        import OPML
        opml = OPML.OPML()
        outlines = OPML.OutlineList()
        for c in RssDb.Category.select():
            o = OPML.Outline()
            o['title'] = c.title
            outlines.add_outline(o)
            for f in c.feeds:
                d = OPML.Outline()
                d['description'] = f.description
                d['xmlUrl'] = f.link
                d['homeUrl'] = f.homelink
                d['title'] = f.title
                d['text'] = f.title
                d['version'] = 'RSS'
                d['type'] = 'rss'
                outlines.add_outline(d)
                outlines.close_outline()
            outlines.close_outline()
        opml.outlines = outlines.roots()
        opml.output(file(filename, "wb"))

    def cate_properties(self, item):
        node = self.sharewin.get_node(item)
        elements = [('string', 'caption', node['caption'], tr('Category Name:'), None)]
        from modules.EasyGuider import EasyDialog
        easy = EasyDialog.EasyDialog(self.sharewin, tr('Category Properties'), elements)
        values = None
        if easy.ShowModal() == wx.ID_OK:
            values = easy.GetValue()
        easy.Destroy()
        if values:
            cate_id = node['data']['id']
            node['caption'] = values['caption']
#            self.sharewin.save()
            c = RssDb.Category.get(cate_id)
            c.title = values['caption']
            c.commit()
            self.sharewin.tree.SetItemText(item, c.title)

    def feed_properties(self, item):
        node = self.sharewin.get_node(item)
        feed_id = node['data']['id']
        f = RssDb.Feed.get(feed_id)
        elements = [
            ('string', 'caption', f.title, tr('Feed Caption:'), None),
            ('string', 'url', f.link, tr('Feed URL:'), None),
            ('string', 'homeurl', f.homelink, tr('Home URL:'), None),
        ]
        from modules.EasyGuider import EasyDialog
        easy = EasyDialog.EasyDialog(self.sharewin, tr('Feed Properties'), elements)
        values = None
        if easy.ShowModal() == wx.ID_OK:
            values = easy.GetValue()
        easy.Destroy()
        if values:
            feed_id = node['data']['id']
            node['caption'] = values['caption']
            node['url'] = values['url']
            node['homeurl'] = values['homeurl']
#            self.sharewin.save()
            f.title = values['caption']
            f.link = values['url']
            f.homelink = values['homeurl']
            f.commit()
            self.refresh_feed_unread(feed_id)

    def add_feed(self):
        dialog = [
        ('string', 'caption', tr('Caption'), tr('Feed Caption:'), None),
        ('string', 'url', tr('New Feed URL'), tr('Feed URL:'), None),
        ]
        from modules.EasyGuider import EasyDialog
        easy = EasyDialog.EasyDialog(self.sharewin, tr('Add Feed'), dialog)
        values = None
        if easy.ShowModal() == wx.ID_OK:
            values = easy.GetValue()
        easy.Destroy()
        if values:
            #add feed to db
            item, node = self.sharewin.get_cur_node()
            RssDb.init(Globals.rss_dbfile)
            f = RssDb.Feed(category_id=node['data']['id'], title=values["caption"], link=values['url'])
            f.commit()
            data = {'type':'rss', 'level':'feed', 'caption':values["caption"], 'data':{'url':values['url'], 'homeurl':'', 'save':False, 'id':f.id}}
            obj = self.sharewin.addnode(item, data=data)
            self.add_feed_ids(node['data']['id'], f.id, obj)

    def parse_feed(self, f, feed):
        """f is instance of Feed, feed ia instance of feedparser"""
        feed_id = f.id
        if feed.has_key('image'):
            imagelink = feed['image'].get('url', f.imagelink)
        else:
            imagelink = f.imagelink
        caption = feed.get('title', f.title)
        if not caption:
            caption = f.title
        homelink = feed.get('link', f.homelink)
        f.imagelink = imagelink
        f.title = caption
        f.homelink = homelink
        f.commit()
        self.get_site_icon(homelink)

    def get_site_icon(self, url):
        if url:
            from urlparse import urlparse, urlunparse
            v = urlparse(url)
            domain = v[1]
            iconurl = urlunparse((v[0], domain, 'favicon.ico', '', '', ''))
            iconfile = os.path.join(self.iconpath, domain+'.ico')
            if not os.path.exists(iconfile):
                text = self.get_feed_text(iconurl)
                if text:
                    file(iconfile, 'wb').write(text)
                    nolog = wx.LogNull()
                    ok = wx.Image(iconfile, wx.BITMAP_TYPE_ANY).Ok()
                    del nolog
                    if not ok:
                        os.remove(iconfile)

    def get_feed_image(self, homeurl):
        image_id = self.RSS_FEED_IMAGE
        if homeurl:
            from urlparse import urlparse
            v = urlparse(homeurl)
            domain = v[1]
            _id = self.sharewin.get_image_id(domain)
            if _id != -1:
                image_id = _id
        return image_id

    def add_category(self):
        dialog = [
        ('string', 'caption', tr('New Category'), tr('Category Name:'), None),
        ]
        from modules.EasyGuider import EasyDialog
        easy = EasyDialog.EasyDialog(self.sharewin, tr('Input'), dialog)
        values = None
        if easy.ShowModal() == wx.ID_OK:
            values = easy.GetValue()
        easy.Destroy()
        if values:
            #add category to db
            import RssDb
            RssDb.init(Globals.rss_dbfile)
            category = RssDb.Category(title=values["caption"])
            category.save()

            data = {'type':'rss', 'level':'category', 'caption':values['caption'], 'data':{'save':False, 'id':category.id}}
            root, node = self.sharewin.get_cur_node()
            obj = self.sharewin.addnode(root, data=data)
            self.add_category_ids(category.id, obj)
