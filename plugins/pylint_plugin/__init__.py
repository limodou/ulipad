#   Programmer: mikem
#   E-mail:     mjmaher@iol.ie
#
#   Copyleft 2009 mjmaher
#
#   Distributed under the terms of the GPL (GNU Public License)
#
#   UliPad is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Found ation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA
#
#   $Id$
#   Updated by limodou 2007/12/03 add report and result panel

"""
Runs the PyLint python code checking program on the current file in
the editor window. PyLint is run from the Project Home directory so 
the project should be set before running PyLint. The output messages 
are sent to pylint_filename.txt and the report to pylint_global.txt 
in the Project Home directory. After running PyLint refresh the Project 
Home directory to show the files in the Directory Browser. PyLint 
must be separately installed.
"""
import wx
from modules import common
from modules import Mixin
from modules import Casing
from modules.Debug import error

def add_mainframe_menu(menulist):
   """ Add the PyLint item to the Tool menu"""
   menulist.extend([('IDM_TOOL',
       [
           (190, 'IDM_TOOL_PYLINT', 'PyLint',
            wx.ITEM_NORMAL, 'OnPylint', tr('Runs the PyLint code checker')),
       ]), ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def OnPylint(win, event):
    """
    Get the filename of the current document. Save it if necessary.
    Chdir to the Project Home directory and run PyLint. The --files-output=y
    option directs the output to the files pylint_filename.txt and
    pylint_global.txt in the Project Home directory.
    """
    try:
        from pylint import lint
    except:
        common.showerror(win, tr("Import pylint error! Maybe you haven't installed it.\nPlease install it first."))
        return
    
    doc = win.editctrl.getCurDoc()
    pyfile = doc.filename
    if doc.isModified() or pyfile == '':
        dialog = wx.MessageDialog(win, tr("The file has not been saved.\n\
Would you like to save the file and then re-run PyLint ?"),
           "PyLint", wx.YES_NO | wx.ICON_QUESTION)
        answer = dialog.ShowModal()
        if answer == wx.ID_YES:
            win.OnFileSave(event)
            return
        else:
            return
        
    from Report import Report
#    projecthome = common.getProjectHome(pyfile)
#    os.chdir(common.encode_string(projecthome))
#    args = ["--files-output=y", pyfile]
    win.createPylintSyntaxCheckWindow()
    if win.pylintsyntaxcheckwindow:
        win.pylintsyntaxcheckwindow.list.DeleteAllItems()
        def f():
            try:
                common.setmessage(win, 'Pylint syntax checking...')
                try:
                    lint.Run([pyfile], Report(win.pylintsyntaxcheckwindow.list))
                except:
                    error.track()
            finally:
                common.setmessage(win, '')
                common.note(tr('Pylint syntax checking finished!'))
                
        d = Casing.Casing(f)
        d.start_thread()
Mixin.setMixin('mainframe', 'OnPylint', OnPylint)

def init(pref):
    pref.pylint_convention = True
    pref.pylint_refactor = True
    pref.pylint_warning = True
    pref.pylint_error = True
    pref.pylint_fatal = True
Mixin.setPlugin('preference', 'init', init)

pylint_syntax_pagename = tr('Pylint Check')
def createPylintSyntaxCheckWindow(win):
    if not win.panel.getPage(pylint_syntax_pagename):
        from CheckPanel import SyntaxCheckWindow

        page = SyntaxCheckWindow(win.panel.createNotebook('bottom'), win)
        win.panel.addPage('bottom', page, pylint_syntax_pagename)
    win.pylintsyntaxcheckwindow = win.panel.getPage(pylint_syntax_pagename)
    win.panel.showPage(pylint_syntax_pagename)
Mixin.setMixin('mainframe', 'createPylintSyntaxCheckWindow', createPylintSyntaxCheckWindow)
