#       Programmer:     limodou
#       E-mail:         limodou@gmail.com
#
#       Copyleft 2006 limodou
#
#       Distributed under the terms of the GPL (GNU Public License)
#
#   NewEdit is free software; you can redistribute it and/or modify
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
#       $Id$
#   Update by Claudio Grondi 2006/08/14 :
#     - changed the design and added column numbers each tenth column
#     - improved synchronization of the column indicator with the cursor
#     - partially fixed the problem with wrong ruler positioning - now it
#   appears where it should,
#       but when margin width changes it still gets out of sync (re-sync by
#   switching it off/on)
#     - Alt+R switches now the ruler on/off
#     still ToDo:
#       - implementing of repainting the ruler on changes of margin width
#       - perfect full synchronization of column indicator with the cursor
#       - implementing resizing of the ruler on font and font size changes
#           (currently it works properly only with 'Courier New - 12')

import wx

class RulerCtrl(wx.Panel):
    def __init__(self, parent, size=(-1, 17), bgcolor='green', offset=0, show=False, font=None):
        wx.Panel.__init__(self, parent, -1, size=size)
        self.parent = parent
        self.bgcolor = bgcolor
        self.size = size
        self.col = -1
        self.showflag = show
        if not font:
            # self.SetFont(wx.Font(10, wx.TELETYPE, wx.NORMAL, wx.BOLD, True))
            self.setfont(wx.Font(12, wx.TELETYPE, wx.NORMAL, wx.BOLD, True))
        else:
            self.setfont(font)
#        self.offset = offset + 2*(self.w - 1)
        self.offset = offset
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        if not show:
            self.Hide()

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.SetBackground(wx.Brush(self.bgcolor))
        dc.Clear()

        # dc.SetFont(self.GetFont())
        # w = self.GetCharWidth() - 1

        ww, hh = self.GetSize()
        x = self.offset
        y = hh / 2 + hh / 4

        dc.SetPen(wx.Pen('black'))
        dc.DrawLine(x, y, ww, y)

        for i, ii in enumerate(range(x, ww, self.w)): # (CGr)
            if i == 0:
                dc.SetPen(wx.Pen('black'))
                dc.DrawLine(ii, y, ii, y - 9)
            elif i % 10 == 0:
                dc.SetPen(wx.Pen('black'))
                dc.DrawLine(ii, y, ii, y - 9)
                dc.SetTextForeground('grey')
                dc.SetFont(wx.Font(8, wx.TELETYPE, wx.NORMAL, wx.LIGHT, False))
                dc.DrawText('%i'%i,ii-6,y-13)
            elif i % 5 == 0:
                dc.SetPen(wx.Pen('black'))
                dc.DrawLine(ii, y, ii, y - 6)
            else:
                dc.SetPen(wx.Pen('black'))
                dc.DrawLine(ii, y, ii, y - 3)

        self.position(self.col)


    def position(self, col):
        def draw_triangle(x, y, size, color):
            dc = wx.ClientDC(self)
            dc.SetPen(wx.Pen(color))
            for i in range(size):
                dc.DrawLine(x-i, y-i, x+i, y-i)

        def get_col_xy(col):
            ww, hh = self.GetSize()
            x = self.offset
            y = hh / 2 - hh / 4
            return self.offset + col*self.w, y

        x, y = get_col_xy(self.col)
        draw_triangle(x, y, 5, self.bgcolor)
        self.col = col
        x, y = get_col_xy(self.col)
        draw_triangle(x, y, 5, 'black')

    def show(self, flag):
        if flag:
            self.Show()
            self.parent.GetSizer().Layout()
        else:
            self.Hide()
            self.parent.GetSizer().Layout()
        self.showflag = flag

    def setfont(self, font):
        self.SetFont(font)
        self.w = self.GetCharWidth() - 1
        if self.showflag:
            self.Refresh()

    def setoffset(self, offset):
        if offset != self.offset:
            self.offset = offset
            self.Refresh()

    def setbgcolor(self, bgcolor):
        self.bgcolor = bgcolor
