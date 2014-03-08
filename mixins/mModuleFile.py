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
#   $Id: mModuleFile.py 1548 2006-10-03 06:57:31Z limodou $

from modules import Mixin
import wx
import wx.stc
import os.path

def add_py_menu(menulist):
    menulist.extend([
        ('IDM_PYTHON', #parent menu id
        [
            (115, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (116, 'IDM_VIEW_OPEN_MODULE', tr('Open Module File') + '\tF6', wx.ITEM_NORMAL, 'OnViewOpenModuleFile', tr('Open current word as Python module file.')),
        ]),
    ])
Mixin.setPlugin('pythonfiletype', 'add_menu', add_py_menu)

def other_popup_menu(editor, projectname, menus):
    if editor.languagename == 'python' :
        menus.extend([(None, #parent menu id
            [
                (10, 'IDPM_OPEN_MODULE', tr('Open Module File') + '\tF6', wx.ITEM_NORMAL, 'OnOpenModuleFile', tr('Open current word as Python module file.')),
                (20, '', '-', wx.ITEM_SEPARATOR, None, ''),
            ]),
        ])
Mixin.setPlugin('editor', 'other_popup_menu', other_popup_menu)

def OnViewOpenModuleFile(win, event):
    openmodulefile(win, getword(win))
Mixin.setMixin('mainframe', 'OnViewOpenModuleFile', OnViewOpenModuleFile)

def OnOpenModuleFile(win, event):
    openmodulefile(win.mainframe, getword(win.mainframe))
Mixin.setMixin('editor', 'OnOpenModuleFile', OnOpenModuleFile)

def openmodulefile(mainframe, module):
    try:
        mod = my_import(module)
        f, ext = os.path.splitext(mod.__file__)
        filename = f + '.py'
        if os.path.exists(filename):
            mainframe.editctrl.new(filename)
    except:
        pass

def my_import(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def getword(mainframe):
    doc = mainframe.document
    if doc.GetSelectedText():
        return doc.GetSelectedText()
    pos = doc.GetCurrentPos()
    start = doc.WordStartPosition(pos, True)
    end = doc.WordEndPosition(pos, True)
    if end > start:
        i = start - 1
        while i >= 0:
            if doc.getChar(i) in mainframe.getWordChars() + '.':
                start -= 1
                i -= 1
            else:
                break
        i = end
        length = doc.GetLength()
        while i < length:
            if doc.getChar(i) in mainframe.getWordChars()+ '.':
                end += 1
                i += 1
            else:
                break
    return doc.GetTextRange(start, end)
