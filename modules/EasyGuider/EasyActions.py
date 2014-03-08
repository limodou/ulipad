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

#action = (id, caption, type, shorttip, longtip, image, funcname)

import wx
import EasyUtils

def makeactions(actions_list):
    actions = {}
    actions['-'] = obj = EasyUtils.EMPTY_CLASS()
    obj.type = wx.ITEM_SEPARATOR
    for i in actions_list:
        obj = EasyUtils.EMPTY_CLASS()
        obj_id, obj.caption, obj.type, obj.shorttip, obj.longtip, obj.image, obj.funcname = i
        actions[obj_id] = obj

    return actions
