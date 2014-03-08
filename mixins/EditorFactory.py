#coding=utf-8
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
#   $Id: EditorFactory.py 2015 2007-03-11 10:59:12Z limodou $

import wx
import os
from modules import Mixin
from modules import makemenu
from MyUnicodeException import MyUnicodeException
from modules.Debug import error
from modules import common
#try:
#    import wx.lib.flatnotebook as FNB
#except:
from modules.wxctrl import FlatNotebook as FNB

class EditorFactory(FNB.FlatNotebook, Mixin.Mixin):

    __mixinname__ = 'editctrl'
    popmenulist = []
    imagelist = {}
    panellist = {}
    pageimagelist = {}
    _id = 0

    def __init__(self, parent, mainframe):
        self.initmixin()

        self.parent = parent
        self.mainframe = mainframe
        self.pref = self.mainframe.pref
        self.app = self.mainframe.app
        self.mainframe.editctrl = self
        self.document = None
        self.lastfilename = None
        self.lastlanguagename = ''
        self.lastdocument = None

        if self.pref.notebook_direction == 0:
            style = 0
        else:
            style = FNB.FNB_BOTTOM
        FNB.FlatNotebook.__init__(self, parent, -1, 
            style=style|FNB.FNB_SMART_TABS|FNB.FNB_VC8|FNB.FNB_X_ON_TAB|
                FNB.FNB_NO_X_BUTTON|FNB.FNB_DROPDOWN_TABS_LIST|FNB.FNB_MOUSE_MIDDLE_CLOSES_TABS)
        self.id = self.GetId()


        #make popup menu
        #@add_menu menulist
        self.callplugin_once('add_menu', EditorFactory.popmenulist)
        #@add_menu_image_list imagelist
        self.callplugin_once('add_menu_image_list', EditorFactory.imagelist)
        #@add_panel_list panellist
        self.callplugin_once('add_panel_list', EditorFactory.panellist)

        self.popmenu = makemenu.makepopmenu(self, EditorFactory.popmenulist, EditorFactory.imagelist)
#        self.SetRightClickMenu(self.popmenu)
        FNB.EVT_FLATNOTEBOOK_PAGE_CHANGED(self, self.id, self.OnChanged)
        FNB.EVT_FLATNOTEBOOK_PAGE_CLOSING(self, self.id, self.OnClose)
        wx.EVT_LEFT_DCLICK(self._pages, self.OnDClick)
        FNB.EVT_FLATNOTEBOOK_PAGE_CONTEXT_MENU(self, self.id, self.OnPopup)

        self.imageindex = {}
        pageimages = wx.ImageList(16, 16)
        for i, v in enumerate(self.pageimagelist.items()):
            name, imagefilename = v
            image = common.getpngimage(imagefilename)
            pageimages.Add(image)
            self.imageindex[name] = i
        self.pageimages = pageimages

#        self.AssignImageList(self.pageimages)
        self.SetImageList(self.pageimages)
        self.skip_closing = False
        self.skip_page_change = False
        self.full = False
        self.last_side_panel_status = None

        #set FlatNotebook style
        x = common.get_config_file_obj()
        tab_color = x.default.get('editor_tab_color', '#98FB98')
        self.SetActiveTabColour(tab_color)
#        self.SetActiveTabTextColour('white')
#        self.SetNonActiveTabTextColour('black')
#        self.SetAllPagesShapeAngle(15)


    def openPage(self):
        self.callplugin('init', self)

        if not self.execplugin('openpage', self):
            self.new()

        for file in self.mainframe.filenames:
            self.new(os.path.join(self.app.workpath, file))

    def changeDocument(self, document, delay=False):
        if not delay:
            #open delayed document
            if not document.opened:
                try:
                    document.openfile(document.filename, document.locale, False)
                    #add restore session process
                    for v in self.pref.sessions:
                        if len(v) == 4:
                            filename, row, col, bookmarks = v
                            state = row
                        else:
                            filename, state, bookmarks = v
                        if filename == document.filename:
                            wx.CallAfter(setStatus, document, state, bookmarks)
                except MyUnicodeException, e:
                    error.traceback()
                    e.ShowMessage()
                    wx.CallAfter(self.closefile, document)
                    return
                except:
                    error.traceback()
                    filename = document.filename
                    common.showerror(self, tr("Can't open the file %s.") % common.uni_file(filename))
                    wx.CallAfter(self.closefile, document)
                    return
            self._changeDocument(document)
            if self.document:
                wx.CallAfter(self.document.SetFocus)
        return document

    def _changeDocument(self, document):
        self.mainframe.document = document
        self.document = document
        self.showTitle(self.document)
        if self.lastdocument != self.document or self.lastfilename != document.filename:
            if self.lastfilename is not None:
                self.callplugin('on_document_leave', self, self.lastfilename, self.lastlanguagename)
            self.callplugin('on_document_enter', self, document)
        if self.lastlanguagename != document.languagename:
            self.callplugin('on_document_lang_leave', self, self.lastfilename, self.lastlanguagename)
            self.callplugin('on_document_lang_enter', self, document)

        self.lastfilename = document.filename
        self.lastlanguagename = document.languagename
        self.lastdocument = document

    def getIndex(self, document):
        for i, d in enumerate(self.getDocuments()):
            if d == document:
                return i
        return -1

    def getDoc(self, index):
        if index < 0 or index >= len(self.getDocuments()):
            return None
        return self.getDocuments()[index]
    
    def new(self, filename='', encoding='', delay=False, defaulttext='', language='', documenttype='texteditor'):
        doc = None
        if filename:
            for document in self.getDocuments():  #if the file has been opened
                if document.isMe(filename, documenttype):
                    self.switch(document, delay)
                    doc = document
                    break
            else:                   #the file hasn't been opened
                #if current page is empty and has not been modified
                if (self.document != None) and self.document.canopenfile(filename, documenttype):
                    #use current page , donot open a new page
                    try:
                        self.document.openfile(filename, encoding, delay, defaulttext)
                    except MyUnicodeException, e:
                        error.traceback()
                        e.ShowMessage()
                        doc = self.document
                    except:
                        error.traceback()
                        common.showerror(self, tr("Can't open the file %s.") % filename)
                        doc = self.document
                    else:
                        self.switch(self.document, delay)
                        doc = self.document
                else:
                    doc = self.newPage(filename, encoding, delay=delay, defaulttext=defaulttext, language=language, documenttype=documenttype)
        else:
            doc = self.newPage(filename, encoding, delay=delay, defaulttext=defaulttext, language=language, documenttype=documenttype)
            
        self.callplugin('afternewfile', self, doc)
        return doc
    
    def newPage(self, filename, encoding=None, documenttype='texteditor', delay=False, defaulttext='', language='', **kwargs):
        try:
            panelclass = self.panellist[documenttype]
        except:
            error.traceback()
            return None

        panel = None
        try:
            panel = panelclass(self, filename, **kwargs)
            document = panel.document
            EditorFactory._id += 1
            document.serial_id = EditorFactory._id
            document.openfile(filename, encoding, delay, defaulttext, language)
        except MyUnicodeException, e:
            error.traceback()
            e.ShowMessage()
            if panel:
                panel.Destroy()
            return None
        except:
            error.traceback()
            if panel:
                panel.Destroy()
            common.showerror(self, tr("Can't open the file %s.") % filename)
            return None

        self.AddPage(panel, document.getShortFilename(), select=False)
        
        imageindex = self.imageindex.get(document.pageimagename, -1)
        if imageindex > -1:
            self.SetPageImage(self.GetPageCount() - 1, imageindex)
        self.switch(document, delay)
        return document

    def OnChanged(self, event):
        if not self.skip_page_change:
            document = self.getDoc(event.GetSelection())
            self.changeDocument(document)
        old = self.getDoc(event.GetOldSelection())
        if old:
            event.FNB = True
            old.callplugin('on_kill_focus', old, event)
        self.skip_page_change = False
        event.Skip()

    def OnPopup(self, event):
        other_menus = []
        if self.popmenu:
            self.popmenu.Destroy()
            self.popmenu = None
        self.callplugin('other_popup_menu', self, self.getCurDoc(), other_menus)
        import copy
        if other_menus:
            pop_menus = copy.deepcopy(EditorFactory.popmenulist + other_menus)
        else:
            pop_menus = copy.deepcopy(EditorFactory.popmenulist)
        self.popmenu = pop_menus = makemenu.makepopmenu(self, pop_menus, EditorFactory.imagelist)
    
        self.PopupMenu(self.popmenu)
        
    def OnPopUpMenu(self, event):
        eid = event.GetId()
        if eid == self.IDPM_CLOSE:
            self.mainframe.OnFileClose(event)
        elif eid == self.IDPM_CLOSE_ALL:
            self.mainframe.OnFileCloseAll(event)
        elif eid == self.IDPM_SAVE:
            self.mainframe.OnFileSave(event)
        elif eid == self.IDPM_FILE_SAVE_ALL:
            self.mainframe.OnFileSaveAll(event)
        elif eid == self.IDPM_SAVEAS:
            self.mainframe.OnFileSaveAs(event)

    def switch(self, document, delay=False):
        try:
            index = self.getIndex(document)
        except:
            error.traceback()
            return
        self.showPageTitle(document)
        if not delay:
#            if index != self.GetSelection():
#                self.SetSelection(index)
            self.SetSelection(index)
            d = document
            if not document.opened:
                d = self.changeDocument(document, False)
            else:
                self._changeDocument(document)

    def getDispTitle(self, ctrl):
        if ctrl.title:
            return ctrl.title

        if ctrl.isModified():
            pagetitle = ctrl.getFilename() + ' *'
        else:
            pagetitle = ctrl.getFilename()

        if isinstance(pagetitle, str):
            pagetitle = common.decode_string(pagetitle, common.defaultfilesystemencoding)

        return pagetitle
    
    def getCurDoc(self):
        return self.getDoc(self.GetSelection())
    
    def getDocuments(self):
        s = []
        for i in range(self.GetPageCount()):
            try:
                s.append(self.GetPage(i).document)
            except:
                pass
        return s

    def showPageTitle(self, ctrl):
        title = os.path.basename(ctrl.getShortFilename())
        if isinstance(title, str):
            title = common.decode_string(title, common.defaultfilesystemencoding)
        if ctrl.isModified():
            title = '* ' + title
        index = self.getIndex(ctrl)
        wx.CallAfter(self.EnsureVisible, self.getIndex(ctrl))
        if title != self.GetPageText(index):
            wx.CallAfter(self.SetPageText, self.getIndex(ctrl), title)

    def showTitle(self, ctrl):
        title = u"%s - %s" % (self.app.appname, self.getDispTitle(ctrl))
        if title != self.mainframe.GetTitle():
            self.mainframe.SetTitle(title)

    def closefile(self, document):
        try:
            index = self.getIndex(document)
        except:
            return
        self.callplugin('beforeclosefile', self, document)
        selected = self.GetSelection()
        self.skip_closing = True
        self.skip_page_change = True
        self.DeletePage(index)
#        if index >= len(self.getDocuments()):
#            index = len(self.getDocuments())-1
#        if index >= 0:
#            self.switch(self.getDoc(index))
#        else:
#            self.new()
#        self.document.SetFocus()
        #if the page to close is not selected, no need to switch page
        if index == selected: 
            #if index > 0:
            if len(self.getDocuments()) > 0:
                if index >= len(self.getDocuments()):
                    index = len(self.getDocuments())-1
                # only swith page when there is a page to switch to
                self.switch(self.getDoc(index))
            else:
                self.new()
        self.document.SetFocus()

        self.callplugin('afterclosefile', self)

    def savefile(self, document, filename, encoding):
        try:
            document.savefile(filename, encoding)
            document.SetFocus()
        except MyUnicodeException, e:
            error.traceback()
            e.ShowMessage()
            return False
        except:
            error.traceback()
            return False
        return True
    
    def OnClose(self, event):
        if not self.skip_closing:
            event.Veto()
            document = self.getDoc(event.GetSelection())
            wx.CallAfter(self.mainframe.CloseFile, document)
        else:
            event.Skip()
        self.skip_closing = False
        
    def OnDClick(self, event):
        pages = self._pages
        where, tabIdx = pages.HitTest(event.GetPosition())
               
        if where == FNB.FNB_RIGHT_ARROW:
            pages.RotateRight()
        
        elif where == FNB.FNB_LEFT_ARROW:
            pages.RotateLeft()
        
        else:            
            panel = self.mainframe.panel
            if not self.full:
                s = self.last_side_panel_status = panel.get_status()
                status = {}
                status['left'] = (False, s['left'][1])
                status['right'] = (False, s['right'][1])
                status['bottom'] = (False, s['bottom'][1])
                panel.restore_status(status)
                self.full = True
            else:
                panel.restore_status(self.last_side_panel_status)
                self.full = False
    
    def new_with_state(self, fullstate):
        filename = fullstate[0]
        for i, s in enumerate(self.pref.sessions):
            f = s[0]
            if f == filename:
                self.pref.sessions[i] = fullstate
        document = self.new(filename)
        if document:
            wx.CallAfter(document.SetFocus)
        return document
    
def setStatus(document, state, bookmarks):
    if isinstance(state, tuple):
        document.restore_state(state)
    else:
        document.GotoLine(state)
    for line in bookmarks:
        document.MarkerAdd(line, 0)
