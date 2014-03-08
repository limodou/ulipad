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
#   $Id: MessageWindow.py 1817 2007-01-10 10:02:56Z limodou $

__doc__ = 'message window'

import wx
import locale
from modules import Mixin
from modules import common
from modules import makemenu

class MessageWindow(wx.stc.StyledTextCtrl, Mixin.Mixin):
    __mixinname__ = 'messagewindow'
    popmenulist = [(None, #parent menu id
        [
            (100, 'IDPM_UNDO', tr('Undo') + '\tCtrl+Z', wx.ITEM_NORMAL, 'OnPopupEdit', tr('Reverse previous editing operation')),
            (110, 'IDPM_REDO', tr('Redo') + '\tCtrl+Y', wx.ITEM_NORMAL, 'OnPopupEdit', tr('Reverse previous undo operation')),
            (120, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (130, 'IDPM_CUT', tr('Cut') + '\tCtrl+X', wx.ITEM_NORMAL, 'OnPopupEdit', tr('Deletes text from the document and moves it to the clipboard')),
            (140, 'IDPM_COPY', tr('Copy') + '\tCtrl+C', wx.ITEM_NORMAL, 'OnPopupEdit', tr('Copies text from the document to the clipboard')),
            (150, 'IDPM_PASTE', tr('Paste') + '\tCtrl+V', wx.ITEM_NORMAL, 'OnPopupEdit', tr('Pastes text from the clipboard into the document')),
            (160, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (170, 'IDPM_SELECTALL', tr('Select All') + '\tCtrl+A', wx.ITEM_NORMAL, 'OnPopupEdit', tr('Selects all text.')),
            (175, 'IDPM_CLEAR', tr('Clear') + '\tShift+F5', wx.ITEM_NORMAL, 'OnClear', tr('Clear all the text.')),
            (180, 'IDPM_WRAP', tr('Wrap Text'), wx.ITEM_CHECK, 'OnWrap', tr('Wrap text.')),
            (185, 'IDPM_AUTO_CLEAR', tr('Auto Clear on Running Program'), wx.ITEM_CHECK, 'OnAutoClaer', tr('Auto clear text on run program.')),
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

        wx.stc.StyledTextCtrl.__init__(self, parent, -1)
        self.parent = parent
        self.mainframe = mainframe
        self.SetMarginWidth(0, 0)
        self.SetMarginWidth(1, 0)
        self.SetMarginWidth(2, 0)

        #add default font settings in config.ini
        x = common.get_config_file_obj()
        font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        fontname = x.default.get('message_font', font.GetFaceName())
        fontsize = x.default.get('message_fontsize', 10)
        #todo fontsize maybe changed for mac
        if wx.Platform == '__WXMAC__':
            fontsize = 13
        #add chinese simsong support, because I like this font
        if not x.default.has_key('message_font') and locale.getdefaultlocale()[0] == 'zh_CN':
            fontname = u'宋体'
        self.defaultfaces = {
            'name':fontname,
            'size':fontsize,
        }

        self.StyleSetSpec(wx.stc.STC_STYLE_DEFAULT, "face:%(name)s,size:%(size)d" % self.defaultfaces)
        self.StyleClearAll()
        
        self.SetScrollWidth(1)
        self.maxline = 'WWWW'

        #disable popup
        self.UsePopUp(0)

        for key in MessageWindow.imagelist.keys():
            f = MessageWindow.imagelist[key]
            MessageWindow.imagelist[key] = common.getpngimage(f)

        self.popmenu = makemenu.makepopmenu(self, self.popmenulist, self.imagelist)

        wx.stc.EVT_STC_MODIFIED(self, self.GetId(), self.OnModified)
        wx.EVT_RIGHT_DOWN(self, self.OnPopUp)

        self.init_update_ui()

#        self.SetCaretForeground(')
        if x.default.has_key('message_caretlineback'):
            self.SetCaretLineBack(x.default.message_caretlineback)
        else:
            self.SetCaretLineBack('#FF8000')
        self.SetCaretLineVisible(True)
        if self.mainframe.pref.message_wrap:
            self.SetWrapMode(wx.stc.STC_WRAP_WORD)
        else:
            self.SetWrapMode(wx.stc.STC_WRAP_NONE)
        self.SetScrollWidth(5000)

        self.callplugin('init', self)

    def init_update_ui(self):
        x, menu = self.popmenulist[0]
        for v in menu:
            _id = v[1]
            if _id:
                wx.EVT_UPDATE_UI(self, getattr(self, _id), self.OnUpdateUI)
                
    def SetText(self, text):
        ro = self.GetReadOnly()
        self.SetReadOnly(0)
        wx.stc.StyledTextCtrl.SetText(self, text)
        self.SetReadOnly(ro)

    def SetSelectedText(self, text):
        ro = self.GetReadOnly()
        self.SetReadOnly(0)
        self.SetTargetStart(self.GetSelectionStart())
        self.SetTargetEnd(self.GetSelectionEnd())
        self.ReplaceTarget(text)
        self.SetReadOnly(ro)

    def setWidth(self, text=''):
        if not text:
            text = self.maxline
        if self.GetWrapMode() == wx.stc.STC_WRAP_NONE:
            ll = self.TextWidth(wx.stc.STC_STYLE_DEFAULT, "W")*4
            line = text.expandtabs(self.GetTabWidth())
            current_width = self.GetScrollWidth()
            width = self.TextWidth(wx.stc.STC_STYLE_DEFAULT, line)
            if width>current_width:
                self.maxline = line
                self.SetScrollWidth(width + ll)

    def OnModified(self, event):
        self.setWidth(self.GetCurLine()[0])

    def canClose(self):
        return True

    def OnPopUp(self, event):
        other_menus = []
        if self.popmenu:
            self.popmenu.Destroy()
            self.popmenu = None
        self.callplugin('other_popup_menu', self, other_menus)
        import copy
        if other_menus:
            pop_menus = copy.deepcopy(self.popmenulist + other_menus)
        else:
            pop_menus = copy.deepcopy(self.popmenulist)
        self.popmenu = pop_menus = makemenu.makepopmenu(self, pop_menus, MessageWindow.imagelist)

        self.PopupMenu(self.popmenu, event.GetPosition())

    def OnPopupEdit(self, event):
        eid = event.GetId()
        if eid == self.IDPM_CUT:
            self.Cut()
        elif eid == self.IDPM_COPY:
            self.Copy()
        elif eid == self.IDPM_PASTE:
            self.Paste()
        elif eid == self.IDPM_SELECTALL:
            self.SelectAll()
        elif eid == self.IDPM_UNDO:
            self.Undo()
        elif eid == self.IDPM_REDO:
            self.Redo()

    def OnUpdateUI(self, event):
        eid = event.GetId()
        if eid == self.IDPM_CUT:
            event.Enable(not self.GetReadOnly() and bool(self.GetSelectedText()))
        elif eid == self.IDPM_COPY:
            event.Enable(bool(self.GetSelectedText()))
        elif eid == self.IDPM_PASTE:
            event.Enable(not self.GetReadOnly() and bool(self.CanPaste()))
        elif eid == self.IDPM_UNDO:
            event.Enable(bool(self.CanUndo()))
        elif eid == self.IDPM_REDO:
            event.Enable(bool(self.CanRedo()))
        elif eid == self.IDPM_WRAP:
            mode = self.GetWrapMode()
            if mode == wx.stc.STC_WRAP_NONE:
                event.Check(False)
            else:
                event.Check(True)
        elif eid == self.IDPM_AUTO_CLEAR:
            event.Check(self.mainframe.pref.clear_message)

    def OnWrap(self, event):
        mode = self.GetWrapMode()
        if mode == wx.stc.STC_WRAP_NONE:
            self.SetWrapMode(wx.stc.STC_WRAP_WORD)
            self.mainframe.pref.message_wrap = True
        else:
            self.SetWrapMode(wx.stc.STC_WRAP_NONE)
            self.mainframe.pref.message_wrap = False

    def OnClear(self, event):
        self.SetText('')
        
    def OnAutoClaer(self, event):
        self.mainframe.pref.clear_message = not self.mainframe.pref.clear_message
        self.mainframe.pref.save()
        
