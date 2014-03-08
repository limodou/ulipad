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
#   $Id: DirBrowser.py 2129 2007-07-19 09:37:15Z limodou $
#
#   Update
#   2008/08/25
#       * improve refresh algorithm

import wx
import os
import copy
import shutil
from modules import common
from modules import makemenu
from modules import Mixin
from modules.Debug import error
from modules import Globals

class DirBrowser(wx.Panel, Mixin.Mixin):

    __mixinname__ = 'dirbrowser'

    FILE_NODE = 'file'
    DIR_NODE = 'dir'

    popmenulist = [ (None,
        [
            (80, 'IDPM_CUT', tr('Cut')+'\tCtrl+X', wx.ITEM_NORMAL, 'OnDirCut', ''),
            (81, 'IDPM_COPY', tr('Copy')+'\tCtrl+C', wx.ITEM_NORMAL, 'OnDirCopy', ''),
            (82, 'IDPM_PASTE', tr('Paste')+'\tCtrl+V', wx.ITEM_NORMAL, 'OnDirPaste', ''),
            (90, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (100, 'IDPM_ADD', tr('Add Directory'), wx.ITEM_NORMAL, '', ''),
            (110, 'IDPM_CLOSE', tr('Close Directory'), wx.ITEM_NORMAL, 'OnCloseDirectory', ''),
            (115, 'IDPM_SETPROJ', tr('Set Project'), wx.ITEM_NORMAL, 'OnSetProject', ''),
            (116, 'IDPM_SEARCHDIR', tr('Search Directory'), wx.ITEM_NORMAL, 'OnSearchDir', ''),
            (117, 'IDPM_COMMANDLINE', tr('Open Command Window Here'), wx.ITEM_NORMAL, 'OnCommandWindow', ''),
            (119, 'IDPM_PRINTDIR', tr('Print Directory Tree'), wx.ITEM_NORMAL, 'OnPrintDir', ''),
            (120, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (125, 'IDPM_OPENDEFAULT', tr('Open with Default Editor'), wx.ITEM_NORMAL, 'OnOpenDefault', ''),
            (130, 'IDPM_ADDPATH', tr('Create Sub Directory'), wx.ITEM_NORMAL, 'OnAddSubDir', ''),
            (140, 'IDPM_ADDFILE', tr('Create File'), wx.ITEM_NORMAL, 'OnAddFile', ''),
            (150, 'IDPM_RENAME', tr('Rename'), wx.ITEM_NORMAL, 'OnRename', ''),
            (160, 'IDPM_DELETE', tr('Delete')+'\tDel', wx.ITEM_NORMAL, 'OnDelete', ''),
            (170, 'IDPM_REFRESH', tr('&Refresh')+'\tF5', wx.ITEM_NORMAL, 'OnRefresh', ''),
            (180, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (190, 'IDPM_IGNORETHIS', tr('Ignore This'), wx.ITEM_NORMAL, 'OnIgnoreThis', ''),
            (200, 'IDPM_IGNORETHISTYPE', tr('Ignore This Type'), wx.ITEM_NORMAL, 'OnIgnoreThisType', ''),
        ]),
        ('IDPM_ADD',
        [
            (99, 'IDPM_ADD_CURDIR', tr('Add Current Directory'), wx.ITEM_NORMAL, 'OnAddCurrentPath', ''), 
            (100, 'IDPM_ADD_NEWDIR', tr('Open New Directory'), wx.ITEM_NORMAL, 'OnAddNewPath', ''),
#            (110, 'IDPM_ADD_ULIPADWORK', tr('Open UliPad Work Path'), wx.ITEM_NORMAL, 'OnAddUliPadWorkPath', ''),
#            (120, 'IDPM_ADD_ULIPADUSER', tr('Open UliPad User Path'), wx.ITEM_NORMAL, 'OnAddUliPadUserPath', ''),
            (130, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (140, 'IDPM_ADD_CLEAN', tr('Clear Recent Directories'), wx.ITEM_NORMAL, 'OnCleanDirectories', ''),
            (150, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (160, 'IDPM_ADD_DIRS', tr('(Empty)'), wx.ITEM_NORMAL, '', ''),
        ]),
    ]
    if wx.Platform == '__WXMSW__':
        popmenulist.extend([(None,
        [
            (118, 'IDPM_EXPLORER', tr('Open Explorer Window Here'), wx.ITEM_NORMAL, 'OnExplorerWindow', ''),
        ]),
    ]
        )

    project_names = []

    def __init__(self, parent, mainframe, dirs=None):
        self.initmixin()
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        self.mainframe = mainframe
        self.pref = mainframe.pref

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        imagelist = mainframe.dirbrowser_imagelist
        self.dirbrowserimagelist = wx.ImageList(16, 16)
        self.close_image = self.add_image(common.getpngimage(imagelist['close']))
        self.open_image = self.add_image(common.getpngimage(imagelist['open']))
        self.item_image = self.add_image(common.getpngimage(imagelist['item']))

        self.deal_file_images()

        style = wx.TR_EDIT_LABELS|wx.TR_SINGLE|wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS|wx.TR_TWIST_BUTTONS
        if wx.Platform == '__WXMSW__':
            style = style | wx.TR_ROW_LINES
        elif wx.Platform == '__WXGTK__':
            style = style | wx.TR_NO_LINES

        self.tree = wx.TreeCtrl(self, -1, style = style)
        self.tree.SetImageList(self.dirbrowserimagelist)

        self.sizer.Add(self.tree, 1, wx.EXPAND)
        self.root = self.tree.AddRoot('DirBrowser')

        #add drop target
        self.SetDropTarget(MyFileDropTarget(self))


#        wx.EVT_TREE_SEL_CHANGED(self.tree, self.tree.GetId(), self.OnChanged)
        wx.EVT_TREE_BEGIN_LABEL_EDIT(self.tree, self.tree.GetId(), self.OnBeginChangeLabel)
        wx.EVT_TREE_END_LABEL_EDIT(self.tree, self.tree.GetId(), self.OnChangeLabel)
        wx.EVT_TREE_ITEM_ACTIVATED(self.tree, self.tree.GetId(), self.OnSelected)
#        wx.EVT_TREE_ITEM_RIGHT_CLICK(self.tree, self.tree.GetId(), self.OnRClick)
        wx.EVT_RIGHT_UP(self.tree, self.OnRClick)
        wx.EVT_RIGHT_DOWN(self.tree, self.OnRightDown)
        wx.EVT_TREE_DELETE_ITEM(self.tree, self.tree.GetId(), self.OnDeleteItem)
        wx.EVT_LEFT_DCLICK(self.tree, self.OnDoubleClick)
        wx.EVT_TREE_ITEM_EXPANDING(self.tree, self.tree.GetId(), self.OnExpanding)
        wx.EVT_KEY_DOWN(self.tree, self.OnKeyDown)
        wx.EVT_CHAR(self.tree, self.OnChar)

        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)

        self.nodes = {}
        self.ID = 1
        self.cache = None

        #@add_project
        self.callplugin_once('add_project', DirBrowser.project_names)

        pop_menus = copy.deepcopy(DirBrowser.popmenulist)
        self.popmenus = makemenu.makepopmenu(self, pop_menus)

        self.dirmenu_ids = [self.IDPM_ADD_DIRS]

        wx.EVT_UPDATE_UI(self, self.IDPM_CUT, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_COPY, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_PASTE, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_CLOSE, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_ADDFILE, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_ADDPATH, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_DELETE, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_REFRESH, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_RENAME, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_IGNORETHIS, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_IGNORETHISTYPE, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_OPENDEFAULT, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_SETPROJ, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_COMMANDLINE, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_PRINTDIR, self.OnUpdateUI)

        self.popmenus = None

        if dirs:
            for i in dirs:
                self.addpath(i, False)

        self.callplugin('init', self)

    def OnUpdateUI(self, event):
        eid = event.GetId()
        item = self.tree.GetSelection()
        if not self.is_ok(item):
            event.Enable(self.is_ok(item))
            return
        if eid in [self.IDPM_CUT, self.IDPM_COPY]:
            event.Enable(not self.is_first_node(item))
        elif eid == self.IDPM_PASTE:
            event.Enable(bool(self.cache))
        elif eid == self.IDPM_CLOSE:
            if self.is_first_node(item):
                event.Enable(True)
            else:
                event.Enable(False)
        elif eid in [self.IDPM_ADDFILE, self.IDPM_ADDPATH]:
            event.Enable(self.is_ok(item))
        elif eid in [self.IDPM_COMMANDLINE, self.IDPM_PRINTDIR]:
            filename = self.get_node_filename(item)
            if os.path.isdir(filename):
                event.Enable(True)
            else:
                event.Enable(False)
        elif eid in [self.IDPM_DELETE, self.IDPM_RENAME, self.IDPM_IGNORETHIS]:
            if self.is_first_node(item):
                event.Enable(False)
            else:
                event.Enable(True)
        elif eid in [self.IDPM_IGNORETHISTYPE, self.IDPM_OPENDEFAULT]:
            filename = self.get_node_filename(item)
            if os.path.isdir(filename):
                event.Enable(False)
            else:
                event.Enable(True)
        elif eid == self.IDPM_SETPROJ:
            if self.project_names:
                filename = self.get_node_filename(item)
                if os.path.isdir(filename):
                    event.Enable(True)
                    return
            event.Enable(False)

    def create_recent_path_menu(self):
        menu = makemenu.findmenu(self.menuitems, 'IDPM_ADD')

        for id in self.dirmenu_ids:
            menu.Delete(id)

        self.dirmenu_ids = []
        if len(self.pref.recent_dir_paths) == 0:
            id = self.IDPM_ADD_DIRS
            menu.Append(id, tr('(Empty)'))
            menu.Enable(id, False)
            self.dirmenu_ids = [id]
        else:
            for i, path in enumerate(self.pref.recent_dir_paths):
                id = wx.NewId()
                self.dirmenu_ids.append(id)
                menu.Append(id, "%d %s" % (i+1, path))
                wx.EVT_MENU(self, id, self.OnAddPath)

    def OnAddNewPath(self, event):
        dlg = wx.DirDialog(self, tr("Select directory:"), defaultPath=self.pref.dirbrowser_last_addpath, style=wx.DD_NEW_DIR_BUTTON)
        path = ''
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.pref.dirbrowser_last_addpath = path
            self.pref.save()
        dlg.Destroy()
        if path:
            self.addpath(path)
            if self.pref.open_project_setting_dlg:
                wx.CallAfter(self.OnSetProject)

    def OnAddPath(self, event):
        eid = event.GetId()
        index = self.dirmenu_ids.index(eid)
        self.addpath(self.pref.recent_dir_paths[index])
        if self.pref.open_project_setting_dlg:
            wx.CallAfter(self.OnSetProject)

    def OnCleanDirectories(self, event):
        self.pref.recent_dir_paths = []
        self.pref.save()

    def addpath(self, path, expand=True):
        self.tree.Freeze()
        dirs = self.getTopDirs()
        path = common.uni_file(path)
        if path not in dirs:
            if path in self.pref.recent_dir_paths:
                self.pref.recent_dir_paths.remove(path)
            self.pref.recent_dir_paths.insert(0, path)
            self.pref.recent_dir_paths = self.pref.recent_dir_paths[:self.pref.recent_dir_paths_num]
            self.pref.save()
            node = self.add_first_level_node(self.root, '', path, self.close_image, self.open_image, self.getid())
            self.tree.SetItemHasChildren(node, True)
            if expand:
                self.addpathnodes(path, node)
#                wx.CallAfter(self.tree.Expand, node)
                wx.CallAfter(self.tree.SelectItem, node)
            self.callplugin('after_addpath', self, node)
        self.tree.Thaw()

    def get_files(self, path):
        try:
            files = os.listdir(path)
        except:
            error.traceback()
            return [], []
        if not files:
            return [], []
        r = [(x, os.path.isdir(os.path.join(path, x))) for x in files if not
            self.validate(os.path.join(path, x))]
        if not r: return [], []
        dirs = []
        files = []
        for x, dir in r:
            if dir:
                dirs.append(x)
            else:
                files.append(x)
        dirs.sort(lambda x, y: cmp(x.lower(), y.lower()))
        files.sort(lambda x, y: cmp(x.lower(), y.lower()))
        return dirs, files

    def addpathnodes(self, path, node):
        dirs, files = self.get_files(path)
        for x in dirs:
            obj = self.addnode(node, path, x, self.close_image, self.open_image, self.getid(), self.DIR_NODE)
            self.tree.SetItemHasChildren(obj, True)
        for x in files:
            item_index = self.get_file_image(x)
            self.addnode(node, path, x, item_index, None, self.getid(), self.FILE_NODE)
#        wx.CallAfter(self.tree.Expand, node)
#        wx.CallAfter(self.tree.SelectItem, node)

        #add check project plugin call point
        project_names = common.getCurrentPathProjectName(path)
        self.callplugin('project_begin', self, project_names, path)

    def insert_filename_node(self, parent, path, filename, is_file=True):
        node, cookie = self.tree.GetFirstChild(parent)
        flag = False
        while self.is_ok(node):
            if is_file:
                if self.isFile(node):
                    text = self.tree.GetItemText(node).lower()
                    if text == filename.lower():
                        break
                    elif text > filename.lower():
                        item_index = self.get_file_image(filename)
                        self.insertnode(parent, node, path, filename, item_index, None, self.getid(), self.FILE_NODE)
                        flag = True
                        break
#                else:
#                    break
            else:
                if self.isFile(node):
                    break
                text = self.tree.GetItemText(node).lower()
                if text == filename.lower():
                    break
                elif text > filename.lower():
                    obj = self.insertnode(parent, node, path, filename, self.close_image, self.open_image, self.getid(), self.DIR_NODE)
                    self.tree.SetItemHasChildren(obj, True)
                    flag = True
                    break

            node, cookie = self.tree.GetNextChild(node, cookie)

        if not flag:
            if is_file:
                item_index = self.get_file_image(filename)
                self.addnode(parent, path, filename, item_index, None, self.getid(), self.FILE_NODE)
            else:
                if self.is_ok(node):
                    obj = self.insertnode(parent, node, path, filename, self.close_image, self.open_image, self.getid(), self.DIR_NODE)
                    self.tree.SetItemHasChildren(obj, True)
                else:
                    obj = self.addnode(parent, path, filename, self.close_image, self.open_image, self.getid(), self.DIR_NODE)
                    self.tree.SetItemHasChildren(obj, True)

    def get_file_image(self, filename):
        fname, ext = os.path.splitext(filename)
        if self.fileimages.has_key(ext):
            return self.fileimageindex[self.fileimages[ext]]
        else:
            return self.item_image

    def add_image(self, image):
        index = self.dirbrowserimagelist.Add(image)
        self.callplugin('add_image', self.dirbrowserimagelist, image, index)
        return index

    def add_first_level_node(self, parent, path, name, imagenormal, imageexpand=None, _id=None):
        objs = self.getTopObjects()
        p = name.lower()
        path = ''
        pos = -1
        for i,o in enumerate(objs):
            path = self.tree.GetItemText(o).lower()
            if p<path:
                pos = i
                break
        if pos>-1:
            obj = self.tree.InsertItemBefore(parent, pos, name)
        else:
            obj = self.tree.AppendItem(parent, name)
        self.nodes[_id] = dict(path=path, name=name, obj=obj, nodetype=self.DIR_NODE)
        self.tree.SetPyData(obj, _id)
        self.tree.SetItemImage(obj, imagenormal, wx.TreeItemIcon_Normal)
        if imageexpand:
            self.tree.SetItemImage(obj, imageexpand, wx.TreeItemIcon_Expanded)
        return obj

    def insertnode(self, parent, previous, path, name, imagenormal, imageexpand=None, _id=None, data='file'):
        item = self.tree.GetPrevSibling(previous)
        if self.is_ok(item):
            obj = self.tree.InsertItem(parent, item, name)
        else:
            obj = self.tree.InsertItemBefore(parent, 0, name)
        self.nodes[_id] = dict(path=path, name=name, obj=obj, nodetype=data)
        self.tree.SetPyData(obj, _id)
        self.tree.SetItemImage(obj, imagenormal, wx.TreeItemIcon_Normal)
        if imageexpand:
            self.tree.SetItemImage(obj, imageexpand, wx.TreeItemIcon_Expanded)
        return obj

    def addnode(self, parent, path, name, imagenormal, imageexpand=None, _id=None, data=''):
        obj = self.tree.AppendItem(parent, name)
        self.nodes[_id] = dict(path=path, name=name, obj=obj, nodetype=data)
        self.tree.SetPyData(obj, _id)
        self.tree.SetItemImage(obj, imagenormal, wx.TreeItemIcon_Normal)
        if imageexpand:
            self.tree.SetItemImage(obj, imageexpand, wx.TreeItemIcon_Expanded)
        return obj

    def validate(self, path):
        import fnmatch
        flag = False

        self.filter = ['*/.*', '*.pyc', '*.bak', '.pyo']
        ini = common.get_config_file_obj()

        if ini.ignore.matches:
            self.filter = ini.ignore.matches

        for p in self.filter:
            flag |= fnmatch.fnmatch(path, p)

        return flag

    def getid(self):
        _id = self.ID
        self.ID += 1
        return _id

    def OnChangeLabel(self, event):
        item = event.GetItem()
        if not self.is_ok(item): return
        is_file = self.isFile(item)
        _id = self.tree.GetPyData(item)
        data = self.nodes[_id]
        path, name, obj, nodetype = data['path'], data['name'], data['obj'], data['nodetype']
        text = event.GetLabel()
        if text == '':
            event.Veto()
            return
        if name != text:
            f = os.path.join(path, name)
            if os.path.exists(os.path.join(path, text)):
                if is_file:
                    common.showerror(self, tr('Filename %s has existed!') % os.path.join(path, text))
                else:
                    common.showerror(self, tr('Directory %s has existed!') % os.path.join(path, text))
                return
            if os.path.exists(f):
                try:
                    os.rename(f, os.path.join(path, text))
                except:
                    event.Veto()
                    error.traceback()
                    if is_file:
                        common.showerror(self, tr('Cannot change the filename %s to %s!') % (name, text))
                    else:
                        common.showerror(self, tr('Cannot change the directory %s to %s!') % (name, text))
                    return
            self.nodes[_id] = dict(path=path, name=text, obj=obj, nodetype=nodetype)
            if is_file:
                doc = None
                for d in self.mainframe.editctrl.getDocuments():
                    if (os.path.exists(os.path.join(path, text)) and d.getFilename() == os.path.join(path, name)) or d.getFilename() == name:
                        d.setFilename(os.path.join(path, text))
                        self.mainframe.editctrl.showPageTitle(d)
                        doc = d
                        if d is self.mainframe.editctrl.getCurDoc():
                            self.mainframe.editctrl.showTitle(d)
                item_index = self.get_file_image(text)
                self.tree.SetItemImage(item, item_index, wx.TreeItemIcon_Normal)
                if doc:
                    self.callplugin('call_lexer', doc, name, text, doc.languagename)
        wx.CallAfter(self.tree.SelectItem, item)

    def OnSelected(self, event):
        item = event.GetItem()
        if not self.is_ok(item): return
        filename = self.get_node_filename(item)
        if self.isFile(item):
            document = self.mainframe.editctrl.new(filename)
            if document:
                wx.CallAfter(document.SetFocus)

#    def OnChanged(self, event):
#        item = event.GetItem()
#        if not self.is_ok(item): return
#        filename = self.get_node_filename(item)
#        if os.path.isdir(filename):
#            if self.tree.GetChildrenCount(item) == 0: #need expand
#                self.addpathnodes(filename, item)
#            else:
#                if not self.tree.IsExpanded(item):
#                    self.tree.Expand(item)

    def OnExpanding(self, event):
        item = event.GetItem()
        if self.tree.GetChildrenCount(item) == 0: #need expand
            self.addpathnodes(self.get_node_filename(item), item)
            self.callplugin('after_expanding', self, item)
        else:
            self.callplugin('after_expanding', self, item)
            event.Skip()

    def OnRightDown(self, event):
        pt = event.GetPosition();
        item, flags = self.tree.HitTest(pt)
        if item:
            self.tree.SelectItem(item)

    def OnRClick(self, event):
        other_menus = []
        if self.popmenus:
            self.popmenus.Destroy()
            self.popmenus = None
        self.callplugin('other_popup_menu', self, self.getCurrentProjectName(), other_menus)
        import copy
        if other_menus:
            pop_menus = copy.deepcopy(DirBrowser.popmenulist + other_menus)
        else:
            pop_menus = copy.deepcopy(DirBrowser.popmenulist)
        self.popmenus = pop_menus = makemenu.makepopmenu(self, pop_menus)

        self.dirmenu_ids = [self.IDPM_ADD_DIRS]

        self.create_recent_path_menu()
        self.tree.PopupMenu(pop_menus)

    def OnCloseDirectory(self, event):
        item = self.tree.GetSelection()
        path = self.get_node_filename(item)
        if not self.is_ok(item): return
        if self.is_first_node(item):
            self.tree.Delete(item)

        self.callplugin('after_closepath', self, path)
        #add check project plugin call point
        project_names = common.getCurrentPathProjectName(path)
        self.callplugin('project_end', self, project_names, path)

    def OnAddSubDir(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
        filename = self.get_node_filename(item)

        foldername = 'NewFolder'
        if self.isFile(item):
            item = self.tree.GetItemParent(item)
            filename = self.get_node_filename(item)
        if os.path.exists(os.path.join(filename, foldername)):
            common.showerror(self, tr('Directory %s has existed!') % os.path.join(filename, foldername))
            return

        try:
            os.mkdir(os.path.join(filename, foldername))
        except:
            error.traceback()
            common.showerror(self, tr('Create directory %s error!') % os.path.join(filename, foldername))
            return
        node = self.addnode(item, filename, foldername, self.close_image, self.open_image, self.getid(), self.DIR_NODE)
        self.tree.SetItemHasChildren(node, True)
        wx.CallAfter(self.tree.Expand, item)
        wx.CallAfter(self.tree.EditLabel, node)

    def OnAddFile(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
        filename = self.get_node_filename(item)
        if self.isFile(item):
            item = self.tree.GetItemParent(item)
            filename = self.get_node_filename(item)
        document = self.mainframe.editctrl.new()
        node = self.addnode(item, filename, document.getShortFilename(), self.item_image, None, self.getid(), self.FILE_NODE)
        try:
            filename = self.get_node_filename(node)
            file(filename, 'w')
        except:
            error.traceback()
            common.showerror(self, tr("Can't open the file %(filename)s") % {'filename':filename})
            return
        wx.CallAfter(self.tree.Expand, item)
        wx.CallAfter(self.tree.EditLabel, node)

    def OnDeleteItem(self, event):
        item = event.GetItem()
        if self.is_ok(item):
            del self.nodes[self.tree.GetPyData(item)]
        event.Skip()

    def OnDelete(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
        parent = self.tree.GetItemParent(item)
        filename = self.get_node_filename(item)
        dlg = wx.MessageDialog(self, tr('Do you want to delete %s ?') % filename, tr("Message"), wx.YES_NO | wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES:
            if os.path.exists(filename):
                if os.path.isdir(filename):
                    try:
                        shutil.rmtree(filename)
                    except:
                        error.traceback()
                        common.showerror(self, tr('Cannot delete directory %s!') % filename)
                        return
                else:
                    try:
                        os.remove(filename)
                    except:
                        error.traceback()
                        common.showerror(self, tr('Cannot delete file %s!') % filename)
                        return
            self.tree.Delete(item)
        if self.tree.GetChildrenCount(parent) == 0:
            self.tree.Collapse(parent)
            self.tree.SetItemImage(parent, self.close_image, wx.TreeItemIcon_Normal)
        dlg.Destroy()

    def OnRefresh(self, event=None):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
        self.refresh(self.get_top_parent(item))

    def refresh(self, item, first=True):
        cur_item = item
        if self.isFile(cur_item):
            item = self.tree.GetItemParent(cur_item)
        else:
            if self.tree.GetChildrenCount(cur_item) == 0 and not self.tree.IsExpanded(cur_item):
                return
        path = common.getCurrentDir(self.get_node_filename(item))
        dirs, files = self.get_files(path)
        node, cookie = self.tree.GetFirstChild(item)
        delnodes = []
        while self.is_ok(node):
            filename = self.tree.GetItemText(node)
            if self.isFile(node):
                if filename in files:
                    files.remove(filename)
                else:
                    delnodes.append(node)
            else:
                if filename in dirs:
                    dirs.remove(filename)
                    if self.tree.GetChildrenCount(node) > 0:
                        self.refresh(node, False)
                else:
                    delnodes.append(node)
            node, cookie = self.tree.GetNextChild(item, cookie)

        for node in delnodes:
            self.tree.Delete(node)

        #add rest dirs and files
        for filename in dirs:
            self.insert_filename_node(item, path, filename, False)
        for filename in files:
            self.insert_filename_node(item, path, filename, True)

        if first:
            self.callplugin('after_refresh', self, item)

    def OnRename(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
        self.tree.EditLabel(item)

    def OnBeginChangeLabel(self, event):
        item = event.GetItem()
        if not self.is_ok(item): return
        if self.is_first_node(item):
            event.Veto()
            return
        else:
            event.Skip()

    def is_first_node(self, item):
        parent = self.tree.GetItemParent(item)
        return parent == self.root

    def get_top_parent(self, item):
        while not self.is_first_node(item):
            item = self.tree.GetItemParent(item)
        return item

    def get_node_filename(self, item):
        _id = self.tree.GetPyData(item)
        data = self.nodes[_id]
        filename = os.path.join(data['path'], data['name'])
        return filename

    def deal_file_images(self):
        self.fileimages = {}
        self.fileimages['.py'] = 'file_py.gif'
        self.fileimages['.pyw'] = 'file_py.gif'
        self.fileimages['.txt'] = 'file_txt.gif'
        self.fileimages['.html'] = 'file_html.gif'
        self.fileimages['.htm'] = 'file_html.gif'
        self.fileimages['.ini'] = 'file_txt.gif'
        self.fileimages['.bat'] = 'file_txt.gif'
        self.fileimages['.xml'] = 'file_xml.gif'
        ini = common.get_config_file_obj()
        self.fileimages.update(ini.fileimages)
        ini.fileimages = self.fileimages
        ini.save()

        self.fileimageindex = {}
        for image in self.fileimages.values():
            if not self.fileimageindex.has_key(image):
                obj = common.getpngimage(os.path.join(self.mainframe.userpath, 'images', image))
                self.fileimageindex[image] = self.add_image(obj)

    def OnIgnoreThis(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
        filename = self.get_node_filename(item)
        if filename not in self.filter:
            self.filter.append(filename)
            ini = common.get_config_file_obj()
            ini.ignore.matches = self.filter
            ini.save()
            self.OnRefresh()

    def OnIgnoreThisType(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
        filename = self.get_node_filename(item)
        fname, ext = os.path.splitext(filename)
        if ext not in self.filter:
            self.filter.append(str('*' + ext))
            ini = common.get_config_file_obj()
            ini.ignore.matches = self.filter
            ini.save()
            self.OnRefresh()

    def getCurrentProjectName(self):
        item = self.tree.GetSelection()
        if not self.is_ok(item):
            projectname = ''
        else:
            projectname = common.getProjectName(self.get_node_filename(item))

        return projectname

    def getCurrentProjectHome(self):
        item = self.tree.GetSelection()
        if not self.is_ok(item):
            path = ''
        else:
            path = common.getProjectHome(self.get_node_filename(item))

        return path

    def OnDoubleClick(self, event):
        pt = event.GetPosition()
        item, flags = self.tree.HitTest(pt)
        if flags in (wx.TREE_HITTEST_NOWHERE, wx.TREE_HITTEST_ONITEMRIGHT,
            wx.TREE_HITTEST_ONITEMLOWERPART, wx.TREE_HITTEST_ONITEMUPPERPART):
            self.tree.Freeze()
            for item in self.getTopObjects():
                self.tree.Collapse(item)
            self.tree.Thaw()
        else:
            if self.isFile(item):
                event.Skip()
            else:
                if self.tree.IsExpanded(item):
                    self.tree.Collapse(item)
                else:
                    self.tree.Expand(item)

    def getTopObjects(self):
        objs = []
        child, cookie = self.tree.GetFirstChild(self.root)
        while self.is_ok(child):
            objs.append(child)
            child, cookie = self.tree.GetNextChild(self.root, cookie)
        return objs

    def getTopDirs(self):
        paths = []
        for item in self.getTopObjects():
            paths.append(self.get_node_filename(item))
        return paths

    def OnOpenDefault(self, event):
        item = self.tree.GetSelection()
        if self.is_ok(item):
            os.startfile(self.get_node_filename(item))

    def isFile(self, item):
        data = self.nodes[self.tree.GetPyData(item)]
        return data['nodetype'] == self.FILE_NODE

    def OnAddUliPadWorkPath(self, event):
        path = Globals.workpath
        self.addpath(path)

    def OnAddUliPadUserPath(self, event):
        path = Globals.userpath
        self.addpath(path)

    def OnSetProject(self, event=None):
        item = self.tree.GetSelection()
        from modules import dict4ini
        filename = self.get_node_filename(item)
        proj_file = os.path.join(filename, '_project')
        name = []
        if os.path.exists(proj_file):
            ini = dict4ini.DictIni(proj_file)
            name = ini.default.get('projectname', [])
        dialog = [
                ('multi', 'project_name', name, tr('Project Names'), self.project_names),
            ]
        from modules.EasyGuider import EasyDialog
        dlg = EasyDialog.EasyDialog(self.mainframe, title=tr("Project Setting"), elements=dialog)
        values = None
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
        dlg.Destroy()
        if values is not None:
            filename = self.get_node_filename(item)
            proj_file = os.path.join(filename, '_project')
            ini = dict4ini.DictIni(proj_file)
            ini.default.projectname = values['project_name']
            self.callplugin('remove_project', ini, list(set(name) - set(values['project_name'])))
            self.callplugin('set_project', ini, values['project_name'])
            ini.save()

            old_project_name = name
            new_project_name = ini.default.projectname
            #add check project plugin call point
            path = filename
            project_names = common.getCurrentPathProjectName(path)
            self.callplugin('project_end', self, list(set(old_project_name) - set(new_project_name)), path)
            self.callplugin('project_begin', self, list(set(new_project_name) - set(old_project_name)), path)

    def OnCommandWindow(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
        filename = self.get_node_filename(item)
        if self.isFile(item):
            item = self.tree.GetItemParent(item)
            filename = self.get_node_filename(item)
        if wx.Platform == '__WXMSW__':
            os.spawnl(os.P_NOWAIT, self.pref.command_line, r" /k %s && cd %s" % (os.path.split(filename)[0][:2], filename))
        else:
            cmdline = self.pref.command_line.replace('{path}', filename)
            wx.Execute(cmdline)

    def is_ok(self, item):
        return item.IsOk() and item != self.root

    def OnExplorerWindow(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
        filename = self.get_node_filename(item)
        dir = common.getCurrentDir(filename)
        wx.Execute(r"explorer.exe /e, %s" % dir)

    def OnSearchDir(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
        filename = self.get_node_filename(item)
        dir = common.getCurrentDir(filename)
        p = self.mainframe.createFindInFilesWindow()
        self.mainframe.panel.showPage(p)
        page = self.mainframe.panel.getPage(p)
        page.reset(dir)

    def OnDirCut(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
        self.cache = 'cut', item

    def OnDirCopy(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
        self.cache = 'copy', item

    def OnDirPaste(self, event):
        if not self.cache:
            return
        action, item = self.cache
        dstobj = self.tree.GetSelection()
        if not self.is_ok(dstobj): return

        src = self.get_node_filename(item)
        if self.isFile(dstobj):
            dstobj = self.tree.GetItemParent(dstobj)
        dst = self.get_node_filename(dstobj)

        if os.path.isfile(src):
            fname = os.path.basename(src)
            flag = False
            while os.path.exists(os.path.join(dst, fname)):
                fname = 'CopyOf' + fname
                flag = True
            if flag:
                from modules.Entry import MyTextEntry
                dlg = MyTextEntry(self, tr("Save File"), tr("Change the filename:"),
                    fname, fit=1, size=(300, -1))
                result = dlg.ShowModal()
                if result == wx.ID_OK:
                    dst = os.path.join(dst, dlg.GetValue())
                    dlg.Destroy()
                else:
                    dlg.Destroy()
                    return
        if src == dst:
            common.showerror(self, tr("Source file or directory can not be the same as destination file or directory"))
            return

        if action == 'copy':
            try:
                if self.isFile(item):
                    shutil.copy(src, dst)
                else:
                    my_copytree(src, dst)
            except:
                error.traceback()
                common.showerror(self, tr("Copy %(filename)s to %(dst)s failed!") % {'filename':src, 'dst':dst})
                return
        elif action == 'cut':
            try:
                my_move(src, dst)
            except:
                error.traceback()
                common.showerror(self, tr("Move %(filename)s to %(dst)s failed!") % {'filename':src, 'dst':dst})
                return
        self.OnRefresh()

    def OnKeyDown(self, event):
        key = event.GetKeyCode()
        ctrl = event.ControlDown()
        alt = event.AltDown()
        shift = event.ShiftDown()
        if key == ord('X') and ctrl:
            wx.CallAfter(self.OnDirCut, None)
        elif key == ord('C') and ctrl:
            wx.CallAfter(self.OnDirCopy, None)
        elif key == ord('V') and ctrl:
            wx.CallAfter(self.OnDirPaste, None)
        event.Skip()

    def OnChar(self, event):
        key = event.GetKeyCode()
        ctrl = event.ControlDown()
        alt = event.AltDown()
        shift = event.ShiftDown()
        if key == wx.WXK_DELETE:
            wx.CallAfter(self.OnDelete, None)
        elif key == wx.WXK_F5:
            wx.CallAfter(self.OnRefresh, None)
        else:
            event.Skip()
            
    def OnPrintDir(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
        
        path = self.get_node_filename(item)
        from modules import print_dir
        
        text = print_dir.walk(path)
        
        Globals.mainframe.createMessageWindow()
        Globals.mainframe.panel.showPage(tr('Messages'))
        Globals.mainframe.messagewindow.SetText('\n'.join(text))
        
    def OnAddCurrentPath(self,event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
        filename = self.get_node_filename(item)
        if self.isFile(item):
            item = self.tree.GetItemParent(item)
            filename = self.get_node_filename(item)
        path = filename
        if path:
            self.addpath(path)
            if self.pref.open_project_setting_dlg:
                wx.CallAfter(self.OnSetProject)

def my_copytree(src, dst):
    """Recursively copy a directory tree using copy2().

    Modified from shutil.copytree

    """
    base = os.path.basename(src)
    dst = os.path.join(dst, base)
    names = os.listdir(src)
    if not os.path.exists(dst):
        os.mkdir(dst)
    for name in names:
        srcname = os.path.join(src, name)
        try:
            if os.path.isdir(srcname):
                my_copytree(srcname, dst)
            else:
                shutil.copy2(srcname, dst)
        except:
            error.traceback()
            raise

class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, dirwin):
        wx.FileDropTarget.__init__(self)
        self.dirwin = dirwin

    def OnDropFiles(self, x, y, filenames):
        for filename in filenames:
            if os.path.isdir(filename):
                self.dirwin.addpath(filename)
                if Globals.pref.open_project_setting_dlg:
                    wx.CallAfter(self.dirwin.OnSetProject)
            else:
                Globals.mainframe.editctrl.new(filename)

def my_move(src, dst):
    """Recursively move a file or directory to another location.

    If the destination is on our current filesystem, then simply use
    rename.  Otherwise, copy src to the dst and then remove src.
    A lot more could be done here...  A look at a mv.c shows a lot of
    the issues this implementation glosses over.

    """

    try:
        os.rename(src, dst)
    except OSError:
        if os.path.isdir(src):
            if os.path.abspath(dst).startswith(os.path.abspath(src)):
                raise Exception, "Cannot move a directory '%s' into itself '%s'." % (src, dst)
            my_copytree(src, dst)
            shutil.rmtree(src)
        else:
            shutil.copy2(src,dst)
            os.unlink(src)
