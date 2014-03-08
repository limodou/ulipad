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
from modules import common
from modules import makemenu
from modules import Mixin
import modules.meide as ui
from modules.wxctrl import FlatButtons

class OutlineBrowser(wx.Panel, Mixin.Mixin):

    __mixinname__ = 'outlinebrowser'

    popmenulist = []

    def __init__(self, parent, editor, autoexpand=True):
        self.initmixin()

        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        self.editor = editor
        self.autoexpand = autoexpand
        
        self.activeflag = False

        self.sizer = ui.VBox(namebinding='widget').create(self).auto_layout()
        self.btnRefresh = FlatButtons.FlatBitmapButton(self, -1, 
            common.getpngimage('images/classbrowserrefresh.gif'))
        self.sizer.add(self.btnRefresh).bind('click', self.OnRefresh)
        
        self.imagelist = wx.ImageList(16, 16)

        #add share image list
        self.imagefilenames = []
        self.imageids = {}
        self.callplugin('add_images', self.imagefilenames)
        for name, imagefile in self.imagefilenames:
            self.add_image(name, imagefile)

        style = wx.TR_SINGLE|wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS|wx.TR_TWIST_BUTTONS
        if wx.Platform == '__WXMSW__':
            style = style | wx.TR_ROW_LINES
        elif wx.Platform == '__WXGTK__':
            style = style | wx.TR_NO_LINES

        self.tree = wx.TreeCtrl(self, -1, style = style)
        self.tree.AssignImageList(self.imagelist)

        self.sizer.add(self.tree, proportion=1, flag=wx.EXPAND)
        self.root = self.tree.AddRoot('OutlineBrowser')

        self.nodes = {}
        self.ID = 1

#        wx.EVT_TREE_SEL_CHANGING(self.tree, self.tree.GetId(), self.OnChanging)
#        wx.EVT_TREE_SEL_CHANGED(self.tree, self.tree.GetId(), self.OnChanged)
#        wx.EVT_TREE_BEGIN_LABEL_EDIT(self.tree, self.tree.GetId(), self.OnBeginChangeLabel)
#        wx.EVT_TREE_END_LABEL_EDIT(self.tree, self.tree.GetId(), self.OnChangeLabel)
        wx.EVT_TREE_ITEM_ACTIVATED(self.tree, self.tree.GetId(), self.OnChanged)
#        wx.EVT_TREE_ITEM_RIGHT_CLICK(self.tree, self.tree.GetId(), self.OnRClick)
#        wx.EVT_RIGHT_UP(self.tree, self.OnRClick)
        wx.EVT_TREE_DELETE_ITEM(self.tree, self.tree.GetId(), self.OnDeleteItem)
#        wx.EVT_LEFT_DCLICK(self.tree, self.OnDoubleClick)
#        wx.EVT_TREE_ITEM_EXPANDING(self.tree, self.tree.GetId(), self.OnExpanding)
        wx.EVT_LEFT_DOWN(self.tree, self.OnLeftDown)
        wx.EVT_TREE_ITEM_GETTOOLTIP(self.tree, self.tree.GetId(), self.OnGetToolTip)
        wx.EVT_LEFT_DCLICK(self.tree, self.OnDoubleClick)
        self.tooltip_func = None

        #add init process
        self.callplugin('init', self)

#        self.SetSizer(self.sizer)
#        self.SetAutoLayout(True)
        self.sizer.auto_fit(0)

        self.popmenus = None

    def OnUpdateUI(self, event):
        self.callplugin('on_update_ui', self, event)
        
    def iter_children(self, parent=None, recursively=True):
        if not parent:
            parent = self.root
            
        child, cookie = self.tree.GetFirstChild(parent)
        while child:
            yield child
            if recursively:
                for node in self.iter_children(child, True):
                    yield node
            child, cookie = self.tree.GetNextChild(parent, cookie)

    def show(self):
        self.activeflag = True
#        self.tree.Freeze()

        childrens = []
        for node in self.iter_children(self.root, True):
            data = self.get_node(node)
            data['flag'] = True
            self.set_node(node, data)
            childrens.append(node)

        #call plugin
        self.callplugin('parsetext', self, self.editor)

        childrens.reverse()
        while childrens:
            node = childrens.pop(0)
            data = self.get_node(node)
            if data.get('flag', False) == True:
                self.tree.Delete(node)

#        self.tree.Thaw()
                
        self.activeflag = False

    def replacenode(self, parent, index, caption, imagenormal, imageexpand=None, 
        data=None, matchimage=None, sorttype=True):
        '''
        sorttype = 1 alphabet
        sorttype = 2 lineno
        '''
        if not parent:
            parent = self.root

        if not isinstance(caption, unicode):
            caption = unicode(caption, self.editor.locale)
            
        u_caption = caption.upper()
        lineno = data['data']
        status = 0
        if self.tree.GetChildrenCount(parent) == 0:
            flag = 'append'
            item = parent
        else:
            for i, node in enumerate(self.iter_children(parent, False)):
                flag = 'after'
                item = node
                img_index = self.tree.GetItemImage(node)
                if status ==0 and img_index < matchimage:
                    continue
                elif status == 0 and img_index == matchimage:
                    status = 1
                elif status == 0 and img_index > matchimage:
                    flag = 'before'
                    item = i
                    break
                elif status == 1 and img_index != matchimage:
                    flag = 'before'
                    item = i
                    break
                
                if sorttype:
                    node_caption = self.tree.GetItemText(node).upper()
                    if node_caption == u_caption:
                        flag = 'replace'
                        item = node
                        break
                    elif node_caption > u_caption:
                        flag = 'before'
                        item = i
                        break
                    
#            elif sorttype == 2:
#                if line == lineno:
#              
#            if self.tree.GetItemText(node) == caption:
#                flag = True
#                item = node
#                break

#        if item is self.root:
#            print flag, 'root', caption
#        else:
#            print flag, self.tree.GetItemText(item), caption
        if flag == 'replace':
            self.set_node(item, data)
            return self.tree.GetPyData(item), item
        else:
            return self.addnode(parent, item, caption, imagenormal, imageexpand, data, 
                flag)
            
    def addnode(self, parent, item, caption, imagenormal, imageexpand=None, data=None, pos='append'):
        if not parent:
            parent = self.root
        if pos == 'append':
            obj = self.tree.AppendItem(parent, caption)
        elif pos == 'before':
            obj = self.tree.InsertItemBefore(parent, item, caption)
        elif pos == 'after':
            obj = self.tree.InsertItem(parent, item, caption)
                
        _id = self.getid()
        self.tree.SetPyData(obj, _id)
        self.nodes[_id] = data
        if imagenormal > -1:
            self.tree.SetItemImage(obj, imagenormal, wx.TreeItemIcon_Normal)
        if imageexpand > -1:
            self.tree.SetItemImage(obj, imageexpand, wx.TreeItemIcon_Expanded)
        if parent!= self.root and not self.tree.IsExpanded(parent) and self.autoexpand:
            self.tree.Expand(parent)
        return _id, obj

    def set_node(self, item, data):
        if not self.is_ok(item): return
        _id = self.tree.GetPyData(item)
        self.nodes[_id] = data
        
    def get_node(self, item):
        if not self.is_ok(item): return
        _id = self.tree.GetPyData(item)
        data = self.nodes.get(_id, None)
        return data

    def getid(self):
        _id = self.ID
        self.ID += 1
        return _id

    def OnCloseWin(self):
        for klass in self.processors.values():
            if hasattr(klass, 'OnOutlineBrowserClose'):
                klass.OnOutlineBrowserClose()

    def OnChangeLabel(self, event):
        item = event.GetItem()
        if not self.is_ok(item): return
        if not self.execplugin('on_change_label', self, item, event.GetLabel()):
            event.Veto()

    def OnSelected(self, event):
        item = event.GetItem()
        if not self.is_ok(item): return
        self.callplugin('on_selected', self, item)

    def OnExpanding(self, event):
        item = event.GetItem()
        if not self.is_ok(item): return
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
            pop_menus = copy.deepcopy(OutlineBrowser.popmenulist + other_menus)
        else:
            pop_menus = copy.deepcopy(OutlineBrowser.popmenulist)
        self.popmenus = pop_menus = makemenu.makepopmenu(self, pop_menus)

        self.tree.PopupMenu(pop_menus, event.GetPosition())

    def OnDeleteItem(self, event):
        item = event.GetItem()
        if self.is_ok(item):
            try:
                del self.nodes[self.tree.GetPyData(item)]
            except:
                pass
        event.Skip()

    def OnBeginChangeLabel(self, event):
        item = event.GetItem()
        if not self.is_ok(item): return
        if not self.execplugin('on_begin_change_label', self, item):
            event.Veto()
            return
        else:
            event.Skip()

    def is_first_node(self, item):
        parent = self.tree.GetItemParent(item)
        return parent == self.root

    def OnLeftDown(self, event):
        pt = event.GetPosition();
        item, flags = self.tree.HitTest(pt)
        if flags == wx.TREE_HITTEST_ONITEMICON:
            if self.tree.ItemHasChildren(item):
                if self.tree.IsExpanded(item):
                    wx.CallAfter(self.tree.Collapse, item)
                else:
                    wx.CallAfter(self.tree.Expand, item)
                return
        event.Skip()

    def getTopObjects(self):
        objs = []
        child, cookie = self.tree.GetFirstChild(self.root)
        while child.IsOk():
            objs.append(child)
            child, cookie = self.tree.GetNextChild(self.root, cookie)
        return objs

    def OnMenu(self, event):
        self.callplugin('on_menu', self, event.GetId())

    def EditLabel(self, item):
        wx.CallAfter(self.tree.EditLabel, item)

    def OnChanged(self, event):
        item = event.GetItem()
        lineno = self.get_node(item)['data']
        if self.editor and not self.activeflag:
            wx.CallAfter(self.editor.goto, lineno-5)
            wx.CallAfter(self.editor.goto, lineno+10)
            wx.CallAfter(self.editor.goto, lineno)

    def OnChanging(self, event):
        item = event.GetOldItem()
        if not self.is_ok(item): return
        if not self.execplugin('on_changing', self, item):
            event.Skip()

    def reset_cur_item(self):
        item = self.tree.GetSelection()
        if self.is_ok(item):
            self.tree.Freeze()
            self.tree.CollapseAndReset(item)
            self.tree.Thaw()
            self.execplugin('on_expanding', self, item)

    def get_image_id(self, name):
        return self.imageids.get(name, -1)

    def add_image(self, name, imagefile):
        if not self.imageids.has_key(name):
            image = common.getpngimage(imagefile)
            self.imageids[name] = self.imagelist.Add(image)

    def is_ok(self, item):
        return item.IsOk() and item != self.root
    
    def set_tooltip_func(self, func):
        self.tooltip_func = func
    
    def OnGetToolTip(self, event):
        if self.tooltip_func:
            self.tooltip_func(self, event)
    
    def OnRefresh(self, event):
        self.show()
        
    def OnDoubleClick(self, event):
        pt = event.GetPosition()
        item, flags = self.tree.HitTest(pt)
        if flags in (wx.TREE_HITTEST_NOWHERE, wx.TREE_HITTEST_ONITEMRIGHT,
            wx.TREE_HITTEST_ONITEMLOWERPART, wx.TREE_HITTEST_ONITEMUPPERPART):
            for item in self.getTopObjects():
                self.tree.Collapse(item)
        else:
            event.Skip()
    