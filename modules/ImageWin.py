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

import wx

class ImageWin(wx.Frame):
    def __init__(self, parent, imagefile):
        wx.Frame.__init__(self, parent, title='Image View', style=wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        image = wx.Image(imagefile).ConvertToBitmap()
        self.image = wx.StaticBitmap(self, -1, image, (0, 0), (image.GetWidth(), image.GetHeight()))
        sizer.Add(self.image, 0)

        self.SetSizer(sizer)
        self.Fit()
