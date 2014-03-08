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
#   $Id$

import wx
import re
import sys
from modules import Globals
from modules import CheckList
from wx.lib.splitter import MultiSplitterWindow

class RegexWindow(wx.Panel):
    def __init__(self, parent):
        self.parent = parent
        wx.Panel.__init__(self, parent, -1)
            
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sizer1, 0, wx.EXPAND|wx.ALL, 2)
        
        regex_title = wx.StaticBox(self, -1, tr("Regular expression"))
        box1 = wx.StaticBoxSizer(regex_title, wx.VERTICAL)
        self.text = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)
        box1.Add(self.text, 1, wx.EXPAND|wx.ALL, 2)
        sizer1.Add(box1, 1, wx.EXPAND|wx.RIGHT, 4)
        
        box = wx.BoxSizer(wx.VERTICAL)
        self.btnRun = wx.Button(self, -1, tr('Run'))
        box.Add(self.btnRun, 0, wx.ALL, 2)
        self.btnCreate = wx.Button(self, -1, tr('Create'))
        box.Add(self.btnCreate, 0, wx.ALL, 2)
        sizer1.Add(box, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 4)
        
        find_title = wx.StaticBox(self, -1, tr("Methods"))
        box2 = wx.StaticBoxSizer(find_title, wx.VERTICAL)
        self.rdoFindFirst = wx.RadioButton( self, -1, tr("Find First"), style = wx.RB_GROUP)
        self.rdoFindAll = wx.RadioButton( self, -1, tr("Find All"))
        box2.Add(self.rdoFindFirst, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)
        box2.Add(self.rdoFindAll, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)
        sizer1.Add(box2, 0, wx.EXPAND|wx.RIGHT, 4)
        
        from_title = wx.StaticBox(self, -1, tr("From"))
        box3 = wx.StaticBoxSizer(from_title, wx.VERTICAL)
        self.rdoFromBeginning = wx.RadioButton( self, -1, tr("From beginning"), style = wx.RB_GROUP)
        self.rdoFromCaret = wx.RadioButton( self, -1, tr("From caret"))
        self.rdoInSelection = wx.RadioButton( self, -1, tr("In Selection"))
        box3.Add(self.rdoFromBeginning, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)
        box3.Add(self.rdoFromCaret, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)
        box3.Add(self.rdoInSelection, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)
        sizer1.Add(box3, 0, wx.EXPAND|wx.RIGHT, 4)

        flag_title = wx.StaticBox(self, -1, tr("Flags"))
        box4 = wx.StaticBoxSizer(flag_title, wx.VERTICAL)
        grid1 = wx.FlexGridSizer(0, 2, 0, 0)
        box4.Add(grid1, 1, wx.EXPAND|wx.ALL, 2)
        sizer1.Add(box4, 0, wx.EXPAND|wx.RIGHT, 4)
        
        groups = [
            ('ignore', tr("Ignore Case(I)"), re.I, 're.I'),
            ('locale', tr("Locale(L)"), re.L, 're.L'),
            ('multiline', tr("Multi Line(M)"), re.M, 're.M'),
            ('dotall', tr("Dot All(S)"), re.S, 're.S'),
            ('unicode', tr("Unicode(U)"), re.U, 're.U'),
            ('verbose', tr("Verbose(V)"), re.X, 're.X'),
        ]
        self.checks = {}
        k = 0
        for i, v in enumerate(groups):
            ctrl_name, label, flag, strflag = v
            obj = wx.CheckBox(self, -1, label)
            wx.EVT_CHECKBOX(obj, obj.GetId(), self.OnChange)
            self.checks[ctrl_name] = obj, flag, strflag
            grid1.Add(obj, k, wx.ALL, 2)
            if i % 2 == 0:
                k += 1
                
        self.splitter = splitter = MultiSplitterWindow(self)
        self.result = CheckList.List(splitter, columns=[
                (tr("Items"), 150, 'left'),
                (tr("Values"), 300, 'left'),
                ], style=wx.LC_REPORT | wx.SUNKEN_BORDER | wx.LC_SINGLE_SEL)
        splitter.AppendWindow(self.result, 450)
        self.matches = wx.TextCtrl(splitter, -1, "", style=wx.TE_MULTILINE|wx.TE_RICH2)
        splitter.AppendWindow(self.matches, 150)
        
        splitter.SetOrientation(wx.HORIZONTAL)
        sizer.Add(splitter, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 4)
        
        self.load()

        wx.EVT_BUTTON(self.btnRun, self.btnRun.GetId(), self.OnChange)
        wx.EVT_BUTTON(self.btnCreate, self.btnCreate.GetId(), self.OnCreateExpression)
        wx.EVT_TEXT(self.text, self.text.GetId(), self.OnChange)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)

    def load(self, b=None):
        methods = ['group', 'groups', 'groupdict', 'span', 'start', 'end']
        self.result.Freeze()
        self.result.DeleteAllItems()
        for i, m in enumerate(methods):
            index = self.result.InsertStringItem(sys.maxint, m)
            if b and not isinstance(b, list): #list is returned by findall
                v = getattr(b, m)()
                if not isinstance(v, (str, unicode)):
                    v = repr(v)
                self.result.SetStringItem(index, 1, v)
        self.result.Thaw()
    
    def getdata(self):
        s = []
        for i, v in enumerate(Globals.commands):
            s.append((v[0], v[1].get('shortcut', ''), i))
        return s
        
    def save_status(self):
        Globals.mainframe.pref.searchwin_pos = self.GetPosition()
        Globals.mainframe.pref.searchwin_size = self.GetSize()
        Globals.mainframe.pref.save()
        
    def OnChange(self, event):
        text = self.text.GetValue()
        try:
            c = self.checks['unicode'][0]
            if c.GetValue(): #unicode
                def u_chr(m):
                    return unichr(int(m.group(1), 16))
                text = re.sub(r'\u(.{4})', u_chr, text)
                r = re.compile(text, self.getflags())
            else:
                r = re.compile(r"%s" % text, self.getflags())
        except Exception, e:
            errmsg = 'Error:' + str(e)
            self.set_error(errmsg)
            return
        if self.rdoFindAll.GetValue():
            method = 'findall'
        else:
            method = 'search'
        mobj = getattr(r, method)(self.get_document_text())
        if mobj:
            if method == 'search':
                self.load(mobj)
                self.set_result(mobj.group())
            else:
                self.load()
                if mobj:
                    if isinstance(mobj[0], tuple):
                        mobj = ['\t'.join(x) for x in mobj]
                self.set_result('\n'.join(mobj))
        else:
            self.set_error('Error: Nothing Found!')
    
    def get_document_text(self):
        document = Globals.mainframe.document
        if self.rdoFromBeginning.GetValue():
            return document.GetText()
        elif self.rdoFromCaret.GetValue():
            return document.GetTextRange(document.GetCurrentPos(), document.GetTextLength())
        else:
            return document.GetSelectedText()

    def set_result(self, text=''):
        self.matches.Clear()
        self.matches.WriteText(text)
        
    def set_error(self, text=''):
        self.matches.Clear()
        self.matches.WriteText(text)
        self.matches.SetInsertionPoint(0)
        self.matches.SetStyle(0, self.matches.GetLastPosition(), wx.TextAttr("RED"))
        
    def getflags(self):
        f = 0
        for chk, v in self.checks.items():
            obj, flag, strflag = v
            if obj.GetValue():
                f |= flag
        return f
    
    def getstringflags(self):
        f = []
        for chk, v in self.checks.items():
            obj, flag, strflag = v
            if obj.GetValue():
                f.append(strflag)
        if f:
            return ', ' + '|'.join(f)
        else:
            return ''
    
    def OnCreateExpression(self, event=None):
        c = self.checks['unicode'][0]
        if c.GetValue(): #unicode
            e = 're.compile(u"%s"%s)' % (self.text.GetValue(), self.getstringflags())
        else:
            e = 're.compile(r"%s"%s)' % (self.text.GetValue(), self.getstringflags())
        self.set_result(e)