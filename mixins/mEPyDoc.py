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

import re
import wx
from modules import Mixin

def other_popup_menu(editor, projectname, menus):
    if editor.languagename == 'python':
        menus.extend([(None, #parent menu id
            [
                (9, 'IDPM_PYTHON_EPYDOC', tr('Create Comment for Function'), wx.ITEM_NORMAL, 'OnPythonEPyDoc', 'Creates comment for a function.'),
            ]),
        ])
Mixin.setPlugin('editor', 'other_popup_menu', other_popup_menu)

re_func = re.compile('^(\s*)def\s+[\w\d_]+\((.*?)\):')
comment_template = """

@author: %(username)s  

%(parameters)s
@return:
@rtype: 
"""
def OnPythonEPyDoc(win, event=None):
    def output(win, indent, parameters, pos):
        t = (indent / win.GetTabWidth() + 1) * win.getIndentChar()
        startpos = win.PositionFromLine(win.LineFromPosition(pos)+1)
        win.GotoPos(startpos)
        text = '"""' + comment_template % {'parameters':parameters, 'username':win.pref.personal_username} + '"""' + win.getEOLChar()
        s = ''.join([t + x for x in text.splitlines(True)])
        win.AddText(s)
        win.EnsureCaretVisible()
        
    line = win.GetCurrentLine()
    text = win.getLineText(line)
    pos = win.GetCurrentPos()
    if not text.strip():
        for i in range(line-1, -1, -1):
            text = win.getLineText(i)
            if text.strip():
                break
    
    b = None
    if text:
        b = re_func.match(text)
    if b:
        indent, parameters = b.groups()
        paras = [x.strip() for x in parameters.split(',')]
        s = []
        for x in paras:
            if x.startswith('**'):
                x = x[2:]
            if x.startswith('*'):
                x = x[1:]
            if '=' in x:
                x = x.split('=')[0]
            x = x.strip()
            s.append('@param %s:' % x)
            s.append('@type %s:' % x)
        s = win.getEOLChar().join(s)
        output(win, len(indent), s, pos)
        return
Mixin.setMixin('editor', 'OnPythonEPyDoc', OnPythonEPyDoc)