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
from modules import common
from modules import Globals
from modules import meide as ui

def getRawText(string):
    if wx.USE_UNICODE:
        s = string.encode('utf-8')
        return s
    else:
        return string

class Finder:
    def __init__(self):
        self.findtext = ''
        self.regular = False
        self.rewind = True
        self.matchcase = False
        self.wholeword = False
        self.inselection = False
        self.direction = 0
        self.replacetext = ''

    def getFlags(self):
        flags = 0
        if self.wholeword:
            flags |= wx.stc.STC_FIND_WHOLEWORD
        if self.matchcase:
            flags |= wx.stc.STC_FIND_MATCHCASE
        if self.regular:
            flags |= wx.stc.STC_FIND_REGEXP

        return flags

    def setWindow(self, win):
        self.win = win

    def find(self, direction=0):
        if direction == 0:      #forwards
            r = self.findNext()
        else:
            r = self.findPrev()

        if r:
            self.setSelection(*r)

    def findNext(self):
        length = len(getRawText(self.findtext))
        if length == 0:
            return None
        if self.regular:
            return self.findReNext()
        start = self.win.GetCurrentPos()
        end = self.win.GetLength()
        pos = self.win.FindText(start, end, self.findtext, self.getFlags())
        if pos == -1:   #not found
            if self.rewind:
                pos = self.win.FindText(0, start, self.findtext, self.getFlags())
            if pos == -1:
                common.note(tr("Can't find the text."))
                return None

        return (pos, pos + length)

    def findPrev(self):
        length = len(getRawText(self.findtext))
        if length == 0:
            return None
        start = self.win.GetCurrentPos()
        text = self.win.GetSelectedText()
        if self.matchcase:
            if text == self.findtext:
                start -= len(getRawText(text))+1
                start = max ([start, 0])
        else:
            if text.lower() == self.findtext.lower():
                start -= len(getRawText(text))+1
                start = max ([start, 0])
        pos = self.win.FindText(start, 0, self.findtext, self.getFlags())
        if pos == -1:   #not found
            if self.rewind:
                pos = self.win.FindText(self.win.GetLength(), start, self.findtext, self.getFlags())
            if pos == -1:
                common.note(tr("Can't find the text."))
                return None

        return (pos, pos + length)

    def findReNext(self):
        length = len(getRawText(self.findtext))
        if length == 0:
            return None

        start = self.win.GetCurrentPos()
        end = self.win.GetLength()

        result = self.regularSearch(start, end)
        if result == None:
            if self.rewind:
                result = self.regularSearch(0, start)
            if result == None:
                common.note(tr("Can't find the text."))
                return None

        return result

    def setSelection(self, start, end):
        self.win.GotoPos(start)
        self.win.SetSelectionStart(start)
        self.win.SetSelectionEnd(end)
        self.win.EnsureCaretVisible()
        self.win.EnsureVisible(self.win.GetCurrentLine())
        

    def regularSearch(self, start, end):
        case = 0
        if not self.matchcase:
            case = re.IGNORECASE
        if self.wholeword:
            ftext = r'\b'+self.findtext+r'\b'
        else:
            ftext = self.findtext
        re_search = re.compile(getRawText(ftext), case | re.MULTILINE)
        matchedtext = re_search.search(self.win.getRawText(), start, end)
        if matchedtext == None:
            return None
        else:
            return matchedtext.span()

    def replace(self):
        text = self.win.GetSelectedText()
        length = len(text)
        if length > 0:
            if self.regular:
                r = self.regularSearch(self.win.GetSelectionStart(), self.win.GetSelectionEnd())
                if r:
                    b, e = r
                    if (e - b) == length:
                        self.win.BeginUndoAction()
                        self.win.ReplaceSelection(self.regularReplace(text))
                        self.win.EndUndoAction()
            else:
                if self.matchcase and (text == self.findtext):
                    self.win.BeginUndoAction()
                    self.win.ReplaceSelection(self.replacetext)
                    self.win.EndUndoAction()
                if (not self.matchcase) and (text.lower() == self.findtext.lower()):
                    self.win.BeginUndoAction()
                    self.win.ReplaceSelection(self.replacetext)
                    self.win.EndUndoAction()

        self.find(self.direction)

    def replaceAll(self, section):
        length = len(getRawText(self.findtext))
        if section == 0:    #whole document
            start = 0
            end = self.win.GetLength()
        else:
            start, end = self.win.GetSelection()

        if self.regular:
            r = self.regularSearch(start, end)
            if r:
                b, e = r
            else:
                b = -1
        else:
            b = self.win.FindText(start, end, self.findtext, self.getFlags())
        count = 0
        self.win.BeginUndoAction()
        while b != -1:
            count += 1
            if not self.regular:
                e = b + length
            self.win.SetTargetStart(b)
            self.win.SetTargetEnd(e)
            if self.regular:
                rtext = self.regularReplace(self.win.GetTextRange(b, e))
            else:
                rtext = self.replacetext
            self.win.ReplaceTarget(rtext)
            rt = getRawText(rtext)
            diff = len(rt) - (e-b)
            end += diff
            start = b + len(rt)
            if self.regular:
                r = self.regularSearch(start, end)
                if r:
                    b, e = r
                else:
                    b = -1
            else:
                b = self.win.FindText(start, end, self.findtext, self.getFlags())
        self.win.EndUndoAction()

        if count == 0:
            common.note(tr("Can't find the text."))
        else:
            common.note(tr("Totally replaced %d places.") % count)

    def regularReplace(self, text):
        return re.sub(self.findtext, self.replacetext, text)

    def count(self, section):
        length = len(getRawText(self.findtext))
        if section == 0:    #whole document
            start = 0
            end = self.win.GetLength()
        else:
            start, end = self.win.GetSelection()

        if self.regular:
            r = self.regularSearch(start, end)
            if r:
                b, e = r
            else:
                b = -1
        else:
            b = self.win.FindText(start, end, self.findtext, self.getFlags())
        count = 0
        while b != -1 and start<end:
            count += 1
            if not self.regular:
                start = b + length
            else:
                start = e
            if self.regular:
                r = self.regularSearch(start, end)
                if r:
                    b, e = r
                else:
                    b = -1
            else:
                b = self.win.FindText(start, end, self.findtext, self.getFlags())
        return count

class FindPanel(wx.Panel):
    def __init__(self, parent, name, replace=False, *args, **kwargs):
        self.parent = parent
        self.name = name
        wx.Panel.__init__(self, parent, -1, *args, **kwargs)

        self.pref = Globals.pref
        self._create(replace)

    def _create(self, replace):
        from modules.wxctrl import FlatButtons

        self.sizer = sizer = ui.HBox(padding=0, namebinding='widget').create(self).auto_layout()

        box1 = ui.HBox(2)
        sizer.add(box1, proportion=0, flag=0)
        btn = FlatButtons.FlatBitmapButton(self, -1, common.getpngimage('images/closewin.gif'))
        btn.SetToolTip(wx.ToolTip(tr("Close")))
        box1.add(btn).bind('click', self.OnClose)
        self.btnToggleReplace = btn = FlatButtons.FlatBitmapButton(self, -1, common.getpngimage('images/replace.gif'))
        btn.SetToolTip(wx.ToolTip(tr("Show Replace Pane")))
        box1.add(btn).bind('click', self.OnOpenReplace)

        box2 = ui.VBox(0)
        sizer.add(box2, name='box2')

        box = ui.HBox(2)
        box2.add(box)

        #add find widgets

        box.add(ui.ComboBox, name='findtext').bind('enter', self.OnNext1)\
            .bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        btn = FlatButtons.FlatBitmapButton(self, -1, common.getpngimage('images/next.gif'))
        btn.SetToolTip(wx.ToolTip(tr("Next")))
        box.add(btn, name='btn_next').bind('click', self.OnNext)
        btn = FlatButtons.FlatBitmapButton(self, -1, common.getpngimage('images/prev.gif'))
        btn.SetToolTip(wx.ToolTip(tr("Prev")))
        box.add(btn).bind('click', self.OnPrev)
        box.add(ui.Check(False, tr("Match case")), name="chkCase")
        box.add(ui.Check(False, tr("Whole word")), name="chkWhole")
        box.add(ui.Check(False, tr("Regular expression")), name="chkRe")
        box.add(ui.Check(False, tr("Wrap search")), name="chkWrap")

        #add replace widgets
        if replace:
            self._create_replace()
            self.btnToggleReplace.SetToolTip(wx.ToolTip(tr("Hide Replace Pane")))
            
        # last_controls tracks the control / controls that are last in
        # navigation.
        self.last_controls = []
        self._navigation_hack()
#        self.SetBackgroundColour('#FFFFE1')

    def _navigation_hack(self):
        'Provide a hack for keyboard navigation.'
        def fix_focus(event):
            self.findtext.SetFocus()
            event.Skip()

        # Unbind because _navigation_hack may be called again from reset.
        for ctrl in self.last_controls:
            ctrl.Unbind(wx.EVT_SET_FOCUS)
            ctrl.Unbind(wx.EVT_KILL_FOCUS)

        # The only time navigation is an issue is when the focus is on the last
        # control in the panel.
        if self.is_replace_show():
            self.last_controls = [self.rdoSelection, self.rdoWhole]
        else:
            self.last_controls = [self.chkWrap]

        # When the last control loses focus navigate accordingly.
        for ctrl in self.last_controls:
            ctrl.Bind(wx.EVT_KILL_FOCUS, lambda e: fix_focus(e))

    def _create_replace(self):
        if 'replace_sizer' not in self.sizer:
            box = ui.HBox(2)
            box2 = self.sizer.find('box2')
            box2.add(box, name='replace_sizer')

            box.add(ui.ComboBox, name='replacetext').bind('enter', self.OnReplace1)\
                .bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
            box.add(ui.Button(tr('Replace')), name='replace_btn').bind('click', self.OnReplace)
            box.add(ui.Button(tr('Replace all'))).bind('click', self.OnReplaceAll)
            box.add(ui.Button(tr('Count'))).bind('click', self.OnCount)
            box.add(ui.Radio(False, tr('Whole file'), style=wx.RB_GROUP), name='rdoWhole')
            box.add(ui.Radio(False, tr('Selected text')), name='rdoSelection')
            self.parent.sizer.layout()

    def is_replace_show(self):
        return ('replace_sizer' in self.sizer) and self.sizer.is_shown('replace_sizer')

    def reset(self, finder, replace=None):
        if replace:
            if 'replace_sizer' not in self.sizer:
                self._create_replace()
            elif not self.sizer.is_shown('replace_sizer'):
                self.sizer.show('replace_sizer')
                self.parent.sizer.layout()
        else:
            if self.sizer.is_shown('replace_sizer'):
                self.sizer.hide('replace_sizer')
                self.parent.sizer.layout()

        self.finder = finder
        self.findtext.Clear()
        text = self.finder.win.GetSelectedText()
        if (len(text) > 0) and (text.count(self.finder.win.getEOLChar()) == 0):
            self.findtext.SetValue(text)
            self.finder.findtext = text
        else:
            self.findtext.SetValue(self.finder.findtext)

        for s in self.pref.findtexts:
            self.findtext.Append(s)

        if self.is_replace_show():
            self._reset_replace()

        self.setValue()
        self.findtext.SetFocus()
        self._navigation_hack()

    re_end = re.compile(r'\r\n|\r|\n', re.DOTALL)
    def _reset_replace(self):
        self.replacetext.Clear()
        text = self.finder.win.GetSelectedText()
        if self.re_end.search(text) > 0:
            self.rdoWhole.SetValue(False)
            self.rdoSelection.SetValue(True)
        else:
            self.rdoWhole.SetValue(True)
            self.rdoSelection.SetValue(False)

        self.replacetext.SetValue(self.finder.replacetext)
        for s in self.pref.replacetexts:
            self.replacetext.Append(s)

    def OnClose(self, event):
        self.getValue()
        self.parent.sizer.remove(self.name)
        self.Destroy()
        wx.CallAfter(Globals.mainframe.document.SetFocus)

    def OnKeyDown(self, event):
        key = event.GetKeyCode()
        if key == wx.WXK_ESCAPE:
            self.OnClose(None)
        elif key == wx.WXK_TAB:
            # Tab is pressed, set the focus appropriately.  This handles the
            # key events from the combo controls.
            if event.GetEventObject() == self.findtext:
                if self.is_replace_show():
                    self.replacetext.SetFocus()
                else:
                    self.btn_next.SetFocus()
            elif event.GetEventObject() == self.replacetext:
                self.replace_btn.SetFocus()
        else:
            event.Skip()

    def _find(self, flag):
        self.getValue()
        if not self.finder.findtext:
            common.warn(tr("Target text can't be empty."))
            return
        self.addFindString(self.finder.findtext)
        self.finder.find(flag)

    def OnNext(self, event):
        self._find(0)
        wx.CallAfter(Globals.mainframe.document.SetFocus)

    def OnNext1(self, event):
        self._find(0)

    def OnPrev(self, event):
        self._find(1)
        wx.CallAfter(Globals.mainframe.document.SetFocus)

    def addFindString(self, text):
        if not text: return
        if text in self.pref.findtexts:
            self.pref.findtexts.remove(text)
            self.pref.findtexts.insert(0, text)
        else:
            self.pref.findtexts.insert(0, text)
        del self.pref.findtexts[self.pref.max_number:]

        self.pref.save()

        self.findtext.Clear()
        for s in self.pref.findtexts:
            self.findtext.Append(s)

        self.findtext.SetValue(text)
        self.findtext.SetMark(0, len(text))

    def OnOpenReplace(self, event=None):
        if 'replace_sizer' not in self.sizer:
            self._create_replace()
            self._reset_replace()
            self.btnToggleReplace.SetToolTip(wx.ToolTip(tr("Hide Replace Pane")))
        else:
            if self.sizer.is_shown('replace_sizer'):
                self.sizer.hide('replace_sizer')
                self.btnToggleReplace.SetToolTip(wx.ToolTip(tr("Show Replace Pane")))
            else:
                self.sizer.show('replace_sizer')
                self.btnToggleReplace.SetToolTip(wx.ToolTip(tr("Hide Replace Pane")))
            self.parent.sizer.layout()

    def getValue(self):
        self.finder.findtext = self.findtext.GetValue()
        self.finder.regular = self.chkRe.GetValue()
        self.finder.rewind = self.chkWrap.GetValue()
        self.finder.matchcase = self.chkCase.GetValue()
        self.finder.wholeword = self.chkWhole.GetValue()
        if self.is_replace_show():
            self.finder.replacetext = self.replacetext.GetValue()
#        self.finder.direction =

    def setValue(self):
        self.chkRe.SetValue(self.finder.regular)
        self.chkWrap.SetValue(self.finder.rewind)
        self.chkCase.SetValue(self.finder.matchcase)
        self.chkWhole.SetValue(self.finder.wholeword)
#        self.obj_ID_DIRECTION.SetSelection(self.finder.direction)
#        self.obj_ID_DIRECTION.Enable(not self.finder.regular)
#        self.chkWhole.Enable(not self.chkRe.GetValue())
        if self.is_replace_show():
            self.replacetext.SetValue(self.finder.replacetext)

    def addReplaceString(self, text):
        if not text: return
        if self.pref.replacetexts.count(text) > 0:
            self.pref.replacetexts.remove(text)
            self.pref.replacetexts.insert(0, text)
        else:
            self.pref.replacetexts.insert(0, text)
        del self.pref.replacetexts[self.pref.max_number:]

        self.pref.save()

        self.replacetext.Clear()
        for s in self.pref.replacetexts:
            self.replacetext.Append(s)

        self.replacetext.SetValue(text)
        self.replacetext.SetMark(0, len(text))

    def OnReplace1(self, event):
        self.getValue()
        if not self.finder.findtext:
            common.warn(tr("Target text can't be empty."))
            return
        self.addFindString(self.finder.findtext)
        self.addReplaceString(self.finder.replacetext)
        self.finder.replace()

    def OnReplace(self, event):
        self.OnReplace1(event)
        wx.CallAfter(Globals.mainframe.document.SetFocus)

    def OnReplaceAll(self, event):
        self.getValue()
        if not self.finder.findtext:
            common.warn(tr("Target text can't be empty."))
            return
        self.addFindString(self.finder.findtext)
        self.addReplaceString(self.finder.replacetext)
        self.finder.replaceAll(int(self.rdoSelection.GetValue()))
        wx.CallAfter(Globals.mainframe.document.SetFocus)

    def OnCount(self, event):
        self.getValue()
        if not self.finder.findtext:
            common.warn(tr("Target text can't be empty."))
            return
        self.addFindString(self.finder.findtext)
        count = self.finder.count(int(self.rdoSelection.GetValue()))
        if count == 0:
            common.note(tr("Can't find the text."))
        else:
            common.note(tr("Totally replaced %d places.") % count)
