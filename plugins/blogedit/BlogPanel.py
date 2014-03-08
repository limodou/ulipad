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
#       $Id: BlogPanel.py 42 2005-09-28 05:19:21Z limodou $

from modules import Mixin
import wx
from mixins import DocumentBase

class BlogPanel(wx.Panel, DocumentBase.PanelBase, Mixin.Mixin):

    __mixinname__ = 'blogpanel'
    documenttype = 'blog'

    def __init__(self, parent, filename, **kwargs):
        self.initmixin()

        wx.Panel.__init__(self, parent, -1)

        DocumentBase.PanelBase.__init__(self, parent, filename, **kwargs)
        self.document.panel = self
        self.callplugin('new_window', self.parent, self.document, self)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.document, 1, wx.EXPAND)

        self.SetSizer(box)
        self.SetAutoLayout(True)

    def createDocument(self, **kwargs):
        from BlogPage import BlogPage

        return BlogPage(self, self.parent.mainframe, self.filename, self.documenttype, **kwargs)
