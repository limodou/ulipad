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

import wx
import os
from modules import common
from modules.Debug import error
from modules import Mixin
from modules import Casing
from modules import Globals

def other_popup_menu(dirwin, projectname, menus):
    item = dirwin.tree.GetSelection()
    if not item.IsOk(): return
    if 'django' in projectname:
        menus.extend([ (None,
            [
                (500, '', '-', wx.ITEM_SEPARATOR, None, ''),
                (530, 'IDPM_DJANGO_INSTALLSYSAPP', tr('Install Contribute Application'), wx.ITEM_NORMAL, '', ''),
                (540, 'IDPM_DJANGO_COMMAND', tr('Django &Command'), wx.ITEM_NORMAL, '', ''),
            ]),
            ('IDPM_DJANGO_INSTALLSYSAPP',
            [
                (100, 'IDPM_DJANGO_INSTALLSYSAPP_ADMIN', tr('Install Admin'), wx.ITEM_NORMAL, 'OnDjangoFunc', ''),
            ]),
            ('IDPM_DJANGO_COMMAND',
            [
                (100, 'IDPM_DJANGO_STARTAPP', tr('Create &New Application'), wx.ITEM_NORMAL, 'OnDjangoFunc', ''),
                (110, 'IDPM_DJANGO_RUNSERVER', tr('Start &Developing Server'), wx.ITEM_NORMAL, 'OnDjangoFunc', ''),
                (120, 'IDPM_DJANGO_RUNSHELL', tr('Start &Shell'), wx.ITEM_NORMAL, 'OnDjangoFunc', ''),
                (130, 'IDPM_DJANGO_DOT', tr('Create &Dot'), wx.ITEM_NORMAL, 'OnDjangoFunc', ''),
            ]),
        ])
        dir = common.getCurrentDir(dirwin.get_node_filename(item))
        if os.path.isdir(dir) and os.path.exists(os.path.join(os.path.dirname(dir), '_project')):
            menus.extend([ (None,
            [
                (520, 'IDPM_DJANGO_INSTALLAPP', tr('Install Application'), wx.ITEM_NORMAL, 'OnDjangoFunc', ''),
            ]),
        ])
Mixin.setPlugin('dirbrowser', 'other_popup_menu', other_popup_menu)

project_names = ['django']
Mixin.setMixin('dirbrowser', 'project_names', project_names)

def set_project(ini, projectnames):
    if 'django' in projectnames:
        common.set_acp_highlight(ini, '.html', ['html.acp', 'django_html.acp'], 'djangotmp')
Mixin.setPlugin('dirbrowser', 'set_project', set_project)

def remove_project(ini, projectnames):
    if 'django' in projectnames:
        common.remove_acp_highlight(ini, '.html', ['html.acp', 'django_html.acp'], 'djangotmp')
Mixin.setPlugin('dirbrowser', 'remove_project', remove_project)

def onprocess(v):
    if not hasattr(v, 'count'):
        v.count = 0
    Globals.mainframe.statusbar.g1.SetValue(v.count)
    v.count += 1
    if v.count >= 100:
        v.count = 0

def onsuccess():
    Globals.mainframe.statusbar.g1.SetValue(0)
    wx.CallAfter(Globals.mainframe.statusbar.g1.Hide)

def OnDjangoFunc(win, event):
    _id = event.GetId()
    try:
        if hasattr(win, 'IDPM_DJANGO_STARTAPP') and _id == win.IDPM_DJANGO_STARTAPP:
            OnDjangoStartApp(win)
        elif hasattr(win, 'IDPM_DJANGO_INSTALLAPP') and _id == win.IDPM_DJANGO_INSTALLAPP:
            d = Casing.Casing(OnDjangoInstallApp, win)
            v = Casing.new_obj()
            v.count = 0
#            d.onprocess(onprocess, v=v, timestep=0.1)
#            d.onsuccess(onsuccess)
#            d.onexception(onsuccess)
            d.start_thread()
        elif hasattr(win, 'IDPM_DJANGO_INSTALLSYSAPP_ADMIN') and _id == win.IDPM_DJANGO_INSTALLSYSAPP_ADMIN:
            d = Casing.Casing(OnDjangoInstallConApp, win, 'admin')
            v = Casing.new_obj()
#            d.onprocess(onprocess, v=v, timestep=0.1)
#            d.onsuccess(onsuccess)
#            d.onexception(onsuccess)
            d.start_thread()
        elif hasattr(win, 'IDPM_DJANGO_RUNSERVER') and _id == win.IDPM_DJANGO_RUNSERVER:
            OnDjangoRunServer(win)
        elif hasattr(win, 'IDPM_DJANGO_RUNSHELL') and _id == win.IDPM_DJANGO_RUNSHELL:
            OnDjangoRunShell(win)
        elif hasattr(win, 'IDPM_DJANGO_DOT') and _id == win.IDPM_DJANGO_DOT:
            OnCreateDot(win)
    except:
        error.traceback()
        common.showerror(win, tr("There is some wrong as executing the menu."))
Mixin.setMixin('dirbrowser', 'OnDjangoFunc', OnDjangoFunc)

def OnDjangoStartApp(win):
    values = get_django_name(win)
    if values:
        appname = values.get('appname', '')
        if appname:
            oldpath = os.getcwd()
            try:
                item = win.tree.GetSelection()
                filename = win.get_node_filename(item)
                if win.isFile(item):
                    item = win.tree.GetItemParent(item)
                    filename = win.get_node_filename(item)

                dir = filename
                os.chdir(dir)
                os.system('django-admin.py startapp %s' % appname)
                if values.get('template', False):
                    os.mkdir(os.path.join(dir, appname, 'templates'))
                if values.get('template_tags', False):
                    path = os.path.join(dir, appname, 'templatetags')
                    os.mkdir(path)
                    file(os.path.join(path, '__init__.py'), 'w').close()
                win.tree.DeleteChildren(item)
                win.addpathnodes(dir, item)
                common.note(tr('Completed!'))
            finally:
                os.chdir(oldpath)

def OnDjangoInstallApp(win):
    oldpath = os.getcwd()
    try:
        path = win.getCurrentProjectHome()
        os.chdir(path)
        module = os.path.basename(path)
        settings_file = os.path.join(path, 'settings.py')
        from modules.DjangoIni import DjangoIni
        ini = DjangoIni(settings_file)
        item = win.tree.GetSelection()
        appname = os.path.basename(win.get_node_filename(item))
        module = str('.'.join([module, appname]))
        if module not in ini['INSTALLED_APPS']:
            ini['INSTALLED_APPS'].append(module)
            ini.save()
        fin, fout = os.popen4('python manage.py install %s' % appname)
        text = fout.read()
        if not text.strip():
            wx.CallAfter(common.showmessage, win, tr('Completed!'))
        else:
            wx.CallAfter(common.show_in_message_window, text)
    finally:
        os.chdir(oldpath)

def OnDjangoInstallConApp(win, appname):
    oldpath = os.getcwd()
    try:
        path = win.getCurrentProjectHome()
        os.chdir(path)
        module = ''
        if appname == 'admin':
            module = 'django.contrib.admin'
        settings_file = os.path.join(path, 'settings.py')
        from modules.DjangoIni import DjangoIni
        ini = DjangoIni(settings_file)
        if module not in ini['INSTALLED_APPS']:
            ini['INSTALLED_APPS'].append(module)
            ini.save()
        fin, fout = os.popen4('python manage.py install %s' % appname)
        text = fout.read()
        if not text.strip():
            wx.CallAfter(common.showmessage, win, tr('Completed!'))
        else:
            wx.CallAfter(common.show_in_message_window, text)
    finally:
        os.chdir(oldpath)

def OnDjangoRunServer(win):
    oldpath = os.getcwd()
    try:
        path = win.getCurrentProjectHome()
        os.chdir(path)
        wx.Execute("python manage.py runserver")
    finally:
        os.chdir(oldpath)

def OnDjangoRunShell(win):
    path = win.getCurrentProjectHome()
    import DjangoShell
    shell = DjangoShell.DjangoShell(win, path)
    shell.Show()

def OnCreateDot(win):
    import djangodot
    path = win.get_node_filename(win.tree.GetSelection())
    if os.path.isdir(path) and os.path.exists(os.path.join(path, 'models.py')):
        app = path
        dotfile = os.path.join(path, app+'.dot')
        imagefile = os.path.join(path, app+'.png')
        djangodot.createdotfile(os.path.basename(app), dotfile)
        create_dot_and_show(Globals.mainframe, imagefile, dotfile)
    else:
        common.showerror(win, tr("Current directory seems not a real Django app"))

def create_dot_and_show(win, imagefile, dotfile):
    try:
        cmd = 'dot -T%s -o%s %s' % ('png', imagefile, dotfile)
        win.createMessageWindow()
        win.panel.showPage(tr('Message'))
        win.messagewindow.SetText(cmd)
        os.system(cmd)
    except:
        error.traceback()
        common.showerror(win, tr("Can't execute [%s]") % cmd)
        return
    if os.path.exists(imagefile):
        from modules import ImageWin
        try:
            win = ImageWin.ImageWin(win, imagefile)
            win.Show()
        except:
            common.showerror(win, tr("Can't open image file %s") % imagefile)

def get_django_name(win):
    elements = [
    ('string', 'appname', '', tr('Django application name:'), None),
    ('bool', 'template', False, tr('Create templates directory in app folder:'), None),
    ('bool', 'template_tags', False, tr('Create templatetags directory in app folder:'), None),
    ]
    from modules.EasyGuider import EasyDialog
    easy = EasyDialog.EasyDialog(win, title=tr('Input'), elements=elements)
    values = None
    if easy.ShowModal() == wx.ID_OK:
        values = easy.GetValue()
        appname = values['appname']
        if not appname:
            common.showerror(win, tr("Django application name cannot be empty."))
    easy.Destroy()
    return values

def project_begin(dirwin, project_names, path):
    if 'django' in project_names:
#        module = os.path.basename(path)
#        dir = os.path.dirname(path)
        import sys
        sys.path.insert(0, path)
        os.environ['DJANGO_SETTINGS_MODULE'] = "settings"
Mixin.setPlugin('dirbrowser', 'project_begin', project_begin)

def project_end(dirwin, project_names, path):
    if 'django' in project_names:
        try:
            del os.environ['DJANGO_SETTINGS_MODULE']
#            dir = os.path.dirname(path)
            import sys
            sys.path.remove(path)
        except:
            error.traceback()
Mixin.setPlugin('dirbrowser', 'project_end', project_end)
