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

from modules import Mixin
import wx
import images
from modules import Globals
import os

popmenulist = [ ('IDPM_ADD',
    [
        (100, 'IDPM_ADD_RSSREADER', tr('RSS Reader'), wx.ITEM_NORMAL, 'OnAddRssReader', ''),
    ]),
]
Mixin.setMixin('sharewin', 'popmenulist', popmenulist)

def add_process_class(type, win, proc_dict):
    if type == 'rss':
        from RssReader import RssReader
        proc_dict['rss'] = RssReader(win)
Mixin.setPlugin('sharewin', 'add_process_class', add_process_class)

def add_images(images):
    s = [
        ('RSS_ROOT_IMAGE', 'rss.gif'),
        ('RSS_CATEGORY_IMAGE', 'category.gif'),
        ('RSS_FEED_IMAGE', 'feed.gif'),
        ('RSS_RUN1', 'run1.gif'),
        ('RSS_RUN2', 'run2.gif'),
        ('RSS_RUN3', 'run3.gif'),
        ('RSS_ERROR', 'error.gif'),
        ]
    for name, f in s:
        images[name] = os.path.join(Globals.workpath, 'plugins/rssreader/%s' % f)
Mixin.setPlugin('sharewin', 'add_images', add_images)

def OnAddRssReader(win, event):
    data = {'type':'rss', 'level':'root', 'caption':tr('RSS Reader'), 'normal_imagename':'RSS_ROOT_IMAGE', 'expand_imagename':'RSS_ROOT_IMAGE', 'data':{'save':True}}
    item = win.addnode(None, data=data, save=True)
    win.tree.SetItemHasChildren(item, True)
Mixin.setMixin('sharewin', 'OnAddRssReader', OnAddRssReader)

def init(pref):
    pref.rss_dbfile = 'rss.db'
    pref.rss_refresh_time = 10  #minute
    pref.rss_read_time = 2 #second
    pref.rss_start = True #refresh as startup
    pref.rss_set_all_read = True
    pref.rss_auto_dig = True
Mixin.setPlugin('preference', 'init', init)

preflist = [
    (tr('Rss Reader'), 100, 'text', 'rss_dbfile', tr('Rss Reader database file'), None),
    (tr('Rss Reader'), 110, 'num', 'rss_refresh_time', tr('How long to refresh the feeds'), None),
    (tr('Rss Reader'), 120, 'num', 'rss_read_time', tr('How long to set readed flag as you are reading a post'), None),
    (tr('Rss Reader'), 130, 'check', 'rss_start', tr('Refresh all the feeds as startup'), None),
    (tr('Rss Reader'), 140, 'check', 'rss_set_all_read', tr('As leaving a feed, set all posts read'), None),
    (tr('Rss Reader'), 150, 'check', 'rss_auto_dig', tr('As dealing a feed, auto parse the feed information'), None),
]
Mixin.setMixin('preference', 'preflist', preflist)

def other_popup_menu(sharewin, menus):
    v = sharewin.get_cur_node()
    if v:
        item, data = v
        if data.get('type', '') == 'rss' and data.get('level', '') == 'root':
            menus.extend([(None, #parent menu id
                [
                    (900, '', '-', wx.ITEM_SEPARATOR, None, ''),
                    (910, 'IDPM_RSS_ADD_CATEGORY', tr('Add Category'), wx.ITEM_NORMAL, 'OnMenu', ''),
                    (920, 'IDPM_RSS_FRESH_ROOT', tr('Refresh'), wx.ITEM_NORMAL, 'OnMenu', ''),
                    (930, '', '-', wx.ITEM_SEPARATOR, None, ''),
                    (940, 'IDPM_RSS_IMPORT', tr('Import OPML'), wx.ITEM_NORMAL, 'OnMenu', ''),
                    (950, 'IDPM_RSS_EXPORT', tr('Export OPML'), wx.ITEM_NORMAL, 'OnMenu', ''),
                    (960, '', '-', wx.ITEM_SEPARATOR, None, ''),
                    (970, 'IDPM_RSS_RECREATE', tr('ReCreate Database'), wx.ITEM_NORMAL, 'OnMenu', ''),
                ]),
            ])
        elif data.get('type', '') == 'rss' and data.get('level', '') == 'category':
            menus.extend([(None, #parent menu id
                [
                    (900, '', '-', wx.ITEM_SEPARATOR, None, ''),
                    (910, 'IDPM_RSS_ADD_FEED', tr('Add Feed'), wx.ITEM_NORMAL, 'OnMenu', ''),
                    (920, 'IDPM_RSS_FRESH_CATEGORY', tr('Refresh'), wx.ITEM_NORMAL, 'OnMenu', ''),
                    (925, 'IDPM_RSS_STOP_CATEGORY', tr('Stop Refresh'), wx.ITEM_NORMAL, 'OnMenu', ''),
                    (930, '', '-', wx.ITEM_SEPARATOR, None, ''),
                    (940, 'IDPM_RSS_CATE_PROPERTY', tr('Properties'), wx.ITEM_NORMAL, 'OnMenu', ''),
                ]),
            ])
        elif data.get('type', '') == 'rss' and data.get('level', '') == 'feed':
            menus.extend([(None, #parent menu id
                [
                    (900, '', '-', wx.ITEM_SEPARATOR, None, ''),
                    (910, 'IDPM_RSS_FRESH_FEED', tr('Refresh'), wx.ITEM_NORMAL, 'OnMenu', ''),
                    (915, 'IDPM_RSS_STOP_FEED', tr('Stop Refresh'), wx.ITEM_NORMAL, 'OnMenu', ''),
                    (920, 'IDPM_RSS_MAKE_READ', tr('Make All Posts Read'), wx.ITEM_NORMAL, 'OnMenu', ''),
                    (930, 'IDPM_RSS_DELETEALL', tr('Delete All Posts'), wx.ITEM_NORMAL, 'OnMenu', ''),
                    (940, '', '-', wx.ITEM_SEPARATOR, None, ''),
                    (950, 'IDPM_RSS_FEED_PROPERTY', tr('Properties'), wx.ITEM_NORMAL, 'OnMenu', ''),
                ]),
            ])
Mixin.setPlugin('sharewin', 'other_popup_menu', other_popup_menu)

def on_menu(win, menu_id):
    if hasattr(win, 'IDPM_RSS_ADD_CATEGORY') and menu_id == win.IDPM_RSS_ADD_CATEGORY:
        klass = win.get_cur_class()
        if klass:
            klass.add_category()
    elif hasattr(win, 'IDPM_RSS_ADD_FEED') and menu_id == win.IDPM_RSS_ADD_FEED:
        klass = win.get_cur_class()
        if klass:
            klass.add_feed()
    elif hasattr(win, 'IDPM_RSS_FRESH_FEED') and menu_id == win.IDPM_RSS_FRESH_FEED:
        v = win.get_cur_node()
        if v:
            item, node = v
            klass = win.get_class(node)
            if klass:
                klass.fresh_feed(item)
    elif hasattr(win, 'IDPM_RSS_FRESH_CATEGORY') and menu_id == win.IDPM_RSS_FRESH_CATEGORY:
        v = win.get_cur_node()
        if v:
            item, node = v
            klass = win.get_class(node)
            if klass:
                klass.fresh_category(item)
    elif hasattr(win, 'IDPM_RSS_MAKE_READ') and menu_id == win.IDPM_RSS_MAKE_READ:
        v = win.get_cur_node()
        if v:
            item, node = v
            klass = win.get_class(node)
            if klass:
                klass.set_all_read(item)
                klass.change_feed(item)
    elif hasattr(win, 'IDPM_RSS_DELETEALL') and menu_id == win.IDPM_RSS_DELETEALL:
        v = win.get_cur_node()
        if v:
            item, node = v
            klass = win.get_class(node)
            if klass:
                klass.delete_all_posts(item)
                klass.change_feed(item)
                klass.refresh_feed_unread(node['data']['id'])
    elif hasattr(win, 'IDPM_RSS_IMPORT') and menu_id == win.IDPM_RSS_IMPORT:
        dlg = wx.FileDialog(win, tr("Choose a OPML filename"), wildcard='*.opml', style=wx.OPEN|wx.FILE_MUST_EXIST|wx.CHANGE_DIR)
        filename = None
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
        dlg.Destroy()
        if filename:
            klass = win.get_cur_class()
            if klass:
                import common
                common.setmessage(Globals.mainframe, tr('Parsing OPML...'))
                klass.import_opml(dlg.GetFilename())
    elif hasattr(win, 'IDPM_RSS_EXPORT') and menu_id == win.IDPM_RSS_EXPORT:
        dlg = wx.FileDialog(win, tr("Choose a OPML filename"), wildcard='*.opml', style=wx.SAVE|wx.CHANGE_DIR)
        filename = None
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
        dlg.Destroy()
        if filename:
            klass = win.get_cur_class()
            if klass:
                import common
                common.setmessage(Globals.mainframe, tr('Saving OPML...'))
                klass.export_opml(dlg.GetFilename())
    elif hasattr(win, 'IDPM_RSS_STOP_FEED') and menu_id == win.IDPM_RSS_STOP_FEED:
        klass = win.get_cur_class()
        item, node = win.get_cur_node()
        if klass:
            klass.stop_feed(item)
    elif hasattr(win, 'IDPM_RSS_STOP_CATEGORY') and menu_id == win.IDPM_RSS_STOP_CATEGORY:
        klass = win.get_cur_class()
        item, node = win.get_cur_node()
        if klass:
            klass.stop_category(item)
    elif hasattr(win, 'IDPM_RSS_RECREATE') and menu_id == win.IDPM_RSS_RECREATE:
        ret = wx.MessageBox(tr("Do you really want to re-create the rss database?\nAll data in it will be lost!"), tr("Confirm"),
            style=wx.YES_NO)
        if ret == wx.YES:
            import RssDb
            RssDb.init(Globals.rss_dbfile, create=True)
            item, node = win.get_cur_node()
            win.reset_cur_item()
            import common
            common.showmessage(win, tr("Rss database is created successfully!"))
    elif hasattr(win, 'IDPM_RSS_CATE_PROPERTY') and menu_id == win.IDPM_RSS_CATE_PROPERTY:
        item, node = win.get_cur_node()
        klass = win.get_cur_class()
        if klass:
            klass.cate_properties(item)
    elif hasattr(win, 'IDPM_RSS_FEED_PROPERTY') and menu_id == win.IDPM_RSS_FEED_PROPERTY:
        item, node = win.get_cur_node()
        klass = win.get_cur_class()
        if klass:
            klass.feed_properties(item)
Mixin.setPlugin('sharewin', 'on_menu', on_menu)

def on_expanding(sharewin, item):
    if sharewin.tree.GetChildrenCount(item) == 0: #need expand
        data = sharewin.get_node(item)
        if data:
            if data.get('type', '') == 'rss' and data.get('level', '') == 'root':
                klass = sharewin.get_class(data)
                if klass:
                    klass.startup(item)
                return True
Mixin.setPlugin('sharewin', 'on_expanding', on_expanding)

from RssPanel import RssPanel

panellist = {'rssview':RssPanel}
Mixin.setMixin('editctrl', 'panellist', panellist)

def on_changed(sharewin, item):
    data = sharewin.get_node(item)
    if data:
        if data.get('type', '') == 'rss' and data.get('level', '') == 'feed':
            klass = sharewin.get_class(data)
            if klass:
                klass.change_feed(item)
Mixin.setPlugin('sharewin', 'on_changed', on_changed)

def on_changing(sharewin, item):
    data = sharewin.get_node(item)
    if data:
        if data.get('type', '') == 'rss' and data.get('level', '') == 'feed':
            klass = sharewin.get_class(data)
            if klass:
                if Globals.mainframe.pref.rss_set_all_read:
                    klass.set_all_read(item)
Mixin.setPlugin('sharewin', 'on_changing', on_changing)

pageimagelist = {
    'rssview': images.getFeedBitmap()
}
Mixin.setMixin('editctrl', 'pageimagelist', pageimagelist)
