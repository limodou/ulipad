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
#   $Id: mLexerFactory.py 2051 2007-04-19 12:08:03Z limodou $

__doc__ = 'Lexer control'

import wx
import os
from modules import Mixin
from modules import common
from modules import dict4ini
from modules import Globals
from LexerFactory import LexerFactory

def call_lexer(win, oldfilename, filename, language):
    
#    if oldfilename == filename and filename:
#        return
    lexer_obj = None
    flag = False
    for lexer in win.mainframe.lexers.lexobjs:
        prjfile = common.getProjectFile(filename)
        ini = dict4ini.DictIni(prjfile)
        ext = os.path.splitext(filename)[1]
        lexname = ini.highlight[ext]
        
        if lexname and lexname == lexer.name:   #find acp option
            if not hasattr(win, 'lexer') or lexname != win.lexer.name:
                lexer_obj = lexer
                flag = True
                break
            
        if not lexname and (language and language == lexer.name or lexer.matchfile(filename)):
            if not hasattr(win, 'lexer') or lexer.name != win.lexer.name:
                lexer_obj = lexer
                flag = True
                break
            
    else:
#        if filename:
#            win.mainframe.lexers.getNamedLexer('text').colourize(win)
#        else:
        if not hasattr(win, 'lexer'):
            lexer_obj = Globals.mainframe.lexers.getDefaultLexer()
            flag = True
    if flag:
        lexer_obj.colourize(win)
        wx.CallAfter(Globals.mainframe.editctrl.switch, win)
Mixin.setPlugin('editor', 'call_lexer', call_lexer)
Mixin.setPlugin('dirbrowser', 'call_lexer', call_lexer)

#def aftersavefile(win, filename):
#    for lexer in win.mainframe.lexers.lexobjs:
#        if lexer.matchfile(filename) and lexer != win.lexer:
##            lexer.colourize(win)
#            return
#Mixin.setPlugin('editor', 'aftersavefile', aftersavefile)

def beforeinit(win):
    win.lexers = LexerFactory(win)
Mixin.setPlugin('mainframe', 'beforeinit', beforeinit)

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_DOCUMENT',
        [
            (130, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (140, 'IDM_DOCUMENT_SYNTAX_HIGHLIGHT', tr('Syntax Highlight...'), wx.ITEM_NORMAL, 'OnDocumentSyntaxHighlight', tr('Specifies the syntax highlight to current document.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def OnDocumentSyntaxHighlight(win, event):
#    items = [lexer.name for lexer in win.lexers.lexobjs]
    items = win.lexers.getLexerNames()
    dlg = wx.SingleChoiceDialog(win, tr('Select a syntax highlight:'), tr('Syntax Highlight'), items, wx.CHOICEDLG_STYLE)
    if dlg.ShowModal() == wx.ID_OK:
        lexer = win.lexers.lexobjs[dlg.GetSelection()]
        lexer.colourize(win.document)
        win.editctrl.switch(win.document)
    dlg.Destroy()
Mixin.setMixin('mainframe', 'OnDocumentSyntaxHighlight', OnDocumentSyntaxHighlight)

def add_pref(preflist):
    preflist.extend([
        (tr('General'), 130, 'choice', 'default_lexer', tr('Default syntax highlight:'), LexerFactory.lexnames),
        (tr('Document'), 120, 'check', 'caret_line_visible', tr('Show caret line'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def pref_init(pref):
    pref.default_lexer = 'text'
    pref.caret_line_visible = True
Mixin.setPlugin('preference', 'init', pref_init)

def savepreference(mainframe, pref):
    mainframe.document.SetCaretLineVisible(pref.caret_line_visible)
Mixin.setPlugin('prefdialog', 'savepreference', savepreference)
