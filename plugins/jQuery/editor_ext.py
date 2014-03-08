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
import re

def other_popup_menu(editor, projectname, menus):
    if editor.languagename == 'js' and 'jquery' in common.getProjectName(editor.filename):
        menus.extend([(None, #parent menu id
            [
                (30, 'IDPM_JQUERY_PROJECT', tr('jQuery'), wx.ITEM_NORMAL, '', ''),
#                (40, '', '-', wx.ITEM_SEPARATOR, None, ''),
            ]),
            ('IDPM_JQUERY_PROJECT',
            [
                (100, 'IDPM_JQUERY_PROJECT_CREATE_COMMENT', tr('Create Comment for Function'), wx.ITEM_NORMAL, 'OnJQueryProjectFunc', tr('Creates comment for a function.')),
#                (110, '', '-', wx.ITEM_SEPARATOR, None, ''),
            ]),
        ])
Mixin.setPlugin('editor', 'other_popup_menu', other_popup_menu)

def OnJQueryProjectFunc(win, event):
    _id = event.GetId()
    try:
        if _id == win.IDPM_JQUERY_PROJECT_CREATE_COMMENT:
            OnJQueryProjectCreateComment(win)
    except:
        error.traceback()
        common.showerror(win, tr("There is some wrong as executing the menu."))
Mixin.setMixin('editor', 'OnJQueryProjectFunc', OnJQueryProjectFunc)

re_func = re.compile('\s*function\s+([$._\w]+)\((.*?)\)')
re_prop_func = re.compile('\s*([$._\w]+)\s*:\s*function\s*\((.*?)\)')
re_dot_func = re.compile('\s*([$._\w]+)\s*=\s*function\s*\((.*?)\)')
comment_template = """/**
 * Description:
 *
 * @name     %(fn_name)s
%(parameters)s
 * @author   %(username)s
 * @example  
 *
 */
"""
def OnJQueryProjectCreateComment(win):
    def output(win, fn_name, parameters, pos):
        startpos = win.PositionFromLine(win.LineFromPosition(pos))
        win.GotoPos(startpos)
        win.AddText(comment_template % {'fn_name':fn_name, 'parameters':parameters, 'username':win.pref.personal_username})
        win.EnsureCaretVisible()
        
    line = win.GetCurrentLine()
    text = win.getLineText(line)
    pos = win.GetCurrentPos()
    if not text.strip():
        for i in range(line+1, win.GetLineCount()):
            text = win.getLineText(i)
            if text.strip():
                break
    
    b = None
    if text:
        b = re_func.match(text)
        if not b:
            b = re_prop_func.match(text)
            if not b:
                b = re_dot_func.match(text)
    if b:
        fn_name, parameters = b.groups()
        
        s = win.getEOLChar().join([' * @param    %s' % x.strip() for x in parameters.split(',')])
        output(win, fn_name, s, pos)
        return
    else:
        output(win, '', ' * @param    ', pos)
        return
