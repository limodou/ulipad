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
#   $Id: DirBrowser.py 262 2005-12-14 04:11:44Z limodou $

import sys
from modules import Mixin
from modules.Debug import error
from modules import common
import wx
import os
from modules import Globals

def add_project(project_names):
    project_names.extend(['python'])
Mixin.setPlugin('dirbrowser', 'add_project', add_project)

def project_begin(dirwin, project_names, path):
    if 'python' in project_names and path not in sys.path:
        sys.path.insert(0, path)
Mixin.setPlugin('dirbrowser', 'project_begin', project_begin)

def project_end(dirwin, project_names, path):
    if 'python' in project_names:
        try:
            if path in sys.path:
                sys.path.remove(path)
        except:
            error.traceback()
Mixin.setPlugin('dirbrowser', 'project_end', project_end)

def other_popup_menu(dirwin, projectname, menus):
    item = dirwin.tree.GetSelection()
    if not item.IsOk(): return
    if 'python' in projectname:
        menus.extend([ (None,
            [
                (145, 'IDPM_PYTHON_CREATE_PACKAGE', tr('Create Python Package'), wx.ITEM_NORMAL, 'OnCreatePythonPackage', ''),
            ]),
        ])
Mixin.setPlugin('dirbrowser', 'other_popup_menu', other_popup_menu)

def OnCreatePythonPackage(dirwin, event):
    item = dirwin.tree.GetSelection()
    if not item.IsOk(): return
    dir = common.getCurrentDir(dirwin.get_node_filename(item))
    
    from modules import Entry
    dlg = Entry.MyTextEntry(Globals.mainframe, tr('Input Directory Name'),
        tr('Input Directory Name'))
    path = ''
    if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetValue()
    dlg.Destroy()
    
    path = os.path.join(dir, path)
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except Exception, e:
            common.showerror(str(e))
    init_file = os.path.join(path, '__init__.py')
    if not os.path.exists(init_file):
        f = file(init_file, 'wb')
        f.close()
    dirwin.OnRefresh()
Mixin.setMixin('dirbrowser', 'OnCreatePythonPackage', OnCreatePythonPackage)
