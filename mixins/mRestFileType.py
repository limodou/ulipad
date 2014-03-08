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
#   $Id$

import wx
from modules import Mixin
import FiletypeBase
from modules import Globals
from modules.Debug import error

class RestFiletype(FiletypeBase.FiletypeBase):

    __mixinname__ = 'restfiletype'
    menulist = [ (None,
        [
            (890, 'IDM_REST', 'ReST', wx.ITEM_NORMAL, None, ''),
        ]),
    ]
    toollist = []               #your should not use supperclass's var
    toolbaritems= {}

def add_filetypes(filetypes):
    filetypes.extend([('rst', RestFiletype)])
Mixin.setPlugin('changefiletype', 'add_filetypes', add_filetypes)

def add_rest_menu(menulist):
    menulist.extend([('IDM_REST', #parent menu id
            [
                (100, 'IDM_REST_VIEW_IN_LEFT', tr('View HTML Result In Left Pane'), wx.ITEM_NORMAL, 'OnRestViewHtmlInLeft', tr('Views HTML result in left pane.')),
                (110, 'IDM_REST_VIEW_IN_BOTTOM', tr('View HTML Result In Bottom Pane'), wx.ITEM_NORMAL, 'OnRestViewHtmlInBottom', tr('Views HTML result in bottom pane.')),
            ]),
    ])
Mixin.setPlugin('restfiletype', 'add_menu', add_rest_menu)

def OnRestViewHtmlInLeft(win, event):
    dispname = win.createRestHtmlViewWindow('left', Globals.mainframe.editctrl.getCurDoc())
    if dispname:
        win.panel.showPage(dispname)
Mixin.setMixin('mainframe', 'OnRestViewHtmlInLeft', OnRestViewHtmlInLeft)

def OnRestViewHtmlInBottom(win, event):
    dispname = win.createRestHtmlViewWindow('bottom', Globals.mainframe.editctrl.getCurDoc())
    if dispname:
        win.panel.showPage(dispname)
Mixin.setMixin('mainframe', 'OnRestViewHtmlInBottom', OnRestViewHtmlInBottom)

def closefile(win, document, filename):
    for pagename, panelname, notebook, page in Globals.mainframe.panel.getPages():
        if is_resthtmlview(page, document):
            Globals.mainframe.panel.closePage(page)
Mixin.setPlugin('mainframe', 'closefile', closefile)

def setfilename(document, filename):
    for pagename, panelname, notebook, page in Globals.mainframe.panel.getPages():
        if is_resthtmlview(page, document):
            title = document.getShortFilename()
#            Globals.mainframe.panel.setName(page, title)
Mixin.setPlugin('editor', 'setfilename', setfilename)

def createRestHtmlViewWindow(win, side, document):
    dispname = document.getShortFilename()
    obj = None
    for pagename, panelname, notebook, page in win.panel.getPages():
        if is_resthtmlview(page, document):
            obj = page
            break

    if not obj:
        if win.document.documenttype == 'texteditor':
            text = html_fragment(document.GetText().encode('utf-8'), win.document.filename)
            if text:
                page = RestHtmlView(win.panel.createNotebook(side), text, document)
                win.panel.addPage(side, page, dispname)
                win.panel.setImageIndex(page, 'html')
                return page
    return obj
Mixin.setMixin('mainframe', 'createRestHtmlViewWindow', createRestHtmlViewWindow)

def other_popup_menu(editctrl, document, menus):
    if document.documenttype == 'texteditor' and document.languagename == 'rst':
        menus.extend([ (None,
            [
                (900, 'IDPM_REST_HTML_LEFT', tr('View Html Result in Left Pane'), wx.ITEM_NORMAL, 'OnRestHtmlViewLeft', tr('Views html result in left pane.')),
                (910, 'IDPM_REST_HTML_BOTTOM', tr('View Html Result in Bottom Pane'), wx.ITEM_NORMAL, 'OnRestHtmlViewBottom', tr('Views html result in bottom pane.')),
            ]),
        ])
Mixin.setPlugin('editctrl', 'other_popup_menu', other_popup_menu)

def OnRestHtmlViewLeft(win, event=None):
    win.mainframe.OnRestViewHtmlInLeft(None)
Mixin.setMixin('editctrl', 'OnRestHtmlViewLeft', OnRestHtmlViewLeft)

def OnRestHtmlViewBottom(win, event=None):
    win.mainframe.OnRestViewHtmlInBottom(None)
Mixin.setMixin('editctrl', 'OnRestHtmlViewBottom', OnRestHtmlViewBottom)

def html_fragment(content, path=''):
    from docutils.core import publish_string
    
    try:
        return publish_string(content, writer_name = 'html', source_path=path)
    except:
        error.traceback()
        return None

from mixins import HtmlPage
import tempfile
import os
_tmp_rst_files_ = []

class RestHtmlView(wx.Panel):
    def __init__(self, parent, content, document):
        wx.Panel.__init__(self, parent, -1)
    
        mainframe = Globals.mainframe
        self.document = document
        self.resthtmlview = True
        self.rendering = False
        box = wx.BoxSizer(wx.VERTICAL)
        self.chkAuto = wx.CheckBox(self, -1, tr("Stop auto updated"))
        box.Add(self.chkAuto, 0, wx.ALL, 2)
        if wx.Platform == '__WXMSW__':
            import wx.lib.iewin as iewin
            
            self.html = HtmlPage.IEHtmlWindow(self)
            if wx.VERSION < (2, 8, 8, 0):
                self.html.ie.Bind(iewin.EVT_DocumentComplete, self.OnDocumentComplete, self.html.ie)
                self.html.ie.Bind(iewin.EVT_ProgressChange, self.OnDocumentComplete, self.html.ie)
            else:
                self.html.ie.AddEventSink(self)
        else:
            self.html = HtmlPage.DefaultHtmlWindow(self)
            self.html.SetRelatedFrame(mainframe, mainframe.app.appname + " - Browser [%s]")
            self.html.SetRelatedStatusBar(0)
            
        self.tmpfilename = None
        self.load(content)
        if wx.Platform == '__WXMSW__':
            box.Add(self.html.ie, 1, wx.EXPAND|wx.ALL, 1)
        else:
            box.Add(self.html, 1, wx.EXPAND|wx.ALL, 1)
    
        self.SetSizer(box)
        
    def create_tempfile(self, content):
        if not self.tmpfilename:
            path = os.path.dirname(self.document.filename)
            if not path:
                path = None
            fd, self.tmpfilename = tempfile.mkstemp('.html', dir=path)
            os.write(fd, content)
            os.close(fd)
            _tmp_rst_files_.append(self.tmpfilename)
        else:
            file(self.tmpfilename, 'w').write(content)
        
    def load(self, content):
        self.create_tempfile(content)
        self.html.Load(self.tmpfilename)
        
    def refresh(self, content):
        self.create_tempfile(content)
        wx.CallAfter(self.html.DoRefresh)
       
    def canClose(self):
        return True
    
    def isStop(self):
        return self.chkAuto.GetValue()
    
    def OnClose(self, win):
        if self.tmpfilename:
            try:
                _tmp_rst_files_.remove(self.tmpfilename)
                os.unlink(self.tmpfilename)
            except:
                pass
    
    #for version lower than 2.8.8.0
    def OnDocumentComplete(self, evt):
        if self.FindFocus() is not self.document:
            self.document.SetFocus()
            
    #for version higher or equal 2.8.8.0
    def DocumentComplete(self, this, pDisp, URL):
        if self.FindFocus() is not self.document:
            self.document.SetFocus()
            
def is_resthtmlview(page, document):
    if hasattr(page, 'resthtmlview') and page.resthtmlview and page.document is document:
        return True
    else:
        return False

def on_modified(win):
    for pagename, panelname, notebook, page in Globals.mainframe.panel.getPages():
        if is_resthtmlview(page, win) and not page.isStop() and not page.rendering:
            page.rendering = True
            from modules import Casing
            
            def f():
                try:
                    text = html_fragment(win.GetText().encode('utf-8'), win.filename)
                    page.refresh(text)
                finally:
                    page.rendering = False
            d = Casing.Casing(f)
            d.start_thread()
            break
Mixin.setPlugin('editor', 'on_modified', on_modified)

def on_close(win, event):
    for i in _tmp_rst_files_:
        if os.path.exists(i):
            try:
                os.unlink(i)
            except:
                pass
Mixin.setPlugin('mainframe','on_close', on_close)
