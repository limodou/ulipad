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

from modules import Mixin
import wx
from modules import common
from modules.Debug import error

def other_popup_menu(editor, projectname, menus):
    if editor.languagename == 'xml' and 'docbook' in common.getProjectName(editor.filename):
        menus.extend([(None, #parent menu id
            [
                (50, 'IDPM_DOCBOOK_PROJECT', 'DocBook', wx.ITEM_NORMAL, '', ''),
                (51, '', '-', wx.ITEM_SEPARATOR, None, ''),
            ]),
            ('IDPM_DOCBOOK_PROJECT',
            [
                (100, 'IDPM_DOCBOOK_PROJECT_ENCLOSE', tr('Add/Enclose With DocBook Element...'), wx.ITEM_NORMAL, 'OnDocbookProjectFunc', tr('Add or enclose selected text with docbook element.')),
            ]),
        ])
Mixin.setPlugin('editor', 'other_popup_menu', other_popup_menu)

def OnDocbookProjectFunc(win, event):
    _id = event.GetId()
    try:
        if _id == win.IDPM_DOCBOOK_PROJECT_ENCLOSE:
            OnDocbookEnclose(win)
    except:
        error.traceback()
        common.showerror(win, tr("There is some wrong as executing the menu."))
Mixin.setMixin('editor', 'OnDocbookProjectFunc', OnDocbookProjectFunc)

def OnDocbookEnclose(editor):
    #find the docbook.acp file
    docbookini = common.getConfigPathFile('docbook_xml.ini')
    from modules import dict4ini
    x = dict4ini.DictIni(docbookini)
    taglist = x.default.taglist
    taglist.sort()
    #popup a selection win
    if taglist:
        from modules.EasyGuider import EasyDialog
        dialog = [
            ('single', 'tagname', taglist[0], tr('Select a tag:'), taglist),
        ]
        dlg = EasyDialog.EasyDialog(editor, tr('Select a DocBook Element Name'), dialog)
        values = None
        if dlg.ShowModal() == wx.ID_OK:
            values = dlg.GetValue()
        dlg.Destroy()
        if values:
            tagname = values['tagname']
            text = editor.GetSelectedText()
            editor.BeginUndoAction()
            if text:
                editor.ReplaceSelection('')
            if x.tag_values.has_key(tagname):
                settext(editor, [x.tag_values[tagname]])
            else:
                editor.AddText('<%s>%s</%s>' % (tagname, text, tagname))
                pos = editor.GetCurrentPos() - len(values['tagname']) - 3
                editor.GotoPos(pos)
            editor.EndUndoAction()
    else:
        common.showerror(editor, tr("There are not tags defined in conf/docbook_xml.ini."))

def settext(win, text):
    cur_pos = -1
    for t in text:
        pos = t.find('!^')
        if pos > -1:
            t = t.replace('!^', '')
            cur_pos = win.GetCurrentPos() + pos
        if t == r'\n':
            if win.pref.autoindent:
                line = win.GetCurrentLine()
                txt = win.GetTextRange(win.PositionFromLine(line), win.GetCurrentPos())
                if txt.strip() == '':
                    win.AddText(win.getEOLChar() + txt)
                else:
                    n = win.GetLineIndentation(line) / win.GetTabWidth()
                    win.AddText(win.getEOLChar() + win.getIndentChar() * n)
            else:
                win.AddText(win.getEOLChar())
        elif t == r'\t':
            win.CmdKeyExecute(wx.stc.STC_CMD_TAB)
        else:
            win.AddText(t)
        if cur_pos > -1:
            win.GotoPos(cur_pos)
