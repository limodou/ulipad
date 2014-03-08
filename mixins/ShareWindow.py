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
#   $Id$

import wx
import os.path
from modules import common
from modules import makemenu
from modules import Mixin
from modules.Debug import error


class ShareWindow(wx.Panel, Mixin.Mixin):

    __mixinname__ = 'sharewin'

    popmenulist = [ (None,
        [
            (100, 'IDPM_ADD', tr('Add ...'), wx.ITEM_NORMAL, '', ''),
            (110, 'IDPM_DEL', tr('Delete'), wx.ITEM_NORMAL, 'OnDelete', ''),
        ]),
    ]

    def __init__(self, parent, mainframe):
        self.initmixin()
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        self.mainframe = mainframe
        self.pref = mainframe.pref
        if not hasattr(self.pref, 'share_nodes'):
            self.pref.share_nodes = []

        self.processors = {}
#        self.callplugin('add_process_class', self, self.processors)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.shareimagelist = imagelist = wx.ImageList(16, 16)

        #add share image list
        self.imagefiles = {}
        self.imageids = {}
        self.callplugin('add_images', self.imagefiles)
        for name, imagefile in self.imagefiles.items():
            self.add_image(name, imagefile)

        self.tree = wx.TreeCtrl(self, -1, style = wx.TR_EDIT_LABELS|wx.TR_SINGLE|wx.TR_TWIST_BUTTONS|wx.TR_HAS_BUTTONS|wx.TR_ROW_LINES|wx.TR_HIDE_ROOT)
        self.tree.SetImageList(self.shareimagelist)

        self.sizer.Add(self.tree, 1, wx.EXPAND)
        self.root = self.tree.AddRoot('Share')

        self.nodes = {}
        self.ID = 1

        self.read()

        wx.EVT_TREE_SEL_CHANGING(self.tree, self.tree.GetId(), self.OnChanging)
        wx.EVT_TREE_SEL_CHANGED(self.tree, self.tree.GetId(), self.OnChanged)
        wx.EVT_TREE_BEGIN_LABEL_EDIT(self.tree, self.tree.GetId(), self.OnBeginChangeLabel)
        wx.EVT_TREE_END_LABEL_EDIT(self.tree, self.tree.GetId(), self.OnChangeLabel)
        wx.EVT_TREE_ITEM_ACTIVATED(self.tree, self.tree.GetId(), self.OnSelected)
        wx.EVT_TREE_ITEM_RIGHT_CLICK(self.tree, self.tree.GetId(), self.OnRClick)
        wx.EVT_RIGHT_UP(self.tree, self.OnRClick)
        wx.EVT_TREE_DELETE_ITEM(self.tree, self.tree.GetId(), self.OnDeleteItem)
        wx.EVT_LEFT_DCLICK(self.tree, self.OnDoubleClick)
        wx.EVT_TREE_ITEM_EXPANDING(self.tree, self.tree.GetId(), self.OnExpanding)

        from modules import Id
        wx.EVT_UPDATE_UI(self, Id.makeid(self, 'IDPM_DEL'), self.OnUpdateUI)

        #add init process
        self.callplugin('init', self)

        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)

        self.popmenus = None

    def OnUpdateUI(self, event):
        _id = event.GetId()
        item = self.tree.GetSelection()
        if _id == self.IDPM_DEL:
            event.Enable(item.IsOk())
            return
        self.callplugin('on_update_ui', self, event)

    def addnode(self, parentnode, data, save=False):
        klass = self.processors.get(data.get('type', ''), None)
        if klass:
            n_image_index = klass.get_image_index(data, wx.TreeItemIcon_Normal)
            e_image_index = klass.get_image_index(data, wx.TreeItemIcon_Expanded)
        else:
            n_image_index = self.imageids.get(data.get('normal_imagename', ''), -1)
            e_image_index = self.imageids.get(data.get('expand_imagename', ''), -1)

        _id, obj = self.addtreenode(parentnode, data.get('caption', ''), n_image_index, e_image_index)
        self.nodes[_id] = data
        if save:
            self.save()
        return obj

    def addtreenode(self, parent, caption, imagenormal, imageexpand=None):
        if not parent:
            parent = self.root
        obj = self.tree.AppendItem(parent, caption)
        _id = self.getid()
        self.tree.SetPyData(obj, _id)
        if imagenormal > -1:
            self.tree.SetItemImage(obj, imagenormal, wx.TreeItemIcon_Normal)
        if imageexpand > -1:
            self.tree.SetItemImage(obj, imageexpand, wx.TreeItemIcon_Expanded)
        if parent!= self.root and not self.tree.IsExpanded(parent):
            self.tree.Expand(parent)
        return _id, obj

    def get_cur_node(self):
        item = self.tree.GetSelection()
        if not item.IsOk(): return
        _id = self.tree.GetPyData(item)
        return item, self.nodes.get(_id, None)

    def get_node(self, item):
        if not item.IsOk(): return
        _id = self.tree.GetPyData(item)
        return self.nodes.get(_id, None)

    def get_class(self, node):
        if node:
            if not self.processors.has_key(node.get('type', '')):
                self.callplugin('add_process_class', node['type'], self, self.processors)
            return self.processors.get(node.get('type', ''), None)

    def getid(self):
        _id = self.ID
        self.ID += 1
        return _id

    def OnCloseWin(self):
        for klass in self.processors.values():
            if hasattr(klass, 'OnSharewinClose'):
                klass.OnSharewinClose()

    def OnChangeLabel(self, event):
        item = event.GetItem()
        if not item.IsOk(): return
        if not self.execplugin('on_change_label', self, item, event.GetLabel()):
            event.Veto()

    def OnSelected(self, event):
        item = event.GetItem()
        if not item.IsOk(): return
        self.import_class(item)
        self.callplugin('on_selected', self, item)

    def OnExpanding(self, event):
        item = event.GetItem()
        if not item.IsOk(): return
        if not self.execplugin('on_expanding', self, item):
            event.Skip()

    def OnRClick(self, event):
        other_menus = []
        if self.popmenus:
            self.popmenus.Destroy()
            self.popmenus = None
        self.callplugin('other_popup_menu', self, other_menus)
        import copy
        if other_menus:
            pop_menus = copy.deepcopy(ShareWindow.popmenulist + other_menus)
        else:
            pop_menus = copy.deepcopy(ShareWindow.popmenulist)
        self.popmenus = pop_menus = makemenu.makepopmenu(self, pop_menus)

        self.tree.PopupMenu(pop_menus)

    def OnDeleteItem(self, event):
        item = event.GetItem()
        if item.IsOk():
            del self.nodes[self.tree.GetPyData(item)]
        event.Skip()

    def OnBeginChangeLabel(self, event):
        item = event.GetItem()
        if not item.IsOk(): return
        if not self.execplugin('on_begin_change_label', self, item):
            event.Veto()
            return
        else:
            event.Skip()

    def is_first_node(self, item):
        parent = self.tree.GetItemParent(item)
        return parent == self.root

    def OnDoubleClick(self, event):
        pt = event.GetPosition()
        item, flags = self.tree.HitTest(pt)
        if flags in (wx.TREE_HITTEST_NOWHERE, wx.TREE_HITTEST_ONITEMRIGHT,
            wx.TREE_HITTEST_ONITEMLOWERPART, wx.TREE_HITTEST_ONITEMUPPERPART):
            for item in self.getTopObjects():
                self.tree.Collapse(item)
        else:
            self.import_class(item)
            if self.tree.GetChildrenCount(item) == 0:
                if not self.callplugin('on_expanding', self, item):
                    event.Skip()
            else:
                event.Skip()

    def getTopObjects(self):
        objs = []
        child, cookie = self.tree.GetFirstChild(self.root)
        while child.IsOk():
            objs.append(child)
            child, cookie = self.tree.GetNextChild(self.root, cookie)
        return objs

    def save(self):
        s = []
        child, cookie = self.tree.GetFirstChild(self.root)
        while child.IsOk():
            item = self.nodes.get(self.tree.GetPyData(child), None)
            if item and item['data'].has_key("save") and item['data']["save"]:
                data = (item, [])
                s.append(data)
                self._save(child, data[1])
            child, cookie = self.tree.GetNextChild(self.root, cookie)
        self.pref.share_nodes = s
        self.pref.save()

    def _save(self, parent, save_list):
        child, cookie = self.tree.GetFirstChild(parent)
        while child.IsOk():
            item = self.nodes.get(self.tree.GetPyData(child), None)
            if item and item['data'].has_key("save") and item['data']["save"]:
                data = (item, [])
                save_list.append(data)
                self._save(child, data[1])
            child, cookie = self.tree.GetNextChild(parent, cookie)

    def read(self):
        if hasattr(self.pref, 'share_nodes'):
            for i in self.pref.share_nodes:
                data, child = i
                node = self.addnode(self.root, data, save=False)
                if node and child:
                    self._read(node, child)

            self.pref.save()

    def _read(self, parent, nodes):
        for i in nodes:
            data, child = i
            node = self.addnode(parent, data, save=False)
            if node and child:
                self._read(node, child)

    def OnMenu(self, event):
        self.callplugin('on_menu', self, event.GetId())

    def EditLabel(self, item):
        wx.CallAfter(self.tree.EditLabel, item)

    def OnDelete(self, event):
        if wx.MessageBox(tr('Do you realy want to delete current item?'), tr('Message'), style=wx.YES_NO|wx.ICON_QUESTION) == wx.YES:
            v = self.get_cur_node()
            if v:
                item, node = v
                klass = self.get_class(node)
                if not klass or klass.delete(node):
                    self.tree.Freeze()
                    self.tree.DeleteChildren(item)
                    self.tree.Delete(item)
                    self.tree.Thaw()
                    self.save()

    def OnChanged(self, event):
        item = event.GetItem()
        if not item.IsOk(): return
        self.callplugin('on_changed', self, item)

    def OnChanging(self, event):
        item = event.GetOldItem()
        if not item.IsOk(): return
        if not self.execplugin('on_changing', self, item):
            event.Skip()

    def get_cur_class(self):
        v = self.get_cur_node()
        if v:
            item, node = v
            klass = self.get_class(node)
            return klass
        return None

    def reset_cur_item(self):
        item = self.tree.GetSelection()
        if item.IsOk():
            self.tree.Freeze()
            self.tree.CollapseAndReset(item)
            self.tree.Thaw()
            self.execplugin('on_expanding', self, item)
            self.save()

    def import_class(self, item):
        if self.is_first_node(item):
            node = self.get_node(item)
            klass = self.get_class(node)
            if not klass:
                self.callplugin('add_process_class', node['type'], self, self.processors)

    def get_image_id(self, name):
        return self.imageids.get(name, -1)

    def add_image(self, name, imagefile):
        if not self.imagefiles.has_key(name):
            self.imagefiles[name] = imagefile
        if not self.imageids.has_key(name):
            image = common.getpngimage(imagefile)
            self.imageids[name] = self.shareimagelist.Add(image)
