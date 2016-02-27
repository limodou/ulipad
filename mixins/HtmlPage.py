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
#   $Id: HtmlPage.py 1731 2006-11-22 03:35:50Z limodou $

from modules import Mixin
import DocumentBase
import wx
import wx.html as html
import tempfile
import os
import sys
from modules import Globals

class HtmlImpactView(wx.Panel):
    def __init__(self, parent, content):
        wx.Panel.__init__(self, parent, -1)

        mainframe = Globals.mainframe
        box = wx.BoxSizer(wx.VERTICAL)
        if sys.platform == 'win32':
            self.html = IEHtmlWindow(self)
        else:
            self.html = DefaultHtmlWindow(self)
        self.tmpfilename = None
        self.load(content)
        if sys.platform == 'win32':
            box.Add(self.html.ie, 1, wx.EXPAND|wx.ALL, 1)
        else:
            box.Add(self.html, 1, wx.EXPAND|wx.ALL, 1)
            self.html.SetRelatedFrame(mainframe, mainframe.app.appname + " - Browser [%s]")
            self.html.SetRelatedStatusBar(0)

        self.SetSizer(box)

    def load(self, content):
        if not self.tmpfilename:
            fd, self.tmpfilename = tempfile.mkstemp('.html')
            os.write(fd, content)
            os.close(fd)
        else:
            file(self.tmpfilename, 'w').write(content)
        self.html.Load(self.tmpfilename)
       
    def canClose(self):
        return True
    
    def OnClose(self, win):
        if self.tmpfilename:
            try:
                os.unlink(self.tmpfilename)
            except:
                pass
    
class HtmlDialog(wx.Dialog):
    def __init__(self, parent, title, message):
        wx.Dialog.__init__(self, parent, -1, style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.RESIZE_BOX,
                size=(400, 300), title = title)

        fd, self.filename = tempfile.mkstemp('.html')
        os.write(fd, message)
        os.close(fd)

        box = wx.BoxSizer(wx.VERTICAL)
        if sys.platform == 'win32':
            self.html = IEHtmlWindow(self)
        else:
            self.html = DefaultHtmlWindow(self)
        self.html.Load(self.filename)
        if sys.platform == 'win32':
            box.Add(self.html.ie, 1, wx.EXPAND|wx.ALL, 1)
        else:
            box.Add(self.html, 1, wx.EXPAND|wx.ALL, 1)
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        btnOK = wx.Button(self, wx.ID_OK, tr("OK"))
        btnOK.SetDefault()
        box2.Add(btnOK, 0, 0)
        box.Add(box2, 0, wx.ALIGN_CENTER|wx.ALL, 2)

        self.SetSizer(box)
#               self.SetAutoLayout(True)

#               box.Fit(self)

        wx.EVT_BUTTON(btnOK, wx.ID_OK, self.OnOk)
        wx.EVT_CLOSE(self, self.OnOk)

    def OnOk(self, event):
        os.remove(self.filename)
        event.Skip()

class HtmlPage(wx.Panel, DocumentBase.DocumentBase, Mixin.Mixin):

    __mixinname__ = 'htmlpage'

    def __init__(self, parent, mainframe, filename, documenttype):
        self.initmixin()
        
        wx.Panel.__init__(self, parent, -1)
        DocumentBase.DocumentBase.__init__(self, parent, filename, documenttype)
        self.mainframe = mainframe
        if sys.platform == 'win32':
            self.html = IEHtmlWindow(self, filename)
        else:
            self.html = DefaultHtmlWindow(self, filename)
            self.html.SetRelatedFrame(mainframe, mainframe.app.appname + " - Browser [%s]")
            self.html.SetRelatedStatusBar(0)

        self.box = wx.BoxSizer(wx.VERTICAL)

        subbox = wx.BoxSizer(wx.HORIZONTAL)

        self.ID_EDIT = wx.NewId()
        self.btnEdit = wx.Button(self, self.ID_EDIT, tr("Edit"))
        subbox.Add(self.btnEdit, 0, wx.RIGHT, 2)

        self.ID_BACK = wx.NewId()
        self.btnBack = wx.Button(self, self.ID_BACK, "<", size=(22, -1))
        subbox.Add(self.btnBack, 0, wx.RIGHT, 2)

        self.ID_FORWARD = wx.NewId()
        self.btnForward = wx.Button(self, self.ID_FORWARD, ">", size=(22, -1))
        subbox.Add(self.btnForward, 0, wx.RIGHT, 2)

        self.ID_REFRESH = wx.NewId()
        self.btnRefresh = wx.Button(self, self.ID_REFRESH, tr("Refresh"))
        subbox.Add(self.btnRefresh, 0, wx.RIGHT, 2)

        self.box.Add(subbox, 0, wx.GROW)

        self.box.Add(wx.StaticLine(self, -1), 0, wx.EXPAND)

        if sys.platform == 'win32':
            self.box.Add(self.html.ie, 1, wx.GROW)
        else:
            self.box.Add(self.html, 1, wx.GROW)

        self.SetSizer(self.box)
        self.SetAutoLayout(True)

        self.needcheck = False
        self.pageimagename = 'htmlview'

        wx.EVT_BUTTON(self.btnEdit, self.ID_EDIT, self.OnEdit)
        wx.EVT_BUTTON(self.btnBack, self.ID_BACK, self.OnBack)
        wx.EVT_BUTTON(self.btnForward, self.ID_FORWARD, self.OnForward)
        wx.EVT_BUTTON(self.btnRefresh, self.ID_REFRESH, self.OnRefresh)
        wx.EVT_UPDATE_UI(self.btnBack, self.ID_BACK, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self.btnForward, self.ID_FORWARD, self.OnUpdateUI)
        if sys.platform == 'win32':
            import wx.lib.iewin as iewin
            iewin.EVT_StatusTextChange(self.html.ie, self.html.ie.GetId(), self.OnStatusTextChange)

    def openfile(self, filename='', encoding='', delay=False, *args, **kwargs):
        self.filename = filename
        self.html.Load(self.filename)
        self.locale = encoding
        self.opened = True

    def savefile(self, filename, encoding):
        pass

    def OnEdit(self, event):
        for document in self.mainframe.editctrl.getDocuments():   #if the file has been opened
            if document.isMe(self.filename, documenttype = 'texteditor'):
                self.mainframe.editctrl.switch(document)

    def OnBack(self, event):
        self.html.DoBack()

    def OnForward(self, event):
        self.html.DoForward()

    def OnRefresh(self, event):
        self.html.DoRefresh()

    def OnUpdateUI(self, event):
        eid = event.GetId()
        if eid == self.ID_BACK:
            event.Enable(self.html.CanBack())
        elif eid == self.ID_FORWARD:
            event.Enable(self.html.CanForward())

    def OnStatusTextChange(self, event):
        self.mainframe.SetStatusText(event.Text, 0)

    def LoadContent(self, content):
        fd, self.filename = tempfile.mkstemp('.html')
        os.write(fd, content)
        os.close(fd)
        self.html.Load(self.filename)
    
class HtmlWindowBase:
    def __init__(self, parent, filename=''):
        self.parent = parent
        self.filename = filename

    def CanBack(self):
        return self.HistoryCanBack()

    def CanForward(self):
        return self.HistoryCanForward()

    def DoBack(self):
        self.HistoryBack()

    def DoForward(self):
        self.HistoryForward()

    def DoRefresh(self):
        self.Load(self.filename)

    def Load(self, filename):
        self.filename = filename
        self.LoadPage(filename)

    def SetPage(self, text):
        self.SetPage(text)

class DefaultHtmlWindow(html.HtmlWindow, HtmlWindowBase):
    def __init__(self, parent, filename=''):
        self.parent = parent
        HtmlWindowBase.__init__(self, parent, filename)
        html.HtmlWindow.__init__(self, parent, -1, style=wx.NO_FULL_REPAINT_ON_RESIZE)
#       comment according issue 12
#        if "gtk2" in wx.PlatformInfo:
#            self.NormalizeFontSizes()

class IEHtmlWindow(HtmlWindowBase):
    def __init__(self, parent, filename=''):
        import wx.lib.iewin as iewin
        HtmlWindowBase.__init__(self, parent, filename)
        self.ie = iewin.IEHtmlWindow(parent, -1, style = wx.NO_FULL_REPAINT_ON_RESIZE)

    def CanBack(self):
        return True

    def CanForward(self):
        return True

    def DoBack(self):
        self.ie.GoBack()

    def DoForward(self):
        self.ie.GoForward()

    def Load(self, filename):
        self.filename = filename
        self.ie.LoadUrl(filename)

    def SetPage(self, text):
        self.ie.LoadString(text)

    def DoRefresh(self):
        import wx.lib.iewin as iewin
        self.ie.RefreshPage(iewin.REFRESH_COMPLETELY)
