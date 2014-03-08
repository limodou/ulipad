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
#   $Id: Id.py 1457 2006-08-23 02:12:12Z limodou $

import wx

def makeidlist(win, idlist):
    for idname in idlist:
        makeid(win, idname)

def makeid(win, idname):
    if isinstance(idname, int):
        return idname
    
    if idname.startswith('wx.'):
        idname = idname[3:]
        if hasattr(wx, idname):
            id = getattr(wx, idname)
            setattr(win, idname, id)

    if not hasattr(win, idname) or not idname in win.__dict__:
        id=wx.NewId()
        setattr(win, idname, id)

    return getattr(win, idname)
