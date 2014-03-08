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
#   $Id: mZoom.py 1566 2006-10-09 04:44:08Z limodou $

import wx
from modules import Mixin
from modules import common

def add_mainframe_menu(menulist):
    menulist.extend([
        ('IDM_VIEW', #parent menu id
        [
            (170, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (185, 'IDM_VIEW_ZOOM_IN', tr('Zoom In'), wx.ITEM_NORMAL, 'OnViewZoomIn', tr('Increases the font size of the document.')),
            (190, 'IDM_VIEW_ZOOM_OUT', tr('Zoom Out'), wx.ITEM_NORMAL, 'OnViewZoomOut', tr('Decreases the font size of the document.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_mainframe_menu_image_list(imagelist):
    imagelist.update({
        'IDM_VIEW_ZOOM_IN':'images/large.gif',
        'IDM_VIEW_ZOOM_OUT':'images/small.gif',
    })
Mixin.setPlugin('mainframe', 'add_menu_image_list', add_mainframe_menu_image_list)

def OnViewZoomIn(win, event):
    win.document.ZoomIn()
Mixin.setMixin('mainframe', 'OnViewZoomIn', OnViewZoomIn)

def OnViewZoomOut(win, event):
    win.document.ZoomOut()
Mixin.setMixin('mainframe', 'OnViewZoomOut', OnViewZoomOut)

#def add_tool_list(toollist, toolbaritems):
#    toollist.extend([
#        (820, 'zoomin'),
#        (830, 'zoomout'),
#    ])
#
#    #order, IDname, imagefile, short text, long text, func
#    toolbaritems.update({
#        'zoomin':(wx.ITEM_NORMAL, 'IDM_VIEW_ZOOM_IN', common.unicode_abspath('images/large.gif'), tr('zoom in'), tr('Increases the font size of the document'), 'OnViewZoomIn'),
#        'zoomout':(wx.ITEM_NORMAL, 'IDM_VIEW_ZOOM_OUT', common.unicode_abspath('images/small.gif'), tr('zoom out'), tr('Decreases the font size of the document'), 'OnViewZoomOut'),
#    })
#Mixin.setPlugin('mainframe', 'add_tool_list', add_tool_list)
