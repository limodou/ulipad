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
#   $Id: Entry.py 1783 2006-12-20 13:33:46Z limodou $

import meide as ui
import wx

class MyTextEntry(ui.SimpleDialog):
    def __init__(self, parent, title, message, defaultvalue='', fit=2, size=wx.DefaultSize):
        box = ui.SimpleGrid(namebinding='element')
        box.add(message, ui.Text(defaultvalue), name='text')
        super(MyTextEntry, self).__init__(parent, box, title, fit=fit, size=size)
        
        self.layout.SetFocus()

    def GetValue(self):
        return self.text.GetValue()

class MyFileEntry(ui.SimpleDialog):
    def __init__(self, parent, title, message, defaultvalue='', fit=1, size=wx.DefaultSize):
        box = ui.SimpleGrid(namebinding='element')
        box.add(message, ui.OpenFile(defaultvalue), name='filename')
        super(MyFileEntry, self).__init__(parent, box, title, fit=fit, size=size)

        self.layout.SetFocus()
        
    def GetValue(self):
        return self.filename.GetValue()
    
