#   Programmer:     ygao
#   E-mail:         ygao2004@gmail.com
#
#   Copyleft 2007 ygao
#
#   Distributed under the terms of the GPL (GNU Public License)
#   this patch was maded by ygao for Ulipad.
import os
import wx
import re
from modules import CheckList
from modules import Globals


def create_import_py(win,flag=False):
    text = file(os.path.join(Globals.workpath,'mixins','__init__.py')).read()
    re_import = re.compile('^#import (.*)$', re.M)
    result = re_import.findall(text)
    sel_name = win.pref.mixin_reload_name
    if result:
        fp = file(os.path.join(Globals.workpath,'mixins','Import.py'), 'wb')
        fp.write("""#   Programmer:     limodou
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


""")
        textlist = []
        if flag:
            if  sel_name:
                for n in sel_name:
                    fp.write('import' + '    '+ n + '\n')  
                result = [n for n in result if n not in sel_name]
                for f in result:
                    f = f.strip()
                    lines = file(os.path.join(Globals.workpath,'mixins',f + '.py')).readlines()
                    fp.write("#-----------------------  %s.py ------------------\n" % f)
                    for line in lines:
                       t = line.rstrip()
                       if t and t[0] == '#': continue
                       fp.write(t+'\n')
                    fp.write("\n\n\n")
            else:
                for f in result:
                    f = f.strip()
                    fp.write('import' + '    '+ f + '\n')     
        else:
            for f in result:
                f = f.strip()
                lines = file(os.path.join(Globals.workpath,'mixins',f + '.py')).readlines()
                fp.write("#-----------------------  %s.py ------------------\n" % f)
                for line in lines:
                    t = line.rstrip()
                    if t and t[0] == '#': continue
                    fp.write(t+'\n')
                fp.write("\n\n\n")
        fp.close()


class MixinDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, tr('Mixins Reload Manage'), size=(400, 300))
        self.parent = parent
        self.mainframe = parent
        self.state = {}

        self.mixins = self.loadMixins()
        
        for key in self.mixins.keys():
            self.state[key] = False

        reload_name = self.mainframe.pref.mixin_reload_name or []
        for key in reload_name:
            self.state[key] = True
        box = wx.BoxSizer(wx.VERTICAL)
        self.list = CheckList.CheckList(self, columns=[
                (tr("Name"), 120, 'left'),
                ], style=wx.LC_REPORT | wx.SUNKEN_BORDER)
                
        self.list.load(self.getdata)
        box.Add(self.list, 1, wx.EXPAND|wx.ALL, 5)
        
        self.list_text = wx.StaticText(self, -1,
                   tr("if you select nothing, All mixins will be reloaded or\n"
                   "only selected mixins will be reloaded.\n\n"
                   "right_click item will open the mixin file."),
                   (0,0))
        text_box = wx.BoxSizer(wx.HORIZONTAL)
        text_box.Add(self.list_text, 0, 0, 5)
        self.warn_text = wx.StaticText(self, -1,
                   tr("after restarting this program, the changes will be taken effect!"),
                   (0,0))
        self.warn_text.SetForegroundColour('Red')
        text2_box = wx.BoxSizer(wx.HORIZONTAL)
        text2_box.Add(self.warn_text, 0, 0, 0)
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        self.btnOK = wx.Button(self, wx.ID_OK, tr("OK"), size=(80, -1))
        self.btnOK.SetDefault()
        box2.Add(self.btnOK, 0, 0, 5)
        self.btnCancel = wx.Button(self, wx.ID_CANCEL, tr("Cancel"), size=(80, -1))
        box2.Add(self.btnCancel, 0, 0, 5)
        box.Add(text_box, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        box.Add(text2_box, 0, wx.ALIGN_LEFT|wx.ALL, 5)
        box.Add(box2, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnEnter, id=self.list.GetId())
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.open_mixins_file, id=self.list.GetId())
        self.btnOK.Bind(wx.EVT_BUTTON, self.OnOK, id=wx.ID_OK)
        self.SetSizer(box)
        self.SetAutoLayout(True)

    def open_mixins_file(self, event):
        index = event.GetIndex()
        s = self.mixins.keys()
        s.sort()
        i = s[index]
        filename = os.path.join(Globals.workpath,'mixins',i + '.py')
        self.mainframe.editctrl.new(filename)
        
    def getdata(self):
        s = self.mixins.keys()
        s.sort()
        for i, name in enumerate(s):
            yield ([unicode(name, 'utf-8')], self.state[name])
           
    def OnEnter(self, event):
        index =  event.GetIndex()
        self.list.notFlag(index)

    def OnOK(self, event):
        for v, flag in self.list.GetValue():
            self.state[v[0]] = flag
        sel_name = [s for s in self.mixins if self.state[s]]
        self.mainframe.pref.mixin_reload_name = sel_name
        self.mainframe.pref.save()
        if  self.mainframe.pref.mixin_reload_mixins_mode:
            create_import_py(self.mainframe,flag=True)
        event.Skip()

    def loadMixins(self):
        text = file(os.path.join(Globals.workpath,'mixins','__init__.py')).read()
        re_import = re.compile('^#import (.*)$', re.M)
        result = re_import.findall(text)
        mixins = {}
        if result:
            for f in result:
                mixins[f] = f
            return mixins

