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
#   $Id: mConvert.py 1897 2007-02-03 10:33:43Z limodou $

import wx
from modules import Mixin
from modules.Debug import error
from modules import common

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_EDIT',
        [
            (270, 'IDM_EDIT_CONVERT', tr('Convert'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDM_EDIT_CONVERT',
        [
            (100, 'IDM_EDIT_CONVERT_OUTPUTHTMLWINDOW', tr('Output To HTML Window'), wx.ITEM_RADIO, 'OnConvertOutput', tr('Outputs converted text in HTML window.')),
            (110, 'IDM_EDIT_CONVERT_OUTPUTMESSAGEWINDOW', tr('Output To Message Window'), wx.ITEM_RADIO, 'OnConvertOutput', tr('Outputs converted text in message window.')),
            (120, 'IDM_EDIT_CONVERT_REPLACEHERE', tr('Replace Selected Text'), wx.ITEM_RADIO, 'OnConvertOutput', tr('Replaces selected text with converted text.')),
            (130, '', '-', wx.ITEM_SEPARATOR, '', ''),
            (140, 'IDM_EDIT_CONVERT_DIRECT', tr('Output Directly To HTML Window'), wx.ITEM_NORMAL, 'OnConvertOutputDirectly', tr('Outputs directly the text in HTML window.')),
            (150, 'IDM_EDIT_CONVERT_REST2HTML', tr('reSt To HTML'), wx.ITEM_NORMAL, 'OnConvertRest2Html', tr('Converts reStructuredText source to HTML.')),
            (160, 'IDM_EDIT_CONVERT_PY2HTML', tr('Py To HTML'), wx.ITEM_NORMAL, 'OnConvertPy2Html', tr('Converts python source to HTML.')),
            (170, 'IDM_EDIT_CONVERT_TEXTILE2HTML', tr('Textile To HTML'), wx.ITEM_NORMAL, 'OnConvertTextile2Html', tr('Converts textile source to HTML.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_editor_menu(popmenulist):
    popmenulist.extend([ (None,
        [
            (240, 'IDPM_EDIT_CONVERT', tr('Convert'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDPM_EDIT_CONVERT',
        [
            (100, 'IDPM_EDIT_CONVERT_OUTPUTHTMLWINDOW', tr('Output To HTML Window'), wx.ITEM_RADIO, 'OnConvertOutput', tr('Outputs converted text in HTML window.')),
            (110, 'IDPM_EDIT_CONVERT_OUTPUTMESSAGEWINDOW', tr('Output To Message Window'), wx.ITEM_RADIO, 'OnConvertOutput', tr('Outputs converted text in message window.')),
            (120, 'IDPM_EDIT_CONVERT_REPLACEHERE', tr('Replace Selected Text'), wx.ITEM_RADIO, 'OnConvertOutput', tr('Replaces selected text with converted text.')),
            (130, '', '-', wx.ITEM_SEPARATOR, '', ''),
            (140, 'IDPM_EDIT_CONVERT_DIRECT', tr('Output Directly To HTML Window'), wx.ITEM_NORMAL, 'OnOutputDirectly', tr('Outputs directly the text in HTML window.')),
            (150, 'IDPM_EDIT_CONVERT_REST2HTML', tr('reSt To HTML'), wx.ITEM_NORMAL, 'OnRest2Html', tr('Converts reStructuredText source to HTML.')),
            (160, 'IDPM_EDIT_CONVERT_PY2HTML', tr('Py To HTML'), wx.ITEM_NORMAL, 'OnPy2Html', tr('Converts python source to HTML.')),
            (170, 'IDPM_EDIT_CONVERT_TEXTILE2HTML', tr('Textile To HTML'), wx.ITEM_NORMAL, 'OnTextile2Html', tr('Converts textile source to HTML.')),
        ]),
    ])
Mixin.setPlugin('editor', 'add_menu', add_editor_menu)


def OnConvertOutputDirectly(win, event):
    text = win.document.GetSelectedText()
    output_text(win, text, mode=0)
Mixin.setMixin('mainframe', 'OnConvertOutputDirectly', OnConvertOutputDirectly)

def OnOutputDirectly(win, event):
    win.mainframe.OnConvertOutputDirectly(event)
Mixin.setMixin('editor', 'OnOutputDirectly', OnOutputDirectly)

def OnConvertRest2Html(win, event):
    try:
        def html_fragment(input_string, source_path=None, destination_path=None,
                       input_encoding='unicode', doctitle=1, initial_header_level=1):
            from docutils import core

            overrides = {'input_encoding': input_encoding,
                         'doctitle_xform': doctitle,
                         'initial_header_level': initial_header_level}
            parts = core.publish_parts(
                source=input_string, source_path=source_path,
                destination_path=destination_path,
                writer_name='html', settings_overrides=overrides)
            fragment = parts['fragment']
            return fragment

        text = win.document.GetSelectedText()
        otext = html_fragment(text)
        output_text(win, otext)
    except Exception, msg:
        error.traceback()
        common.showerror(win, msg)
Mixin.setMixin('mainframe', 'OnConvertRest2Html', OnConvertRest2Html)

def OnRest2Html(win, event):
    win.mainframe.OnConvertRest2Html(event)
Mixin.setMixin('editor', 'OnRest2Html', OnRest2Html)

def OnConvertTextile2Html(win, event):
    try:
        import textile
    except:
        error.traceback()
        common.showmessage(win, tr("You should install textile module first!"))

    class MyTextiler(textile.Textiler):
        def process(self, head_offset=textile.HEAD_OFFSET):
            self.head_offset = head_offset

            # Process each block.
            self.blocks = self.split_text()

            text = []
            for [function, captures] in self.blocks:
                text.append(function(**captures))

            text = '\n\n'.join(text)

            # Add titles to footnotes.
            text = self.footnotes(text)

#           # Convert to desired output.
#           if encoding != 'unicode':
#               text = unicode(text, encoding)
#           if output != 'unicode':
#               text = text.encode(output, 'xmlcharrefreplace')

            return text
    try:
        text = win.document.GetSelectedText()
        t = MyTextiler(text)
        otext = t.process()

        output_text(win, otext)
    except Exception, msg:
        error.traceback()
        common.showerror(win, msg)
Mixin.setMixin('mainframe', 'OnConvertTextile2Html', OnConvertTextile2Html)

def OnTextile2Html(win, event):
    win.mainframe.OnConvertTextile2Html(event)
Mixin.setMixin('editor', 'OnTextile2Html', OnTextile2Html)

def OnConvertPy2Html(win, event):
    from modules import colourize

    text = win.document.GetSelectedText()
    otext = colourize.Parser(text).format()

    output_text(win, otext)
Mixin.setMixin('mainframe', 'OnConvertPy2Html', OnConvertPy2Html)

def OnPy2Html(win, event):
    win.mainframe.OnConvertPy2Html(event)
Mixin.setMixin('editor', 'OnPy2Html', OnPy2Html)

def OnConvertOutput(win, event):
    eid = event.GetId()
    if eid == win.IDM_EDIT_CONVERT_OUTPUTHTMLWINDOW:
        win.pref.converted_output = 0
    elif eid == win.IDM_EDIT_CONVERT_OUTPUTMESSAGEWINDOW:
        win.pref.converted_output = 1
    elif eid == win.IDM_EDIT_CONVERT_REPLACEHERE:
        win.pref.converted_output = 2
    win.pref.save()
Mixin.setMixin('mainframe', 'OnConvertOutput', OnConvertOutput)

def OnConvertOutput(win, event):
    eid = event.GetId()
    if eid == win.IDPM_EDIT_CONVERT_OUTPUTHTMLWINDOW:
        win.pref.converted_output = 0
    elif eid == win.IDPM_EDIT_CONVERT_OUTPUTMESSAGEWINDOW:
        win.pref.converted_output = 1
    elif eid == win.IDPM_EDIT_CONVERT_REPLACEHERE:
        win.pref.converted_output = 2
    win.pref.save()
Mixin.setMixin('editor', 'OnConvertOutput', OnConvertOutput)

def mainframe_init(win):
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_CONVERT_REST2HTML, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_CONVERT_PY2HTML, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_CONVERT_TEXTILE2HTML, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_CONVERT_OUTPUTHTMLWINDOW, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_CONVERT_DIRECT, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_CONVERT_OUTPUTMESSAGEWINDOW, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_CONVERT_REPLACEHERE, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'init', mainframe_init)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if hasattr(win, 'document') and win.document:
        if eid in [win.IDM_EDIT_CONVERT_DIRECT, win.IDM_EDIT_CONVERT_REST2HTML,
            win.IDM_EDIT_CONVERT_PY2HTML, win.IDM_EDIT_CONVERT_TEXTILE2HTML]:
            event.Enable(win.document.GetSelectedText and len(win.document.GetSelectedText()) > 0)
        elif eid == win.IDM_EDIT_CONVERT_OUTPUTHTMLWINDOW:
            event.Check(win.pref.converted_output == 0)
        elif eid == win.IDM_EDIT_CONVERT_OUTPUTMESSAGEWINDOW:
            event.Check(win.pref.converted_output == 1)
        elif eid == win.IDM_EDIT_CONVERT_REPLACEHERE:
            event.Check(win.pref.converted_output == 2)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def editor_init(win):
    wx.EVT_UPDATE_UI(win, win.IDPM_EDIT_CONVERT_REST2HTML, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDPM_EDIT_CONVERT_PY2HTML, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDPM_EDIT_CONVERT_TEXTILE2HTML, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDPM_EDIT_CONVERT_DIRECT, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDPM_EDIT_CONVERT_OUTPUTHTMLWINDOW, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDPM_EDIT_CONVERT_OUTPUTMESSAGEWINDOW, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDPM_EDIT_CONVERT_REPLACEHERE, win.OnUpdateUI)
Mixin.setPlugin('editor', 'init', editor_init)

def on_editor_updateui(win, event):
    eid = event.GetId()
    if eid in [win.IDPM_EDIT_CONVERT_DIRECT, win.IDPM_EDIT_CONVERT_REST2HTML,
        win.IDPM_EDIT_CONVERT_PY2HTML, win.IDPM_EDIT_CONVERT_TEXTILE2HTML]:
        event.Enable(len(win.GetSelectedText()) > 0)
    elif eid == win.IDPM_EDIT_CONVERT_OUTPUTHTMLWINDOW:
        event.Check(win.pref.converted_output == 0)
    elif eid == win.IDPM_EDIT_CONVERT_OUTPUTMESSAGEWINDOW:
        event.Check(win.pref.converted_output == 1)
    elif eid == win.IDPM_EDIT_CONVERT_REPLACEHERE:
        event.Check(win.pref.converted_output == 2)
Mixin.setPlugin('editor', 'on_update_ui', on_editor_updateui)

def pref_init(pref):
    pref.converted_output = 0
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('Document'), 150, 'choice', 'converted_output', tr('Choose where converted text is to be outputted:'), [tr('To HTML window'), tr('To message window'), tr('Replace selected text')]),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def output_text(mainframe, text, mode=-1):
    win = mainframe

    if mode == -1:
        mode = win.pref.converted_output

    if mode == 0:
        from HtmlPage import HtmlDialog

        ot = """<html>
<head>
   <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
</head>
<body>
%s
</body>
</html>
""" % text.encode('utf-8')

        HtmlDialog(win, tr('Html Convertion'), ot).ShowModal()
    elif mode == 1:
        win.createMessageWindow()
        win.panel.showPage(tr('Messages'))
        win.messagewindow.SetText(text)
    elif mode == 2:
        win.document.ReplaceSelection(text)
