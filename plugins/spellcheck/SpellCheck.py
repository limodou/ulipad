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
#   $Id$

import locale
import wx
import re
import enchant
from enchant.checker import SpellChecker
from modules import Globals
from modules import common
import modules.meide as ui

class SpellCheck(wx.Panel):
    def __init__(self, parent):
        self.parent = parent
        wx.Panel.__init__(self, parent, -1)
        
        self.pref = Globals.pref

        self.sizer = sizer = ui.VBox(padding=0, namebinding='widget').create(self).auto_layout()
        h = sizer.add(ui.HBox)
        h.add(ui.Label(tr("Replace with") + ':'))
        h.add(ui.Text('', size=(150, -1)), name='text')
        h.add(ui.Button(tr('Start')), name='btnRun').bind('click', self.OnRun)
        h.add(ui.Button(tr('Replace')), name='btnReplace').bind('click', self.OnReplace)
        h.add(ui.Button(tr('Replace All')), name='btnReplaceAll').bind('click', self.OnReplaceAll)
        h.add(ui.Button(tr('Ignore')), name='btnIgnore').bind('click', self.OnIgnore)
        h.add(ui.Button(tr('Ignore All')), name='btnIgnoreAll').bind('click', self.OnIgnoreAll)
        h.add(ui.Button(tr('Add')), name='btnAdd').bind('click', self.OnAdd)

        h = sizer.add(ui.HBox, proportion=1)
        h.add(ui.Label(tr("Suggest") + ':'))
        h.add(ui.ListBox(size=(250, -1)), name='list').binds(
                (wx.EVT_LISTBOX, self._OnReplSelect),
                (wx.EVT_LISTBOX_DCLICK, self.OnReplace),
            )
        h.add(ui.Label(tr("Available Dict") + ':'))
        h.add(ui.ListBox(size=(100, -1), choices=enchant.list_languages()), name='dict_list').bind(
            wx.EVT_LISTBOX, self.OnDictSelect
            )

        sizer.auto_fit(0)

        self.init()

        self._DisableButtons()

    def init(self):
        defLoc = locale.getdefaultlocale()[0]
        if self.pref.default_spellcheck_dict:
            defLoc = self.pref.default_spellcheck_dict
            
        index = self.dict_list.FindString(defLoc)
        if index > -1:
            self.dict_list.SetSelection(index)
        else:
            defLoc = 'en_US'
            
        self.pref.default_spellcheck_dict = defLoc
        self.pref.save()
        
        #todo add multi dict support
        self.chkr = SpellChecker(defLoc)

        self.mainframe = Globals.mainframe
        self._buttonsEnabled = True
        self.running = False

    def OnRun(self, event):
        if self.running:
            self.running = False
            self._DisableButtons()
        else:
            self.running = True
            self.document = self.mainframe.document
            if self.document.edittype != 'edit':
                common.showerror(self, tr("This document can't be spell checked"))
                return
            self.begin_line = 0
            self.begin_pos = 0
            self.last_line_pos = 0
            self.last_col = 0
            self.ignore_list = []
            self.new = True
            self._Advance()

    def _Advance(self):
        """Advance to the next error.
        This method advances the SpellChecker to the next error, if
        any.  It then displays the error and some surrounding context,
        and well as listing the suggested replacements.
        """
        # Advance to next error, disable if not available
        while 1:
            try:
                if self.new:
                    self.begin_pos = self.document.PositionFromLine(self.begin_line)
                    line = self.document.getLineText(self.begin_line)
                    line_len = self.document.GetLineEndPosition(self.begin_line) - self.begin_pos
                    new = False
                if self.last_line_pos < line_len:
                    self.chkr.set_text(line[self.last_col:])
                self.chkr.next()
#                while self.chkr.word in self.ignore_list:
#                    self.chkr.next()
#                    pass
                self.last_col += self.chkr.wordpos
                self.last_line_pos = len(line[:self.last_col].encode('utf-8'))
                break
            except StopIteration:
                if self.begin_line < self.document.GetLineCount():
                    self.begin_line += 1
                    self.last_line_pos = 0
                    self.last_col = 0
                    self.new = True
                else:
                    self._DisableButtons()
                    self.list.Clear()
                    self.text.SetValue("")
                    common.note(tr('No more error found'))
                    return
        self._EnableButtons()
        self.document.SetSelectionStart(self.begin_pos + self.last_line_pos)
        self.document.SetSelectionEnd(self.begin_pos + self.last_line_pos + len(self.chkr.word.encode('utf-8')))
        self.document.EnsureCaretVisible()

        suggs = self.chkr.suggest()
        self.list.Clear()
        for s in suggs:
            self.list.Append(s)
        if len(suggs) > 0:
            self.text.SetValue(suggs[0])
        else:
            self.text.SetValue("")

    def OnIgnore(self, evnt=None):
        """Callback for the "ignore" button.
        This simply advances to the next error.
        """
        self.last_col += len(self.chkr.word)
        self._Advance()

    def OnIgnoreAll(self, evnt=None):
        """Callback for the "ignore all" button."""
        self.chkr.ignore_always()
#        self.ignore_list.append(self.chkr.word)
#        self._Advance()
        self.OnIgnore()

    def OnReplace(self, evnt=None):
        """Callback for the "replace" button."""
        repl = self._GetRepl()
        self.document.ReplaceSelection(repl)
        self.document.EnsureCaretVisible()
        self.last_col += len(repl.encode('utf-8'))
        self._Advance()

    def OnReplaceAll(self, evnt=None):
        """Callback for the "replace all" button."""
        repl = self._GetRepl()
        status = self.document.save_state()
        content = self.document.getRawText()
        text = content[self.begin_pos + self.last_line_pos:]
        r = re.compile(r'\b%s\b' % self.chkr.word.encode('utf-8'))
        text = content[:self.begin_pos + self.last_line_pos] + r.sub(repl.encode('utf-8'), text)
        self.document.SetText(unicode(text, 'utf-8'))
        self.document.restore_state(status)
        self.last_col += len(repl)

#        self.chkr.replace_always(repl)
        self._Advance()

    def _OnReplSelect(self,evnt=None):
        """Callback when a new replacement option is selected."""
        sel = self.list.GetSelection()
        if sel == -1:
            return
        opt = self.list.GetString(sel)
        self.text.SetValue(opt)

    def OnDictSelect(self, event=None):
        sel = self.dict_list.GetSelection()
        if sel == -1:
            return
        opt = self.dict_list.GetString(sel)
        self.chkr = SpellChecker(str(opt))
        
        self.pref.default_spellcheck_dict = str(opt)
        self.pref.save()

    def _GetRepl(self):
        """Get the chosen replacement string."""
        repl = self.text.GetValue()
        # Coercion now done automatically in SpellChecker class
        #repl = self._checker.coerce_string(repl)
        return repl

    def _EnableButtons(self):
        """Enable the checking-related buttons"""
        if self._buttonsEnabled:
            return
#        self.btnAdd.Enable(True)
        self.btnIgnore.Enable(True)
        self.btnIgnoreAll.Enable(True)
        self.btnReplace.Enable(True)
        self.btnReplaceAll.Enable(True)
        self.btnAdd.Enable(True)
        self.list.Enable()
        self.dict_list.Disable()
        self.btnRun.SetLabel(tr("Stop"))
        self._buttonsEnabled = True

    def _DisableButtons(self):
        """Disable the checking-related buttons"""
        if not self._buttonsEnabled:
            return
#        self.btnAdd.Disable()
        self.btnIgnore.Disable()
        self.btnIgnoreAll.Disable()
        self.btnReplace.Disable()
        self.btnReplaceAll.Disable()
        self.btnAdd.Disable()
        self.list.Disable()
        self.dict_list.Enable()
        self.btnRun.SetLabel(tr("Start"))
        self._buttonsEnabled = False

    def OnAdd(self, event=None):
        """
        Callback for the "add" button.
        """
        self.chkr.add()
        self._Advance()