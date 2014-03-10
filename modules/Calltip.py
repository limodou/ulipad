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
#   $Id: Calltip.py 2055 2007-04-21 15:53:00Z limodou $
   
import wx

class MyCallTip(wx.ScrolledWindow):
    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, -1, size=(200, 50), style=wx.SIMPLE_BORDER)
        self.EnableScrolling(False, True)
        
#        self.Enable(False)
        self.parent = parent
        self.text = wx.StaticText(self, -1, label='', pos=(3, 3))
#               self.bgcolor = 'yellow'
        self.bgcolor = '#FFFFE1'

        self.active = False
        self.Hide()

    def show(self, pos, text):
        self.text.SetLabel(text.strip())
        self.active = True
        self.SetBackgroundColour(self.bgcolor)
        self.text.SetBackgroundColour(self.bgcolor)
        self.move(pos)
        self.Show()
        self.parent.SetFocus()
            
            
    def move(self, pos):    
        cw, ch = self.parent.GetClientSize()
        self.text.Wrap(int(cw*0.5))
        w, h = self.text.GetBestSize()
        fw = w + 30
        fh = min(ch*0.5, h) + 10
        self.SetSize((fw, fh))
        self.SetScrollbars(0, 20, 0, (h+19)/20)
        x, y = self.parent.PointFromPosition(pos)
        dh = self.parent.TextHeight(self.parent.LineFromPosition(pos))
        cw, ch = self.parent.GetClientSize()
        if y + dh + fh > ch:
            if y - fh + 8 >= 0:
                y -= fh + 8
            else:
                y += dh
        else:
            y += dh
        if x + fw > cw:
            x -= fw
            if x < 0:
                x = 20
        self.Move((x, y))
        
        
    def cancel(self):
        if self.active:
            self.Scroll(0, 0)
            self.Hide()
            self.active = False

    def setHightLight(self, start, end):
        pass
