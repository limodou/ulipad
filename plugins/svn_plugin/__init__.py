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

import os
import wx
from modules import Mixin
from modules import common
from modules.Debug import error

def pref_init(pref):
    pref.svn_log_history = []
    pref.svn_proxy_server = ''
    pref.svn_proxy_port = 0
    pref.svn_proxy_username = ''
    pref.svn_proxy_password = ''
    pref.svn_proxy_timeout = 0
    pref.svn_urls = []
    pref.svn_checkout_folder = ''
Mixin.setPlugin('preference', 'init', pref_init)

def other_popup_menu(dirwin, projectname, menus):
    item = dirwin.tree.GetSelection()
    if not dirwin.is_ok(item):
        is_svn_dir = False
    else:
        is_svn_dir = detect_svn(common.getCurrentDir(dirwin.get_node_filename(item)))
    menus.extend([ (None,
        [
            (93.0, 'IDPM_VC_CHECKOUT', tr('SVN Checkout'), wx.ITEM_NORMAL, 'OnVC_DoCommand', ''),
            (93.3, 'IDPM_VC_COMMANDS', tr('SVN Commands'), wx.ITEM_NORMAL, '', ''),
            (93.4, '', '-', wx.ITEM_SEPARATOR, None, ''),
        ]),
        ('IDPM_VC_COMMANDS',
        [
            (900, 'IDPM_VC_COMMANDS_SETTINGS', tr('Settings...'), wx.ITEM_NORMAL, 'OnVC_Settings', ''),
        ]),
    ])

    if is_svn_dir:
        menus.extend([ (None,
            [
                (93.1, 'IDPM_VC_UPDATE', tr('SVN Update'), wx.ITEM_NORMAL, 'OnVC_DoCommand', ''),
                (93.2, 'IDPM_VC_COMMIT', tr('SVN Commit'), wx.ITEM_NORMAL, 'OnVC_DoCommand', ''),
            ]),
            ('IDPM_VC_COMMANDS',
            [
                (100, 'IDPM_VC_COMMANDS_LIST', tr('&List'), wx.ITEM_NORMAL, 'OnVC_DoCommand', ''),
                (110, 'IDPM_VC_COMMANDS_SHOWLOG', tr('Show l&og'), wx.ITEM_NORMAL, 'OnVC_DoCommand', ''),
                (120, 'IDPM_VC_COMMANDS_STATUS', tr('&Status'), wx.ITEM_NORMAL, 'OnVC_DoCommand', ''),
                (130, 'IDPM_VC_COMMANDS_DIFF', tr('Di&ff'), wx.ITEM_NORMAL, 'OnVC_DoCommand', ''),
                (145, '', '-', wx.ITEM_SEPARATOR, None, ''),
                (150, 'IDPM_VC_COMMANDS_ADD', tr('&Add'), wx.ITEM_NORMAL, 'OnVC_DoCommand', ''),
                (160, 'IDPM_VC_COMMANDS_RENAME', tr('&Rename'), wx.ITEM_NORMAL, 'OnVC_DoCommand', ''),
                (170, 'IDPM_VC_COMMANDS_DELETE', tr('&Delete'), wx.ITEM_NORMAL, 'OnVC_DoCommand', ''),
                (180, 'IDPM_VC_COMMANDS_REVERSE', tr('Re&vert'), wx.ITEM_NORMAL, 'OnVC_DoCommand', ''),
                (190, '', '-', wx.ITEM_SEPARATOR, None, ''),
                (200, 'IDPM_VC_COMMANDS_EXPORT', tr('&Export'), wx.ITEM_NORMAL, 'OnVC_DoCommand', ''),
                (210, '', '-', wx.ITEM_SEPARATOR, None, ''),
            ]),
        ])
Mixin.setPlugin('dirbrowser', 'other_popup_menu', other_popup_menu)

def OnVC_DoCommand(win, event):
    mapping = {
        'IDPM_VC_CHECKOUT':'checkout',
        'IDPM_VC_COMMIT':'commit',
        'IDPM_VC_UPDATE':'update',
        'IDPM_VC_COMMANDS_LIST':'list',
        'IDPM_VC_COMMANDS_STATUS':'status',
        'IDPM_VC_COMMANDS_SHOWLOG':'log',
        'IDPM_VC_COMMANDS_ADD':'add',
        'IDPM_VC_COMMANDS_RENAME':'rename',
        'IDPM_VC_COMMANDS_DELETE':'delete',
        'IDPM_VC_COMMANDS_REVERSE':'revert',
        'IDPM_VC_COMMANDS_DIFF':'diff',
        'IDPM_VC_COMMANDS_EXPORT':'export',
    }
    item = win.tree.GetSelection()
    if item.IsOk():
        path = win.get_node_filename(item)
    else:
        path = ''
    import SvnSupport as vc
    _id = event.GetId()
    for id, cmd in mapping.items():
        if _id == getattr(win, id, None):
            vc.do(win, cmd, path)
Mixin.setMixin('dirbrowser', 'OnVC_DoCommand', OnVC_DoCommand)

def OnVC_Settings(win, event):
    from SvnSettings import SVNSettings

    try:
        dlg = SVNSettings(win)
        dlg.ShowModal()
    except:
        error.traceback()
Mixin.setMixin('dirbrowser', 'OnVC_Settings', OnVC_Settings)

_image_ids = {}
def add_image(imagelist, image, imgindex):
    global _image_ids
    m = [
        ('modified', common.getpngimage('images/TortoiseModified.gif')),
        ('added', common.getpngimage('images/TortoiseAdded.gif')),
        ('conflicted', common.getpngimage('images/TortoiseConflict.gif')),
        ('deleted', common.getpngimage('images/TortoiseDeleted.gif')),
        ('normal', common.getpngimage('images/TortoiseInSubVersion.gif')),
    ]

    _image_ids[imgindex] = {}
    for f, imgfile in m:
        bmp = common.merge_bitmaps(image, imgfile)
        index = imagelist.Add(bmp)
        _image_ids[imgindex][f] = index
Mixin.setPlugin('dirbrowser', 'add_image', add_image)

def get_fix_imgindex(index, f):
    return _image_ids[index].get(f, index)

def set_image(tree, node, index, img_flag):
    wx.CallAfter(tree.SetItemImage, node, index, img_flag)

#import threading
#svn_lock = threading.Lock()
def after_addpath(dirwin, item):
    from modules import common
    import SvnSupport as vc
    from modules import Casing

    def walk(dirwin, item):
#        svn_lock.acquire()
#        try:
        if dirwin.isFile(item):
            path = dirwin.get_node_filename(item)
            entries = vc.get_entries(path)
            filename = dirwin.tree.GetItemText(item)
            f = entries.get(filename, '')
            img_index = dirwin.get_file_image(filename)
            new_img_index = get_fix_imgindex(img_index, f)
            old_img_index = dirwin.tree.GetItemImage(item)
            if new_img_index != old_img_index:
                set_image(dirwin.tree, item, new_img_index, wx.TreeItemIcon_Normal)
            return
        else:
            if dirwin.tree.GetChildrenCount(item) == 0 and not dirwin.tree.IsExpanded(item):
                return
        path = common.getCurrentDir(dirwin.get_node_filename(item))
        entries = vc.get_entries(path)
        node, cookie = dirwin.tree.GetFirstChild(item)
        while dirwin.is_ok(node):
            filename = dirwin.tree.GetItemText(node)
            f = entries.get(filename, ' ')
            if dirwin.isFile(node):
                img_index = dirwin.get_file_image(filename)
                new_img_index = get_fix_imgindex(img_index, f)
                old_img_index = dirwin.tree.GetItemImage(node)
                if new_img_index != old_img_index:
                    set_image(dirwin.tree, node, new_img_index, wx.TreeItemIcon_Normal)
            else:
                img_index = (dirwin.close_image, dirwin.open_image)
                new_img_index = (get_fix_imgindex(dirwin.close_image, f),
                    get_fix_imgindex(dirwin.open_image, f))
                old_img_index = dirwin.tree.GetItemImage(node)
                if old_img_index not in new_img_index:
                    set_image(dirwin.tree, node, new_img_index[1], wx.TreeItemIcon_Expanded)
                    set_image(dirwin.tree, node, new_img_index[0], wx.TreeItemIcon_Normal)
                if dirwin.tree.GetChildrenCount(node) > 0:
                    walk(dirwin, node)
            node, cookie = dirwin.tree.GetNextChild(item, cookie)
#        finally:
#            svn_lock.release()

    is_svn_dir = detect_svn(common.getCurrentDir(dirwin.get_node_filename(item)))

    if is_svn_dir:
        d = Casing.Casing(walk, dirwin, item)
        d.start_thread()

Mixin.setPlugin('dirbrowser', 'after_expanding', after_addpath)
Mixin.setPlugin('dirbrowser', 'after_refresh', after_addpath)

def aftersavefile(editor, filename):
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
                    after_addpath(dirwin, node)
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
Mixin.setPlugin('editor', 'aftersavefile', aftersavefile)

#functions
########################################################

def detect_svn(path):
    lastdir = ''
    while lastdir != path:
        if os.path.exists(os.path.join(path, '.svn')):
            return True
        lastdir = path
        path = os.path.dirname(path)