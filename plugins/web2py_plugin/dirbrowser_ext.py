#   Programmer: limodou
#   E-mail:     limodou@gmail.com
#
#   Copyleft 2008 limodou
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

import wx
import os
from modules import common
from modules.Debug import error
from modules import Mixin
from modules import Globals

def other_popup_menu(dirwin, projectname, menus):
    item = dirwin.tree.GetSelection()
    if not item.IsOk(): return
    if 'web2py' in projectname:
        dir = common.getCurrentDir(dirwin.get_node_filename(item))
        basedir = os.path.basename(os.path.dirname(dir))
        if os.path.isdir(dir) and basedir == 'applications':
            menus.extend([ (None,
            [
                (500, '', '-', wx.ITEM_SEPARATOR, None, ''),
                (520, 'IDPM_WEB2PY_SHELL', tr('Start web2py Shell'), wx.ITEM_NORMAL, 'OnWeb2pyShell', ''),
            ]),
        ])
Mixin.setPlugin('dirbrowser', 'other_popup_menu', other_popup_menu)

project_names = ['web2py']
Mixin.setMixin('dirbrowser', 'project_names', project_names)

def set_project(ini, projectnames):
    if 'web2py' in projectnames:
        common.set_acp_highlight(ini, '.html', ['html.acp', 'web2py_html.acp'], 'web2pyview')
        common.set_acp_highlight(ini, '.py', ['web2py_py.acp'], 'python')
Mixin.setPlugin('dirbrowser', 'set_project', set_project)

def remove_project(ini, projectnames):
    if 'web2py' in projectnames:
        common.remove_acp_highlight(ini, '.html', ['html.acp', 'web2py_html.acp'], 'web2pyview')
        common.remove_acp_highlight(ini, '.py', ['web2py_py.acp'], 'python')
Mixin.setPlugin('dirbrowser', 'remove_project', remove_project)

def OnWeb2pyShell(dirwin, event):
    item = dirwin.tree.GetSelection()
    if not item.IsOk(): return

    win = Globals.mainframe
    dir = common.getCurrentDir(dirwin.get_node_filename(item))
    appname = os.path.basename(dir)
    pagename = tr('web2py Shell') + ' [%s]' % appname
    
    page = win.panel.getPage(pagename)
    if not page:
        from web2py_shell import Web2pyShell
        page = Web2pyShell(win.panel.createNotebook('bottom'), win)
        win.panel.addPage('bottom', page, pagename)
    win.panel.showPage(pagename)
    page.set_locals(dir, appname)
Mixin.setMixin('dirbrowser', 'OnWeb2pyShell', OnWeb2pyShell)

#def project_begin(dirwin, project_names, path):
#    if 'django' in project_names:
##        module = os.path.basename(path)
##        dir = os.path.dirname(path)
#        import sys
#        sys.path.insert(0, path)
#        os.environ['DJANGO_SETTINGS_MODULE'] = "settings"
#Mixin.setPlugin('dirbrowser', 'project_begin', project_begin)
#
#def project_end(dirwin, project_names, path):
#    if 'django' in project_names:
#        try:
#            del os.environ['DJANGO_SETTINGS_MODULE']
##            dir = os.path.dirname(path)
#            import sys
#            sys.path.remove(path)
#        except:
#            error.traceback()
#Mixin.setPlugin('dirbrowser', 'project_end', project_end)
