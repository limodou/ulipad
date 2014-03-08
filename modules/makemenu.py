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
#   $Id: makemenu.py 1609 2006-10-15 09:27:37Z limodou $

import wx
import Id
import copy
from modules import common
from Debug import debug, DEBUG

disableimage = False

def makesubmenu(mlist, win, pid, accel=None, imagelist=None):
    menu = wx.Menu()
    if not mlist.has_key(pid):
        return menu
    for m in mlist[pid]:
        order, idname, caption, kind, func, message = m
        if mlist.has_key(idname):
            id = Id.makeid(win, idname)
            submenu = makesubmenu(mlist, win, idname, accel, imagelist)
            menu.AppendMenu(id, caption, submenu)
            win.menuitems[idname] = submenu
        else:
            if kind == wx.ITEM_SEPARATOR:
                menu.AppendSeparator()
            else:
                id = Id.makeid(win, idname)
                if accel and accel.has_key(idname):
                    caption = caption.split('\t')[0]
                    mitem = wx.MenuItem(menu, id, caption, message, kind)
                    #mitem.SetText(caption + '\t' + accel[idname][0])
                else:
                    pos = caption.find('\t')
                    if pos > -1:
                        a, b = caption.split('\t')
                        #caption = a + '\t' + b.replace('+', ',')
                    mitem = wx.MenuItem(menu, id, caption, message, kind)
                if imagelist and disableimage == False:
                    imagename = imagelist.get(idname, '')
                    if imagename:
                        image = common.getpngimage(imagename)
                        if kind == wx.ITEM_CHECK:
                            mitem.SetBitmaps(image)
                        else:
                            mitem.SetBitmap(image)
#                else:
#                    print 'nobitmap'
#                    if wx.Platform == '__WXMSW__':
#                        mitem.SetBitmap(common.getpngimage('images/empty.gif'))
                menu.AppendItem(mitem)
                win.menuitems[idname] = mitem

            if kind in (wx.ITEM_NORMAL, wx.ITEM_CHECK, wx.ITEM_RADIO):
                if func:
                    try:
                        f = getattr(win, func)
                        wx.EVT_MENU(win, id, f)
                    except:
                        debug.error("[makemenu] Can't find function [%s] in class %s" % (func, win.__class__.__name__))
    return menu

def makepopmenu(win, popmenu, imagelist=None):
    win.menuitems = {}

    mlist = mergemenu(popmenu)
    debug.info('[makemenu] Popmenu Menu listing...')
    printmenu(mlist, imagelist)
    menu = makesubmenu(mlist, win, None, None, imagelist)
    return menu

def bind_id_to_menu(mlist, win, pid=None):
    if pid not in mlist:
        return
    
    for m in mlist[pid]:
        order, idname, caption, kind, func, message = m
        if mlist.has_key(idname):
            id = Id.makeid(win, idname)
            bind_id_to_menu(mlist, win, idname)
        else:
            if kind == wx.ITEM_SEPARATOR:
                pass
            else:
                id = Id.makeid(win, idname)

def bind_popup_menu_ids(win, menu):
    mlist = mergemenu(menu)
    bind_id_to_menu(mlist, win)
    
def makemenu(win, menulist, accel=None, editoraccel=None, imagelist=None):
    menuBar = wx.MenuBar()
    win.menuitems = {}

    mlist = mergemenu(menulist)
    debug.info('[makemenu] Main Menu listing...')
    printmenu(mlist, imagelist)
    makeaccelerator(mlist, accel, editoraccel)

    a = {}
    a.update(accel)
    a.update(editoraccel)
    menuBar.Freeze()
    for m in mlist[None]:
        order, idname, caption, kind, func, message = m
        id = Id.makeid(win, idname)
        menu = makesubmenu(mlist, win, idname, a, imagelist)
        menuBar.Append(menu, caption)
        win.menuitems[idname] = menu

    menuBar.Thaw()
    return menuBar

def mergemenu(menulist):
    m = {}

    for pid, menu in menulist:
        newmenu = copy.deepcopy(menu)
        if m.has_key(pid):
            m[pid].extend(newmenu)
        else:
            m[pid] = newmenu
        m[pid].sort()

    return m

def printmenu(m, imagelist=None):
    if not DEBUG: return
    debug.info('[makemenu] Menu listing...')
    if m.has_key(None):
        for order, idname, caption, kind, func, message in m[None]:
            debug.info('\t%s  %s\t"%s"' % (order, idname, caption))
            if m.has_key(idname):
                printsubmenu(m, '\t    ', idname)

    if imagelist and (disableimage == False):
        debug.info('[makemenu] Image list...')
        for idname, filename in imagelist.items():
            debug.info('\t%s\t%s' % (idname, filename))

def printsubmenu(m, space,idname):
    if not DEBUG: return
    for order, idname, caption, kind, func, message in m[idname]:
        debug.info('%s%s  %s\t"%s"' % (space, order, idname, caption))
        if m.has_key(idname):
            printsubmenu(m, space + '    ', idname)

def makeaccelerator(m, accellist, editoraccellist):
    debug.info('[makemenu] makeaccelerator...')
    for itementry in m.values():
        for order, idname, caption, kind, func, message in itementry:
            pos = caption.find('\t')
            if pos>= 0:
                accel = caption[pos+1:]
                if accel.startswith('E='):  #editor shortcut
                    if editoraccellist.has_key(idname):
                        accelkey = editoraccellist[idname][0]
                    else:
                        accelkey = accel[2:]
                    editoraccellist[idname] = (accelkey, func)
                else:
                    if accellist.has_key(idname):
                        accelkey = accellist[idname][0]
                    else:
                        accelkey = accel
                    accellist[idname] = (accelkey, func)
            else:
                if idname:
                    accelkey = ''
                    accellist[idname] = (accelkey, func)
            if idname:
                debug.info('\t%s [%s]' % (idname, accelkey))

def findmenu(menuitems, id):
    return menuitems[id]

def setmenutext(win, accel):
    for idname, menu in win.menuitems.items():
        if accel and accel.has_key(idname):
            if accel[idname][0]:
                label = menu.GetText()
                setmenuitemtext(menu, label, accel[idname][0])

def setmenuitemtext(menuitem, label, accel):
    caption = label + accel.rjust(40-common.string_width(label))
    menuitem.SetText(caption)
    