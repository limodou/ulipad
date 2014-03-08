#   Programmer:     limodou
#   E-mail:         limodou@gmail.com
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
#   $Id: mDosPrompt.py,v 1.1 2005/07/31 09:08:14 limodou Exp $
    
import wx
from modules import Mixin
from modules import common

def init(win):
    wx.EVT_IDLE(win, win.OnIdle)
    wx.EVT_END_PROCESS(win.mainframe, -1, win.mainframe.OnDosProcessEnded)
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

    win.commandlen = 0
    win.firstread = 0
Mixin.setPlugin('dospromptwindow', 'init', init)

def RunDosCommand(win, command, guiflag=False, redirect=True):
    """replace $file = current document filename"""
    if redirect:
        win.createDosWindow()

        win.panel.showPage(tr('Dos'))

        win.dosprompt.SetText('')
        win.dosprompt.editpoint = 0
        win.dosprompt.writeposition = 0
        try:
            win.dosprompt.process = wx.Process(win)
            win.dosprompt.process.Redirect()
            if guiflag:
                win.dosprompt.pid = wx.Execute(command, wx.EXEC_ASYNC|wx.EXEC_NOHIDE, win.dosprompt.process)
            else:
                win.dosprompt.pid = wx.Execute(command, wx.EXEC_ASYNC, win.dosprompt.process)
            win.dosprompt.inputstream = win.dosprompt.process.GetInputStream()
            win.dosprompt.errorstream = win.dosprompt.process.GetErrorStream()
            win.dosprompt.outputstream = win.dosprompt.process.GetOutputStream()
        except:
            win.dosprompt.process = None
            dlg = wx.MessageDialog(win, tr("There are some problems when running the program!\nPlease run it in shell.") ,
                    "Stop running", wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
    else:
        wx.Execute(command)
Mixin.setMixin('mainframe', 'RunDosCommand', RunDosCommand)

def OnIdle(win, event):
    if win.process is not None:
        if win.inputstream:
            if win.inputstream.CanRead():
                text = win.inputstream.read()
                if win.commandlen > 0:
                    if len(text) >= win.commandlen:
                        text = text[win.commandlen:]
                        win.commandlen = 0
                    else:
                        text = ''
                        win.commandlen -= len(text)
                appendtext(win, text)
                print repr(text)
                win.writeposition = win.GetLength()
                win.editpoint = win.GetLength()
        if win.errorstream:
            if win.errorstream.CanRead():
                text = win.errorstream.read()
                appendtext(win, text)
                win.writeposition = win.GetLength()
                win.editpoint = win.GetLength()
Mixin.setMixin('dospromptwindow', 'OnIdle', OnIdle)

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

            if isinstance(text, unicode):
                text = common.encode_string(text)
            win.commandlen = len(text) + 1
            win.firstread = True

            win.outputstream.write(text + '\n')
            win.GotoPos(win.GetLength())

        if keycode == wx.WXK_UP:
            l = len(win.CommandArray)
            if (len(win.CommandArray) > 0):
                if (win.CommandArrayPos + 1) < l:
                    win.GotoPos(win.editpoint)
                    win.SetTargetStart(win.editpoint)
                    win.SetTargetEnd(win.GetLength())
                    win.CommandArrayPos = win.CommandArrayPos + 1
                    win.ReplaceTarget(win.CommandArray[win.CommandArrayPos])

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
    if ((pos > win.editpoint) and (not keycode == wx.WXK_UP)) or ((not keycode == wx.WXK_BACK) and (not keycode == wx.WXK_LEFT) and (not keycode == wx.WXK_UP) and (not keycode == wx.WXK_DOWN)):
        if (pos < win.editpoint):
            if (not keycode == wx.WXK_RIGHT):
                event.Skip()
        else:
            event.Skip()
Mixin.setMixin('dospromptwindow', 'OnKeyDown', OnKeyDown)

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
Mixin.setMixin('dospromptwindow', 'OnKeyUp', OnKeyUp)

def OnDosProcessEnded(win, event):
    if win.dosprompt.inputstream.CanRead():
        text = win.dosprompt.inputstream.read()
        appendtext(win.dosprompt, text)
    if win.dosprompt.errorstream.CanRead():
        text = win.dosprompt.errorstream.read()
        appendtext(win.dosprompt, text)

    if win.dosprompt.process:
        win.dosprompt.process.Destroy()
        win.dosprompt.process = None
        win.dosprompt.pid = -1
Mixin.setMixin('mainframe', 'OnDosProcessEnded', OnDosProcessEnded)

def appendtext(win, text):
    win.GotoPos(win.GetLength())
    if not isinstance(text, unicode):
        text = common.decode_string(text)
    win.AddText(text)
    win.GotoPos(win.GetLength())
    win.EmptyUndoBuffer()

def RunCheck(win, event):
    if (win.GetCurrentPos() < win.editpoint) or (win.pid == -1):
        win.SetReadOnly(1)
    else:
        win.SetReadOnly(0)
Mixin.setMixin('dospromptwindow', 'RunCheck', RunCheck)
