#   Programmer: zhangchunlin
#   E-mail:     zhangchunlin@gmail.com
#
#   Copyleft 2008 limodou
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
#   $Id: mLuaRun.py 1888 2007-02-01 14:47:13Z zhangchunlin $

import wx
import os

from modules import common
from modules import Mixin
from modules import Globals
from modules import Entry

def check_lua():
    interpreters = []
    if wx.Platform == '__WXMSW__':
        # try to check ENVIRONMENT:LUA_DEV
        if (os.environ.has_key("LUA_DEV")):
            LUA_DEV = os.environ["LUA_DEV"]
            lua_exe_fp = os.path.join(LUA_DEV,"lua.exe")
            if os.path.exists(lua_exe_fp):
                interpreters.append(('console', lua_exe_fp))
            wlua_exe_fp = os.path.join(LUA_DEV,"wlua.exe")
            if os.path.exists(wlua_exe_fp):
                interpreters.append(('window', wlua_exe_fp))
            
    
    return interpreters
        
def pref_init(pref):
    s = check_lua()
    pref.lua_interpreter = s
    if len(s) == 1:
        pref.default_lua_interpreter = s[0][0]
    else:
        pref.default_lua_interpreter = 'noexist'
    pref.lua_show_args = False
    pref.lua_save_before_run = False
    pref.lua_default_paramters = {}
    for i in s:
        pref.lua_default_paramters[i[0]] = '-e "io.stdout:setvbuf \'no\'"'
Mixin.setPlugin('preference', 'init', pref_init)

def OnSetLuaInterpreter(win, event):
    dlg = LuaInterpreterDialog(win, win.pref)
    dlg.ShowModal()
Mixin.setMixin('prefdialog', 'OnSetLuaInterpreter', OnSetLuaInterpreter)

def add_pref(preflist):
    preflist.extend([
        ('Lua', 150, 'button', 'lua_interpreter', tr('Setup Lua interpreter...'), 'OnSetLuaInterpreter'),
        ('Lua', 155, 'check', 'lua_show_args', tr('Show the Select Arguments dialog at Lua program run'), None),
        ('Lua', 156, 'check', 'lua_save_before_run', tr('Save the modified document at Lua program run'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def add_luaftype_menu(menulist):
    menulist.extend([('IDM_LUA', #parent menu id
        [
            (120, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (130, 'IDM_LUA_RUN', tr('Run')+u'\tE=F5', wx.ITEM_NORMAL, 'OnLuaRun', tr('Runs the Lua program.')),
            (140, 'IDM_LUA_SETARGS', tr('Set Arguments...'), wx.ITEM_NORMAL, 'OnLuaSetArgs', tr('Sets the command-line arguments for a Lua program.')),
            (150, 'IDM_LUA_END', tr('Stop Program'), wx.ITEM_NORMAL, 'OnLuaEnd', tr('Stops the current Lua program.')),
        ]),
    ])
Mixin.setPlugin('luafiletype', 'add_menu', add_luaftype_menu)

def editor_init(win):
    win.args = ''
    win.redirect = True
Mixin.setPlugin('editor', 'init', editor_init)

def _get_lua_exe(win):
    s = win.pref.lua_interpreter
    interpreters = dict(s)
    interpreter = interpreters.get(win.pref.default_lua_interpreter, '')

    #check lua execute
    e = check_lua()
    for x, v in e:
        flag = False
        for i, t in enumerate(s):
            name, exe = t
            if exe == v:
                flag = True
                if name != x:
                    s[i] = (x, v)
        if not flag:
            s.append((x, v))
    win.pref.save()
    
    if not interpreter:
        value = ''
        if s:
            if len(s) > 1:
                dlg = SelectInterpreter(win, s[0][0], [x for x, v in s])
                if dlg.ShowModal() == wx.ID_OK:
                    value = dlg.GetValue()
                dlg.Destroy()
            else:
                value = s[0][0]
                
        if not value:
            common.showerror(win, tr("You didn't set the Lua interpreter.\nPlease set it up first in the preferences."))
        
        interpreter = dict(s).get(value, '')
        win.pref.default_lua_interpreter = value
        win.pref.save()
        
    return interpreter

def OnLuaRun(win, event):
    interpreter = _get_lua_exe(win)
    if not interpreter: return

    doc = win.editctrl.getCurDoc()
    if doc.isModified() or doc.filename == '':
        if win.pref.lua_save_before_run:
            win.OnFileSave(event)
        else:
            d = wx.MessageDialog(win, tr("The script can't run because the document hasn't been saved.\nWould you like to save it?"), tr("Run"), wx.YES_NO | wx.ICON_QUESTION)
            answer = d.ShowModal()
            d.Destroy()
            if answer == wx.ID_YES:
                win.OnFileSave(event)
            else:
                return
        
    if win.pref.lua_show_args:
        if not get_lua_args(win):
            return
        
    args = doc.args.replace('$path', os.path.dirname(doc.filename))
    args = args.replace('$file', doc.filename)
    ext = os.path.splitext(doc.filename)[1].lower()
    parameter = Globals.pref.lua_default_paramters.get(Globals.pref.default_lua_interpreter, '')
    interpreter = dict(Globals.pref.lua_interpreter).get(Globals.pref.default_lua_interpreter, '')
    command = u'"%s" %s "%s" %s' % (interpreter, parameter, doc.filename, args)
    #chanage current path to filename's dirname
    path = os.path.dirname(doc.filename)
    os.chdir(common.encode_string(path))

    win.RunCommand(command, redirect=win.document.redirect)
Mixin.setMixin('mainframe', 'OnLuaRun', OnLuaRun)

def get_lua_args(win):
    if not Globals.pref.lua_interpreter:
        common.showerror(win, tr("You didn't set the Lua interpreter.\nPlease set it up first in the preferences."))
        return False
    
    dlg = LuaArgsDialog(win, tr('Lua Arguments Manager'),
        win.document.args, win.document.redirect)
    answer = dlg.ShowModal()
    value = dlg.GetValue()
    dlg.Destroy()
    if answer == wx.ID_OK:
        win.document.args = value['command_line']
        win.document.redirect = value['redirect']
        return True
    else:
        return False
    
def OnLuaSetArgs(win, event=None):
    get_lua_args(win)
Mixin.setMixin('mainframe', 'OnLuaSetArgs', OnLuaSetArgs)

def OnLuaEnd(win, event):
    win.StopCommand()
    win.SetStatusText(tr("Stopped!"), 0)
Mixin.setMixin('mainframe', 'OnLuaEnd', OnLuaEnd)

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (2100, 'run'),
        (2110, 'setargs'),
        (2120, 'stop'),
        (2150, '|'),
    ])

    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'run':(wx.ITEM_NORMAL, 'IDM_LUA_RUN', 'images/run.gif', tr('Run'), tr('Runs the Lua program.'), 'OnLuaRun'),
        'setargs':(wx.ITEM_NORMAL, 'IDM_LUA_SETARGS', 'images/setargs.gif', tr('Set Arguments'), tr('Sets the command-line arguments for a Lua program.'), 'OnLuaSetArgs'),
        'stop':(wx.ITEM_NORMAL, 'IDM_LUA_END', 'images/stop.gif', tr('Stop Program'), tr('Stops the current Lua program.'), 'OnLuaEnd'),
    })
Mixin.setPlugin('luafiletype', 'add_tool_list', add_tool_list)

def OnLuaRunUpdateUI(win, event):
    eid = event.GetId()
    if eid in [ win.IDM_LUA_RUN, win.IDM_LUA_SETARGS ]:
        if not hasattr(win, 'messagewindow') or not win.messagewindow or not (win.messagewindow.pid > 0):
            event.Enable(True)
        else:
            event.Enable(False)
    elif eid == win.IDM_LUA_END:
        if hasattr(win, 'messagewindow') and win.messagewindow and (win.messagewindow.pid > 0):
            event.Enable(True)
        else:
            event.Enable(False)
Mixin.setMixin('mainframe', 'OnLuaRunUpdateUI', OnLuaRunUpdateUI)

def on_enter(mainframe, document):
    wx.EVT_UPDATE_UI(mainframe, mainframe.IDM_LUA_RUN, mainframe.OnLuaRunUpdateUI)
    wx.EVT_UPDATE_UI(mainframe, mainframe.IDM_LUA_SETARGS, mainframe.OnLuaRunUpdateUI)
    wx.EVT_UPDATE_UI(mainframe, mainframe.IDM_LUA_END, mainframe.OnLuaRunUpdateUI)
Mixin.setPlugin('luafiletype', 'on_enter', on_enter)

def on_leave(mainframe, filename, languagename):
    ret = mainframe.Disconnect(mainframe.IDM_LUA_RUN, -1, wx.wxEVT_UPDATE_UI)
    ret = mainframe.Disconnect(mainframe.IDM_LUA_SETARGS, -1, wx.wxEVT_UPDATE_UI)
    ret = mainframe.Disconnect(mainframe.IDM_LUA_END, -1, wx.wxEVT_UPDATE_UI)
Mixin.setPlugin('luafiletype', 'on_leave', on_leave)


################################# Dialogs
from modules import meide as ui

class SelectInterpreter(ui.SimpleDialog):
    def __init__(self, parent, value, interpreters):
        box = ui.VBox(namebinding='element')
        box.add(ui.Label(tr('Which Lua interpreter do you want to use?')))
        box.add(ui.ComboBox(value, choices=interpreters, style=wx.CB_READONLY), name='interpreter')
        super(SelectInterpreter, self).__init__(parent, box, title=tr('Lua Interpreters List'), fit=2)
        
        self.layout.SetFocus()

    def GetValue(self):
        return self.interpreter.GetValue()


class LuaInterpreterDialog(wx.Dialog):
    def __init__(self, parent, pref):
        wx.Dialog.__init__(self, parent, -1, tr('Lua Interpreter Setup'))
        self.parent = parent
        self.pref = pref

        box = wx.BoxSizer(wx.VERTICAL)
        self.list = wx.ListCtrl(self, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_EDIT_LABELS)
        self.list.InsertColumn(0, tr("Description"))
        self.list.InsertColumn(1, tr("Interpreter path"))
        self.list.SetColumnWidth(0, 150)
        self.list.SetColumnWidth(1, 330)
        for i, item in enumerate(pref.lua_interpreter):
            description, path = item
            self.list.InsertStringItem(i, description)
            self.list.SetStringItem(i, 1, path)

        box.Add(self.list, 1, wx.EXPAND|wx.ALL, 5)
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        self.ID_ADD = wx.NewId()
        self.ID_REMOVE = wx.NewId()
        self.ID_MODIFY = wx.NewId()
        self.btnAdd = wx.Button(self, self.ID_ADD, tr("Add"))
        box2.Add(self.btnAdd, 0, 0, 5)
        self.btnModify = wx.Button(self, self.ID_MODIFY, tr("Modify"))
        box2.Add(self.btnModify, 0, 0, 5)
        self.btnRemove = wx.Button(self, self.ID_REMOVE, tr("Remove"))
        box2.Add(self.btnRemove, 0, 0, 5)
        self.btnOK = wx.Button(self, wx.ID_OK, tr("OK"))
        self.btnOK.SetDefault()
        box2.Add(self.btnOK, 0, 0, 5)
        self.btnCancel = wx.Button(self, wx.ID_CANCEL, tr("Cancel"))
        box2.Add(self.btnCancel, 0, 0, 5)
        box.Add(box2, 0, wx.ALIGN_CENTER|wx.ALL, 5)

        wx.EVT_BUTTON(self.btnAdd, self.ID_ADD, self.OnAdd)
        wx.EVT_BUTTON(self.btnModify, self.ID_MODIFY, self.OnModify)
        wx.EVT_BUTTON(self.btnRemove, self.ID_REMOVE, self.OnRemove)
        wx.EVT_BUTTON(self.btnOK, wx.ID_OK, self.OnOK)
        wx.EVT_LIST_ITEM_SELECTED(self.list, self.list.GetId(), self.OnItemSelected)
        wx.EVT_LIST_ITEM_DESELECTED(self.list, self.list.GetId(), self.OnItemDeselected)

        self.OnItemDeselected(None)

        self.SetSizer(box)
        self.SetAutoLayout(True)

    def getItemText(self, item):
        return self.list.GetItemText(item), self.list.GetItem(item, 1).GetText()

    def OnRemove(self, event):
        lastitem = -1
        item = self.list.GetNextItem(lastitem, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        while item > -1:
            if self.getItemText(item)[0] == tr('default'):
                common.showmessage(self, tr("You can't delete the default interpreter!"))
                return
            dlg = wx.MessageDialog(self, tr("Do you realy want to delete current item [%s]?") % self.getItemText(item)[0],
                    tr("Deleting Interpreter"), wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
            answer = dlg.ShowModal()
            if answer == wx.ID_YES:
                self.list.DeleteItem(item)
            elif answer == wx.ID_NO:
                lastitem = item
            else:
                return
            item = self.list.GetNextItem(lastitem, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)

    def OnAdd(self, event):
        dlg = Entry.MyFileEntry(self, tr("Interpreter Path"),
                tr("Enter the interpreter path"), '')
        answer = dlg.ShowModal()
        if answer == wx.ID_OK:
            path = dlg.GetValue()
            if len(path) > 0:
                i = self.list.GetItemCount()
                self.list.InsertStringItem(i, 'Change the description')
                self.list.SetStringItem(i, 1, path)
                self.list.EditLabel(i)

    def OnModify(self, event):
        if self.list.GetSelectedItemCount() > 1:
            dlg = wx.MessageDialog(self, tr("You can select only one item"), tr("Modify Interpreter Path"), wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            return
        item = self.list.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        dlg = Entry.MyFileEntry(self, tr("Interpreter Path"), tr("Enter the interpreter path"), self.getItemText(item)[1])
        answer = dlg.ShowModal()
        if answer == wx.ID_OK:
            path = dlg.GetValue()
            if len(path) > 0:
                self.list.SetStringItem(item, 1, path)

    def OnOK(self, event):
        interpreters = []
        for i in range(self.list.GetItemCount()):
            description, path = self.getItemText(i)
            interpreters.append((description, path))
            if (description == '') or (description == 'Change the description'):
                dlg = wx.MessageDialog(self, tr("The description must not be empty or ") + '"Change the description"' +
                         tr('.\nPlease change them first!'), tr("Saving Interpreter Setting"), wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                return
        else:
            self.pref.lua_interpreter = interpreters[:]
            self.pref.save()
            event.Skip()

    def OnItemSelected(self, event):
        self.btnRemove.Enable(True)
        self.btnModify.Enable(True)

    def OnItemDeselected(self, event):
        self.btnRemove.Enable(False)
        self.btnModify.Enable(False)

class LuaArgsDialog(wx.Dialog):
    def __init__(self, parent, title, defaultvalue, defaultchkvalue):
        wx.Dialog.__init__(self, parent, -1, style = wx.DEFAULT_DIALOG_STYLE, title = title)
        
        self.pref = Globals.pref
        
        self.sizer = sizer = ui.VBox(namebinding='widget').create(self).auto_layout()
        box = sizer.add(ui.VGroup(tr('Lua interpreter')))
        h = box.add(ui.HBox())
        h.add(ui.Label(tr('Select:')))
        
        interpreters = dict(self.pref.lua_interpreter)
        default_lua_interpreter = self.pref.default_lua_interpreter
        if not default_lua_interpreter in interpreters:
            default_lua_interpreter = self.pref.default_lua_interpreter[0][0]
        
        h.add(ui.SingleChoice(default_lua_interpreter, sorted(interpreters.keys())), name='interpreter').bind(wx.EVT_COMBOBOX, self.OnChanged)
        h.add(ui.Label(tr('Parameters:')))
        h.add(ui.Text(self.pref.lua_default_paramters.get(default_lua_interpreter, '')), name='parameter')
        
        h = self.sizer.add(ui.HBox())
        h.add(ui.Label(tr('Parameters of script:')))
        h.add(ui.Text(defaultvalue), name='command_line').tooltip("$file will be replaced with the filename of the current document\n"
            "$path will be replaced with the filename's directory of the current document")
        self.sizer.add(ui.Check(defaultchkvalue, tr('Redirect input and output')), name='redirect')
        self.sizer.add(ui.Check(self.pref.lua_show_args, tr('Show the Select Arguments dialog at Lua program run')), name='show_args')
        
        sizer.add(ui.simple_buttons(), flag=wx.ALIGN_CENTER|wx.BOTTOM)
        self.sizer.bind('btnOk', 'click', self.OnOK)
        self.btnOk.SetDefault()
        
        sizer.auto_fit(1)
        
    def GetValue(self):
        return self.sizer.GetValue()
    
    def OnOK(self, event):
        self.pref.default_lua_interpreter = self.interpreter.GetValue()
        self.pref.lua_default_paramters[self.pref.default_lua_interpreter] = self.parameter.GetValue()
        self.pref.lua_show_args = self.show_args.GetValue()
        self.pref.save()
        event.Skip()

    def OnChanged(self, event):
        self.parameter.SetValue(self.pref.lua_default_paramters.get(self.interpreter.GetValue(), ''))

def goto_error_line(msgwin, line, lineno):
    import re
    r = re.compile('((\w:)?[^:\t\n\r\?\;]+):(\d+)')
    b = r.search(common.encode_string(line, common.defaultfilesystemencoding))
    if b:
        return True, (b.groups()[0],b.groups()[2])
Mixin.setPlugin('messagewindow', 'goto_error_line', goto_error_line)
