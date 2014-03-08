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

import os
import wx
import copy
import re
import datetime
from modules import common
from modules import makemenu
from modules import Mixin
from modules import Globals
from modules.Debug import error
from modules import Casing
from modules.wxctrl import FlatButtons
import modules.meide as ui
try:
    from xml.etree.ElementTree import ElementTree, Element, SubElement
except:
    from elementtree.ElementTree import ElementTree, Element, SubElement
try:
    import xml.etree.TreeBuilder as XMLWriter
except:
    from elementtree.SimpleXMLWriter import XMLWriter

class MyDropTarget(wx.PyDropTarget):
    def __init__(self, parent):
        wx.PyDropTarget.__init__(self)
        self.tree = parent
        self.snippet = parent.GetParent()
        self.last = None
        self.text = wx.TextDataObject('')
        self.SetDataObject(self.text)

    def highlight(self, item, flag=True):
        if not item:
            return
        if flag:
            self.tree.SetItemTextColour(item, 
                wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT))
            self.tree.SetItemBackgroundColour(item, 
                wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))
        else:
            self.tree.SetItemTextColour(item, 
                wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))
            self.tree.SetItemBackgroundColour(item, 
                wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
            
    def OnEnter(self, x, y, d):
        return d

    def OnLeave(self):
        self.highlight(self.last, False)

    def OnDrop(self, x, y):
        self.highlight(self.last, False)
        return True

    def OnDragOver(self, x, y, d):
        item, flags = self.tree.HitTest((x, y))
        if item:
            if self.last != item:
                self.highlight(self.last, False)
                self.highlight(item, True)
            if flags in (wx.TREE_HITTEST_ONITEMBUTTON, 
                    wx.TREE_HITTEST_ONITEMICON, wx.TREE_HITTEST_ONITEM):
                self.tree.Expand(item)
            self.last = item
        return d

    def OnData(self, x, y, d):
        self.highlight(self.last, False)
        if self.GetData():
            if self.snippet.is_node(self.last):
                if wx.GetKeyState(wx.WXK_SHIFT):
                    pos = 'before'
                else:
                    pos = 'after'
            else:
                if wx.GetKeyState(wx.WXK_CONTROL):
                    pos = 'after'
                elif wx.GetKeyState(wx.WXK_SHIFT):
                    pos = 'before'
                else:
                    pos = 'sub'
            self.snippet.new_node(self.last, tr('NewNode'), 'node', 
                text=self.text.GetText(), pos=pos)
                    
            
        return wx.DragCopy  

class DragTreeCtrl(wx.TreeCtrl):
    def __init__(self, parent, id=-1, style=wx.TR_HAS_BUTTONS):
        wx.TreeCtrl.__init__(self, parent, id, style=style)
        wx.EVT_TREE_BEGIN_DRAG(self, self.GetId(), self.OnBeginDrag)
        wx.EVT_TREE_END_DRAG(self, self.GetId(), self.OnEndDrag)
        wx.EVT_MOTION(self, self.OnDragging)
        self.snippet = parent
        self.SetDropTarget(MyDropTarget(self))
        self._dragItem = None
        
    def OnDrop(self, dropItem, dragItem):
        if self.snippet.is_node(dropItem):
            if wx.GetKeyState(wx.WXK_SHIFT):
                pos = 'before'
            else:
                pos = 'after'
        else:
            if wx.GetKeyState(wx.WXK_CONTROL):
                pos = 'after'
            elif wx.GetKeyState(wx.WXK_SHIFT):
                pos = 'before'
            else:
                pos = 'sub'
        self.Freeze()
        node = self.snippet.move_nodes(dragItem, dropItem, pos=pos)
        self.Thaw()
        self.SelectItem(node)
    
    def OnBeginDrag(self, event):
        # We allow only one item to be dragged at a time, to keep it simple
        self._dragItem = event.GetItem()
        if (self._dragItem and self._dragItem != self.GetRootItem() and 
                not self.snippet.is_root(self._dragItem)): 
            self.StartDragging()
            event.Allow()
        else:
            event.Veto()
    
    def OnDragging(self, event):
        if not event.Dragging():
            self.StopDragging()
            event.Skip()
            return
        if event.Dragging():
            pt = event.GetPosition();
            item, flags = self.HitTest(pt)
            if self.IsValidDropTarget(item):
                self.SetCursorToDragging()
            else:
                self.SetCursorToDroppingImpossible()
            if flags in (wx.TREE_HITTEST_ONITEMBUTTON, 
                    wx.TREE_HITTEST_ONITEMICON, wx.TREE_HITTEST_ONITEM):
                self.Expand(item)
        event.Skip()

    def OnEndDrag(self, event):
        self.StopDragging()
        dropTarget = event.GetItem()
        if self.IsValidDropTarget(dropTarget):
            self.OnDrop(dropTarget, self._dragItem)
    
    def SetCursorToDragging(self):
        self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        
    def SetCursorToDroppingImpossible(self):
        self.SetCursor(wx.StockCursor(wx.CURSOR_NO_ENTRY))
        
    def ResetCursor(self):
        self.SetCursor(wx.NullCursor)
    
    def GetItemChildren(self, item, recursively=False):
        ''' Return the children of item as a list. '''
        children = []
        child, cookie = self.GetFirstChild(item)
        while child:
            children.append(child)
            if recursively:
                children.extend(self.GetItemChildren(child, True))
            child, cookie = self.GetNextChild(item, cookie)
        return children
    
    def GetItemIndex(self, item):
        count = 0
        while 1:
            item = self.GetPrevSibling(item)
            if not item.IsOk():
                return count
            count += 1

    def IsValidDropTarget(self, dropTarget):
        if dropTarget and self._dragItem: 
            allChildren = self.GetItemChildren(self._dragItem, recursively=True)
            parent = self.GetItemParent(self._dragItem) 
            return dropTarget not in [self._dragItem, parent] + allChildren
        else:
            return False
    
    def StartDragging(self):
        self.SetCursorToDragging()
        
    
    def StopDragging(self):
        self.ResetCursor()
#        self.UnselectAll()
#        if self._dragItem:
#            self.SelectItem(self._dragItem)
    
class CodeSnippetWindow(wx.Panel, Mixin.Mixin):

    __mixinname__ = 'codesnippet'

    popmenulist = [ (None,
        [
            (100, 'IDPM_CUT', tr('Cut')+'\tCtrl+X', wx.ITEM_NORMAL, 'OnCodeSnippetCut', ''),
            (110, 'IDPM_COPY', tr('Copy')+'\tCtrl+C', wx.ITEM_NORMAL, 'OnCodeSnippetCopy', ''),
            (120, 'IDPM_PASTE', tr('Paste')+'\tCtrl+V', wx.ITEM_NORMAL, 'OnCodeSnippetPaste', ''),
            (125, 'IDPM_PASTE_BEFORE', tr('Paste Before')+'\tCtrl+Shift+V', wx.ITEM_NORMAL, 'OnCodeSnippetPasteBefore', ''),
            (130, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (132, 'IDPM_EXPANDALL', tr('Expand All'), wx.ITEM_NORMAL, 'OnCodeSnippetExpandAll', ''),
            (133, 'IDPM_COLLAPSEALL', tr('Collapse All'), wx.ITEM_NORMAL, 'OnCodeSnippetCollapseAll', ''),
            (137, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (140, 'IDPM_NEW', tr('New Snippet File...'), wx.ITEM_NORMAL, 'OnNewSnippet', ''),
            (150, 'IDPM_OPEN', tr('Open Snippet File...'), wx.ITEM_NORMAL, 'OnOpenSnippet', ''),
            (160, 'IDPM_RECENT', tr('Recent Snippet Files'), wx.ITEM_NORMAL, '', ''),
            (170, 'IDPM_SAVE', tr('Save Snippet File'), wx.ITEM_NORMAL, 'OnSaveSnippet', ''),
            (175, 'IDPM_SAVE_ALL', tr('Save All Snippet Files'), wx.ITEM_NORMAL, 'OnSaveAllSnippet', ''),
            (180, 'IDPM_SAVEAS', tr('Save Snippet File As...'), wx.ITEM_NORMAL, 'OnSaveAsSnippet', ''),
            (185, 'IDPM_CLOSE', tr('Close Snippet File'), wx.ITEM_NORMAL, 'OnCloseSnippet', ''),
            (190, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (191, 'IDPM_DELETE_ENTRY', tr('Delete Folder or Node')+'\tDel', wx.ITEM_NORMAL, 'OnDeleteEntry', ''),
            (192, 'IDPM_EDIT_CAPTION', tr('Edit Caption'), wx.ITEM_NORMAL, 'OnEditCaption', ''),
            (900, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (910, 'IDPM_PREFERENCES', tr('Preferences...'), wx.ITEM_NORMAL, 'OnPreferences', ''),
        ]),
        ('IDPM_RECENT',
        [
            (160, 'IDPM_snippet_recents', tr('(Empty)'), wx.ITEM_NORMAL, '', ''),
        ]),
    ]

    def __init__(self, parent, mainframe):
        self.initmixin()
        wx.Panel.__init__(self, parent, -1)
        
        self.parent = parent
        self.mainframe = mainframe
        self.pref = mainframe.pref

        self.sizer = ui.VBox(padding=2, namebinding='widget').create(self).auto_layout()
        box = self.sizer.add(ui.HBox(padding=2))
        self.btnSave = FlatButtons.FlatBitmapButton(self, -1, 
            common.getpngimage('images/save.gif'))
        box.add(self.btnSave).bind('click', self.OnSaveSnippet).tooltip(tr('Save'))
        self.btnSaveAll = FlatButtons.FlatBitmapButton(self, -1, 
            common.getpngimage('images/saveall.gif'))
        box.add(self.btnSaveAll).bind('click', self.OnSaveAllSnippet).tooltip(tr('Save All'))
        self.code_snippet_imagelist = imagelist = wx.ImageList(16, 16)

        #add share image list
        self.imagefiles = {}
        self.imageids = {}
        self.callplugin('add_images', self.imagefiles)
        for name, imagefile in self.imagefiles.items():
            self.add_image(name, imagefile)
        
        style = wx.TR_EDIT_LABELS|wx.TR_SINGLE|wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS|wx.TR_TWIST_BUTTONS
        if wx.Platform == '__WXMSW__':
            style = style | wx.TR_ROW_LINES
        elif wx.Platform == '__WXGTK__':
            style = style | wx.TR_NO_LINES
        self.tree = DragTreeCtrl(self, -1, style = style)
        self.tree.AssignImageList(self.code_snippet_imagelist)

        self.sizer.add(self.tree, proportion=1, flag=wx.EXPAND)
        self.root = self.tree.AddRoot('Code Snippet')

        self.nodes = {}
        self.ID = 1
        self.cache = None
        self.changing = False

#        wx.EVT_TREE_SEL_CHANGING(self.tree, self.tree.GetId(), self.OnChanging)
#        wx.EVT_TREE_SEL_CHANGED(self.tree, self.tree.GetId(), self.OnChanged)
#        wx.EVT_TREE_BEGIN_LABEL_EDIT(self.tree, self.tree.GetId(), self.OnBeginChangeLabel)
        wx.EVT_TREE_END_LABEL_EDIT(self.tree, self.tree.GetId(), self.OnChangeLabel)
        wx.EVT_TREE_ITEM_ACTIVATED(self.tree, self.tree.GetId(), self.OnSelected)
#        wx.EVT_TREE_ITEM_RIGHT_CLICK(self.tree, self.tree.GetId(), self.OnRClick)
        wx.EVT_LEFT_DOWN(self.tree, self.OnLeftDown)
        wx.EVT_RIGHT_UP(self.tree, self.OnRClick)
        wx.EVT_RIGHT_DOWN(self.tree, self.OnRightDown)
#        wx.EVT_TREE_DELETE_ITEM(self.tree, self.tree.GetId(), self.OnDeleteItem)
        wx.EVT_LEFT_DCLICK(self.tree, self.OnDoubleClick)
        wx.EVT_TREE_ITEM_EXPANDING(self.tree, self.tree.GetId(), self.OnExpanding)
        wx.EVT_KEY_DOWN(self.tree, self.OnKeyDown)
        wx.EVT_CHAR(self.tree, self.OnChar)
        wx.EVT_TREE_ITEM_GETTOOLTIP(self.tree, self.tree.GetId(), self.OnGetToolTip)
        
        pop_menus = copy.deepcopy(CodeSnippetWindow.popmenulist)
        self.popmenus = makemenu.makepopmenu(self, pop_menus)
        self.recentmenu_ids = [self.IDPM_snippet_recents]

        wx.EVT_UPDATE_UI(self, self.IDPM_CUT, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_COPY, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_PASTE, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_PASTE_BEFORE, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_SAVE, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_SAVEAS, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_CLOSE, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_DELETE_ENTRY, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_EDIT_CAPTION, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_PREFERENCES, self.OnUpdateUI)

        #add init process
        self.callplugin('init', self)

        self.sizer.auto_fit(0)

        self.popmenus = None
        
        #process last opened dirs
        for f in self.pref.snippet_files:
            self.addsnippet(f, expand=False)
        
    def OnUpdateUI(self, event):
        eid = event.GetId()
        item = self.tree.GetSelection()
        if not self.is_ok(item):
            event.Enable(self.is_ok(item))
            return
        if eid in [self.IDPM_CUT, self.IDPM_COPY, self.IDPM_CLOSE, 
            self.IDPM_SAVE, self.IDPM_EDIT_CAPTION]:
            event.Enable(self.is_ok(item))
        elif eid == self.IDPM_DELETE_ENTRY:
            event.Enable(not self.is_root(item))
        elif eid in (self.IDPM_PASTE, self.IDPM_PASTE_BEFORE):
            event.Enable(self.can_paste())
        elif eid == self.IDPM_PREFERENCES:
            event.Enable(self.is_root(item) or self.is_node(item))
        self.callplugin('on_update_ui', self, event)

    def can_paste(self):
        flag = False
        item = self.tree.GetSelection()
        if not self.is_ok(item):
            return False
        if self.cache:
            t, node = self.cache
            allChildren = self.tree.GetItemChildren(node, recursively=True)
            parent = self.tree.GetItemParent(node) 
            flag = bool(item not in [node, parent] + allChildren)
        return flag
    
    def OnGetToolTip(self, event):
        item = event.GetItem()
        if self.is_ok(item):
            if self.is_root(item):
                e = self.get_node_data(item)['etree']
                values = {}
                values['filename'] = self.get_node_data(item)['filename']
                values['title'] = self.get_title(item)
                values['author'] = self.get_element_text(e, 'snippet/properties/author')
                values['version'] = self.get_element_text(e, 'snippet/properties/version')
                values['date'] = self.get_element_text(e, 'snippet/properties/date', datetime.datetime.now())
                values['description'] = self.get_element_text(e, 'snippet/properties/description')
                
                text = tr('''Filename: %(filename)s
Title   : %(title)s
Author  : %(author)s
Version : %(version)s
Date    : %(date)s
Description: 
    %(description)s''') % values
                event.SetToolTip(text)
        
    def addnode(self, node, caption, imagenormal, imageexpand=None, 
            _id=None, data=None, pos='sub'):
        parent = self.tree.GetItemParent(node)
        if pos == 'sub':
            obj = self.tree.AppendItem(node, caption)
        elif pos == 'before':
            obj = self.tree.InsertItemBefore(parent, self.tree.GetItemIndex(node), caption)
        elif pos == 'after':
            obj = self.tree.InsertItem(parent, node, caption)
        else:
            obj = self.tree.InsertItemBefore(parent, self.tree.GetFirstChild(parent), 
                caption)
        if not _id:
            _id = self.getid()
        self.nodes[_id] = data
        self.tree.SetPyData(obj, _id)
        self.tree.SetItemImage(obj, imagenormal, wx.TreeItemIcon_Normal)
        if imageexpand:
            self.tree.SetItemImage(obj, imageexpand, wx.TreeItemIcon_Expanded)
        return obj

    def get_element(self, item):
        data = self.get_node_data(item)
        return data['element']
    
    def getid(self):
        _id = self.ID
        self.ID += 1
        return _id

    def OnChangeLabel(self, event):
        item = event.GetItem()
        if not item.IsOk(): return
        text = event.GetLabel()
        if text:
            self.update_node(item, text)
        
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
        if item.IsOk():
#            if item == self.tree.GetSelection():
#                self.tree.SelectItem(self.tree.GetSelection(), False)
#                wx.CallAfter(self.tree.SelectItem, item, True)
            if event.ControlDown():
                wx.CallAfter(self.node_paste, item)
        event.Skip()

    def OnSelected(self, event):
        item = event.GetItem()
        if not item.IsOk(): return
        self.node_active(item)
    
    def node_paste(self, item):
        if self.is_node(item):
            text = self.get_element(item).text
            if text:
                doc = Globals.mainframe.editctrl.getCurDoc()
                elements = []
                
                def dosup(matchobj):
                    text = matchobj.groups()[0]
                    v = text.split(',')
                    result = ''
                    values = {}
                    for i in v:
                        s = i.split('=')
                        values[s[0].strip()] = s[1].strip()
                    elements.append((values.get('type', 'string'), values['name'], values.get('default', ''), values.get('description', values['name']), None))
                
                    return '<#' + values['name'] + '#>'
                
                r = re.compile("<#\{(.*?)\}#>")
                text = re.sub(r, dosup, text)
                if elements:
                    from modules.EasyGuider import EasyDialog
                    dlg = EasyDialog.EasyDialog(Globals.mainframe, title=tr("Code Template"), elements=elements)
                    values = None
                    if dlg.ShowModal() == wx.ID_OK:
                        values = dlg.GetValue()
                    dlg.Destroy()
                    if values:
                        from modules.meteor import render
                        text = render(text, values, type='string')
                    else:
                        return
                    
                start = doc.GetCurrentPos()
                if not self.mainframe.Indent_paste(doc, text):
                    doc.AddText(text)
                end = doc.GetCurrentPos()
                
                def f():
                    #add snippet process
                    if doc.snippet:
                        snippet = doc.snippet
                    else:
                        import SnipMixin

                        snippet = doc.snippet = SnipMixin.SnipMixin(doc)
                    snippet.start(text, start, end)
#                    wx.CallAfter(doc.SetFocus)
                    wx.FutureCall(1000, doc.SetFocus)
                wx.CallAfter(f)
                
            wx.CallAfter(doc.SetFocus)
            
    def OnExpanding(self, event):
        item = event.GetItem()
        if not item.IsOk(): return
        if not self.execplugin('on_expanding', self, item):
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
        self.callplugin('other_popup_menu', self, other_menus)
        import copy
        
        item = self.tree.GetSelection()
        if self.is_ok(item):
            if self.is_root(item):
                extra_menus = [(None,
                    [
                        (200, '', '-', wx.ITEM_SEPARATOR, None, ''),
                        (210, 'IDPM_ADD_SUB_FOLDER', tr('Add Sub Folder'), wx.ITEM_NORMAL, 'OnAddSubFolder', ''),
                        (230, '', '-', wx.ITEM_SEPARATOR, None, ''),
                        (240, 'IDPM_ADD_SUB_NODE', tr('Add Sub Node'), wx.ITEM_NORMAL, 'OnAddSubNode', ''),
                    ]),
                ]
            elif self.is_folder(item):
                extra_menus = [(None,
                    [
                        (200, '', '-', wx.ITEM_SEPARATOR, None, ''),
                        (210, 'IDPM_ADD_SUB_FOLDER', tr('Add Sub Folder'), wx.ITEM_NORMAL, 'OnAddSubFolder', ''),
                        (220, 'IDPM_ADD_FOLDER_BEFORE', tr('Add Folder Before'), wx.ITEM_NORMAL, 'OnAddFolderBefore', ''),
                        (230, 'IDPM_ADD_FOLDER_AFTER', tr('Add Folder After'), wx.ITEM_NORMAL, 'OnAddFolderAfter', ''),
                        (250, '', '-', wx.ITEM_SEPARATOR, None, ''),
                        (260, 'IDPM_ADD_SUB_NODE', tr('Add Sub Node'), wx.ITEM_NORMAL, 'OnAddSubNode', ''),
                        (270, 'IDPM_ADD_NODE_BEFORE', tr('Add Node Before'), wx.ITEM_NORMAL, 'OnAddNodeBefore', ''),
                        (280, 'IDPM_ADD_NODE_AFTER', tr('Add Node After'), wx.ITEM_NORMAL, 'OnAddNodeAfter', ''),
                    ]),
                ]
            else:
                extra_menus = [(None,
                    [
                        (200, '', '-', wx.ITEM_SEPARATOR, None, ''),
                        (210, 'IDPM_ADD_FOLDER_BEFORE', tr('Add Folder Before'), wx.ITEM_NORMAL, 'OnAddFolderBefore', ''),
                        (220, 'IDPM_ADD_FOLDER_AFTER', tr('Add Folder After'), wx.ITEM_NORMAL, 'OnAddFolderAfter', ''),
                        (230, '', '-', wx.ITEM_SEPARATOR, None, ''),
                        (240, 'IDPM_ADD_NODE_BEFORE', tr('Add Node Before'), wx.ITEM_NORMAL, 'OnAddNodeBefore', ''),
                        (250, 'IDPM_ADD_NODE_AFTER', tr('Add Node After'), wx.ITEM_NORMAL, 'OnAddNodeAfter', ''),
                    ]),
                ]
                
        else:
            extra_menus = []
        
        if other_menus:
            pop_menus = copy.deepcopy(CodeSnippetWindow.popmenulist + other_menus + extra_menus)
        else:
            pop_menus = copy.deepcopy(CodeSnippetWindow.popmenulist + extra_menus)
        self.popmenus = pop_menus = makemenu.makepopmenu(self, pop_menus)
        self.recentmenu_ids = [self.IDPM_snippet_recents]
        self.create_recent_snippet_menu()
        self.tree.PopupMenu(pop_menus)
  
    def is_ok(self, item):
        return item.IsOk() and item != self.root

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

    def get_snippet_document(self):
        snippet = None
        for pagename, panelname, notebook, page in self.mainframe.panel.getPages():
            if hasattr(page, 'code_snippet') and page.code_snippet:
                snippet = page
                break
        return snippet
    
#    def OnChanged(self, event):
#        item = event.GetItem()
#        if not item.IsOk(): return
#        self.node_active(item)
        
    def node_active(self, item):
        if self.changing:return
        else:
            self.changing = True
            
        if not self.is_node(item):
            snippet = self.get_snippet_document()
            if snippet:
                self.mainframe.panel.closePage(snippet, savestatus=False)
        else:
            document = self.mainframe.createCodeSnippetEditWindow()
            if document:
                document.snippet_obj = self
                e = self.get_element(item)
                language = self.get_element(item).attrib.get('language', 'python')
                lexer = Globals.mainframe.lexers.getNamedLexer(language)
                if not lexer:
                    lexer = Globals.mainframe.lexers.getDefaultLexer()
                if lexer:
                    lexer.colourize(document)
                
                self.change_snippet_document_title(item, e.attrib['caption'])
                if e.text:
                    text = e.text
                else:
                    text = ''
                document.SetText(text)
                document.SetSavePoint()
            wx.CallAfter(self.tree.SetFocus)
        
        self.changing = False

    def get_image_id(self, name):
        return self.imageids.get(name, -1)

    def add_image(self, name, imagefile):
        if not self.imagefiles.has_key(name):
            self.imagefiles[name] = imagefile
        if not self.imageids.has_key(name):
            image = common.getpngimage(imagefile)
            self.imageids[name] = self.code_snippet_imagelist.Add(image)
            if name in ('close', 'open'):
                imgfile = common.getpngimage('images/TortoiseModified.gif')
                bmp = common.merge_bitmaps(image, imgfile)
                index = self.code_snippet_imagelist.Add(bmp)
                self.imageids[name+'_modified'] = index
            
    def OnCodeSnippetCut(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
        self.cache = 'cut', item
      
    def OnCodeSnippetCopy(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
        self.cache = 'copy', item
      
    def OnCodeSnippetPaste(self, event):
        if not self.can_paste():
            return
        action, item = self.cache
        dstobj = self.tree.GetSelection()
        if not self.is_ok(dstobj): return
    
        if action == 'cut':
            flag = True
        else:
            flag = False
        
        if self.is_node(item):
            pos = 'after'
        else:
            pos = 'sub'
        
        self.move_nodes(item, dstobj, pos=pos, delete=flag)
  
    def OnCodeSnippetPasteBefore(self, event):
        if not self.can_paste():
            return
        action, item = self.cache
        dstobj = self.tree.GetSelection()
        if not self.is_ok(dstobj): return
    
        if action == 'cut':
            flag = True
        else:
            flag = False
        
        self.move_nodes(item, dstobj, pos='before', delete=flag)
        
    def OnKeyDown(self, event):
        key = event.GetKeyCode()
        ctrl = event.ControlDown()
        alt = event.AltDown()
        shift = event.ShiftDown()
        if key == ord('X') and ctrl:
            wx.CallAfter(self.OnCodeSnippetCut, None)
        elif key == ord('C') and ctrl:
            wx.CallAfter(self.OnCodeSnippetCopy, None)
        elif key == ord('V') and ctrl and not shift:
            wx.CallAfter(self.OnCodeSnippetPaste, None)
        elif key == ord('V') and ctrl and shift:
            wx.CallAfter(self.OnCodeSnippetPasteBefore, None)
        event.Skip()
      
    def OnChar(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
        key = event.GetKeyCode()
        ctrl = event.ControlDown()
        alt = event.AltDown()
        shift = event.ShiftDown()
        if key == wx.WXK_DELETE:
            wx.CallAfter(self.OnDeleteEntry, None)
#        elif key == wx.WXK_INSERT and not ctrl: #insert a node
#            self.new_node(item, tr('NewItem'), 'node')
#        elif key == wx.WXK_INSERT and ctrl: #insert a node
#            self.new_node(item, tr('NewFolder'), 'folder')
        else:
            event.Skip()
  
    def OnSaveAsSnippet(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
        dlg = wx.FileDialog(self, tr("Save Snippet File As..."), self.pref.snippet_lastdir, '', 'Snippet File(*.spt)|*.spt|All Files(*.*)|*.*', wx.SAVE|wx.OVERWRITE_PROMPT)
        dlg.SetFilterIndex(0)
        filename = None
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            self.pref.snippet_lastdir = os.path.dirname(filename)
            self.pref.save()
        dlg.Destroy()
        files = self.getTopSnippets()
        filename = common.uni_file(filename)
        if filename in files:
            common.showerror(tr('The file %s has been existed, so please rename it.') % filename)
            return
        data = self.get_node_data(item)
        data['filename'] = filename
        self.save_snippet(item)
        
    def OnNewSnippet(self, event):
        dlg = wx.FileDialog(self, tr("New Snippet File"), self.pref.snippet_lastdir, '', 'Snippet File(*.spt)|*.spt|All Files(*.*)|*.*', wx.SAVE|wx.OVERWRITE_PROMPT)
        dlg.SetFilterIndex(0)
        filename = None
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            self.pref.snippet_lastdir = os.path.dirname(filename)
            self.pref.save()
        dlg.Destroy()
        f = file(filename, 'wb')
        w = XMLWriter(f)
        w.start('xml')
        w.start('snippet')
        w.start('properties')
        w.start('title')
        w.data('Untitled')
        w.end('title')
        w.end('properties')
        w.start('content')
        w.end('content')
        w.end('snippet')
        w.end('xml')
        f.close()
        self.addsnippet(filename, type='new')
        
    def OnOpenSnippet(self, event):
        dlg = wx.FileDialog(self, tr("Open Snippet File"), self.pref.snippet_lastdir, '', 'Snippet File(*.spt)|*.spt|All Files(*.*)|*.*', wx.OPEN)
        dlg.SetFilterIndex(0)
        filename = None
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
            self.pref.snippet_lastdir = os.path.dirname(filename)
            self.pref.save()
        dlg.Destroy()
        if filename:
            self.addsnippet(filename, 'open')
    
    def save_all_snippets(self):
        objs = []
        for obj in self.getTopObjects():
            if self.get_modify(obj):
                objs.append(obj)
        for obj in objs:
            self.save_snippet(obj)
        
    def canClose(self):
        objs = []
        for obj in self.getTopObjects():
            if self.get_modify(obj):
                objs.append(obj)
        if objs:
            flag = wx.MessageBox(tr('Some changes have been made to the Code Snippets Window. Do you want to save them?'), 
                tr('Saving Confirm'), style=wx.YES|wx.NO|wx.CANCEL)
            if flag == wx.CANCEL:
                return False
            if flag == wx.YES:
                self.save_all_snippets()
        
        return True
        
    def create_recent_snippet_menu(self):
        menu = makemenu.findmenu(self.menuitems, 'IDPM_RECENT')
        for id in self.recentmenu_ids:
            menu.Delete(id)
            self.recentmenu_ids = []
        if len(self.pref.snippet_recents) == 0:
            id = self.IDPM_snippet_recents
            menu.Append(id, tr('(Empty)'))
            menu.Enable(id, False)
            self.recentmenu_ids = [id]
        else:
            for i, path in enumerate(self.pref.snippet_recents):
                id = wx.NewId()
                self.recentmenu_ids.append(id)
                menu.Append(id, "%d %s" % (i+1, path))
                wx.EVT_MENU(self, id, self.OnRecentSnippet)
  
    def getTopSnippets(self):
        files = []
        for item in self.getTopObjects():
            data = self.get_node_data(item)
            files.append(data['filename'])
        return files

    def deal_recent(self, filename):
        if filename in self.pref.snippet_recents:
            self.pref.snippet_recents.remove(filename)
        self.pref.snippet_recents.insert(0, filename)
        self.pref.snippet_recents = self.pref.snippet_recents[:30]
        self.pref.save()
        
    def addsnippet(self, filename, type='open', expand=True):
        #test if the filename is existed
        if not os.path.exists(filename):
            common.showerror(tr("Can't open the file %s") % filename)
            return
        files = self.getTopSnippets()
        filename = common.uni_file(filename)
        if filename not in files:
            self.deal_recent(filename)
            
            def f():
                self.read_snippet_file(filename, type, expand)
            d = Casing.Casing(f)
            d.start_thread()
            
        self.callplugin('after_addsnippetfile', self)
    
    def read_snippet_file(self, filename, type, expand):
        try:
            e = ElementTree(file=filename)
            
            def f():
                
                title = e.find('snippet/properties/title')
                nodes = e.find('snippet/content')
                data = {'type':'root', 'filename':filename, 'element':nodes, 
                    'etree':e, 'caption':title.text}
                node = self.add_new_folder(self.root, title.text, data, modified=False)
                
                def add_nodes(root, nodes):
                    for n in nodes:
                        if n.tag == 'node':
                            obj = self.add_new_node(root, n.attrib['caption'], data={'element':n}, modified=False)
                        elif n.tag == 'folder':
                            obj = self.add_new_folder(root, n.attrib['caption'], data={'element':n}, modified=False)
                            add_nodes(obj, n.getchildren())
                    if expand:
                        self.tree.Expand(root)
                            
                add_nodes(node, nodes)
                wx.CallAfter(self.tree.SelectItem, node)
                if type == 'new':
                    wx.CallAfter(self.tree.EditLabel, node)
                    
                self._save_files()
            
            wx.CallAfter(f)
        except:
            error.traceback()
            common.showerror(tr("There are some errors as openning the Snippet file"))
    
    def OnRecentSnippet(self, event):
        eid = event.GetId()
        index = self.recentmenu_ids.index(eid)
        self.addsnippet(self.pref.snippet_recents[index])
        
    def update_node(self, node, newcaption=None, newcontent=None):
        data = self.get_node_data(node)
        element = data['element']
        if self.is_root(node):
            e = data['etree'].find('snippet/properties/title')
            if newcaption != e.text:
                e.text = newcaption
                self.set_modify(node)
        else:
            if newcaption is not None and self.tree.GetItemText(node) != newcaption:
                element.attrib['caption'] = newcaption
                self.change_snippet_document_title(node, newcaption)
                self.set_modify(node)
            if self.is_node(node) and newcontent is not None and element.text != newcontent:
                element.text = newcontent
                self.set_modify(node)
          
    def change_snippet_document_title(self, node, title):
        if self.is_node(node):
            win = self.mainframe
            doc = self.get_snippet_document()
            
            if doc:
                win = doc.GetParent()
                win.SetPageText(win.getPageIndex(doc), tr('Snippet') + ' - [%s]' % 
                    title)
        
    def add_new_folder(self, parent, caption, data=None, modified=True, pos='sub'):
        if not data:
            data={'type':'folder'}
        if not data.has_key('type'):
            data['type'] = 'folder'
        node = self.addnode(parent, caption, self.get_image_id('close'), 
            self.get_image_id('open'), data=data, pos=pos)
        self.set_modify(node, modified)
        return node
    
    def add_new_node(self, parent, caption, data=None, modified=True, pos='sub'):
        if not data:
            data={'type':'node'}
        if not data.has_key('type'):
            data['type'] = 'node'
        node = self.addnode(parent, caption, self.get_image_id('item'), 
            data=data, pos=pos)
        self.set_modify(node, modified)
        return node
    
    def get_root_node(self, node):
        if self.is_root(node):
            return node
        while not self.is_root(node):
            node = self.tree.GetItemParent(node)
        return node
        
    def get_node_data(self, node):
        try:
            _id = self.tree.GetPyData(node)
            return self.nodes[_id]
        except:
            print 'except', _id, self.tree.GetItemText(node)
    
    def set_modify(self, node, flag=True):
        root = self.get_root_node(node)
        self.get_node_data(root)['modified'] = flag
        if flag:
            index_close = self.imageids['close_modified']
            index_open = self.imageids['open_modified']
        else:
            index_close = self.imageids['close']
            index_open = self.imageids['open']
            
        self.tree.SetItemImage(root, index_close, wx.TreeItemIcon_Normal)
        self.tree.SetItemImage(root, index_open, wx.TreeItemIcon_Expanded)
        
    def get_modify(self, node):
        root = self.get_root_node(node)
        data = self.get_node_data(root)
        return data.has_key('modified') and data['modified']
        
    def OnSaveSnippet(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
        self.save_snippet(item)
           
    def OnSaveAllSnippet(self, event):
        self.save_all_snippets()
        
    def save_snippet(self, node):
        root = self.get_root_node(node)
        data = self.get_node_data(root)
        try:
            data['etree'].write(data['filename'], 'utf-8')
            self.set_modify(root, False)
            self.deal_recent(data['filename'])
        except:
            error.traceback()
            common.showerror(self, tr("There is something wrong as saving the snippet file."))
        
    def OnCloseSnippet(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
        item = self.get_root_node(item)
        
        if self.get_modify(item):
            flag = wx.MessageBox(tr('The snippet has been modified, do you want to save it ?'), tr("Saving Confirm"), wx.YES|wx.NO|wx.CANCEL)
            if flag == wx.YES:
                self.save_snippet(item)
            elif flag == wx.CANCEL:
                return
        
        self.tree.Freeze()    
        self.tree.Delete(item)
        self.tree.Thaw()
        self._save_files()
        snippet = None
        for pagename, panelname, notebook, page in self.mainframe.panel.getPages():
            if hasattr(page, 'code_snippet') and page.code_snippet:
                self.mainframe.panel.closePage(page, savestatus=False)
        
    def is_folder(self, node):
        data = self.get_node_data(node)
        return data['type'] == 'folder'
    
    def is_node(self, node):
        data = self.get_node_data(node)
        return data['type'] == 'node'
      
    def is_root(self, node):
        data = self.get_node_data(node)
        return data['type'] == 'root'
        
    def _save_files(self):
        files = self.getTopSnippets()
        self.pref.snippet_files = files
        self.pref.save()
        
    def OnEditCaption(self, event):
        item = self.tree.GetSelection()
        if self.is_ok(item):
            self.tree.EditLabel(item)
            
    def OnDeleteEntry(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
        self.delete_node(item)
            
    def delete_node(self, item):
        data = self.nodes.pop(self.tree.GetPyData(item))
        parent = self.tree.GetItemParent(item)
        p_data = self.get_node_data(parent)
        root = p_data['element']
        root.remove(data['element'])
        self.tree.Delete(item)
        self.set_modify(parent)

    def add_element(self, node, element, pos='sub'):
        def _get_index(node):
            element = self.get_element(node)
            parent = self.tree.GetItemParent(node)
            parent_element = self.get_element(parent)
            for i, node in enumerate(parent_element.getchildren()):
                if node is element:
                    return i, parent_element
            return -1, None

        cur = self.get_element(node)
        if pos == 'sub':
            cur.append(element)
        elif pos == 'before':
            index, p_element = _get_index(node)
            if index > -1:
                p_element.insert(index, element)
        elif pos == 'after':
            index, p_element = _get_index(node)
            if index > -1:
                p_element.insert(index+1, element)
        else:
            cur.insert(0, element)
        
    def new_node(self, node, caption, type, text='', expand=True, edit=True, 
            modified=True, pos='sub', element=None):
                
#        element = self.get_element(node)
        if element is None:
            new_element = Element(type, caption=caption)
            new_element.text = text
        else:
            new_element = element
        self.add_element(node, new_element, pos)
        if type == 'folder':
            new_node = self.add_new_folder(node, caption, 
                data={'element':new_element}, modified=modified, 
                pos=pos)
        else:
            new_node = self.add_new_node(node, caption, 
                data={'element':new_element}, modified=modified,
                pos=pos)
        
        if expand:
            wx.CallAfter(self.tree.Expand, node)
        self.tree.SelectItem(new_node)
        if edit:
            wx.CallAfter(self.tree.EditLabel, new_node)
        
        return new_node
        
    def OnAddSubFolder(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return

        self.new_node(item, tr('NewFolder'), 'folder', pos='sub')
        
    def OnAddFolderBefore(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
        
        self.new_node(item, tr('NewFolder'), 'folder', pos='before')
        
    def OnAddFolderAfter(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
        
        self.new_node(item, tr('NewFolder'), 'folder', pos='after')
        
    def OnAddSubNode(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
        
        self.new_node(item, tr('NewNode'), 'node', pos='sub')
        
    def OnAddNodeBefore(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
        
        self.new_node(item, tr('NewNode'), 'node', pos='before')
        
    def OnAddNodeAfter(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
        
        self.new_node(item, tr('NewNode'), 'node', pos='after')
        
    def copy_node(self, src, des, pos='sub'):
        data = self.get_node_data(src)
        e = data['element']
        element = Element(e.tag, caption=e.attrib['caption'])
        element.text = e.text
        
        node = self.new_node(des, e.attrib['caption'], data['type'], pos=pos,
            element=element, edit=False)
        return node
        
    def move_nodes(self, src, des, pos='sub', delete=True):
        node = self.copy_node(src, des, pos=pos)
        def f(node1, node2):
            if self.tree.GetChildrenCount(node1) > 0:
                item, cookie = self.tree.GetFirstChild(node1)
                while item:
                    last = self.copy_node(item, node2, 'sub')
                    f(item, last)
                    item, cookie = self.tree.GetNextChild(node1, cookie)
                    
        f(src, node)
        if delete:
            self.delete_node(src)
        return node

    def get_title(self, node):
        root = self.get_root_node(node)
        data = self.get_node_data(root)
        title = data['etree'].find('snippet/properties/title')
        return title.text
        
    def set_title(self, node, title):
        root = self.get_root_node(node)
        data = self.get_node_data(root)
        t = data['etree'].find('snippet/properties/title')
        t.text = title
        self.tree.SetItemText(node, title)
        self.set_modify(node)
        
    def get_element_text(self, etree, path, default=''):
        node = etree.find(path)
        if node is None:
            return default
        else:
            return node.text
        
    def set_element_text(self, node, etree, path, text):
        paths = filter(None, path.split('/'))
        s = ''
        root = etree.getroot()
        for p in paths:
            s += '/' + p
            e = etree.find(s)
            if e is None:
                e = SubElement(root, p)
            root = e
        e.text = text
        self.set_modify(node)
        
    def OnPreferences(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item): return
    
        if self.is_node(item):
            win = Globals.mainframe
            items = [lexer.name for lexer in win.lexers.lexobjs]
            dlg = wx.SingleChoiceDialog(win, tr('Select a syntax highlight'), tr('Syntax Highlight'), items, wx.CHOICEDLG_STYLE)
            language = self.get_element(item).attrib.get('language', 'python')
            try:
                index = items.index(language)
            except:
                index = 0
            dlg.SetSelection(index)
            if dlg.ShowModal() == wx.ID_OK:
                lexer = win.lexers.lexobjs[dlg.GetSelection()]
                self.get_element(item).attrib['language'] = lexer.name
                self.set_modify(item)
                doc = self.get_snippet_document()
                if doc:
                    lexer.colourize(doc)
            dlg.Destroy()
        elif self.is_root(item):
            values = {}
            e = self.get_node_data(item)['etree']
            values['title'] = self.get_title(item)
            values['author'] = self.get_element_text(e, 'snippet/properties/author')
            values['version'] = self.get_element_text(e, 'snippet/properties/version')
            values['date'] = self.get_element_text(e, 'snippet/properties/date', datetime.datetime.now())
            values['description'] = self.get_element_text(e, 'snippet/properties/description')
            dlg = PropertyDialog(self, -1, values=values)
            values = None
            if dlg.ShowModal() == wx.ID_OK:
                values = dlg.GetValue()
            dlg.Destroy()
            if values:
                if self.get_title(item) != values['title']:
                    self.set_title(item, values['title'])
                self.set_element_text(item, e, 'snippet/properties/author', values['author'])
                self.set_element_text(item, e, 'snippet/properties/version', values['version'])
                self.set_element_text(item, e, 'snippet/properties/date', values['date'].strftime('%Y-%m-%d'))
                self.set_element_text(item, e, 'snippet/properties/description', values['description'])
                
    def OnCodeSnippetExpandAll(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item):
            self.tree.ExpandAll()
        else:
            self.tree.ExpandAllChildren(item)
        
    def OnCodeSnippetCollapseAll(self, event):
        item = self.tree.GetSelection()
        if not self.is_ok(item):
            self.tree.CollapseAll()
        else:
            self.tree.CollapseAllChildren(item)
        
class PropertyDialog(wx.Dialog):
    def __init__(self, parent, id=-1, title=tr('Property'), size=(400, 300), values=None):
        wx.Dialog.__init__(self, parent, id, title=title, size=size)
        
        self.sizer = ui.VBox(namebinding='widget').create(self).auto_layout()
        grid = self.sizer.add(ui.SimpleGrid)
        grid.add(tr('Title'), ui.Text, name='title')
        grid.add(tr('Author'), ui.Text, name='author')
        grid.add(tr('Version'), ui.Text, name='version')
        grid.add(tr('Date'), ui.Date, name='date')
        grid.add(tr('Description'), ui.MultiText('', size=(-1, 60)), name='description', span=True)
        
        self.sizer.add(ui.simple_buttons(), flag=wx.ALIGN_CENTER|wx.BOTTOM)
        self.btnOk.SetDefault()
        
        if values:
            self.sizer.SetValue(values)
        self.sizer.auto_fit(1)
        
    def GetValue(self):
        return self.sizer.GetValue()