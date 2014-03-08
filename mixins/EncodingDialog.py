#   Programmer:     limodou
#   E-mail:         limodou@gmail.com
#  
#   Copyleft 2008 limodou
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
#   $Id: EncodingDialog.py 1457 2006-08-23 02:12:12Z limodou $

__doc__ = 'Encoding selection dialog'

import wx
from modules import meide as ui
from modules import Globals

class EncodingDialog(wx.Dialog):
    EncodingList = [
            (tr('Default'),''),
            ('UTF-8','UTF-8'),
            ('Base64','Base64'),
            ('ASCII','ASCII'),
            ('ISO 8859-1','ISO 8859-1'),
            ('GBK','GBK'),
    ]

    def __init__(self, title=tr('Select Encoding'), style = wx.DEFAULT_DIALOG_STYLE):
        wx.Dialog.__init__(self, Globals.mainframe, -1, title=title, style = style)
        
        self.sizer = box = ui.VBox(namebinding='widget').create(self).auto_layout()
        grid = box.add(ui.Grid)
        grid.add((0, 0), ui.Radio(label=tr('Encoding:')), name='rdo_encoding').bind(wx.EVT_RADIOBUTTON, self.OnRadio)
        grid.add((0, 1), ui.SingleChoice(None, self.EncodingList), name='encoding')
        grid.add((1, 0), ui.Radio(label=tr('Custom Encoding:')), name='rdo_cus_encoding').bind(wx.EVT_RADIOBUTTON, self.OnRadio)
        grid.add((1, 1), ui.Text, name='cus_encoding')
        
        self.encoding.Enable(True)
        self.cus_encoding.Enable(False)
        
        box.add(ui.simple_buttons(), flag=wx.ALIGN_CENTER|wx.BOTTOM)
        self.btnOk.SetDefault()
        
        box.auto_fit(2)

    def OnRadio(self, event):
        obj = event.GetEventObject()
        if obj == self.rdo_encoding:
            self.encoding.Enable(True)
            self.cus_encoding.Enable(False)
        elif obj == self.rdo_cus_encoding:
            self.encoding.Enable(False)
            self.cus_encoding.Enable(True)

    def GetValue(self):
        if self.rdo_encoding.GetValue():
            return self.encoding.GetValue()
        else:
            return self.cus_encoding.GetValue()
        