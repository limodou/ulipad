#coding=utf-8
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
#   $Id: ShellWindow.py 1500 2006-09-01 13:47:51Z limodou $

import os
import types
import locale
import wx.py
from wx.py.interpreter import Interpreter
from wx.py import dispatcher
from modules import Mixin
from modules import common
from modules import makemenu


class ShellWindow(wx.py.shell.Shell, Mixin.Mixin):
    __mixinname__ = 'shellwindow'
    
    popmenulist = [(None, #parent menu id
        [
            (100, 'IDPM_UNDO', tr('Undo') + '\tCtrl+Z', wx.ITEM_NORMAL, 'OnPopupEdit', tr('Reverse previous editing operation')),
            (110, 'IDPM_REDO', tr('Redo') + '\tCtrl+Y', wx.ITEM_NORMAL, 'OnPopupEdit', tr('Reverse previous undo operation')),
            (120, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (130, 'IDPM_CUT', tr('Cut') + '\tCtrl+X', wx.ITEM_NORMAL, 'OnPopupEdit', tr('Deletes text from the shell window and moves it to the clipboard')),
            (140, 'IDPM_COPY', tr('Copy') + '\tCtrl+C', wx.ITEM_NORMAL, 'OnPopupEdit', tr('Copies text from the shell window to the clipboard')),
            (145, 'IDPM_COPY_CLEAR', tr('Copy Without Prompts'), wx.ITEM_NORMAL, 'OnPopupEdit', tr('Copies text without prompts from the shell window to the clipboard')),
            (150, 'IDPM_PASTE', tr('Paste') + '\tCtrl+V', wx.ITEM_NORMAL, 'OnPopupEdit', tr('Pastes text from the clipboard into the shell window')),
            (155, 'IDPM_PASTE_RUN', tr('Paste and Run') + '\tCtrl+Shift+V', wx.ITEM_NORMAL, 'OnPopupEdit', tr('Pastes text from the clipboard into the shell window and also run it')),
            (160, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (170, 'IDPM_SELECTALL', tr('Select All') + '\tCtrl+A', wx.ITEM_NORMAL, 'OnPopupEdit', tr('Selects all text.')),
            (180, 'IDPM_CLEAR', tr('Clear Shell Window') + '\tCtrl+Alt+R', wx.ITEM_NORMAL, 'OnClearShell', tr('Clears content of shell window.')),
            (185, 'IDPM_RESTART_SHELL', tr('Restart Shell') + '\tCtrl+R', wx.ITEM_NORMAL, 'OnRestartShell', tr('Restarts the shell')),
            
        ]),
    ]
    imagelist = {
        'IDPM_UNDO':'images/undo.gif',
        'IDPM_REDO':'images/redo.gif',
        'IDPM_CUT':'images/cut.gif',
        'IDPM_COPY':'images/copy.gif',
        'IDPM_PASTE':'images/paste.gif',
    }
    
    def __init__(self, parent, mainframe):
        self.initmixin()

        #add default font settings in config.ini
        x = common.get_config_file_obj()
        font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        fontname = x.default.get('shell_font', font.GetFaceName())
        fontsize = x.default.get('shell_fontsize', 10)
        #todo fontsize maybe changed for mac
        if wx.Platform == '__WXMAC__':
            fontsize = 13
        #add chinese simsong support, because I like this font
        if not x.default.has_key('shell_font') and locale.getdefaultlocale()[0] == 'zh_CN':
            fontname = u'宋体'

        import wx.py.editwindow as edit
        edit.FACES['mono'] = fontname
        edit.FACES['size'] = fontsize

        wx.py.shell.Shell.__init__(self, parent, -1, InterpClass=NEInterpreter)

        #disable popup
        self.UsePopUp(0)
        
        self.parent = parent
        self.mainframe = mainframe
        wx.EVT_KILL_FOCUS(self, self.OnKillFocus)
        
        for key in ShellWindow.imagelist.keys():
            f = ShellWindow.imagelist[key]
            ShellWindow.imagelist[key] = common.getpngimage(f)
        
        self.popmenu = makemenu.makepopmenu(self, ShellWindow.popmenulist, ShellWindow.imagelist)
        
        wx.EVT_RIGHT_DOWN(self, self.OnPopUp)
        
        wx.EVT_UPDATE_UI(self, self.IDPM_UNDO, self._OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_REDO, self._OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_CUT, self._OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_COPY, self._OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_COPY_CLEAR, self._OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_PASTE, self._OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.IDPM_PASTE_RUN, self._OnUpdateUI)

    def OnPopUp(self, event):
        other_menus = []
        if self.popmenu:
            self.popmenu.Destroy()
            self.popmenu = None
        self.callplugin('other_popup_menu', self, other_menus)
        import copy
        if other_menus:
            pop_menus = copy.deepcopy(ShellWindow.popmenulist + other_menus)
        else:
            pop_menus = copy.deepcopy(ShellWindow.popmenulist)
        self.popmenu = pop_menus = makemenu.makepopmenu(self, pop_menus, ShellWindow.imagelist)
    
        self.PopupMenu(self.popmenu, event.GetPosition())
    
    def OnPopupEdit(self, event):
        eid = event.GetId()
        if eid == self.IDPM_CUT:
            self.Cut()
        elif eid == self.IDPM_COPY:
            self.Copy()
        elif eid == self.IDPM_COPY_CLEAR:
            super(ShellWindow, self).Copy()
        elif eid == self.IDPM_PASTE:
            self.Paste()
        elif eid == self.IDPM_PASTE_RUN:
            self.PasteAndRun()
        elif eid == self.IDPM_SELECTALL:
            self.SelectAll()
        elif eid == self.IDPM_UNDO:
            self.Undo()
        elif eid == self.IDPM_REDO:
            self.Redo()
    
    def _OnUpdateUI(self, event):
        eid = event.GetId()
        if eid == self.IDPM_CUT:
            event.Enable(not self.GetReadOnly() and bool(self.GetSelectedText()))
        elif eid in (self.IDPM_COPY, self.IDPM_COPY_CLEAR):
            event.Enable(bool(self.GetSelectedText()))
        elif eid in (self.IDPM_PASTE, self.IDPM_PASTE_RUN):
            event.Enable(not self.GetReadOnly() and bool(self.CanPaste()))
        elif eid == self.IDPM_UNDO:
            event.Enable(bool(self.CanUndo()))
        elif eid == self.IDPM_REDO:
            event.Enable(bool(self.CanRedo()))
    
    def OnClearShell(self, event):
        self.clear()
        self.prompt()
    
    def OnKillFocus(self, event):
        if self.AutoCompActive():
            self.AutoCompCancel()
        if self.CallTipActive():
            self.CallTipCancel()
        event.Skip()

    def canClose(self):
        return True

    def write(self, text):
        """Display text in the shell.

        Replace line endings with OS-specific endings."""
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
        text = self.fixLineEndings(text)
        self.AddText(text)
        self.EnsureCaretVisible()
        
    def Copy(self):
        self.CopyWithPrompts()
        
    def OnKeyDown(self, event):
        key = event.GetKeyCode()
        # If the auto-complete window is up let it do its thing.
        if self.AutoCompActive():
            event.Skip()
            return
        
        # Prevent modification of previously submitted
        # commands/responses.
        controlDown = event.ControlDown()
        altDown = event.AltDown()
        shiftDown = event.ShiftDown()
        currpos = self.GetCurrentPos()
        endpos = self.GetTextLength()
        selecting = self.GetSelectionStart() != self.GetSelectionEnd()
        
        # If the user presses CTRL-R, then restart the shell.
        if controlDown and not altDown and key == ord('R'):
            self.OnRestartShell(None)
        
        if not controlDown and altDown and not shiftDown and key in [wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER]:
            if self.CallTipActive():
                self.CallTipCancel()
            if currpos == endpos:
                self.processLine()
            else:
                self.insertLineBreak()
        else:
            super(ShellWindow, self).OnKeyDown(event)
            
    def OnRestartShell(self, event):
        'Replace the interpreter, "in place"'
        self.SetSelection(self.GetCurrentPos(), self.GetCurrentPos())
        self.Execute('## --- RESTARTING SHELL ---\n')
        self.interp = NEInterpreter(locals = None,
                                    rawin = self.raw_input,
                                    stdin = self.interp.stdin,
                                    stdout = self.interp.stdout,
                                    stderr = self.interp.stderr)
        self.setLocalShell()

class NEInterpreter(Interpreter):
    def push(self, command):
        """Send command to the interpreter to be executed.

        Because this may be called recursively, we append a new list
        onto the commandBuffer list and then append commands into
        that.  If the passed in command is part of a multi-line
        command we keep appending the pieces to the last list in
        commandBuffer until we have a complete command. If not, we
        delete that last list."""

        if isinstance(command, types.UnicodeType):
            command = command.encode(common.defaultencoding)
        if not self.more:
            try: del self.commandBuffer[-1]
            except IndexError: pass
        if not self.more: self.commandBuffer.append([])
        self.commandBuffer[-1].append(command)
        source = os.linesep.join(self.commandBuffer[-1])
        more = self.more = self.runsource(source)
        dispatcher.send(signal='Interpreter.push', sender=self,
                        command=command, more=more, source=source)
        return more
