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
from wx.lib.buttons import GenBitmapButton

class FlatBitmapButton(GenBitmapButton):
    def __init__(self, parent, ID=-1, bitmap=wx.NullBitmap,
                 pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = 0, validator = wx.DefaultValidator,
                 name = "genbutton"):
        self.bitmap = bitmap
        GenBitmapButton.__init__(self, parent, ID, bitmap, pos, size, style, validator, name)
        self.SetBezelWidth(0)
        self.useFocusInd = False
        self.SetBestSize(None)
        self.Bind(wx.EVT_ENTER_WINDOW, self.ButtonOnMouseEnter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.ButtonOnMouseLeave)

    def SetBestSize(self, size=None):
        size = (23, 22)
        try:
            wx.PyControl.SetInitialSize(self, size)
        except:
            wx.PyControl.SetBestFittingSize(self, size)
        
    def ButtonOnMouseEnter(self, event):
        self.SetBezelWidth(1)
        self.Refresh()
        event.Skip()
        
    def ButtonOnMouseLeave(self, event):
        self.SetBezelWidth(0)
        self.Refresh()
        event.Skip()
  
class FlatBitmapMenuButton(FlatBitmapButton):
    def __init__(self, parent, ID=-1, bitmap=wx.NullBitmap,
                 pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = 0, validator = wx.DefaultValidator,
                 name = "genbutton"):
        bitmap = self.createBitmap(bitmap)
        FlatBitmapButton.__init__(self, parent, ID, bitmap, pos, size, style, validator, name)
        self.Bind(wx.EVT_PAINT,        self.OnPaint)
        self.Bind(wx.EVT_LEFT_UP,    self.OnLeftUp)
        self.popmenu = None
        self.func = None
        
    def SetRightClickMenu(self, menu=None):
        self.popmenu = menu
        
    def SetRightClickFunc(self, func=None):
        self.func = func
        
    def createBitmap(self, image):
        bmp = wx.EmptyBitmap(36, 20)
        
        mem_dc = wx.MemoryDC()
        mem_dc.SelectObject(bmp)
        mem_dc.SetBackground(self.getBrush())
        mem_dc.Clear()
        mem_dc.DrawBitmap(image, 3, 2, True)
        self.draw_triangle(mem_dc, 29, 12, 5)
        return bmp

    def getBrush(self):
        myAttr = self.GetDefaultAttributes()
        colBg = myAttr.colBg
        brush = wx.Brush(colBg, wx.SOLID)
        return brush
        
    def SetBestSize(self, size=None):
        size = (38, 22)
        wx.PyControl.SetBestSize(self, size)
        
    def OnPaint(self, event):
        (width, height) = self.GetClientSizeTuple()
        x1 = y1 = 0
        x2 = width-1
        y2 = height-1
        
        dc = wx.BufferedPaintDC(self)
        brush = None
        
        if self.up:
            colBg = self.GetBackgroundColour()
            brush = wx.Brush(colBg, wx.SOLID)
            if self.style & wx.BORDER_NONE:
                myAttr = self.GetDefaultAttributes()
                parAttr = self.GetParent().GetDefaultAttributes()
                myDef = colBg == myAttr.colBg
                parDef = self.GetParent().GetBackgroundColour() == parAttr.colBg
                if myDef and parDef:
                    if wx.Platform == "__WXMAC__":
                        brush.MacSetTheme(1) # 1 == kThemeBrushDialogBackgroundActive
                    elif wx.Platform == "__WXMSW__":
                        if self.DoEraseBackground(dc):
                            brush = None
                elif myDef and not parDef:
                    colBg = self.GetParent().GetBackgroundColour()
                    brush = wx.Brush(colBg, wx.SOLID)
        else:
            brush = wx.Brush(self.faceDnClr, wx.SOLID)
        if brush is not None:
            dc.SetBackground(brush)
            dc.Clear()
                    
        self.DrawLabel(dc, 38, 22)
        self.DrawBezel(dc, 0, 0, 22, 21)
        self.DrawBezel(dc, 23, 0, 37, 21)
        
    def draw_triangle(self, dc, x, y, size, color=None):
        dc.SetPen(wx.Pen('black'))
        for i in range(size):
            dc.DrawLine(x-i, y-i, x+i, y-i)
            
    def OnLeftUp(self, event):
        if not self.IsEnabled() or not self.HasCapture():
            return
        if self.HasCapture():
            self.ReleaseMouse()
            if not self.up:    # if the button was down when the mouse was released...
                if not self.in_triangle(event):
                    self.Notify()
            self.up = True
            if self:           # in case the button was destroyed in the eventhandler
                self.Refresh()
                if self.in_triangle(event):
                    if self.popmenu:
                        self.PopupMenu(self.popmenu)
                    elif self.func:
                        self.func(self)
                event.Skip()

    def in_triangle(self, event):
        x, y = event.GetPosition()
        if 23 < x < 37 and 0 < y < 21:
            return True
        else:
            return False

    def PopupMenu(self, menu):
        x, y = self.GetPosition()
        self.GetParent().PopupMenu(menu, (x+23, y+22))
        