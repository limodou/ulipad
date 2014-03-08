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
#   $Id: mLineending.py 1805 2007-01-04 02:07:31Z limodou $

import wx
from modules import Mixin
from modules import common

eolmess = [tr(r"Unix mode (\n)"), tr(r"DOS/Windows mode (\r\n)"), tr(r"Mac mode (\r)")]

def beforeinit(win):
    win.lineendingsaremixed = False
    win.eolmode = win.pref.default_eol_mode
    win.eols = {0:wx.stc.STC_EOL_LF, 1:wx.stc.STC_EOL_CRLF, 2:wx.stc.STC_EOL_CR}
#    win.eolstr = {0:'Unix', 1:'Win', 2:'Mac'}
    win.eolstr = {0:r'\n', 1:r'\r\n', 2:r'\r'}
    win.eolstring = {0:'\n', 1:'\r\n', 2:'\r'}
    win.eolmess = eolmess
    win.SetEOLMode(win.eols[win.eolmode])
Mixin.setPlugin('editor', 'init', beforeinit)

def add_pref(preflist):
    preflist.extend([
        (tr('Document'), 140, 'choice', 'default_eol_mode', tr('Default line ending used in the document:'), eolmess)
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def pref_init(pref):
    if wx.Platform == '__WXMSW__':
        pref.default_eol_mode = 1
    else:
        pref.default_eol_mode = 0
Mixin.setPlugin('preference', 'init', pref_init)

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_DOCUMENT',
        [
            (120, 'IDM_DOCUMENT_EOL_CONVERT', tr('Convert Line Ending'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDM_DOCUMENT_EOL_CONVERT',
        [
            (100, 'IDM_DOCUMENT_EOL_CONVERT_PC', tr('Convert To Windows Format'), wx.ITEM_NORMAL, 'OnDocumentEolConvertWin', tr('Converts line ending to Windows format.')),
            (200, 'IDM_DOCUMENT_EOL_CONVERT_UNIX', tr('Convert To Unix Format'), wx.ITEM_NORMAL, 'OnDocumentEolConvertUnix', tr('Converts line ending to Unix format.')),
            (300, 'IDM_DOCUMENT_EOL_CONVERT_MAX', tr('Convert To Mac Format'), wx.ITEM_NORMAL, 'OnDocumentEolConvertMac', tr('Converts line ending to Mac format.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def setEOLMode(win, mode, convert=True):
    win.lineendingsaremixed = False
    win.eolmode = mode
    if convert:
        win.ConvertEOLs(win.eols[mode])
    win.SetEOLMode(win.eols[mode])
    common.set_line_ending(win.eolstr[mode])

def OnDocumentEolConvertWin(win, event):
    setEOLMode(win.document, 1)
Mixin.setMixin('mainframe', 'OnDocumentEolConvertWin', OnDocumentEolConvertWin)

def OnDocumentEolConvertUnix(win, event):
    setEOLMode(win.document, 0)
Mixin.setMixin('mainframe', 'OnDocumentEolConvertUnix', OnDocumentEolConvertUnix)

def OnDocumentEolConvertMac(win, event):
    setEOLMode(win.document, 2)
Mixin.setMixin('mainframe', 'OnDocumentEolConvertMac', OnDocumentEolConvertMac)

def check_mixed(text):
    lineendingsaremixed = False

    eollist = "".join(map(getEndOfLineCharacter, text))

    len_win = eollist.count('\r\n')
    len_unix = eollist.count('\n')
    len_mac = eollist.count('\r')
    eolmode = -1
    if len_mac > 0 and len_unix == 0:
        eolmode = 2
    elif len_win == len_unix == len_mac:
        eolmode = 1
    elif len_unix > 0 and len_win == 0 and len_mac == 0:
        eolmode = 0
    else:
        lineendingsaremixed = True
        
    return eolmode, lineendingsaremixed

def fileopentext(win, stext):
    text = stext[0]
    win.eolmode, win.lineendingsaremixed = check_mixed(text)
Mixin.setPlugin('editor', 'openfiletext', fileopentext)

def confirm_eol(win):
    eolmodestr = "MIX"
    d = wx.MessageDialog(win,
        tr('%s is currently mixed.\nWould you like to change it to default?\nThe default is: %s')
        % (win.filename, win.eolmess[win.pref.default_eol_mode]),
        tr("Mixed Line Ending"), wx.YES_NO | wx.ICON_QUESTION)
    if d.ShowModal() == wx.ID_YES:
        setEOLMode(win, win.pref.default_eol_mode)
        return True
    else:
        return False
    
def afteropenfile(win, filename):
    if win.lineendingsaremixed:
        wx.CallAfter(confirm_eol, win)
    else:
        eolmodestr = win.eolstr[win.eolmode]
        common.set_line_ending(eolmodestr)
        setEOLMode(win, win.eolmode, convert=False)
Mixin.setPlugin('editor', 'afteropenfile', afteropenfile)

#def savefile(win, filename):
#    if not win.lineendingsaremixed:
#        win.SetUndoCollection(0)
#        setEOLMode(win, win.eolmode)
#        win.SetUndoCollection(1)
#Mixin.setPlugin('editor', 'savefile', savefile)

def savefile(win, filename):
    text = win.GetText()
    win.eolmode, win.lineendingsaremixed = check_mixed(text)
    if win.lineendingsaremixed:
        confirm_eol(win)
Mixin.setPlugin('editor', 'savefile', savefile)
    
def on_document_enter(win, document):
    if document.edittype == 'edit':
        if document.lineendingsaremixed:
            eolmodestr = "MIX"
        else:
            eolmodestr = document.eolstr[document.eolmode]
        common.set_line_ending(eolmodestr)
Mixin.setPlugin('editctrl', 'on_document_enter', on_document_enter)

def getEndOfLineCharacter(character):
    if character == '\r' or character == '\n':
        return character
    return ""

########################
#remove line ending

def add_pref(preflist):
    preflist.extend([
        (tr('Document')+'/'+tr('Edit'), 180, 'check', 'edit_linestrip', tr('Strip line ending at file saving'), eolmess)
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def pref_init(pref):
    pref.edit_linestrip = False
Mixin.setPlugin('preference', 'init', pref_init)

def savefile(win, filename):
    if win.pref.edit_linestrip:
        status = win.save_state()
        try:
    #        if not win.lineendingsaremixed:
    #            setEOLMode(win, win.eolmode)
            win.mainframe.OnEditFormatChop(None)
        finally:
            win.restore_state(status)
Mixin.setPlugin('editor', 'savefile', savefile)

