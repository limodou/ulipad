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
#   $Id: PrefDialog.py 1886 2007-02-01 12:58:18Z limodou $

import sys
import wx
import Preference
from modules import Mixin
from modules.Debug import error
from modules import common
from modules import meide as ui
try:
    set
except:
    from sets import Set as set

CONFIG_PREFIX = '_config_'

class TreeBookPanel(wx.Panel):
    def __init__(self, parent, id=-1, treewidth=150):
        wx.Panel.__init__(self, parent, id, size=wx.DefaultSize)
        
        self._id = 0
        self.last = None
        
        self.sizer = sizer = ui.HBox(namebinding='widget').create(self).auto_layout()
        sizer.add(ui.Tree(size=(treewidth, -1), style=wx.TR_HAS_BUTTONS
                               | wx.TR_LINES_AT_ROOT
                               | wx.TR_HIDE_ROOT), name='tree', flag=wx.EXPAND|wx.ALL)

        self.panels = sizer.add(ui.VBox)
        
        sizer.auto_fit(0)
        
        self.init()
        
    def get_id(self):
        self._id += 1
        return self._id
    
    def init(self):
        wx.EVT_TREE_SEL_CHANGED(self.tree, self.tree.GetId(), self.OnSelected)
        self.root = self.tree.AddRoot("The Root Item")
#        self.add_pages()
        
    def add_page(self, page, title='', parent=None):
        if not parent:
            parent = self.root
        child = self.tree.AppendItem(parent, title)
        if parent is not self.root:
            self.tree.Expand(parent)
        
        _id = self.get_id()
        name = 'page%d' % _id
        self.tree.SetPyData(child, _id)
        node = self.panels.add(page, proportion=1, flag=wx.EXPAND, name=name)
        self.panels.hide(name)
        return child
        
    def select(self, item=None):
        if not item:
            item, cookie = self.tree.GetFirstChild(self.root)
        if not self.is_ok(item): return
        self.tree.SelectItem(item)
        
    def OnSelected(self, event):
        item = event.GetItem()
        if self.last:
            self.panels.hide(self.last)
        self.last = self.show(item)
        
    def is_ok(self, item):
        return item and item.IsOk() and item is not self.root
    
    def show(self, item=None):
        if not item:
            item, cookie = self.tree.GetFirstChild(self.root)
        if not self.is_ok(item): return
        try:
            _id = self.tree.GetPyData(item)
            name = 'page%d' % _id
            self.panels.show(name)
            self.panels.layout()
            return name
        except:
            import traceback
            traceback.print_exc()
            
#    def add_pages(self):
#        for x in ('white', 'red', 'blue'):
#            child = self.add_page(ColorPanel(self, color=x), title=x)
#            for y in ('white', 'red', 'blue'):
#                last = self.add_page(ColorPanel(self, color=x), title=x, parent=child)
#        

class PrefDialog(wx.Dialog, Mixin.Mixin):
    __mixinname__ = 'prefdialog'

    def __init__(self, parent, size=(850, 500), style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER):
        self.initmixin()

        #config.ini
        self.ini = common.get_config_file_obj()
        
        wx.Dialog.__init__(self, parent, -1, title=tr("Preferences"), size=size, style=style)

        self.value_set = []
        self.pages = {}
        self.pagenames = {}
        self.values = {}

        self.parent = parent
        self.pref = self.parent.pref
        self.default_pref = Preference.Preference()
        
        self.box = box = ui.VBox(namebinding='widget')
        self.treebook = TreeBookPanel(self, -1)
        self.addPages(self.treebook)
        
        box.add(self.treebook, proportion=1, flag=wx.EXPAND|wx.ALL)

        box.add(wx.StaticLine(self), flag=wx.EXPAND|wx.ALL)
        
        buttons = [(tr('OK'), wx.ID_OK, 'btnOk'), 
            (tr('Cancel'), wx.ID_CANCEL, 'btnCancel'),
            (tr('Apply'), wx.ID_APPLY, 'btnApply')]
        box.add(ui.simple_buttons(buttons), flag=wx.ALIGN_CENTER|wx.BOTTOM)
        box.bind('btnOk', 'click', self.OnOk)
        box.bind('btnApply', 'click', self.OnApply)
        
        self.create_pages()
        
        self.callplugin('initpreference', self)
        ui.create(self, box, 0)
        self.btnOk.SetDefault()
        
        self.treebook.select()
        self.values = self.get_values()
        
        wx.EVT_UPDATE_UI(self, self.btnApply.GetId(), self.OnUpdateApply)

        self.callplugin('aftercreate', self)
        
    def addPages(self, treebook):
        for v in self.pref.preflist:
            pagename, order, kind, prefname, message, extern = v
            #add config options process
            prefvalue = None
            if prefname.startswith(CONFIG_PREFIX):
                section, key = prefname[len(CONFIG_PREFIX):].split('_')
                if section in self.ini and key in self.ini[section]:
                    prefvalue = self.ini[section][key]
            else:
                prefvalue = getattr(self.parent.pref, prefname, prefvalue)
            
            n = []
            for p in pagename.split('/'):
                n.append(p)
                page = self.create_page('/'.join(n))

            value = self.validate(prefname, kind, prefvalue)
            self.addItem(page, kind, prefname, prefvalue, message, extern)

    def create_page(self, pagename):
        self.pagenames[pagename] = sys.maxint
        if pagename not in self.pages:
            page = wx.ScrolledWindow(self.treebook, -1)
#            page.SetBackgroundColour('white')
            page.EnableScrolling(False, True)
            page.SetScrollbars(10, 10, 30, 30)
            self.pages[pagename] = page
            page.box = ui.SimpleGrid().create(page).auto_layout()
            self.value_set.append(page.box)
        else:
            page = self.pages[pagename]
            
        return page
    
    def create_pages(self):
        self.pagenames.update(self.pref.pages_order)
        plist = self.sort_pages(self.pagenames)
        parents = {}
        for parent_caption, order, title in plist:
            if not parent_caption:
                parent = None
            else:
                parent = parents.get(parent_caption, None)
            
            if parent_caption:
                pagename = '/'.join([parent_caption, title])
            else:
                pagename = title
            if pagename not in self.pages:
                continue
            child = self.treebook.add_page(self.pages[pagename], title, parent)
            parents[pagename] = child
        
    def sort_pages(self, plist):
        p = []
        for k, v in plist.items():
            if '/' in k:
                x = k.rsplit('/', 1)
                item = x[0], v, x[1]
            else:
                item = '', v, k
            p.append(item)
        p.sort()
        return p
        
    def addItem(self, page, kind, prefname, prefvalue, message, extern):
#        if self.execplugin("additem", self, page, kind, prefname, prefvalue, message, extern):
#            return
#        
        obj = None
        label = message
        kwargs = None
        if not isinstance(kind, str):
            obj = kind
            kwargs = extern
        else:
            if kind == 'check':
                obj = ui.Check(prefvalue, label=message)
                label = ''
#            elif kind == 'num':
#                obj = ui.IntSpin(prefvalue, max=100000, min=1, size=(60, -1))
            elif kind in ('num', 'int'):
                obj = ui.Int(prefvalue)
            elif kind == 'choice':
                obj = ui.SingleChoice(prefvalue, choices=extern)
            elif kind == 'text':
                obj = ui.Text(prefvalue)
            elif kind == 'password':
                obj = ui.Password(prefvalue)
            elif kind == 'openfile':
                obj = ui.OpenFile(prefvalue)
            elif kind == 'opendir':
                obj = ui.Dir(prefvalue)
            elif kind == 'button':
                label = ''
                func = getattr(self, extern)
                obj = ui.Button(message).bind('click', func)
                
        if not kwargs:
            if isinstance(extern, dict):
                span = extern.get('span', True)
            else:
                if label:
                    span = False
                else:
                    span = True
            page.box.add(label, obj, name=prefname, span=span)
        else:
            page.box.add(label, obj, name=prefname, **kwargs)

    def validate(self, name, kind, value):
        if kind == 'check':
            return bool(value)
        elif kind == 'num' or kind == 'int':
            try:
                value = int(value)
            except:
                error.traceback()
                error.info((name, kind, value))
                return getattr(self.default_pref, name)
        else:
            return value

    def OnOk(self, event):
        self.OnApply(event)
        event.Skip()
        
    def get_values(self):
        values = {}
        for b in self.value_set:
            values.update(b.GetValue())
        return values
    
    def OnApply(self, event):
        values = self.get_values()
        config = []
        for name, v in values.items():
            #if a name starts with CONFIG_PREFIX, so this value should be saved
            #in config.ini file, but not preference file
            if name.startswith(CONFIG_PREFIX):
                config.append((name, v))
            else:
                setattr(self.parent.pref, name, v)
        self.parent.pref.save()
        
        #process config options
        for name, v in config:
            section, key = name[len(CONFIG_PREFIX):].split('_')
            self.ini[section][key] = v
        self.ini.save()
        
        #you can use self.values to get the old value, use pref to get the latest values
        self.callplugin('savepreferencevalues', self.values)
        self.callplugin('savepreference', self.parent, self.parent.pref)
        self.values = values
        #self.parent = mainframe

    def OnUpdateApply(self, event):
        values = self.get_values()
        a = set(self._plain_value(self.values))
        b = set(self._plain_value(values))
        self.btnApply.Enable(bool(a-b))
        
    def _plain_value(self, v):
        if isinstance(v, (list, tuple)):
            s = []
            for i in v:
                s.append(self._plain_value(i))
            return s
        elif isinstance(v, dict):
            s = []
            for k, _v in v.items():
                s.append((self._plain_value(k), self._plain_value(_v)))
            s.sort()
            return s
        else:
            return v
                