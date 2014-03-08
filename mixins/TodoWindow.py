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

import sys
import StringIO
import re
import wx
from modules.EasyGuider import EasyList
from modules import common
from modules.Debug import error
from modules.Mixin import Mixin

TODO_C_PATTERN1 = re.compile(r'^\s*/\*\s*todo:?\s+(.*?)$', re.I)
TODO_C_PATTERN2 = re.compile(r'^\s*//\s*todo:?\s+(.*?)$', re.I)
TODO_PY_PATTERN = re.compile(r'^\s*#\s*todo:?\s+(.*?)$', re.I)

todo_patten = {
    'python':TODO_PY_PATTERN,
    'ruby':TODO_PY_PATTERN,
    'perl':TODO_PY_PATTERN,
    'c':(TODO_C_PATTERN1, TODO_C_PATTERN2),
    'java':(TODO_C_PATTERN1, TODO_C_PATTERN2),
}
class TodoWindow(wx.Panel, Mixin):
    __mixinname__ = 'todowindow'
    
    def __init__(self, parent, mainframe):
        self.initmixin()
        
        wx.Panel.__init__(self, parent, -1)

        self.mainframe = mainframe
        self.pref = mainframe.pref

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.list = EasyList.AutoWidthListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.list.InsertColumn(0, tr("Important"))
        self.list.InsertColumn(1, tr("Line"))
        self.list.InsertColumn(2, tr("Due date"))
        self.list.InsertColumn(3, tr("Description"))
        self.list.InsertColumn(4, tr("Filename"))
        self.list.SetColumnWidth(0, self.pref.todo_column1)
        self.list.SetColumnWidth(1, self.pref.todo_column2)
        self.list.SetColumnWidth(2, self.pref.todo_column3)
        self.list.SetColumnWidth(3, self.pref.todo_column4)
        self.list.SetColumnWidth(4, self.pref.todo_column5)

        self.sizer.Add(self.list, 1, wx.EXPAND)
        
        self.editor = None

        wx.EVT_LIST_ITEM_ACTIVATED(self.list, self.list.GetId(), self.OnEnter)
        wx.EVT_LIST_COL_END_DRAG(self.list, self.list.GetId(), self.OnSize)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)

    def adddata(self, data):
        self.list.Freeze()
        self.list.DeleteAllItems()
        for i in data:
            important, lineno, duedate, desc, filename = i
            lineno = str(lineno)
            desc = desc.strip()
            index = self.list.InsertStringItem(sys.maxint, important)
            self.list.SetStringItem(index, 1, lineno)
            self.list.SetStringItem(index, 2, duedate)
            self.list.SetStringItem(index, 3, desc)
            self.list.SetStringItem(index, 4, filename)
        self.list.Thaw()

    def OnEnter(self, event):
        index = event.GetIndex()
        filename = self.list.GetItem(index, 4).GetText()
        lineno = self.list.GetItem(index, 1).GetText()
        self.mainframe.editctrl.new(filename)
        wx.CallAfter(self.mainframe.document.goto, int(lineno))

    def canClose(self):
        return True

    def show(self, editor, data=None):
        self.editor = editor
        if not data:
            data = read_todos(editor)
        self.adddata(data)
        self.callplugin('show', self)

    def OnClose(self, parent, **kwargs):
        if self.editor:
            self.callplugin('close', self, **kwargs)
    
    def OnSize(self, event):
        self.save_state()
        
    def save_state(self):
        self.pref.todo_column1 = self.list.GetColumnWidth(0)
        self.pref.todo_column2 = self.list.GetColumnWidth(1)
        self.pref.todo_column3 = self.list.GetColumnWidth(2)
        self.pref.todo_column4 = self.list.GetColumnWidth(3)
        self.pref.todo_column5 = self.list.GetColumnWidth(4)
        self.pref.save()
 
r_duedate = re.compile(r'\(?\$D:(\d{4}[/-]\d{1,2}[/-]\d{1,2})\)?')
#todo example:
#     #todo This is a todo test $D:2008-05-06 !!!!
def read_todos(editor):
    lang = editor.languagename
    filename = editor.filename
    #set default pattern
    pl = todo_patten.get(lang, [])
    if not isinstance(pl, (list, tuple)):
        pl = [pl]
    #first check the config.ini
    ini = common.get_config_file_obj()
    if ini.todo_pattern.has_key(lang):
        pattern = ini.todo_pattern[lang]
        if isinstance(pattern, list):
            pl = []
            for i in pattern:
                try:
                    pl.append(re.compile(i))
                except:
                    error.traceback()
                    error.info('pattern=' + i)
        else:
            pl = []
            try:
                pl.append(re.compile(pattern))
            except:
                error.traceback()
                error.info('pattern=' + pattern)
    data = []
    if pl:
        buf = StringIO.StringIO(editor.GetText())
        for i, line in enumerate(buf):
            for r in pl:
                b = r.search(line)
                if b:
                    date = ''
                    result = filter(None, b.groups())
                    if not result:
                        message = ''
                        important = ''
                    else:
                        message = result[0].rstrip()
                        important = ''
                        for n in range(len(message)-1, -1, -1):
                            if message[n] == '!':
                                important += '!'
                            else:
                                break
                        if n > 0:
                            message = message[:n+1]
                        else:
                            message = ''
                        #find duedate
                        m = r_duedate.search(message)
                        if m:
                            message = message[:m.start()] + message[m.end():]
                            date = m.group(1)
                    data.append((important, i+1, date, message, filename))
    def _cmp(x, y):
        if x[1] > y[1]:
            return -1
        elif x[1] < y[1]:
            return 1
        else:
            return cmp(x[2], y[2])
        
    data.sort(_cmp)
    return data

