#   Programmer: limodou
#   E-mail:     limodou@gmail.com
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
#   $Id: mPyRun.py 1888 2007-02-01 14:47:13Z limodou $

import wx
import os
import sys
from modules import common
from modules import Mixin
from modules import Globals

def check_python():
    interpreters = []
    if wx.Platform == '__WXMSW__':
        from modules import winreg
        for v in ('2.3', '2.4', '2.5', '2.6', '2.7', '3.0', '3.1'):
            try:
                key = winreg.Key(winreg.HKLM, r'SOFTWARE\Python\Pythoncore\%s\InstallPath' % v)
                interpreters.append((v+' console', os.path.join(key.value, 'python.exe')))
                interpreters.append((v+' window', os.path.join(key.value, 'pythonw.exe')))
            except:
                pass
    else:
        version = '.'.join(map(str, sys.version_info[:2]))
        interpreters.append((version, sys.executable))
    return interpreters
        
def pref_init(pref):
    s = check_python()
    pref.python_interpreter = s
    if len(s) == 1:
        pref.default_interpreter = s[0][0]
    else:
        pref.default_interpreter = 'noexist'
    pref.python_show_args = False
    pref.python_save_before_run = False
    pref.python_default_paramters = {}
    for i in s:
        pref.python_default_paramters[i[0]] = '-u'
Mixin.setPlugin('preference', 'init', pref_init)

def OnSetPythonInterpreter(win, event):
    from InterpreterDialog import InterpreterDialog
    dlg = InterpreterDialog(win, win.pref)
    dlg.ShowModal()
Mixin.setMixin('prefdialog', 'OnSetPythonInterpreter', OnSetPythonInterpreter)

def add_pref(preflist):
    preflist.extend([
        ('Python', 150, 'button', 'python_interpreter', tr('Setup Python interpreter...'), 'OnSetPythonInterpreter'),
        ('Python', 155, 'check', 'python_show_args', tr('Show the Select Arguments dialog at Python program run'), None),
        ('Python', 156, 'check', 'python_save_before_run', tr('Save the modified document at Python program run'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def add_pyftype_menu(menulist):
    menulist.extend([('IDM_PYTHON', #parent menu id
        [
            (120, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (130, 'IDM_PYTHON_RUN', tr('Run')+u'\tE=F5', wx.ITEM_NORMAL, 'OnPythonRun', tr('Runs the Python program.')),
            (140, 'IDM_PYTHON_SETARGS', tr('Set Arguments...'), wx.ITEM_NORMAL, 'OnPythonSetArgs', tr('Sets the command-line arguments for a Python program.')),
            (150, 'IDM_PYTHON_END', tr('Stop Program'), wx.ITEM_NORMAL, 'OnPythonEnd', tr('Stops the current Python program.')),
            (155, 'IDM_PYTHON_DOCTEST', tr('Run Doctest'), wx.ITEM_NORMAL, 'OnPythonDoctests', tr('Runs doctest in the current document.')),
        ]),
    ])
Mixin.setPlugin('pythonfiletype', 'add_menu', add_pyftype_menu)

def editor_init(win):
    win.args = ''
    win.redirect = True
Mixin.setPlugin('editor', 'init', editor_init)

def _get_python_exe(win):
    s = win.pref.python_interpreter
    interpreters = dict(s)
    interpreter = interpreters.get(win.pref.default_interpreter, '')

    #check python execute
    e = check_python()
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
            common.showerror(win, tr("You didn't set the Python interpreter.\nPlease set it up first in the preferences."))
        
        interpreter = dict(s).get(value, '')
        win.pref.default_interpreter = value
        win.pref.save()
        
    return interpreter

def OnPythonRun(win, event):
    interpreter = _get_python_exe(win)
    if not interpreter: return

    doc = win.editctrl.getCurDoc()
    if doc.isModified() or doc.filename == '':
        if win.pref.python_save_before_run:
            win.OnFileSave(event)
        else:
            d = wx.MessageDialog(win, tr("The script can't run because the document hasn't been saved.\nWould you like to save it?"), tr("Run"), wx.YES_NO | wx.ICON_QUESTION)
            answer = d.ShowModal()
            d.Destroy()
            if answer == wx.ID_YES:
                win.OnFileSave(event)
            else:
                return
        
    if win.pref.python_show_args:
        if not get_python_args(win):
            return
        
    args = doc.args.replace('$path', os.path.dirname(doc.filename))
    args = args.replace('$file', doc.filename)
    ext = os.path.splitext(doc.filename)[1].lower()
    parameter = Globals.pref.python_default_paramters.get(Globals.pref.default_interpreter, '')
    interpreter = dict(Globals.pref.python_interpreter).get(Globals.pref.default_interpreter, '')
    command = u'"%s" %s "%s" %s' % (interpreter, parameter, doc.filename, args)
    #chanage current path to filename's dirname
    path = os.path.dirname(doc.filename)
    os.chdir(common.encode_string(path))

    win.RunCommand(command, redirect=win.document.redirect)
Mixin.setMixin('mainframe', 'OnPythonRun', OnPythonRun)

def get_python_args(win):
    if not Globals.pref.python_interpreter:
        common.showerror(win, tr("You didn't set the Python interpreter.\nPlease set it up first in the preferences."))
        return False
    
    from InterpreterDialog import PythonArgsDialog
    
    dlg = PythonArgsDialog(win, tr('Python Arguments Manager'),
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
    
def OnPythonSetArgs(win, event=None):
    get_python_args(win)
Mixin.setMixin('mainframe', 'OnPythonSetArgs', OnPythonSetArgs)

def OnPythonEnd(win, event):
    win.StopCommand()
    win.SetStatusText(tr("Stopped!"), 0)
Mixin.setMixin('mainframe', 'OnPythonEnd', OnPythonEnd)

def OnPythonDoctests(win, event):
    from modules import Globals
    from modules.Debug import error
    
    def appendtext(win, text):
        win.SetReadOnly(0)
        win.SetText('')
        win.GotoPos(win.GetLength())
        if not isinstance(text, unicode):
            try:
                text = unicode(text, common.defaultencoding)
            except UnicodeDecodeError:
                def f(x):
                    if ord(x) > 127:
                        return '\\x%x' % ord(x)
                    else:
                        return x
                text = ''.join(map(f, text))
        win.AddText(text)
        win.GotoPos(win.GetLength())
        win.EmptyUndoBuffer()
        win.SetReadOnly(1)
    
    def pipe_command(cmd, callback):
        from modules import Casing
        
        def _run(cmd):
            try:
                sin, sout, serr = os.popen3(cmd)
                if callback:
                    wx.CallAfter(callback, sout.read()+serr.read())
            except:
                error.traceback()
                
        d = Casing.Casing(_run, cmd)
        d.start_thread()
    
    def f(text):
        try:
            win.createMessageWindow()
            win.panel.showPage(tr('Messages'))
            if not text:
                text = 'Doctest for %s is successful!' % doc.filename
            appendtext(win.messagewindow, text)
        except:
            error.traceback()
        
    doc = win.editctrl.getCurDoc()
    if doc.isModified() or doc.filename == '':
        d = wx.MessageDialog(win, tr("The script can't run because the document hasn't been saved.\nWould you like to save it?"), tr("Run"), wx.YES_NO | wx.ICON_QUESTION)
        answer = d.ShowModal()
        d.Destroy()
        if answer == wx.ID_YES:
            win.OnFileSave(event)
        else:
            return
    
    path = os.path.normpath(os.path.join(Globals.workpath, 'packages/cmd_doctest.py'))
    filename = Globals.mainframe.editctrl.getCurDoc().filename
    interpreter = _get_python_exe(win)
    cmd = u'%s "%s" "%s"' % (interpreter, path, filename)
    pipe_command(cmd, f)
Mixin.setMixin('mainframe', 'OnPythonDoctests', OnPythonDoctests)

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (2100, 'run'),
        (2110, 'setargs'),
        (2120, 'stop'),
        (2130, 'doctest'),
        (2150, '|'),
    ])

    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'run':(wx.ITEM_NORMAL, 'IDM_PYTHON_RUN', 'images/run.gif', tr('Run'), tr('Runs the Python program.'), 'OnPythonRun'),
        'setargs':(wx.ITEM_NORMAL, 'IDM_PYTHON_SETARGS', 'images/setargs.gif', tr('Set Arguments'), tr('Sets the command-line arguments for a Python program.'), 'OnPythonSetArgs'),
        'stop':(wx.ITEM_NORMAL, 'IDM_PYTHON_END', 'images/stop.gif', tr('Stop Program'), tr('Stops the current Python program.'), 'OnPythonEnd'),
        'doctest':(wx.ITEM_NORMAL, 'IDM_PYTHON_DOCTEST', 'images/doctest.png', tr('Run Doctest'), tr('Runs dotest in the current document.'), 'OnPythonDoctests'),
    })
Mixin.setPlugin('pythonfiletype', 'add_tool_list', add_tool_list)

def OnPythonRunUpdateUI(win, event):
    eid = event.GetId()
    if eid in [ win.IDM_PYTHON_RUN, win.IDM_PYTHON_SETARGS ]:
        if not hasattr(win, 'messagewindow') or not win.messagewindow or not (win.messagewindow.pid > 0):
            event.Enable(True)
        else:
            event.Enable(False)
    elif eid == win.IDM_PYTHON_END:
        if hasattr(win, 'messagewindow') and win.messagewindow and (win.messagewindow.pid > 0):
            event.Enable(True)
        else:
            event.Enable(False)
Mixin.setMixin('mainframe', 'OnPythonRunUpdateUI', OnPythonRunUpdateUI)

def on_enter(mainframe, document):
    wx.EVT_UPDATE_UI(mainframe, mainframe.IDM_PYTHON_RUN, mainframe.OnPythonRunUpdateUI)
    wx.EVT_UPDATE_UI(mainframe, mainframe.IDM_PYTHON_SETARGS, mainframe.OnPythonRunUpdateUI)
    wx.EVT_UPDATE_UI(mainframe, mainframe.IDM_PYTHON_END, mainframe.OnPythonRunUpdateUI)
Mixin.setPlugin('pythonfiletype', 'on_enter', on_enter)

def on_leave(mainframe, filename, languagename):
    ret = mainframe.Disconnect(mainframe.IDM_PYTHON_RUN, -1, wx.wxEVT_UPDATE_UI)
    ret = mainframe.Disconnect(mainframe.IDM_PYTHON_SETARGS, -1, wx.wxEVT_UPDATE_UI)
    ret = mainframe.Disconnect(mainframe.IDM_PYTHON_END, -1, wx.wxEVT_UPDATE_UI)
Mixin.setPlugin('pythonfiletype', 'on_leave', on_leave)

def goto_error_line(msgwin, line, lineno):
    import re
    r = re.compile('File\s+"(.*?)",\s+line\s+(\d+)')
    b = r.search(common.encode_string(line, common.defaultfilesystemencoding))
    if b:
        return True, b.groups()
Mixin.setPlugin('messagewindow', 'goto_error_line', goto_error_line)

################################# Dialogs
from modules import meide as ui

class SelectInterpreter(ui.SimpleDialog):
    def __init__(self, parent, value, interpreters):
        box = ui.VBox(namebinding='element')
        box.add(ui.Label(tr('Which Python interpreter do you want to use?')))
        box.add(ui.ComboBox(value, choices=interpreters, style=wx.CB_READONLY), name='interpreter')
        super(SelectInterpreter, self).__init__(parent, box, title=tr('Python Interpreters List'), fit=2)
        
        self.layout.SetFocus()

    def GetValue(self):
        return self.interpreter.GetValue()
