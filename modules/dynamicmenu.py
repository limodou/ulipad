#   Programmer:     limodou
#   E-mail:         limodou@gmail.com
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
#   $Id: dynamicmenu.py 1871 2007-01-28 08:49:56Z limodou $

import makemenu
from Debug import debug
import Id
from modules import common
import wx

def menuRemove(win, menulist):
    if len(menulist) == 0:
        return
    mlist = makemenu.mergemenu(win.menulist+menulist)
    removemlist = makemenu.mergemenu(menulist)
    m = sortmenu(removemlist)
#    win.menubar.Freeze()
    removemenu(mlist, removemlist, m, win)
#    win.menubar.Thaw()

def menuInsert(win, menulist):
    if len(menulist) == 0:
        return

    accel = {}
    editoraccel = {}
    m = makemenu.mergemenu(menulist)
    makemenu.makeaccelerator(m, accel, editoraccel)

    mlist = makemenu.mergemenu(win.menulist+menulist)
    insertmlist = makemenu.mergemenu(menulist)
    m = sortmenu(insertmlist)
#    win.menubar.Freeze()
    a = {}
    a.update(accel)
    a.update(editoraccel)
    insertmenu(mlist, insertmlist, m, win, a)
#    win.menubar.Thaw()
    
    return accel, editoraccel

def sortmenu(menulist):
    keys = menulist.keys()
    m = [keys[0]]

    for i in range(1, len(keys)):
        menu =  menulist[keys[i]]
        pos = len(m)
        for mitem in menu:
            if mitem[1] in m[:i]:
                pos = min([pos, m.index(mitem[1])])
        m.insert(pos, keys[i])

    return m

def removemenu(mlist, removemlist, sortedmenukey, win):
#    debug.info('[makemenu] Removing dynamic menu...')
#    makemenu.printmenu(removemlist)
    keys = sortedmenukey[:]
    while len(keys) > 0:
        key = keys[0]
        if key == None:
            for order, idname, caption, kind, func, message in removemlist[key]:
                pos = findpos(mlist, None, idname)
                win.menubar.Remove(pos)
            removekey(removemlist, keys, key)
        else:
            for order, idname, caption, kind, func, message in removemlist[key]:
                menu = win.menuitems[key]
                menu.Delete(getattr(win, idname))
            removekey(removemlist, keys, key)

    for m in removemlist.values():
        for order, idname, caption, kind, func, message in m:
            if idname:
                del win.menuitems[idname]

def insertmenu(mlist, insertmlist, sortedmenukey, win, accel=None, imagelist=None):
#    debug.info('[makemenu] Inserting dynamic menu...')
#    makemenu.printmenu(insertmlist)
    
    keys = sortedmenukey[:]
    while len(keys) > 0:
        key = keys[0]
        if key == None:
            for     order, idname, caption, kind, func, message in insertmlist[key]:
                id = Id.makeid(win, idname)
                menu = makemenu.makesubmenu(insertmlist, win, idname, accel, imagelist)
                makemenu.setmenutext(win, accel)
                win.menubar.Insert(findpos(mlist, key, idname), menu, caption)
                win.menuitems[idname] = menu
            removekey(insertmlist, keys, key)
        else:
            menu = win.menuitems[key]
            for     order, idname, caption, kind, func, message in insertmlist[key]:
                pos = findpos(mlist, key, idname)
                if insertmlist.has_key(idname): #submenu
                    id = Id.makeid(win, idname)
                    submenu = makemenu.makesubmenu(mlist, win, idname, accel, imagelist)
                    menu.InsertMenu(pos, id, caption, submenu)
                    win.menuitems[idname] = submenu
                else:
                    if kind == wx.ITEM_SEPARATOR:
                        menu.InsertSeparator(pos)
                    else:
                        id = Id.makeid(win, idname)
                        mitem = wx.MenuItem(menu, id, caption, message, kind)
                        if imagelist and makemenu.disableimage == False:
                            imagename = imagelist.get(idname, '')
                            if imagename:
                                image = common.getpngimage(imagename)
                                if kind == wx.ITEM_CHECK:
                                    mitem.SetBitmaps(image)
                                else:
                                    mitem.SetBitmap(image)
                        menu.InsertItem(pos, mitem)
                        win.menuitems[idname] = mitem

                    if kind in (wx.ITEM_NORMAL, wx.ITEM_CHECK, wx.ITEM_RADIO):
                        if func:
                            try:
                                f = getattr(win, func)
                                wx.EVT_MENU(win, id, f)
                            except:
                                debug.error("[makemenu] Can't find function [%s] in class %s" % (func, win.__class__.__name__))
            removekey(insertmlist, keys, key)

def findpos(mlist, pid, idname):
    length = len(mlist[pid])
    for i in range(len(mlist[pid])):
        order, id, caption, kind, func, message = mlist[pid][i]
        if id == idname :
            return i
    else:
        return length

def removekey(mlist, keys, key):
    for order, idname, caption, kind, func, message in mlist[key]:
        if idname in keys:
            k = idname
            removekey(mlist, keys, k)
    keys.remove(key)
