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
from modules import Mixin

menulist = [('IDM_PYTHON', #parent menu id
        [
            (170, 'IDM_PYTHON_CHECK', tr('Check Syntax'), wx.ITEM_NORMAL,
                'OnPythonCheck', tr('Check python source code syntax.')),
        ]),
]
Mixin.setMixin('pythonfiletype', 'menulist', menulist)

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (2140, 'check'),
    ])

    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'check':(wx.ITEM_NORMAL, 'IDM_PYTHON_CHECK', 'images/spellcheck.gif', tr('Check Syntax'), tr('Check python source code syntax.'), 'OnPythonCheck'),
    })
Mixin.setPlugin('mainframe', 'add_tool_list', add_tool_list)

def OnPythonCheck(win, event):
    import SyntaxCheck
    SyntaxCheck.Check(win, win.document)
Mixin.setMixin('mainframe', 'OnPythonCheck', OnPythonCheck)

def init(pref):
    pref.auto_py_check = True
    pref.auto_py_pep8_check = True
    pref.py_check_skip_long_line = True
    pref.py_check_skip_blank_lines = True
    pref.py_check_skip_tailing_whitespace = True
Mixin.setPlugin('preference', 'init', init)

preflist = [
        (tr('Python'), 160, 'check', 'auto_py_check', tr('Check for syntax errors at file saving'), None),
        (tr('Python'), 170, 'check', 'auto_py_pep8_check', tr('Check syntax for PEP8-style at python program run'), None),
]
Mixin.setMixin('preference', 'preflist', preflist)

def aftersavefile(win, filename):
    if win.edittype == 'edit' and win.languagename == 'python' and win.pref.auto_py_check:
        import SyntaxCheck
        wx.CallAfter(SyntaxCheck.Check, win.mainframe, win)
Mixin.setPlugin('editor', 'aftersavefile', aftersavefile, Mixin.LOW)

def createSyntaxCheckWindow(win):
    if not win.panel.getPage(tr('Check Syntax')):
        from SyntaxCheck import SyntaxCheckWindow

        page = SyntaxCheckWindow(win.panel.createNotebook('bottom'), win)
        win.panel.addPage('bottom', page, tr('Check Syntax'))
    win.syntaxcheckwindow = win.panel.getPage(tr('Check Syntax'))
Mixin.setMixin('mainframe', 'createSyntaxCheckWindow', createSyntaxCheckWindow)
