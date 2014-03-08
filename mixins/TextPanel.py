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
#
#   $Id: TextPanel.py 1492 2006-08-30 07:34:36Z limodou $

import wx
import MyPanel
from modules import Mixin
import DocumentBase

class TextPanel(MyPanel.SashPanel, DocumentBase.PanelBase, Mixin.Mixin):

    __mixinname__ = 'textpanel'
    documenttype = 'texteditor'

    def __init__(self, parent, filename):
        self.initmixin()

        MyPanel.SashPanel.__init__(self, parent)
        DocumentBase.PanelBase.__init__(self, parent, filename)
        self.document.panel = self
        self.callplugin('new_window', self.parent, self.document, self)

    def createDocument(self):
        from mixins.Editor import TextEditor

        panel = wx.Panel(self.top, -1)
        document = TextEditor(panel, self.parent, self.filename, self.documenttype)
        box = wx.BoxSizer(wx.VERTICAL)

        self.callplugin('new_control', document, panel, box)
        box.Add(document, 1, wx.EXPAND)

        panel.SetSizer(box)
        panel.SetAutoLayout(True)

        return document
