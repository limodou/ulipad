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
#   $Id: SnippetWindow.py,v 1.11 2004/11/27 15:52:08 limodou Exp $

import wx
import os
import sys
from modules import common
from modules.Debug import error

class WizardPanel(wx.Panel):
    def __init__(self, parent, mainframe):
        wx.Panel.__init__(self, parent, -1)
        self.parent = parent
        self.mainframe = mainframe

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.refresh = wx.Button(self, -1, tr('Refresh'))
        self.Bind(wx.EVT_BUTTON, self.OnRefresh, id=self.refresh.GetId())
        self.sizer.Add(self.refresh, 0, wx.LEFT, 2)

        style = wx.TR_SINGLE|wx.TR_HAS_BUTTONS|wx.TR_TWIST_BUTTONS
        if wx.Platform == '__WXMSW__':
            style = style | wx.TR_ROW_LINES
        elif wx.Platform == '__WXGTK__':
            style = style | wx.TR_NO_LINES

        self.tree = wx.TreeCtrl(self, -1, style = style)
        self.sizer.Add(self.tree, 1, wx.EXPAND)
        self.root = self.tree.AddRoot(tr('Wizard'))
        self.tree.SetPyData(self.root, 0)

        self.loadData()

        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnEnter, id = self.tree.GetId())

        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)

    def OnRefresh(self, event):
        self.loadData()

    def loadData(self):
        self.tree.CollapseAndReset(self.root)

        self.items = {}
        self.ids = 1

        #check and create wizard path
        wizardpath = os.path.join(self.mainframe.app.workpath, 'wizard')
        if not os.path.exists(wizardpath):
            os.mkdir(wizardpath)

        self._loadPath(self.root, wizardpath)

        x = common.get_config_file_obj()
        if x.wizard.path:
            if isinstance(x.wizard.path, list):
                for p in x.wizard.path:
                    self._loadPath(self.root, p)
            else:
                self._loadPath(self.root, p)

        self.tree.Expand(self.root)

    def _loadPath(self, root, path):
        import glob
        files = os.listdir(path)
        for f in files:
            if os.path.isdir(os.path.join(path, f)):
                files = glob.glob(os.path.join(path, f, '*.wiz'))
                if files:
                    wizfile = files[0]
                    obj = self._addNode(root, wizfile)
                    self._loadPath(obj, os.path.join(path, f))

    def _addNode(self, root, wizfile):
        from modules import dict4ini

        x = dict4ini.DictIni(wizfile, encoding='utf-8')
        obj = self.tree.AppendItem(root, x.options.name)
        self.items[self.ids] = x
        self.tree.SetPyData(obj, self.ids)
        self.ids += 1
        return obj

    def OnEnter(self, event):
        i = self.tree.GetPyData(event.GetItem())
        if not i: return
        x = self.items[i]
        mod, path = importfile(x)
        datafile = ''
        if x.options.datafile == 'open':
            from modules import FileDialog
            datafile = FileDialog.openfiledlg(tr('Open'), tr('Input a data file:'))
        old_path = os.getcwd()
        try:
            os.chdir(path)
            try:
                if x.options.execute == 'wizard':
                    from modules.EasyGuider import EasyCommander
                    easy = EasyCommander.EasyCommander(parent=self, easyfile=mod, inline=True, cmdoption='', outputencoding=x.options.encoding)
                    easy.inipickle = datafile
                    if x.options.output == 'inline':
                        import StringIO
                        buf = StringIO.StringIO()
                        easy.outputfile = buf
                        if easy.run():
                            self.mainframe.document.AddText(common.decode_string(buf.getvalue(), x.options.encoding))
                    elif x.options.output == 'save':
                        from modules import FileDialog
                        datafile = FileDialog.savefiledlg(tr('Save'), tr('Input saving filename:'))
                        if datafile:
                            easy.outputfile = datafile
                            if easy.run():
                                self.mainframe.editctrl.new(datafile, encoding=x.options.encoding)
                    elif x.options.output == 'newfile':
                        import StringIO
                        buf = StringIO.StringIO()
                        easy.outputfile = buf
                        if easy.run():
                            document = self.mainframe.editctrl.new()
                            document.SetText(common.decode_string(buf.getvalue(), x.options.encoding))
                    else:
                        if easy.run():
                            common.showmessage(self, tr("Completed!"))
                elif x.options.execute == 'program':
                    easy = mod
                    easy.datafile = datafile
                    if x.options.output == 'inline':
                        import StringIO
                        buf = StringIO.StringIO()
                        easy.outputfile = buf
                        if easy.run(self.mainframe, x):
                            self.mainframe.document.AddText(common.decode_string(buf.getvalue(), x.options.encoding))
                    elif x.options.output == 'save':
                        from modules import FileDialog
                        datafile = FileDialog.savefiledlg(tr('Save'), tr('Input saving filename:'))
                        if datafile:
                            easy.outputfile = datafile
                            if easy.run(self.mainframe, x):
                                self.mainframe.editctrl.new(datafile, encoding=x.options.encoding)
                    elif x.options.output == 'newfile':
                        import StringIO
                        buf = StringIO.StringIO()
                        easy.outputfile = buf
                        if easy.run(self.mainframe, x):
                            document = self.mainframe.editctrl.new()
                            document.SetText(common.decode_string(buf.getvalue(), x.options.encoding))
                    else:
                        if easy.run(self.mainframe, x):
                            common.showmessage(self, tr("Completed!"))
            except:
                error.traceback()
                common.showerror(self, tr("There is something wrong, see the error.log!"))
        finally:
            os.chdir(old_path)

        if path:
            del sys.path[0]

def importfile(x):
    dirname = os.path.dirname(x.getfilename())
    importfile = os.path.join(dirname, x.options.file)
    path = os.path.dirname(os.path.abspath(importfile))
    filename, ext = os.path.splitext(os.path.basename(importfile))
    if sys.modules.has_key(filename):
        del sys.modules[filename]
    if path:
        sys.path.insert(0, dirname)
    mod = __import__(filename)
    return mod, path
