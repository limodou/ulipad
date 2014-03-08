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
#   $Id: mRun.py 1858 2007-01-25 14:15:57Z limodou $
#
#   update
#   2008/08/25
#       * Add callback support, when the process is terminated, the callback
#         will be invoked
#   2008/08/27
#       * if the result can't be convert to unicode, then display the result
#         as repr().


import wx
import types
from modules import Mixin
from modules import common
from modules import Globals

def message_init(win):

    wx.EVT_IDLE(win, win.OnIdle)
    wx.EVT_END_PROCESS(win.mainframe, -1, win.mainframe.OnProcessEnded)
    wx.EVT_KEY_DOWN(win, win.OnKeyDown)
    wx.EVT_KEY_UP(win, win.OnKeyUp)
    wx.EVT_UPDATE_UI(win, win.GetId(),  win.RunCheck)

    win.MAX_PROMPT_COMMANDS = 25

    win.process = None
    win.pid = -1

    win.CommandArray = []
    win.CommandArrayPos = -1

    win.editpoint = 0
    win.writeposition = 0
    win.callback = None
Mixin.setPlugin('messagewindow', 'init', message_init)

#patameters:
#   (redirect=True, hide=False, input_decorator=None, callback=None)
def RunCommand(win, command, redirect=True, hide=False, input_decorator=None,
        callback=None):
    """replace $file = current document filename"""
    global input_appendtext

    #test if there is already a running process
    if hasattr(win, 'messagewindow') and win.messagewindow and win.messagewindow.process:
        common.showmessage(win, tr("The last process didn't stop yet. Please stop it and try again."))
        return
    if input_decorator:
        input_appendtext = input_decorator(appendtext)
    else:
        input_appendtext = appendtext
    if redirect:
        win.createMessageWindow()
        win.panel.showPage(tr('Messages'))
        win.callplugin('start_run', win, win.messagewindow)
        win.messagewindow.SetReadOnly(0)
        win.messagewindow.callback = callback
        appendtext(win.messagewindow, '> ' + command + '\n')

        win.messagewindow.editpoint = win.messagewindow.GetLength()
        win.messagewindow.writeposition = win.messagewindow.GetLength()
        win.SetStatusText(tr("Running "), 0)
        try:
            win.messagewindow.process = wx.Process(win)
            win.messagewindow.process.Redirect()
            if wx.Platform == '__WXMSW__':
                if hide == False:
                    win.messagewindow.pid = wx.Execute(command, wx.EXEC_ASYNC|wx.EXEC_NOHIDE, win.messagewindow.process)
                else:
                    win.messagewindow.pid = wx.Execute(command, wx.EXEC_ASYNC, win.messagewindow.process)
            else:
                win.messagewindow.pid = wx.Execute(command, wx.EXEC_ASYNC|wx.EXEC_MAKE_GROUP_LEADER, win.messagewindow.process)
            if hasattr(win.messagewindow, 'inputstream') and win.messagewindow.inputstream:
                win.messagewindow.inputstream.close()
            win.messagewindow.inputstream = win.messagewindow.process.GetInputStream()
            win.messagewindow.outputstream = win.messagewindow.process.GetOutputStream()
            win.messagewindow.errorstream = win.messagewindow.process.GetErrorStream()
        except:
            win.messagewindow.process = None
            dlg = wx.MessageDialog(win, tr("There are some issues with running the program.\nPlease run it in the shell.") ,
                "Error", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
    else:
        wx.Execute(command, wx.EXEC_ASYNC)
Mixin.setMixin('mainframe', 'RunCommand', RunCommand)

def StopCommand(win):
    if win.messagewindow.process:
        wx.Process_Kill(win.messagewindow.pid, wx.SIGKILL)
        win.messagewindow.SetReadOnly(1)
        win.messagewindow.pid = -1
        win.messagewindow.process = None
    if Globals.pref.message_setfocus_back:
        wx.CallAfter(win.document.SetFocus)
Mixin.setMixin('mainframe', 'StopCommand', StopCommand)


def OnIdle(win, event):
    if win.process is not None:
        if win.inputstream:
            if win.inputstream.CanRead():
                text = win.inputstream.read()
                input_appendtext(win, text)
                win.writeposition = win.GetLength()
                win.editpoint = win.GetLength()
        if win.errorstream:
            if win.errorstream.CanRead():
                text = win.errorstream.read()
                input_appendtext(win, text)
                win.writeposition = win.GetLength()
                win.editpoint = win.GetLength()
Mixin.setMixin('messagewindow', 'OnIdle', OnIdle)

def OnKeyDown(win, event):
    keycode = event.GetKeyCode()
    pos = win.GetCurrentPos()
    if win.pid > -1:
        if (pos >= win.editpoint) and (keycode == wx.WXK_RETURN):
            text = win.GetTextRange(win.writeposition, win.GetLength())
            l = len(win.CommandArray)
            if (l < win.MAX_PROMPT_COMMANDS):
                win.CommandArray.insert(0, text)
                win.CommandArrayPos = -1
            else:
                win.CommandArray.pop()
                win.CommandArray.insert(0, text)
                win.CommandArrayPos = -1

            if isinstance(text, types.UnicodeType):
                text = common.encode_string(text)
            win.outputstream.write(text + '\n')
            win.GotoPos(win.GetLength())
            win.CmdKeyExecute(wx.stc.STC_CMD_NEWLINE)
            win.writeposition = win.GetLength()
            return
        if keycode == wx.WXK_UP:
            if (len(win.CommandArray) > 0):
                if (win.CommandArrayPos + 1) < l:
                    win.GotoPos(win.editpoint)
                    win.SetTargetStart(win.editpoint)
                    win.SetTargetEnd(win.GetLength())
                    win.CommandArrayPos = win.CommandArrayPos + 1
                    win.ReplaceTarget(win.CommandArray[win.CommandArrayPos])
            else:
                event.Skip()

        elif keycode == wx.WXK_DOWN:
            if len(win.CommandArray) > 0:
                win.GotoPos(win.editpoint)
                win.SetTargetStart(win.editpoint)
                win.SetTargetEnd(win.GetLength())
                if (win.CommandArrayPos - 1) > -1:
                    win.CommandArrayPos = win.CommandArrayPos - 1
                    win.ReplaceTarget(win.CommandArray[win.CommandArrayPos])
                else:
                    if (win.CommandArrayPos - 1) > -2:
                        win.CommandArrayPos = win.CommandArrayPos - 1
                    win.ReplaceTarget("")
            else:
                event.Skip()
#    if ((pos > win.editpoint) and (not keycode == wx.WXK_UP)) or ((not keycode == wx.WXK_BACK) and (not keycode == wx.WXK_LEFT) and (not keycode == wx.WXK_UP) and (not keycode == wx.WXK_DOWN)):
#        if (pos < win.editpoint):
#            if (not keycode == wx.WXK_RIGHT):
#                event.Skip()
#        else:
#            event.Skip()
    event.Skip()
Mixin.setMixin('messagewindow', 'OnKeyDown', OnKeyDown)

def OnKeyUp(win, event):
    keycode = event.GetKeyCode()
    #franz: pos was not used
    if keycode == wx.WXK_HOME:
        if (win.GetCurrentPos() < win.editpoint):
            win.GotoPos(win.editpoint)
        return
    elif keycode == wx.WXK_PRIOR:
        if (win.GetCurrentPos() < win.editpoint):
            win.GotoPos(win.editpoint)
        return
    event.Skip()
Mixin.setMixin('messagewindow', 'OnKeyUp', OnKeyUp)

def OnProcessEnded(win, event):
    if win.messagewindow.inputstream.CanRead():
        text = win.messagewindow.inputstream.read()
        input_appendtext(win.messagewindow, text)
    if win.messagewindow.errorstream.CanRead():
        text = win.messagewindow.errorstream.read()
        input_appendtext(win.messagewindow, text)

    if win.messagewindow.process:
        win.messagewindow.process.Destroy()
        win.messagewindow.process = None
        win.messagewindow.inputstream.close()
        win.messagewindow.inputstream = None
        win.messagewindow.outputstream = None
        win.messagewindow.errorstream = None
        win.messagewindow.pid = -1
        win.SetStatusText(tr("Finished! "), 0)
        if win.messagewindow.callback:
            wx.CallAfter(win.messagewindow.callback)
        if Globals.pref.message_setfocus_back:
            wx.CallAfter(win.document.SetFocus)
#        common.note(tr("Finished!"))
Mixin.setMixin('mainframe', 'OnProcessEnded', OnProcessEnded)

def appendtext(win, text):
#    win.GotoPos(win.GetLength())
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
    win.SetReadOnly(0)
    if Globals.pref.msgwin_max_lines>0:
        lines = (win.GetText().splitlines() + text.splitlines())[-1*Globals.pref.msgwin_max_lines:]
        eol = ['\n', '\r\n', '\r']
        win.SetText('')
        text = eol[win.GetEOLMode()].join(lines)
    flag = win.GetCurrentLine() == win.GetLineCount() - 1
    win.AppendText(text)
    if flag:
        win.GotoPos(win.GetLength())
    win.EmptyUndoBuffer()
input_appendtext = appendtext

def RunCheck(win, event):
#    if (win.GetCurrentPos() < win.editpoint) or (win.pid == -1):
    if (win.GetCurrentPos() < win.editpoint) or (win.pid == -1):
        win.SetReadOnly(1)
    else:
        win.SetReadOnly(0)
Mixin.setMixin('messagewindow', 'RunCheck', RunCheck)

####################################################
# 2009-05-20 Add maxmize message windows lines
####################################################
def pref_init(pref):
    pref.msgwin_max_lines = 0
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('General'), 190, 'num', 'msgwin_max_lines', tr('Maxmize message window lines(0 no limited)'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)
