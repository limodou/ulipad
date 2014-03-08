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

#menulist = [(parent_menu_id, [(order, action_id),...])]

import wx
import copy
import EasyUtils

_item_type = {'-':wx.ITEM_SEPARATOR, 'radio':wx.ITEM_RADIO, 'check':wx.ITEM_CHECK, 'normal':wx.ITEM_NORMAL}

def makeid(win, idname):
    if not hasattr(win, idname):
        _id=wx.NewId()
        setattr(win, idname, _id)
        win._menuids[_id] = idname

    return getattr(win, idname)

def makesubmenu(win, alist, mlist, pid):
    menu = wx.Menu()
    if not mlist.has_key(pid):
        return menu
    for i in mlist[pid]:
        order, obj_id = i
        obj = alist.get(obj_id, None)
        if not obj:
            raise EasyUtils.EasyException, 'You should define action[%s] first!' % obj_id

        if mlist.has_key(obj_id):
            menu_id = makeid(win, obj_id)
            submenu = makesubmenu(mlist, win, obj_id, pid)
            menu.AppendMenu(menu_id, obj.caption, submenu)
            win._menuitems[obj_id] = submenu
        else:
            _type = _item_type.get(obj.type, wx.ITEM_NORMAL)
            if obj_id == '-':
                menu.AppendSeparator()
            else:
                menu_id = makeid(win, obj_id)
                if not obj.longtip:
                    obj.longtip = ''
                mitem = wx.MenuItem(menu, menu_id, obj.caption, obj.longtip, _type)
                if obj.image:
                    image = EasyUtils.getimage(obj.image)
                    if _type == wx.ITEM_CHECK:
                        mitem.SetBitmaps(image)
                    else:
                        mitem.SetBitmap(image)
                menu.AppendItem(mitem)
                win._menuitems[obj_id] = mitem

            if _type in (wx.ITEM_NORMAL, wx.ITEM_CHECK, wx.ITEM_RADIO):
                wx.EVT_MENU(win, menu_id, win.OnExecuteMenuCommand)
    return menu

def makepopmenu(win, alist, menulist):
    win._menuitems = {}
    win._menuids = {}
    win._actionlist = alist
    win._menulist = menulist
    setattr(win.__class__, 'OnExecuteMenuCommand', _OnExecuteMenuCommand)

    mlist = _mergemenu(menulist)
    menu = makesubmenu(win, alist, mlist, None)
    return menu

def _OnExecuteMenuCommand(win, event):
    _id = event.GetId()
    idname = win._menuids.get(_id, None)
    if not idname:
        raise EasyUtils.EasyException, "Can't find the id[%s]'s name!" % _id

    obj = win._actionlist.get(idname, None)
    if not obj:
        raise EasyUtils.EasyException, 'You should define action[%s] first!' % idname

    funcname = obj.funcname
    if not funcname:
        funcname = 'On' + idname
    if hasattr(win, funcname):
        func = getattr(win, funcname)
        func(event)
    else:
        print 'Not defint event handler, menu id = [%s]' % idname

def makemenubar(win, alist, menulist):
    menuBar = wx.MenuBar()
    win._menuitems = {}
    win._menuids = {}
    win._actionlist = alist
    win._menulist = menulist
    setattr(win.__class__, 'OnExecuteMenuCommand', _OnExecuteMenuCommand)

    mlist = _mergemenu(menulist)

    for i in mlist[None]:
        order, obj_id = i
        obj = alist.get(obj_id, None)
        if not obj:
            raise EasyUtils.EasyException, 'You should define action[%s] first!' % obj_id
        menu = makesubmenu(win, alist, mlist, obj_id)
        menuBar.Append(menu, obj.caption)
        win._menuitems[obj_id] = menu

    win.SetMenuBar(menuBar)

def _mergemenu(menulist):
    m = {}

    for pid, menu in menulist:
        newmenu = copy.deepcopy(menu)
        if m.has_key(pid):
            m[pid].extend(newmenu)
        else:
            m[pid] = newmenu
        m[pid].sort()

    return m

def findmenu(win, id):
    return win._menuitems[id]

def maketoolbar(win, alist, toollist):
    setattr(win.__class__, 'OnExecuteMenuCommand', _OnExecuteMenuCommand)

    win.toolbar = toolbar = win.CreateToolBar(wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT | wx.TB_TEXT)

    #judge image size by the first item of the toolbar item list
    for order, obj_id in toollist:
        obj = alist.get(obj_id, None)
        if not obj:
            raise EasyUtils.EasyException, 'You should define action[%s] first!' % obj_id

        if obj_id == '-': continue
        image = EasyUtils.getimage(obj.image)
        size = wx.Size(image.GetWidth(), image.GetHeight())
        toolbar.SetToolBitmapSize(size)
        break

    toollist.sort()
    for order, obj_id in toollist:
        obj = alist.get(obj_id, None)
        if not obj:
            raise EasyUtils.EasyException, 'You should define action[%s] first!' % obj_id
        if obj_id == '-':
            toolbar.AddSeparator()
        else:
            _type = _item_type.get(obj.type, wx.ITEM_NORMAL)
            image = EasyUtils.getimage(obj.image)
            tool_id = makeid(win, obj_id)
            if not obj.shorttip:
                obj.shorttip = ''
            if not obj.longtip:
                obj.longtip = ''
            if _type == wx.ITEM_NORMAL:
                toolbar.AddSimpleTool(tool_id, image, obj.shorttip, obj.longtip)
            elif _type == wx.ITEM_CHECK:
                toolbar.AddCheckTool(tool_id, image, obj.shorttip, obj.longtip)
            wx.EVT_TOOL(win, tool_id, win.OnExecuteMenuCommand)
    toolbar.Realize()
