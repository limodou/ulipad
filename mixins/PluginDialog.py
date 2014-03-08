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
#   $Id: PluginDialog.py 2093 2007-06-25 10:14:44Z limodou $

import wx
import glob
import os.path
import re
from modules import dict4ini
from modules import CheckList
from modules import common
from modules.Debug import error

class PluginDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, tr('Plugin Manager'), size=(600, 400))
        self.parent = parent
        self.mainframe = parent
        self.state = {}

        self.plugins = self.loadPlugins()
        for key in self.plugins.keys():
            self.state[key] = False
        text = file(self.mainframe.plugin_initfile).read()
        re_i = re.compile("^\s+import\s+(\w+)$", re.M)
        result = re_i.findall(text)
        for key in result:
            self.state[key] = True

        box = wx.BoxSizer(wx.VERTICAL)
        self.list = CheckList.CheckList(self, columns=[
                (tr("Name"), 120, 'left'),
                (tr("Description"), 220, 'left'),
                (tr("Author"), 80, 'left'),
                (tr("Version"), 40, 'center'),
                (tr("Date"), 80, 'left'),
                ], style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.list.load(self.getdata)

        box.Add(self.list, 1, wx.EXPAND|wx.ALL, 5)
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        self.btnOK = wx.Button(self, wx.ID_OK, tr("OK"), size=(80, -1))
        self.btnOK.SetDefault()
        box2.Add(self.btnOK, 0, 0, 5)
        self.btnCancel = wx.Button(self, wx.ID_CANCEL, tr("Cancel"), size=(80, -1))
        box2.Add(self.btnCancel, 0, 0, 5)
        box.Add(box2, 0, wx.ALIGN_CENTER|wx.ALL, 5)

        wx.EVT_LIST_ITEM_ACTIVATED(self.list, self.list.GetId(), self.OnEnter)
        wx.EVT_BUTTON(self.btnOK, wx.ID_OK, self.OnOK)

        self.SetSizer(box)
        self.SetAutoLayout(True)

    def getdata(self):
        s = self.plugins.keys()
        s.sort()
        for i, name in enumerate(s):
            ini = dict4ini.DictIni(self.plugins[name])
            description = ini.info.description or ''
            author = ini.info.author or ''
            version = ini.info.version or ''
            date = ini.info.date or ''
            yield ([unicode(name, 'utf-8'), unicode(description, 'utf-8'),
                    unicode(author, 'utf-8'), unicode(version, 'utf-8'), 
                    unicode(date, 'utf-8')], self.state[name])

    def OnEnter(self, event):
        index =  event.GetIndex()
        self.list.notFlag(index)

    def OnOK(self, event):
        for v, flag in self.list.GetValue():
            self.state[v[0]] = flag
        text = file(self.mainframe.plugin_initfile).read()
        pos1 = text.find('from')
        pos2 = text.find('import')
        pos = min([pos1, pos2])
        if pos:
            text = text[:pos]
        file(self.mainframe.plugin_initfile, 'w').write(text + "from modules.Debug import error\nflag=False\n" + '\n'.join(["""
try:
    import %s
except:
    error.traceback()
    flag = True
""" % s for s in self.plugins if self.state[s]]) + """
if flag:
    raise Exception
""")
        self.copy_mo()
        common.showmessage(self, tr("If you changed plugins selection, you should restart again"))
        event.Skip()

    def loadPlugins(self):
        files = glob.glob(os.path.join(self.mainframe.workpath, 'plugins/*/*.pin'))
        plugins = {}
        for f in files:
            plugins[os.path.basename(os.path.dirname(f))] = f
        return plugins

    def copy_mo(self):
        langpath = os.path.join(self.mainframe.workpath, 'lang')
        dirs = [d for d in os.listdir(langpath) if os.path.isdir(os.path.join(langpath, d))]
        files = glob.glob(os.path.join(self.mainframe.workpath, 'plugins/*/*.mo'))
        import shutil
        for f in files:
            fname = os.path.splitext(os.path.basename(f))[0]
            flag = False
            for lang in dirs:
                if fname.endswith(lang):
                    flag = True
                    break
            if not flag:
                lang = fname[-5:]
                try:
                    os.makedirs(os.path.join(self.mainframe.workpath, 'lang', fname[-5:]))
                except Exception, e:
                    error.traceback()
                    common.showerror(self, str(e))
                    continue
            dst = os.path.join(self.mainframe.workpath, 'lang', lang, os.path.basename(f))
            try:
                shutil.copyfile(f, dst)
            except Exception, e:
                error.traceback()
                common.showerror(self, str(e))
                continue
            
