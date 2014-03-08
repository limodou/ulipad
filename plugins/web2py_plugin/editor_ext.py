#   Programmer: ygao
#   E-mail:     ygao2004@gmail.com
#
#   Copyleft 2008 ygao
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
import os
import re
from modules import Mixin
import wx
import wx.stc
from modules import common
from modules.Debug import error
regex_def=re.compile('^def\s+(?P<name>(?:[a-zA-Z0-9]\w*)|(?:_[a-zA-Z0-9]\w*))\(')
root = 'applications'
views = 'views'
controllers = 'controllers'

def get_path(win, name=None):
    filename = win.filename
    if name is None:
        temp = filename.split(os.path.sep)
        try:
            index = temp.index(root)
            app_path = os.path.sep.join(temp[:index + 2])
        except :
            return
        return app_path
    else:
        if name:
            app_path = get_path(win)
            if app_path:
                name_path = os.path.join(app_path, name)
                if os.path.exists(name_path):
                    return name_path
    
def get_controller(win):
    controller = ''
    line = win.GetCurrentLine()
    def_match = regex_def.match(win.GetLine(line))
    if def_match:
        controller = def_match.groups('name')[0]
    elif  win.syntax_info:
        obj = win.syntax_info.guess(line)
        if  len(obj) > 0:
            controller = obj[0].name
    return controller

controller_function=''
def get_view_from_controller(win):
    global controller_function
    controller_function = ''
    controllers_path = get_path(win, controllers)
    if controllers_path and controllers_path in win.filename:
        app = get_path(win)
        name = os.path.split(win.filename)[1]
        if  name == 'default.py':
            view = os.path.join(app, views, "default", get_controller(win) + ".html")
            controller_function = os.path.join(os.path.split(app)[1], "default", get_controller(win)).replace('\\', '/')
        elif name == 'appadmin.py':
            view = os.path.join(app, views, "appadmin" + ".html") 
        else:
            view = os.path.join(app, views, os.path.splitext(name)[0], get_controller(win) + ".html")
            controller_function = os.path.join(os.path.split(app)[1], os.path.splitext(name)[0] ,get_controller(win)).replace('\\', '/')
            
            if not os.path.exists(view):
                view = os.path.join(app, views, os.path.splitext(name)[0], "generic.html")
        return view
    
controller_name = ''
def get_controller_from_view(win):
    views_path = get_path(win, views)
    if views_path and views_path in win.filename:
        app = get_path(win)
        global controller_name
        controller = None
        name = os.path.split(os.path.dirname(win.filename))[1]
        if  name == 'default':
            controller = os.path.join(app, controllers, "default.py")
        elif name == 'views':
            os.path.split(win.filename) == 'appadmin.html'
            controller = os.path.join(app, controllers, "appadmin.py")
        else:
            controller_path = os.path.join(app, controllers, os.path.splitext(name)[0] + ".py")
            if os.path.exists(controller_path):
                controller = controller_path
        controller_name = os.path.splitext(os.path.split(win.filename)[1])[0]
        return controller
    
def dynamic_menu(win, flag = ''):
    view = get_view_from_controller(win)
    if flag == 'web':
        return tr('&Visit %s in web') % controller_function
    if view:
        if os.path.exists(view):
            return tr('&Goto %s view ') % get_controller(win)
        else:
            return tr('&Create %s view') % get_controller(win)
    controller = get_controller_from_view(win)
    if controller:
        return tr('&Goto %s of %s') % (controller_name, os.path.split(controller)[1])
        
    
def other_popup_menu(editor, projectname, menus):
    if 'web2py' in common.getProjectName(editor.filename):
        path = common.getProjectHome(editor.filename)
        if not os.path.exists(os.path.join(path, "web2py.py")):
            common.showerror(win, tr("setting web2py project is not correctly, you must setting project on web2py folder"))
            return
        if  editor.filename.count(root)>1:
            common.showerror(win, tr(" '%s' occur twice, we can't handle this situation" % root))
            return 
        if dynamic_menu(editor):
            menus.extend([(None, #parent menu id
                [
                    (30, 'IDPM_WEB2PY_PROJECT', tr('&Web2py'), wx.ITEM_NORMAL, '', ''),
                    (35, 'IDPM_WEB2PY_PROJECT_CONTROLLERS_VIEW', dynamic_menu(editor), wx.ITEM_NORMAL, 'OnWeb2pyProjectFunc', tr('Create a view or open view.')),
                    (38, 'IDPM_WEB2PY_PROJECT_CONTROLLERS_WEB', dynamic_menu(editor, 'web'), wx.ITEM_NORMAL, 'OnWeb2pyProjectFunc', tr('visit web site')),
                    
                    (40, '', '-', wx.ITEM_SEPARATOR, None, ''),
                ]),
                ('IDPM_WEB2PY_PROJECT',
                [
##                    (100, 'IDPM_WEB2PY_PROJECT_CONTROLLERS_VIEW', dynamic_menu(editor), wx.ITEM_NORMAL, 'OnWeb2pyProjectFunc', tr('Create a view or open view.')),
                    (110, '', '-', wx.ITEM_SEPARATOR, None, ''),
                ]),
            ])
Mixin.setPlugin('editor', 'other_popup_menu', other_popup_menu)

def OnWeb2pyProjectFunc(win, event):
    _id = event.GetId()
    
    try:
        if _id == win.IDPM_WEB2PY_PROJECT_CONTROLLERS_VIEW:
            OnWeb2pyProjectControllersView(win)
        elif  _id == win.IDPM_WEB2PY_PROJECT_CONTROLLERS_WEB:
            
            OnWeb2pyProjectControllersWeb(win)
    except:
        error.traceback()
        common.showerror(win, tr("There is some wrong as executing the menu."))
Mixin.setMixin('editor', 'OnWeb2pyProjectFunc', OnWeb2pyProjectFunc)

def OnWeb2pyProjectControllersView(win):
    global controller_name
    view = get_view_from_controller(win)
    if view:
        if os.path.exists(view):
            win.mainframe.editctrl.new(view)
            return
        else:
            open(view, 'w').close()
            win.mainframe.editctrl.new(view).SetText("{{extend 'layout.html'}}\n")
            return
    controller = get_controller_from_view(win)
    if  controller:
        doc = win.mainframe.editctrl.new(controller)
        pos = doc.FindText(0, doc.GetTextLength(), r'^def[ \t]+%s' % controller_name,wx.stc.STC_FIND_REGEXP)
        controller_name = ''
        if  pos > -1:
            doc.GotoPos(pos)
            doc.SetFocus()
            doc.EnsureCaretVisible()
            
def OnWeb2pyProjectControllersWeb(win):
    
    global controller_function
    if controller_function:
        common.webopen("http://127.0.0.1:8000/%s" % controller_function)
    controllers_path = ''
