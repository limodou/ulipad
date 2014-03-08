#       Programmer:     limodou
#       E-mail:         limodou@gmail.com
#
#       Copyleft 2006 limodou
#
#       Distributed under the terms of the GPL (GNU Public License)
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
#       $Id: BlogEdit.py 42 2005-09-28 05:19:21Z limodou $

from modules import Mixin
import os.path
import wx
import images
from modules.Debug import error
from modules import common

menulist = [ ('IDM_WINDOW',
        [
                (170, 'IDM_WINDOW_BLOG', tr('Open Blog Window'), wx.ITEM_NORMAL, 'OnWindowBlog', tr('Opens blog window.'))
        ]),
]
Mixin.setMixin('mainframe', 'menulist', menulist)

popmenulist = [ (None,
        [
                (150, 'IDPM_BLOGWINDOW', tr('Open Blog Window'), wx.ITEM_NORMAL, 'OnBlogWindow', tr('Opens blog window.')),
        ]),
]
Mixin.setMixin('notebook', 'popmenulist', popmenulist)

def createBlogWindow(win):
    page = win.panel.getPage('Blog')
    if not page:
        from BlogManageWindow import BlogManageWindow

        page = BlogManageWindow(win.panel.createNotebook('bottom'), win)
        win.panel.addPage('bottom', page, 'Blog')
Mixin.setMixin('mainframe', 'createBlogWindow', createBlogWindow)

def OnWindowBlog(win, event):
    try:
        win.createBlogWindow()
        win.panel.showPage('Blog')
    except:
        error.traceback()
        common.showerror(win, tr('There is something wrong as running Blog Edit'))
Mixin.setMixin('mainframe', 'OnWindowBlog', OnWindowBlog)

def OnBlogWindow(win, event):
    try:
        win.mainframe.createBlogWindow()
        win.panel.showPage('Blog')
    except:
        error.traceback()
        common.showerror(win, tr('There is something wrong as running Blog Edit'))
Mixin.setMixin('notebook', 'OnBlogWindow', OnBlogWindow)

blog_resfile = os.path.join(__path__[0], 'blogmanagedialog.xrc')
def afterinit(win):
    win.blog_resfile = blog_resfile
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def init(pref):
    pref.blog_sites = []
    pref.blog_sites_info = {}
    pref.last_blog_site = 0
Mixin.setPlugin('preference', 'init', init)

toollist = [
        (128, 'blog'),
]
Mixin.setMixin('mainframe', 'toollist', toollist)

#order, IDname, imagefile, short text, long text, func
toolbaritems = {
        'blog':(wx.ITEM_NORMAL, 'IDM_NEW_BLOG', images.getBlogBitmap(), tr('new blog'), tr('Opens new blog window.'), 'OnNewBlog'),
}
Mixin.setMixin('mainframe', 'toolbaritems', toolbaritems)

def OnNewBlog(win, event):
    win.editctrl.newPage('', documenttype='blogpanel')
Mixin.setMixin('mainframe', 'OnNewBlog', OnNewBlog)

pageimagelist = {
        'blog': images.getBlogBitmap(),
}
Mixin.setMixin('editctrl', 'pageimagelist', pageimagelist)

from BlogPanel import BlogPanel

panellist = {'blogpanel':BlogPanel}
Mixin.setMixin('editctrl', 'panellist', panellist)
