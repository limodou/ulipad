#   Programmer: limodou
#   E-mail:     limodou@gmail.com
#
#   Copyleft 2006 limodou
#
#   Distributed under the terms of the GPL (GNU Public License)
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
#   $Id$
#   Update:
#   2008/08/27
#       * CheckList Add DeleteAllItems method
#       * CheckListMixin Add checkAll(flag) method

import wx
from wx import ImageFromStream, BitmapFromImage
import cStringIO, zlib
import wx.lib.mixins.listctrl as listmix
import sys


def getUncheckData():
    return zlib.decompress(
"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2\x02 \xcc\xc1\
\x06$\xe5?\xffO\x04R,\xc5N\x9e!\x1c@P\xc3\x91\xd2\x01\xe4\xbb{\xba8\x86X\xf4\
&\xa7\xa4$\xa5-`1\x08\\2\xbb\xb1\xb1\x91\xf5\xd8\x84o\xeb\xff\xfaw\x1d[.=[2\
\x90'\x01\x08v\xec]\xd3\xa3qvU`l\x81\xd9\xd18\t\xd3\x84+\x0cll[\xa6t\xcc9\
\xd4\xc1\xda\xc3<O\x9a1\xc3\x88\xc3j\xfa\x86_\xee@#\x19<]\xfd\\\xd69%4\x01\
\x00\xdc\x80-\x05" )

def getUncheckBitmap():
    return BitmapFromImage(getUncheckImage())

def getUncheckImage():
    stream = cStringIO.StringIO(getUncheckData())
    return ImageFromStream(stream)

#----------------------------------------------------------------------
def getCheckData():
    return zlib.decompress(
'x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2\x02 \xcc\xc1\
\x06$\xe5?\xffO\x04R,\xc5N\x9e!\x1c@P\xc3\x91\xd2\x01\xe47{\xba8\x86X\xf4&\
\xa7\xa4$\xa5-`1\x08\\2\xbb\xb1\xb1\x91\xf5\xd8\x84o\xeb\xff\xfaw\x1d[.=[2\
\x90\'\x01\x08v\xec\\2C\xe3\xec+\xc3\xbd\x05fG\xe3\x14n1\xcc5\xad\x8a8\x1a\
\xb9\xa1\xeb\xd1\x853-\xaa\xc76\xecb\xb8i\x16c&\\\xc2\xb8\xe9Xvbx\xa1T\xc3U\
\xd6p\'\xbd\x85\x19\xff\xbe\xbf\xd7\xe7R\xcb`\xd8\xa5\xf8\x83\xe1^\xc4\x0e\
\xa1"\xce\xc3n\x93x\x14\xd8\x16\xb0(\x15q)\x8b\x19\xf0U\xe4\xb10\x08V\xa8\
\x99\xf3\xdd\xde\xad\x06t\x0e\x83\xa7\xab\x9f\xcb:\xa7\x84&\x00\xe0HE\xab' )

def getCheckBitmap():
    return BitmapFromImage(getCheckImage())

def getCheckImage():
    stream = cStringIO.StringIO(getCheckData())
    return ImageFromStream(stream)

class List(wx.ListView, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, columns, style=wx.LC_REPORT):
        wx.ListView.__init__(self, parent, -1, style=style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.parent = parent
        self.columns = columns

        self._id = 0
        self.createlist(self.columns)

    def createlist(self, columns):
        self.columns_num = len(columns)

        self.DeleteAllItems()

        for i, v in enumerate(columns):
            info = wx.ListItem()
            info.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_FORMAT

            name, length, align = v

            if align == 'left':
                info.m_format = wx.LIST_FORMAT_LEFT
            elif align == 'center':
                info.m_format = wx.LIST_FORMAT_CENTER
            else:
                info.m_format = wx.LIST_FORMAT_RIGHT
            info.m_text = name
            self.InsertColumnInfo(i, info)
            self.SetColumnWidth(i, length)

    def load(self, getdata):
        for v in getdata():
            i = v[0]
            index = self.InsertStringItem(sys.maxint, i)
            for i, t in enumerate(v[1:]):
                self.SetStringItem(index, i+1, t)

    def insertline(self, index, data, id=None):
        index = self.InsertStringItem(index, data[0])
        if id is None:
            self._id += 1
            id = self._id
        self.SetItemData(index, id)
        for i, t in enumerate(data[1:]):
            self.SetStringItem(index, i+1, t)
        return index
    
    def updateline(self, index, data):
        for i in range(self.GetColumnCount()):
            self.setCell(index, i, data[i])
        
    def addline(self, data, id=None):
        return self.insertline(sys.maxint, data, id)
    
    def delline(self, index):
        _id = self.GetItemData(index)
        self.DeleteItem(index)

    def GetValue(self):
        for i in range(self.GetItemCount()):
            s = []
            for j in range(self.GetColumnCount()):
                s.append(self.GetItem(i, j).GetText())
            yield tuple(s)
            
    def getline(self, index):
        s = []
        for j in range(self.GetColumnCount()):
            s.append(self.GetItem(index, j).GetText())
        return s
    
    def exchangeline(self, a, b):
        if b<0 or b>self.GetItemCount()-1:
            return
        selected = self.GetFirstSelected()
        item = max([a, b])
        ins = min([a, b])
        data = self.getline(item)
        id_a = self.GetItemData(a)
        id_b = self.GetItemData(b)
        self.delline(item)
        if ins == a:
            index = self.insertline(ins, data, id_b)
        else:
            index = self.insertline(ins, data, id_a)
        if ins == selected:
            self.selectSingle(index+1)
        else:
            self.selectSingle(index)
            
#    def Select(self, index, on=True):
#        if on:
#            self.SetItemState(index, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
#        else:
#            self.SetItemState(index, 0, wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED)
#            
    def selectSingle(self, index, on=True):
        if self.GetSelectedItemCount() > 0:
            item = self.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            while item > -1:
                self.Select(item, False)
                item = self.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        self.Select(index, on)
        
    def selectAll(self, on=True):
        for i in range(self.GetItemCount()):
            self.Select(i, on)
            
    def getCell(self, index, col=0):
        return self.GetItem(index, col).GetText()
    
    def setCell(self, index, col=0, text=''):
        self.SetStringItem(index, col, text)

class CheckListMixin:
    def __init__(self, check_image=None, uncheck_image=None):
        self.imagelist = wx.ImageList(16, 16)
        if not check_image:
            check_image = getCheckBitmap()
        if not uncheck_image:
            uncheck_image = getUncheckBitmap()
        self.uncheck_image = self.imagelist.Add(uncheck_image)
        self.check_image = self.imagelist.Add(check_image)
        self.SetImageList(self.imagelist, wx.IMAGE_LIST_SMALL)

        wx.EVT_LEFT_DOWN(self, self.OnLeftDown)

        self.on_check = None

        self.values = {}

    def load(self, getdata):
        self.values = {}
        for v, flag in getdata():
            self.addline(v, flag)
          
    def insertline(self, index, data, flag=False, id=None):
        if flag != -1:
            index = self.InsertImageStringItem(index, data[0], int(flag))
        else:
            index = self.InsertStringItem(index, data[0])
        if id is None:
            self._id += 1
            id = self._id
        self.values[id] = int(flag)
        self.SetItemData(index, id)
        for i, t in enumerate(data[1:]):
            self.SetStringItem(index, i+1, t)
        return index
        
    def addline(self, data, flag=False, id=None):
        return self.insertline(sys.maxint, data, flag, id)
    
    def delline(self, index):
        _id = self.GetItemData(index)
        del self.values[_id]
        self.DeleteItem(index)

    def exchangeline(self, a, b):
        if b<0 or b>self.GetItemCount()-1:
            return
        item = max([a, b])
        ins = min([a, b])
        data = self.getline(item)
        id_a = self.GetItemData(a)
        id_b = self.GetItemData(a)
        self.delline(item)
        if ins == a:
            self.insertline(ins, data, id_b)
        else:
            self.insertline(ins, data, id_a)
    
    def OnLeftDown(self,event):
        (index, flags) = self.HitTest(event.GetPosition())
        if flags == wx.LIST_HITTEST_ONITEMICON:
            i = self.GetItemData(index)
            self.values[i] ^= 1
            self.SetItemImage(index, self.values[i])
            if self.on_check:
                self.on_check(index, self.values[i])
            else:
                self.OnCheck(index, self.values[i])
        event.Skip()

    def OnCheck(self, index, f):
        pass

    def GetValue(self):
        for i in range(self.GetItemCount()):
            s = []
            for j in range(self.GetColumnCount()):
                s.append(self.GetItem(i, j).GetText())
            yield (s, self.values[self.GetItemData(i)])

    def getFlag(self, index):
        i = self.GetItemData(index)
        return self.values[i]

    def setFlag(self, index, f):
        i = self.GetItemData(index)
        self.values[i] = f
        self.SetItemImage(index, self.values[i])

    def notFlag(self, index):
        f = self.getFlag(index)
        self.setFlag(index, f ^ 1)
        
    def checkAll(self, f):
        for i in range(self.GetItemCount()):
            self.setFlag(i, f)
            
    def getline(self, index):
        s = []
        for j in range(self.GetColumnCount()):
            s.append(self.GetItem(index, j).GetText())
            
        return s, self.getFlag(index)
            
class CheckList(CheckListMixin, List):
    def __init__(self, parent, columns, check_image=None, uncheck_image=None, style=wx.LC_REPORT):
        List.__init__(self, parent, columns, style=style)
        CheckListMixin.__init__(self, check_image, uncheck_image)

    def load(self, getdata):
        CheckListMixin.load(self, getdata)

    def GetValue(self):
        for i in CheckListMixin.GetValue(self):
            yield i
            
    def DeleteAllItems(self):
        super(CheckList, self).DeleteAllItems()
        self.values = {}

if __name__ == '__main__':
    class wxApp(wx.App):
        def OnInit(self):
            frame = MyFrame(None)
            frame.Show()
            self.SetTopWindow(frame)
            return True

    class MyFrame(wx.Frame):
        def __init__(self, parent):
            wx.Frame.__init__(self, parent)
            self.list = CheckList(self, columns=[
                (u'ID', 40, 'left'),
                (u'Description', 100, 'right'),
            ])
            self.list.load(self.getdata)

            wx.EVT_CLOSE(self, self.OnClose)

        def getdata(self):
            return [(True, ('a', 'b')), (False, ('c', 'd'))]

        def OnClose(self, event):
            for i in self.list.GetValue():
                print i

            event.Skip()

    app = wxApp(0)
    app.MainLoop()
