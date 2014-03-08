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
#   $Id: MyPanel.py 1852 2007-01-25 01:50:35Z limodou $
#
#   This file's code is mostly copy from DrPython. Thanks to Daniel Pozmanter

import wx
from modules import Id
from modules import makemenu
from modules import Mixin
from modules import common
from modules import Globals

class SashPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, size=(0,0))

        self.parent = parent
        self.mainframe = parent

        width, height = self.GetSizeTuple()

        self.pages = []

        self.ID_TOP = Id.makeid(self, 'ID_TOP')
        self.ID_BOTTOM = Id.makeid(self, 'ID_BOTTOM')
        self.ID_LEFT = Id.makeid(self, 'ID_LEFT')
        self.ID_RIGHT = Id.makeid(self, 'ID_RIGHT')

        wx.EVT_SASH_DRAGGED(self, self.ID_TOP, self.OnSashDrag)
        wx.EVT_SASH_DRAGGED(self, self.ID_BOTTOM, self.OnSashDrag)
        wx.EVT_SASH_DRAGGED(self, self.ID_LEFT, self.OnSashDrag)
        wx.EVT_SASH_DRAGGED(self, self.ID_RIGHT, self.OnSashDrag)

        self.toptuple = (width, height)
        self.lefttuple = (0, 0)
        self.righttuple = (0, 0)
        self.bottomtuple = (0, 0)

        self.bottomsize = 20
        self.leftsize = 20
        self.rightsize = 30

        self.BottomIsVisible = False
        self.LeftIsVisible = False
        self.RightIsVisible = False

        self.top = wx.SashLayoutWindow(self, self.ID_TOP, wx.DefaultPosition, wx.DefaultSize, wx.NO_BORDER)

        self.top.SetDefaultSize((width, height))
        self.top.SetOrientation(wx.LAYOUT_HORIZONTAL)
        self.top.SetAlignment(wx.LAYOUT_TOP)

        self.bottom = wx.SashLayoutWindow(self, self.ID_BOTTOM, wx.DefaultPosition, wx.DefaultSize, wx.NO_BORDER)

        self.bottom.SetDefaultSize((width, height))
        self.bottom.SetOrientation(wx.LAYOUT_HORIZONTAL)
        self.bottom.SetAlignment(wx.LAYOUT_BOTTOM)
        self.bottom.SetSashVisible(wx.SASH_TOP, True)
#        self.bottom.SetSashBorder(wx.SASH_TOP, True)

        self.left = wx.SashLayoutWindow(self, self.ID_LEFT, wx.DefaultPosition, wx.DefaultSize, wx.NO_BORDER)

        self.left.SetDefaultSize((100, 1000))
        self.left.SetOrientation(wx.LAYOUT_VERTICAL)
        self.left.SetAlignment(wx.LAYOUT_LEFT)
        self.left.SetSashVisible(wx.SASH_RIGHT, True)
#        self.left.SetSashBorder(wx.SASH_RIGHT, True)

        self.right = wx.SashLayoutWindow(self, self.ID_RIGHT, wx.DefaultPosition, wx.DefaultSize, wx.NO_BORDER)

        self.right.SetDefaultSize((100, 1000))
        self.right.SetOrientation(wx.LAYOUT_VERTICAL)
        self.right.SetAlignment(wx.LAYOUT_RIGHT)
        self.right.SetSashVisible(wx.SASH_LEFT, True)
#        self.right.SetSashBorder(wx.SASH_LEFT, True)

        wx.EVT_SIZE(self, self.OnSize)

        self.leftbook = None
        self.rightbook = None
        self.bottombook = None

    def OnSashDrag(self, event):
        evtheight = event.GetDragRect().height
        evtwidth = event.GetDragRect().width
        width, height = self.GetSizeTuple()
        if (evtwidth < 0):
            evtwidth = 0
        elif (evtwidth > width):
            evtwidth = width
        if event.GetDragStatus() == wx.SASH_STATUS_OUT_OF_RANGE:
            if (not self.BottomIsVisible) or (evtheight < height):
                evtheight = 0
            else:
                evtheight = height
        elif evtheight > height:
            evtheight = height

        oldsize = self.bottomsize
        loldsize = self.leftsize
        roldsize = self.rightsize

        e = event.GetId()
        edge = event.GetEdge()
        if e == self.ID_TOP:
            if edge == wx.SASH_BOTTOM:
                self.top.SetDefaultSize((width, evtheight))
                self.bottom.SetDefaultSize((width, height-evtheight))
                self.bottomsize = ((height*100) - (evtheight*100)) / height
                self.toptuple = (self.toptuple[0], evtheight)
                self.bottomtuple = (self.bottomtuple[0], height-evtheight)
            elif edge == wx.SASH_LEFT:
                if self.RightIsVisible:
                    evtwidth = evtwidth + self.righttuple[0]
                self.top.SetDefaultSize((evtwidth, height))
                self.left.SetDefaultSize((width-evtwidth, height))
                self.lefttuple = (width-evtwidth, height)
                self.toptuple = (evtwidth, self.toptuple[1])
                self.leftsize = ((width*100) - (evtwidth*100)) / width
            elif edge == wx.SASH_RIGHT:
                if self.LeftIsVisible:
                    evtwidth = evtwidth + self.lefttuple[0]
                self.top.SetDefaultSize((evtwidth, height))
                self.right.SetDefaultSize((width-evtwidth, height))
                self.righttuple = (width-evtwidth, height)
                self.toptuple = (evtwidth, self.toptuple[1])
                self.rightsize = ((width*100) - (evtwidth*100)) / width
        elif e == self.ID_BOTTOM:
            self.top.SetDefaultSize((width, height-evtheight))
            self.bottomsize = ((evtheight*100) / height)
        elif e == self.ID_LEFT:
            if self.LeftIsVisible:
                if self.lefttuple[0] == evtwidth:
                    evtwidth = 0
            self.top.SetDefaultSize((width-evtwidth, height))
            self.left.SetDefaultSize((evtwidth, height))
            self.lefttuple = (evtwidth, height)
            self.toptuple = (width-evtwidth, self.toptuple[1])
            self.leftsize = (evtwidth*100) / width
        elif e == self.ID_RIGHT:
            if self.RightIsVisible:
                if self.righttuple[0] == evtwidth:
                    evtwidth = 0
            self.top.SetDefaultSize((width-evtwidth, height))
            self.right.SetDefaultSize((evtwidth, height))
            self.righttuple = (evtwidth, height)
            self.toptuple = (width-evtwidth, self.toptuple[1])
            self.rightsize = (evtwidth*100) / width
        if self.bottomsize == 0:
            self.bottomsize = oldsize
            self.BottomIsVisible = False
        elif not self.BottomIsVisible and self.bottomtuple[1] > 0:
            self.BottomIsVisible = True

        if self.leftsize == 0:
            self.leftsize = loldsize
            self.LeftIsVisible = False
        elif not self.LeftIsVisible and self.lefttuple[0] > 0:
            self.LeftIsVisible = True

        if self.rightsize == 0:
            self.rightsize = roldsize
            self.RightIsVisible = False
        elif not self.RightIsVisible and self.righttuple[0] > 0:
            self.RightIsVisible = True

        self.OnSize(event)
        self.Refresh()

    def OnSize(self, event):
        width, height = self.GetSizeTuple()
        if self.BottomIsVisible:
            heightDocument = (height * (100 - self.bottomsize)) / 100
            heightPrompt = (height * self.bottomsize) / 100
        else:
            heightDocument = height
            heightPrompt = 0
        if self.LeftIsVisible and self.RightIsVisible:
            w = (width * (100 - self.leftsize - self.rightsize)) / 100
        elif self.LeftIsVisible:
            w = (width * (100 - self.leftsize)) / 100
        elif self.RightIsVisible:
            w = (width * (100 - self.rightsize)) / 100
        else:
            w = width
        wl = 0
        wr = 0
        if self.LeftIsVisible:
            wl = (width * self.leftsize) / 100
        if self.RightIsVisible:
            wr = (width * self.rightsize) / 100

        self.toptuple = (w, heightDocument)
        self.lefttuple = (wl, height)
        self.righttuple = (wr, height)
        self.bottomtuple = (w, heightPrompt)

        self.top.SetDefaultSize(self.toptuple)
        self.bottom.SetDefaultSize(self.bottomtuple)
        self.left.SetDefaultSize(self.lefttuple)
        self.right.SetDefaultSize(self.righttuple)
        wx.LayoutAlgorithm().LayoutWindow(self, self.top)

    def showWindow(self, panelname, showflag):
        name = panelname.lower()

        if name == 'left':
            self.LeftIsVisible = showflag
        elif name == 'right':
            self.RightIsVisible = showflag
        elif name == 'bottom':
            self.BottomIsVisible = showflag

        self.OnSize(None)
        self.Refresh()

    def setSize(self, side, percent):
        if side == 'left':
            self.leftsize = percent
            if percent == 100:
                self.rightsize = 0
                self.bottomsize = 0
        elif side == 'right':
            self.rightsize = percent
            if percent == 100:
                self.leftsize = 0
                self.bottomsize = 0
        elif side == 'bottom':
            self.bottomsize = percent
            if percent == 100:
                self.leftsize = 0
                self.rightsize = 0
            
    def showPage(self, name):
        if self.leftbook and self.leftbook.getPageIndex(name) > -1:
            self.showWindow('left', True)
            self.leftbook.showPage(name)
            return

        if self.rightbook and self.rightbook.getPageIndex(name) > -1:
            self.showWindow('right', True)
            self.rightbook.showPage(name)
            return

        if self.bottombook and self.bottombook.getPageIndex(name) > -1:
            self.showWindow('bottom', True)
            self.bottombook.showPage(name)
            return

    def getNotebook(self, name):
        name = name.lower()
        if name == 'left':
            return self.leftbook
        elif name == 'right':
            return self.rightbook
        elif name == 'bottom':
            return self.bottombook
        
    def getSide(self, sidename):
        sidename = sidename.lower()
        if sidename == 'left':
            return self.left
        elif sidename == 'right':
            return self.right
        elif sidename == 'bottom':
            return self.bottom

    def delNotebook(self, name):
        name = name.lower()
        if name == 'left':
            self.leftbook.Destroy()
            self.leftbook = None
        elif name == 'right':
            self.rightbook.Destroy()
            self.rightbook = None
        elif name == 'bottom':
            self.bottombook.Destroy()
            self.bottombook = None

    def createNotebook(self, name):
        name = name.lower()
        if name == 'left':
            if not self.leftbook:
                self.leftbook = Notebook(self.left, self, name)
            return self.leftbook
        elif name == 'right':
            notebook = self.rightbook
            if not self.rightbook:
                self.rightbook = Notebook(self.right, self, name)
            return self.rightbook
        elif name == 'bottom':
            notebook = self.bottombook
            if not self.bottombook:
                self.bottombook = Notebook(self.bottom, self, name)
            return self.bottombook

    def addPage(self, panelname, page, name):
        pname = panelname.lower()
        notebook = self.getNotebook(panelname)
        notebook.addPage(page, name)
        self.pages.append((name, pname, notebook, page))

    def delPage(self, side, name):
        notebook = self.getNotebook(side)
        i, v = self.getPageItem(name)
        if v:
            del self.pages[i]
        if notebook.GetPageCount() == 0:
            self.delNotebook(side)
            self.showWindow(side, False)

    def closePage(self, name, **kwargs):
        i, v = self.getPageItem(name)
        if v:
            pagename, panelname, notebook, page = v
            return notebook.closePage(page, **kwargs)

    def getPage(self, name):
        i, v = self.getPageItem(name)
        if v:
            pagename, panelname, notebook, page = v
            return page
        else:
            return None
            
    def getPageItem(self, name):
        """
        Find the page object according to name parameter.
        name can be a string or a page object
        """
        
        for i, v in enumerate(self.pages):
            pagename, panelname, notebook, page = v
            if isinstance(name, (str, unicode)):
                if name == pagename:
                    return i, v
            else:   #is page object
                if page is name:
                    return i, v
        else:
            return -1, None
        
    def getPages(self):
        """
        Return pages list
        """
        return self.pages
    
    def setName(self, page, name):
        """
        Change page title
        """
        i, obj = self.getPageItem(page)
        if obj:
            pagename, pname, notebook, p = obj
            index = notebook.getPageIndex(p)
            if index > 0:
                notebook.SetPageText(index, name)
                self.pages[i] = name, pname, notebook, p
                return
            
    def setImageIndex(self, page, imagename):
        i, obj = self.getPageItem(page)
        if obj:
            pagename, pname, notebook, p = obj
            notebook.setImageIndex(page, imagename)
            
    def get_status(self):
        s = {}
        s['left'] = (self.LeftIsVisible, self.leftsize)
        s['right'] = (self.RightIsVisible, self.rightsize)
        s['bottom'] = (self.BottomIsVisible, self.bottomsize)
        return s
    
    def restore_status(self, s):
        if s:
            self.LeftIsVisible, self.leftsize = s['left']
            notebook = self.getNotebook('left')
            if not notebook or notebook.GetPageCount() == 0:
                self.LeftIsVisible = False
            self.RightIsVisible, self.rightsize = s['right']
            notebook = self.getNotebook('right')
            if not notebook or notebook.GetPageCount() == 0:
                self.RightIsVisible = False
            self.BottomIsVisible, self.bottomsize = s['bottom']
            notebook = self.getNotebook('bottom')
            if not notebook or notebook.GetPageCount() == 0:
                self.BottomIsVisible = False
            wx.CallAfter(self.OnSize, None)
            wx.CallAfter(self.Refresh)
            
    def visible(self, sidename):
        sidename = sidename.lower()
        if sidename == 'left':
            return self.LeftIsVisible
        elif sidename == 'right':
            return self.RightIsVisible
        elif sidename == 'bottom':
            return self.BottomIsVisible

from modules.wxctrl import FlatNotebook as FNB
class Notebook(FNB.FlatNotebook, Mixin.Mixin):
    __mixinname__ = 'notebook'
    popmenulist = [ (None,
    [
        (100, 'IDPM_CLOSE', tr('Close'), wx.ITEM_NORMAL, 'OnClose', tr('Closes an opened window.')),
        (110, '', '-', wx.ITEM_SEPARATOR, None, ''),
    ]),
]
    imagelist = {}
    pageimagelist = {'html':'images/file_html.gif', 'document':'images/file_txt.gif'}
    
    def __init__(self, parent, panel, side, style=0):
        self.initmixin()

        FNB.FlatNotebook.__init__(self, parent, -1, style=style|FNB.FNB_VC8|FNB.FNB_X_ON_TAB|FNB.FNB_NO_X_BUTTON, size=(0, 0))
        self.parent = parent
        self.panel = panel
        self.side = side
        self.mainframe = self.panel.mainframe

        #@add_menu menulist
        self.callplugin_once('add_menu', Notebook.popmenulist)
        #@add_menu_image_list imagelist
        self.callplugin_once('add_menu_image_list', Notebook.imagelist)
        #@add_page_image_list imagelist
        self.callplugin_once('add_page_image_list', Notebook.pageimagelist)
        self.popmenu = makemenu.makepopmenu(self, self.popmenulist, self.imagelist)
        self.SetRightClickMenu(self.popmenu)
        FNB.EVT_FLATNOTEBOOK_PAGE_CHANGED(self, self.GetId(), self.OnPageChanged)
#        wx.EVT_LEFT_UP(self, self.OnPageChanged)
        wx.EVT_LEFT_DCLICK(self._pages, self.OnDClick)
#        wx.EVT_RIGHT_DOWN(self, self.OnPopUp)
        FNB.EVT_FLATNOTEBOOK_PAGE_CLOSING(self, self.GetId(), self.OnClose)
        self.SetActiveTabColour('#7FFFD4')

        self.pageimageindex = {}
        pageimages = wx.ImageList(16, 16)
        for i, v in enumerate(self.pageimagelist.items()):
            name, imagefilename = v
            image = common.getpngimage(imagefilename)
            pageimages.Add(image)
            self.pageimageindex[name] = i
        self.pageimages = pageimages
        
        self.SetImageList(self.pageimages)
        
        self.delete_must = False
        self.old_size = None
        self.full = False
        
        self.callplugin('init', self)

    def OnPageChanged(self, event):
#        wx.CallAfter(self.GetPage(self.GetSelection()).SetFocus)
        event.Skip()

    def OnUpdateUI(self, event):
        if hasattr(Globals.app.wxApp, 'Active') and Globals.app.wxApp.Active:
            self.callplugin('on_update_ui', self, event)
    
    def OnClose(self, event):
        if not self.delete_must:
            if hasattr(event, 'Veto'):
                event.Veto()
            name = self.GetPageText(self.GetSelection())
            wx.CallAfter(self.closePage, name)
        else:
            self.delete_must = False

    def OnPopUp(self, event):
        self.PopupMenu(self.popmenu, event.GetPosition())

    def closePage(self, name, **kwargs):
        index = self.getPageIndex(name)
        if index > -1:
            page = self.GetPage(index)
            if hasattr(page, 'canClose'):
                if page.canClose():
                    self.callplugin('close_page', page, name)
                    if hasattr(page, 'OnClose'):
                        page.OnClose(self, **kwargs)
                    self.delete_must = True
                    self.DeletePage(index)
                    self.panel.delPage(self.side, name)
            else:
                self.callplugin('close_page', page, name)
                if hasattr(page, 'OnClose'):
                    page.OnClose(self, **kwargs)
                self.delete_must = True
                self.DeletePage(index)
                self.panel.delPage(self.side, name)
            return True
        else:
            return False

    def addPage(self, page, name):
        self.AddPage(page, name)

    def showPage(self, name):
        index = self.getPageIndex(name)
        if index > -1:
            self.SetSelection(index)
            self.GetPage(index).SetFocus()
            return True
        else:
            return False

    def getPageIndex(self, name):
        for i in range(self.GetPageCount()):
            if isinstance(name, (str, unicode)):
                if self.GetPageText(i) == name:
                    return i
            else:
                if self.GetPage(i) is name:
                    return i
        else:
            return -1

    def getSide(self):
        return self.side
    
    def OnDClick(self, event):
        pages = self._pages
        where, tabIdx = pages.HitTest(event.GetPosition())
               
        if where == FNB.FNB_RIGHT_ARROW:
            pages.RotateRight()
        
        elif where == FNB.FNB_LEFT_ARROW:
            pages.RotateLeft()
        else:
            panel = self.parent.GetParent()
            if not self.full:
                if self.side == 'left':
                    self.old_size = panel.leftsize
                elif self.side == 'right':
                    self.old_size = panel.rightsize
                elif self.side == 'bottom':
                    self.old_size = panel.bottomsize
                panel.setSize(self.side, 50)
                panel.OnSize(None)
                panel.Refresh()
                self.full = True
            else:
                panel.setSize(self.side, self.old_size)
                panel.OnSize(None)
                panel.Refresh()
                self.full = False
            
    def setImageIndex(self, page, imagename):
        imageindex = self.pageimageindex.get(imagename, -1)
        if imageindex > -1:
            self.SetPageImage(self.getPageIndex(page), imageindex)
        