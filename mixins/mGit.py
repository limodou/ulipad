#   Programmer: limodou
#   E-mail:     limodou@gmail.com
#
#   Copyleft 2014 limodou
#
#   Distributed under the terms of the GPL (GNU Public License)
#
#   Ulipad is free software; you can redistribute it and/or modify
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
import wx
from modules import Mixin
from modules import common
from modules.Debug import error

_git_image_ids = {}
def git_add_image(imagelist, image, imgindex):
    global _git_image_ids
    m = [
        ('M', common.getpngimage('images/TortoiseModified.gif')),
        ('A', common.getpngimage('images/TortoiseAdded.gif')),
        ('C', common.getpngimage('images/TortoiseConflict.gif')),
        ('D', common.getpngimage('images/TortoiseDeleted.gif')),
        (' ', common.getpngimage('images/TortoiseInSubVersion.gif')),
    ]

    _git_image_ids[imgindex] = {}
    for f, imgfile in m:
        bmp = common.merge_bitmaps(image, imgfile)
        index = imagelist.Add(bmp)
        _git_image_ids[imgindex][f] = index
Mixin.setPlugin('dirbrowser', 'add_image', git_add_image)

def git_get_fix_imgindex(index, f):
    return _git_image_ids[index].get(f, index)

def git_set_image(tree, node, index, img_flag):
    wx.CallAfter(tree.SetItemImage, node, index, img_flag)

def git_after_addpath(dirwin, item):
    from modules import common
    from modules import Casing
    from Git import Git

    def walk(dirwin, item, dir, files):
        
        if files is None:
            files = {}
            for flag, filename in repo.status_files():
                files[filename] = flag

        dir = os.path.normpath(dir).replace('\\', '/')
        if dir == '.':
            dir = ''
        if dirwin.isFile(item):
            path = dirwin.get_node_filename(item)
            filename = os.path.join(dir, dirwin.tree.GetItemText(item)).replace('\\', '/')
            f = files.get(filename, ' ')
            img_index = dirwin.get_file_image(filename)
            new_img_index = git_get_fix_imgindex(img_index, f)
            old_img_index = dirwin.tree.GetItemImage(item)
            if new_img_index != old_img_index:
                git_set_image(dirwin.tree, item, new_img_index, wx.TreeItemIcon_Normal)
            return
        else:
            if dirwin.tree.GetChildrenCount(item) == 0 and not dirwin.tree.IsExpanded(item):
                return
        path = common.getCurrentDir(dirwin.get_node_filename(item))
        node, cookie = dirwin.tree.GetFirstChild(item)
        while dirwin.is_ok(node):
            filename = os.path.join(dir, dirwin.tree.GetItemText(node)).replace('\\', '/')
            if not dirwin.isFile(node):
                filename = filename + '/'
            f = files.get(filename, ' ')
            if dirwin.isFile(node):
                img_index = dirwin.get_file_image(filename)
                new_img_index = git_get_fix_imgindex(img_index, f)
                old_img_index = dirwin.tree.GetItemImage(node)
                if new_img_index != old_img_index:
                    git_set_image(dirwin.tree, node, new_img_index, wx.TreeItemIcon_Normal)
            else:
                img_index = (dirwin.close_image, dirwin.open_image)
                new_img_index = (git_get_fix_imgindex(dirwin.close_image, f),
                    git_get_fix_imgindex(dirwin.open_image, f))
                old_img_index = dirwin.tree.GetItemImage(node)
                if old_img_index not in new_img_index:
                    git_set_image(dirwin.tree, node, new_img_index[1], wx.TreeItemIcon_Expanded)
                    git_set_image(dirwin.tree, node, new_img_index[0], wx.TreeItemIcon_Normal)
                if dirwin.tree.GetChildrenCount(node) > 0:
                    walk(dirwin, node, os.path.join(dir, filename), files)
            node, cookie = dirwin.tree.GetNextChild(item, cookie)

    path = common.getCurrentDir(dirwin.get_node_filename(item))
    repo_path = detect_git(path)
    if repo_path:
        repo = Git(path)
        d = Casing.Casing(walk, dirwin, item, os.path.relpath(path, repo_path), None)
        d.start_thread()

Mixin.setPlugin('dirbrowser', 'after_expanding', git_after_addpath)
Mixin.setPlugin('dirbrowser', 'after_refresh', git_after_addpath)

def git_aftersavefile(editor, filename):
    from modules import Globals
    m = Globals.mainframe

    #get dirbrowser instance
    dirwin = m.panel.getPage(tr('Directory Browser'))
    if not dirwin: return

    def get_node(tree, parent):
        node, cookie = tree.GetFirstChild(parent)
        while node.IsOk():
            yield node
            node, cookie = tree.GetNextChild(node, cookie)

    class StopException(Exception):pass
    dir = os.path.dirname(filename)
    def find(dirwin, parent, dir, filename):
        for node in get_node(dirwin.tree, parent):
            if dirwin.isFile(node):
                if filename == dirwin.get_node_filename(node):
                    git_after_addpath(dirwin, node)
                    raise StopException
            else:
                if not dir.startswith(dirwin.get_node_filename(node)):
                    continue
                else:
                    if dirwin.tree.IsExpanded(node):
                        find(dirwin, node, dir, filename)

    try:
        find(dirwin, dirwin.root, dir, filename)
    except StopException:
        pass
Mixin.setPlugin('editor', 'aftersavefile', git_aftersavefile)

#functions
########################################################

def detect_git(path):
    lastdir = ''
    while lastdir != path:
        if os.path.exists(os.path.join(path, '.git')):
            return path
        lastdir = path
        path = os.path.dirname(path)