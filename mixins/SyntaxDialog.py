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
#   $Id: SyntaxDialog.py 1892 2007-02-02 05:19:37Z limodou $

__doc__ = 'syntax preference setup dialog class'

import wx

class SyntaxDialog(wx.Dialog):
    def __init__(self, *args, **kwargs):
        wx.Dialog.__init__(self, *args, **kwargs)

    def init(self, mainframe, lexers, languagename):
        self.mainframe = mainframe
        self.lexers = lexers

        #init styledtextctrl
        pos = self.obj_ID_PREVIEW.GetPosition()
        size = self.obj_ID_PREVIEW.GetSize()
        self.obj_ID_PREVIEW.Destroy()
        self.obj_ID_PREVIEW = wx.stc.StyledTextCtrl(self, -1, pos=pos, size=size)
        self.obj_ID_PREVIEW.SetReadOnly(True)
        self.obj_ID_PREVIEW.SetMarginType(0, wx.stc.STC_MARGIN_NUMBER)
        self.obj_ID_PREVIEW.SetMarginWidth(0, 25)
        self.obj_ID_PREVIEW.SetUseTabs(False)
        self.obj_ID_PREVIEW.SetTabWidth(4)
        self.obj_ID_PREVIEW.languagename = ''
        wx.stc.EVT_STC_STYLENEEDED(self.obj_ID_PREVIEW, self.obj_ID_PREVIEW.GetId(), self.OnStyleNeeded)

        self.language = []
        self.oldlanguage =[]
        self.syntaxitems = []

        self.update = False

        self.langindex = 0
        for i, lexer in enumerate(self.lexers.items()):
            self.oldlanguage.append(lexer)
            newlexer = lexer.clone()
            newlexer.cur = 0
            self.language.append(newlexer)
            self.obj_ID_LANGUAGE.Append(newlexer.wildcharprompt)
            if newlexer.name == languagename:
                self.langindex = i

        self.obj_ID_FORE_VALUE.Enable(False)
        self.obj_ID_BACK_VALUE.Enable(False)

        self.obj_ID_OK.SetId(wx.ID_OK)
        self.obj_ID_CANCEL.SetId(wx.ID_CANCEL)

        e = wx.FontEnumerator()
        e.EnumerateFacenames()
        list = e.GetFacenames()
        list.sort()
        self.obj_ID_FACE.AppendItems(list)

        wx.EVT_CLOSE(self, self.OnClose)
        wx.EVT_COMBOBOX(self.obj_ID_LANGUAGE, self.ID_LANGUAGE, self.OnLanguageSelected)
        wx.EVT_COMBOBOX(self.obj_ID_FACE, self.ID_FACE, self.OnUpdate)
        wx.EVT_COMBOBOX(self.obj_ID_SIZE, self.ID_SIZE, self.OnUpdate)
        wx.EVT_BUTTON(self.obj_ID_OK, wx.ID_OK, self.OnOk)
        wx.EVT_BUTTON(self.obj_ID_CANCEL, wx.ID_CANCEL, self.OnCancel)
        wx.EVT_BUTTON(self.obj_ID_APPLY, self.ID_APPLY, self.OnApply)
        wx.EVT_LISTBOX(self.obj_ID_ITEMS, self.ID_ITEMS, self.OnItemSelected)
        wx.EVT_CHECKBOX(self.obj_ID_CHK_FACE, self.ID_CHK_FACE, self.OnChkFace)
        wx.EVT_CHECKBOX(self.obj_ID_CHK_SIZE, self.ID_CHK_SIZE, self.OnChkSize)
        wx.EVT_CHECKBOX(self.obj_ID_CHK_FORE, self.ID_CHK_FORE, self.OnChkFore)
        wx.EVT_CHECKBOX(self.obj_ID_CHK_BACK, self.ID_CHK_BACK, self.OnChkBack)
        wx.EVT_CHECKBOX(self.obj_ID_BOLD, self.ID_BOLD, self.OnUpdate)
        wx.EVT_CHECKBOX(self.obj_ID_ITALIC, self.ID_ITALIC, self.OnUpdate)
        wx.EVT_CHECKBOX(self.obj_ID_UNDERLINE, self.ID_UNDERLINE, self.OnUpdate)
        wx.EVT_BUTTON(self.obj_ID_FORE, self.ID_FORE, self.OnForeClick)
        wx.EVT_BUTTON(self.obj_ID_BACK, self.ID_BACK, self.OnBackClick)
        wx.EVT_TEXT(self.obj_ID_EXTENSIONS, self.ID_EXTENSIONS, self.OnExtensionsChange)
        wx.EVT_TEXT(self.obj_ID_FORE_VALUE, self.ID_FORE_VALUE, self.OnUpdate)
        wx.EVT_TEXT(self.obj_ID_BACK_VALUE, self.ID_BACK_VALUE, self.OnUpdate)
        wx.EVT_IDLE(self, self.OnIdle)

        self.obj_ID_LANGUAGE.SetSelection(self.langindex)
        self.reset()

    def OnLanguageSelected(self, event):
        self.reset()

    def OnItemSelected(self, event):
        self.setStyle()

    def OnOk(self, event):
        self.save()
        self.Destroy()
        event.Skip()

    def OnCancel(self, event):
        self.Destroy()
        event.Skip()

    def OnClose(self, event):
        self.Destroy()
        event.Skip()

    def OnApply(self, event):
        self.save()

    def OnForeClick(self, event):
        colordata = wx.ColourData()
        colordata.SetChooseFull(True)
        fore = self.obj_ID_FORE_VALUE.GetValue()
        if fore:
            colour = wx.Colour(*self.StrToRGB(fore))
            colordata.SetColour(colour)

        dlg = wx.ColourDialog(self, colordata)
        if dlg.ShowModal()== wx.ID_OK:
            color = dlg.GetColourData().GetColour()
            self.obj_ID_FORE_VALUE.SetValue(self.RGBToStr(color.Get()))
        dlg.Destroy()
        self.update = True

    def OnBackClick(self, event):
        colordata = wx.ColourData()
        colordata.SetChooseFull(True)
        back = self.obj_ID_BACK_VALUE.GetValue()
        if back:
            colour = wx.Colour(*self.StrToRGB(back))
            colordata.SetColour(colour)
            c = colordata.GetColour()

        dlg = wx.ColourDialog(self, colordata)
        if dlg.ShowModal()== wx.ID_OK:
            color = dlg.GetColourData().GetColour()
            self.obj_ID_BACK_VALUE.SetValue(self.RGBToStr(color.Get()))
        dlg.Destroy()
        self.update = True

    def OnExtensionsChange(self, event):
        self.curlang.wildchar = self.obj_ID_EXTENSIONS.GetValue()

    def OnUpdate(self, event):
        self.update = True
        event.Skip()

    def OnIdle(self, event):
        if self.update:
            self.getStyle()
        self.update = False

    def StrToRGB(self, string):
        if string:
            return int(string[1:3], 16), int(string[3:5], 16), int(string[5:7], 16)
        return 0, 0, 0

    def RGBToStr(self, rgb):
        return '#%02X%02X%02X' % rgb

    def save(self):
        for i, lexer in enumerate(self.language):
            lexer.copyto(self.oldlanguage[i])
            lexer.save()

        for document in self.mainframe.editctrl.getDocuments():
            for lexer in self.mainframe.lexers.items():
                if document.languagename == lexer.name:
                    lexer.colourize(document, force=True)
                    break

    def reset(self):
        self.curlang = self.language[self.obj_ID_LANGUAGE.GetSelection()]
        #set wildchar
        self.obj_ID_EXTENSIONS.SetValue(self.curlang.wildchar)

        #set syntax item
        items = self.curlang.getSyntaxItems()
        keys = self.curlang.getSyntaxNames()
        self.syntaxitems = []
        self.obj_ID_ITEMS.Clear()
        for key in keys:
            self.syntaxitems.append(key)
            self.obj_ID_ITEMS.Append(items[key].dispname)

        #set preview code
        p_code = 'empty'
        if self.curlang.preview_code:
            p_code = self.curlang.preview_code
        self.obj_ID_PREVIEW.SetReadOnly(False)
        self.obj_ID_PREVIEW.SetText(p_code)
        self.obj_ID_PREVIEW.SetReadOnly(True)
        self.curlang.colourize(self.obj_ID_PREVIEW)
        if p_code:
            maxlen = max(map(len, p_code.splitlines()))
        else:
            maxlen = 0
        width = self.obj_ID_PREVIEW.TextWidth(wx.stc.STC_STYLE_DEFAULT, "W")*(maxlen+4)
        self.obj_ID_PREVIEW.SetScrollWidth(width)

        self.obj_ID_ITEMS.SetSelection(self.curlang.cur)
        self.setStyle()

    def setStyle(self):
        style = self.getCurrentStyle()
        index = self.obj_ID_ITEMS.GetSelection()
        name = self.syntaxitems[index]

        if name in ('-caretfore', '-caretback', '-selback'):
            self.obj_ID_CHK_FACE.Enable(False)
            self.obj_ID_CHK_SIZE.Enable(False)
            self.obj_ID_BOLD.Enable(False)
            self.obj_ID_ITALIC.Enable(False)
            self.obj_ID_UNDERLINE.Enable(False)
            if name == '-caretfore':
                self.obj_ID_CHK_FORE.Enable(True)
                self.obj_ID_CHK_BACK.Enable(False)
            else:
                self.obj_ID_CHK_FORE.Enable(False)
                self.obj_ID_CHK_BACK.Enable(True)
        else:
            self.obj_ID_CHK_FACE.Enable(True)
            self.obj_ID_CHK_SIZE.Enable(True)
            self.obj_ID_BOLD.Enable(True)
            self.obj_ID_ITALIC.Enable(True)
            self.obj_ID_UNDERLINE.Enable(True)
            self.obj_ID_CHK_FORE.Enable(True)
            self.obj_ID_CHK_BACK.Enable(True)

        if style.bold:
            self.obj_ID_BOLD.SetValue(True)
        else:
            self.obj_ID_BOLD.SetValue(False)

        if style.italic:
            self.obj_ID_ITALIC.SetValue(True)
        else:
            self.obj_ID_ITALIC.SetValue(False)

        if style.underline:
            self.obj_ID_UNDERLINE.SetValue(True)
        else:
            self.obj_ID_UNDERLINE.SetValue(False)

        if style.face:
            self.obj_ID_CHK_FACE.SetValue(True)
            self.obj_ID_FACE.Enable(True)
        else:
            self.obj_ID_CHK_FACE.SetValue(False)
            self.obj_ID_FACE.Enable(False)
        self.obj_ID_FACE.SetValue(style.face)

        if style.size:
            self.obj_ID_CHK_SIZE.SetValue(True)
            self.obj_ID_SIZE.Enable(True)
        else:
            self.obj_ID_CHK_SIZE.SetValue(False)
            self.obj_ID_SIZE.Enable(False)
        self.obj_ID_SIZE.SetValue(style.size)

        if style.fore:
            self.obj_ID_CHK_FORE.SetValue(True)
            self.obj_ID_FORE.Enable(True)
            self.obj_ID_FORE_VALUE.Enable(True)
            self.obj_ID_FORE_VALUE.SetValue(style.fore)
        else:
            self.obj_ID_CHK_FORE.SetValue(False)
            self.obj_ID_FORE.Enable(False)
            self.obj_ID_FORE_VALUE.Enable(False)
            self.obj_ID_FORE_VALUE.SetValue('')

        if style.back:
            self.obj_ID_CHK_BACK.SetValue(True)
            self.obj_ID_BACK.Enable(True)
            self.obj_ID_BACK_VALUE.Enable(True)
            self.obj_ID_BACK_VALUE.SetValue(style.back)
        else:
            self.obj_ID_CHK_BACK.SetValue(False)
            self.obj_ID_BACK.Enable(False)
            self.obj_ID_BACK_VALUE.Enable(False)
            self.obj_ID_BACK_VALUE.SetValue('')

    def getStyle(self):
        style = self.getCurrentStyle()

        if self.obj_ID_CHK_FACE.GetValue():
            style.face = self.obj_ID_FACE.GetValue()
        else:
            style.face = ''
        if self.obj_ID_CHK_SIZE.GetValue():
            style.size = self.obj_ID_SIZE.GetValue()
        else:
            style.size = ''
        if self.obj_ID_CHK_FORE.GetValue():
            style.fore = self.obj_ID_FORE_VALUE.GetValue()
        else:
            style.fore = ''
        if self.obj_ID_CHK_BACK.GetValue():
            style.back = self.obj_ID_BACK_VALUE.GetValue()
        else:
            style.back = ''
        if self.obj_ID_BOLD.GetValue():
            style.bold = 'bold'
        else:
            style.bold = ''
        if self.obj_ID_ITALIC.GetValue():
            style.italic = 'italic'
        else:
            style.italic = ''
        if self.obj_ID_UNDERLINE.GetValue():
            style.underline = 'underline'
        else:
            style.underline = ''

        self.curlang.colourize(self.obj_ID_PREVIEW, True)

    def OnChkFace(self, event):
        self.obj_ID_FACE.Enable(self.obj_ID_CHK_FACE.GetValue())
        self.update = True

    def OnChkSize(self, event):
        self.obj_ID_SIZE.Enable(self.obj_ID_CHK_SIZE.GetValue())
        self.update = True

    def OnChkFore(self, event):
        self.obj_ID_FORE.Enable(self.obj_ID_CHK_FORE.GetValue())
        self.obj_ID_FORE_VALUE.Enable(self.obj_ID_CHK_FORE.GetValue())
        self.update = True

    def OnChkBack(self, event):
        self.obj_ID_BACK.Enable(self.obj_ID_CHK_BACK.GetValue())
        self.obj_ID_BACK_VALUE.Enable(self.obj_ID_CHK_BACK.GetValue())
        self.update = True

    def getCurrentStyle(self):
        self.cur = index = self.obj_ID_ITEMS.GetSelection()
        name = self.syntaxitems[index]
        style = self.curlang.getSyntaxItems()[name].style
        return style

    def OnStyleNeeded(self, event):
        if self.curlang.syntaxtype == wx.stc.STC_LEX_CONTAINER:
            self.curlang.styleneeded(self.obj_ID_PREVIEW, event.GetPosition())
