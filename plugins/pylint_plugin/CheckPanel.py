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
from modules import CheckList
import modules.meide as ui
from modules import Globals

class SyntaxCheckWindow(wx.Panel):
    def __init__(self, parent, mainframe):
        wx.Panel.__init__(self, parent, -1)

        self.mainframe = mainframe
        self.pref = Globals.pref

        self.sizer = sizer = ui.VBox(namebinding='widget').create(self).auto_layout()
        box = sizer.add(ui.HBox)
        box.add(ui.Check(self.pref.pylint_convention, tr('Convention')), name='convention').bind('check', self.OnCheckConvention)
        box.add(ui.Check(self.pref.pylint_refactor, tr('Refactor')), name='refactor').bind('check', self.OnCheckRefactor)
        box.add(ui.Check(self.pref.pylint_warning, tr('Warning')), name='warning').bind('check', self.OnCheckWarning)
        box.add(ui.Check(self.pref.pylint_error, tr('Error')), name='error').bind('check', self.OnCheckError)
        box.add(ui.Check(self.pref.pylint_fatal, tr('Fatal')), name='fatal').bind('check', self.OnCheckFatal)
        self.list = CheckList.List(self, columns=[
                (tr("Filename"), 400, 'left'),
                (tr("Type"), 100, 'left'),
                (tr("LineNo"), 60, 'left'),
                (tr("Description"), 200, 'left'),
                ], style=wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL)

        sizer.add(self.list, proportion=1, flag=wx.EXPAND)

        wx.EVT_LIST_ITEM_ACTIVATED(self.list, self.list.GetId(), self.OnEnter)

        sizer.auto_fit(0)

    def OnEnter(self, event):
        index = event.GetIndex()
        filename = self.list.getCell(index, 0)
        lineno = self.list.getCell(index, 2)
        self.mainframe.editctrl.new(filename)
        wx.CallAfter(self.mainframe.document.goto, int(lineno))
        
    def canClose(self):
        return True

    def OnCheckConvention(self, event):
        self.pref.pylint_convention = self.convention.GetValue()
        self.pref.save()
            
    def OnCheckRefactor(self, event):
        self.pref.pylint_refactor = self.refactor.GetValue()
        self.pref.save()
        
    def OnCheckWarning(self, event):
        self.pref.pylint_warning = self.warning.GetValue()
        self.pref.save()
        
    def OnCheckError(self, event):
        self.pref.pylint_error = self.error.GetValue()
        self.pref.save()
        
    def OnCheckFatal(self, event):
        self.pref.pylint_fatal = self.fatal.GetValue()
        self.pref.save()
    