#   Programmer: limodou
#   E-mail:     limodou@gmail.com
#
#   Copyleft 2007 limodou
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

import sys
import traceback
import wx
from mixins.Editor import TextEditor
from modules import Globals
import modules.meide as ui
from modules.wxctrl import FlatButtons
from modules import common
import wx.lib.dialogs

class MyWindow(wx.Window):
    def __init__(self, parent, codes):
        wx.Window.__init__(self, parent, -1, style=wx.SUNKEN_BORDER )
        self.parent = parent
        
        self.codes = codes
        
        self.SetBackgroundColour(wx.WHITE)
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.error = False
        
    def OnPaint(self, event):
        namespace = {'self':self, 'event':event, 'wx':wx}
        if not self.error and self.codes.get('OnPaint', None):
            try:
                code = compile((self.codes['OnPaint'].replace('\r\n', '\n') + '\n'), 'canvastest', 'exec')
                self.error = False
            except:
                self.error = True
                traceback.format_exception(*sys.exc_info())
                def f():
                    d = wx.lib.dialogs.ScrolledMessageDialog(self.parent, (tr("Error compiling script.\n\nTraceback:\n\n") +
                        ''.join(trace)), tr("Error"), wx.DefaultPosition, wx.Size(400,300))
                    d.ShowModal()
                    d.Destroy()
                wx.CallAfter(f)
                return
            
            try:
                exec code in namespace
                self.error = False
            except:
                self.error = True
                trace = traceback.format_exception(*sys.exc_info())
                def f():
                    d = wx.lib.dialogs.ScrolledMessageDialog(self.parent, (tr("Error running script.\n\nTraceback:\n\n") +
                        ''.join(trace)), tr("Error"), wx.DefaultPosition, wx.Size(400,300))
                    d.ShowModal()
                    d.Destroy()
                wx.CallAfter(f)
                return
        else:
            dc = wx.PaintDC(self)
            dc.Clear()
            event.Skip
            
    def refresh(self):
        self.error = False
        self.Refresh(True)
        self.Update()
        
class MyCode(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        
        self.sizer = sizer = ui.VBox(padding=0, namebinding='widget').create(self).auto_layout()
        box = sizer.add(ui.HBox(padding=2))
        self.btnRefresh = FlatButtons.FlatBitmapButton(self, -1, 
            common.getpngimage('images/classbrowserrefresh.gif'))
        box.add(self.btnRefresh)
        self.code = TextEditor(self, None, 'canvas test', 'texteditor', True)
        self.code.cansavefileflag = False
        self.code.needcheckfile = False
        self.code.savesession = False
        sizer.add(self.code, proportion=1, flag=wx.EXPAND|wx.ALL, border=3)
        sizer.auto_fit(0)
        
class Canvas(wx.Frame):

    def __init__(self, parent):
        
        self.codes = {}

        wx.Frame.__init__(self, parent, -1, title=tr('Canvas Test'))
        
        self.splitter = wx.SplitterWindow(self)
        
#        self.top = wx.SplitterWindow(self.splitter)
#        self.events = wx.TreeCtrl(self.top)
#        self.canvas = MyWindow(self.top, self.codes)
        self.canvas = MyWindow(self.splitter, self.codes)
#        self.top.SplitVertically(self.events, self.canvas, -200)
        
        self.code_panel = MyCode(self.splitter)
        self.code = self.code_panel.code
        self.code.AddText('import wx\ndc = wx.PaintDC(self)\n')
        self.btnRefresh = self.code_panel.btnRefresh
        lexer = Globals.mainframe.lexers.getNamedLexer('python')
        if lexer:
            lexer.colourize(self.code)
        self.splitter.SetMinimumPaneSize(50)
#        self.splitter.SplitHorizontally(self.top, self.code_panel)
        self.splitter.SplitHorizontally(self.canvas, self.code_panel)
        
        wx.EVT_BUTTON(self.btnRefresh, self.btnRefresh.GetId(), self.OnRefresh)
        
        wx.CallAfter(self.code.SetFocus)
        
    def OnRefresh(self, event):
        self.codes['OnPaint'] = self.code.GetText()
        self.canvas.refresh()
        
