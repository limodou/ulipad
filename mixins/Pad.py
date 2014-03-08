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
import os.path
from modules import Globals

class PAD(wx.MiniFrame):
    def __init__(self, parent, filename='memo.txt', title='', style=wx.DEFAULT_FRAME_STYLE):
        x, y, w, h = Globals.mainframe.GetClientRect().Get()
        x, y = Globals.mainframe.ClientToScreenXY(x, y)
        if not hasattr(Globals.mainframe.pref, 'memo_pos'):
            memo_pos = (max(0, x+w-200), y)
        else:
            memo_pos = Globals.mainframe.pref.memo_pos
        if not hasattr(Globals.mainframe.pref, 'memo_size'):
            memo_size = (200, 300)
        else:
            memo_size = Globals.mainframe.pref.memo_size
        wx.MiniFrame.__init__(self, parent, -1, title, memo_pos, memo_size, style)
        self.filename = filename
        self.text = wx.stc.StyledTextCtrl(self, -1)
        self.text.SetMarginWidth(0, 0)   #used as symbol
        self.text.SetMarginWidth(1, 0)   #used as symbol
        self.text.SetMarginWidth(2, 0)   #used as folder
        self.text.SetMargins(0,0)
        self.text.SetWrapMode(wx.stc.STC_WRAP_WORD)
        if os.path.exists(self.filename):
            text = unicode(file(self.filename).read(), 'utf-8')
            self.text.SetText(text)
        self.text.SetFocus()
        self.text.EnsureCaretVisible()
        self.text.GotoLine(Globals.mainframe.pref.easy_memo_lastpos)

        wx.stc.EVT_STC_MODIFIED(self.text, self.text.GetId(), self.OnModified)
        wx.EVT_KEY_UP(self.text, self.OnKeyUp)
        wx.EVT_LEFT_UP(self.text, self.OnMouseUp)
        wx.EVT_CLOSE(self, self.OnClose)

    def OnModified(self, event):
        self.save()

    def save(self):
        file(self.filename, 'w').write(self.text.GetText().encode('utf-8'))
        self.save_pos()

    def save_pos(self):
        Globals.mainframe.pref.easy_memo_lastpos = self.text.GetCurrentLine()
        Globals.mainframe.pref.save()

    def OnKeyUp(self, event):
        self.save_pos()
        event.Skip()

    def OnMouseUp(self, event):
        self.save_pos()
        event.Skip()

    def OnClose(self, event):
        Globals.mainframe.pref.memo_pos = self.GetPosition()
        Globals.mainframe.pref.memo_size = self.GetSize()
        Globals.mainframe.pref.save()
        event.Skip()
