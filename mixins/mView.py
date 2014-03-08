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
#   $Id: mView.py 2045 2007-04-16 07:57:13Z limodou $

import wx
from modules import Mixin

def add_mainframe_menu(menulist):
    menulist.extend([ (None,
        [
            (300, 'IDM_VIEW', tr('View'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDM_VIEW', #parent menu id
        [
            (100, 'IDM_VIEW_TAB', tr('Tabs And Spaces'), wx.ITEM_CHECK, 'OnViewTab', tr('Shows or hides whitespace indicators.')),
            (110, 'IDM_VIEW_INDENTATION_GUIDES', tr('Indentation Guides'), wx.ITEM_CHECK, 'OnViewIndentationGuides', tr('Shows or hides indentation guides.')),
            (120, 'IDM_VIEW_RIGHT_EDGE', tr('Long-Line Indicator'), wx.ITEM_CHECK, 'OnViewRightEdge', tr('Shows or hides the long-line indicator.')),
            (130, 'IDM_VIEW_LINE_NUMBER', tr('Line Numbers'), wx.ITEM_CHECK, 'OnViewLineNumber', tr('Shows or hides line numbers.')),
            (131, 'IDM_VIEW_ENDOFLINE_MARK', tr('End-Of-Line Marker'), wx.ITEM_CHECK, 'OnViewEndOfLineMark', tr('Shows or hides the end-of-line marker.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_VIEW_TAB, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_VIEW_INDENTATION_GUIDES, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_VIEW_RIGHT_EDGE, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_VIEW_LINE_NUMBER, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_VIEW_ENDOFLINE_MARK, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def editor_init(win):
    #show long line indicator
    if win.mainframe.pref.startup_show_longline:
        win.SetEdgeMode(wx.stc.STC_EDGE_LINE)
    else:
        win.SetEdgeMode(wx.stc.STC_EDGE_NONE)
        win.SetEdgeColour(wx.Colour(200,200,200))

    #long line width
    win.SetEdgeColumn(win.mainframe.pref.edge_column_width)

    #show tabs
    if win.mainframe.pref.startup_show_tabs:
        win.SetViewWhiteSpace(wx.stc.STC_WS_VISIBLEALWAYS)
    else:
        win.SetViewWhiteSpace(wx.stc.STC_WS_INVISIBLE)

    #show indentation guides
    win.SetIndentationGuides(win.mainframe.pref.startup_show_indent_guide)

    win.mwidth = 0     #max line number
    win.show_linenumber = win.mainframe.pref.startup_show_linenumber
Mixin.setPlugin('editor', 'init', editor_init)

def OnViewTab(win, event):
    stat = win.document.GetViewWhiteSpace()
    if stat == wx.stc.STC_WS_INVISIBLE:
        win.document.SetViewWhiteSpace(wx.stc.STC_WS_VISIBLEALWAYS)
    elif stat == wx.stc.STC_WS_VISIBLEALWAYS:
        win.document.SetViewWhiteSpace(wx.stc.STC_WS_INVISIBLE)
Mixin.setMixin('mainframe', 'OnViewTab', OnViewTab)

def OnViewIndentationGuides(win, event):
    win.document.SetIndentationGuides(not win.document.GetIndentationGuides())
Mixin.setMixin('mainframe', 'OnViewIndentationGuides', OnViewIndentationGuides)

def pref_init(pref):
    pref.edge_column_width = 79
    pref.startup_show_tabs = False
    pref.startup_show_indent_guide = False
    pref.startup_show_longline = True
    pref.startup_show_linenumber = True
Mixin.setPlugin('preference', 'init', pref_init)

tab_startup = tr('Document') + '/' + tr('Startup')
tab_view = tr('Document') + '/' + tr('View')
tab_edit = tr('Document') + '/' + tr('Edit')
tab_backend = tr('Document') + '/' + tr('Backend')
def add_pref_page(pages_order):
    pages_order.update({
        tab_startup:100,
        tab_view:110,
        tab_edit:120,
        tab_backend:130,
    }
    )
Mixin.setPlugin('preference', 'add_pref_page', add_pref_page)

def add_pref(preflist):
    preflist.extend([
        (tab_startup, 110, 'check', 'startup_show_tabs', tr('Show whitespace indicators at startup'), None),
        (tab_startup, 120, 'check', 'startup_show_indent_guide', tr('Make indentation guides visible at startup'), None),
        (tab_startup, 130, 'check', 'startup_show_longline', tr('Make long-line indicator visible at startup'), None),
        (tab_startup, 140, 'check', 'startup_show_linenumber', tr('Show line numbers at startup'), None),
        (tr('Document'), 100, 'num', 'edge_column_width', tr('Long-line indicator column position:'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def savepreference(mainframe, pref):
    for document in mainframe.editctrl.getDocuments():
        if document.CanView():
            document.SetEdgeColumn(mainframe.pref.edge_column_width)
Mixin.setPlugin('prefdialog', 'savepreference', savepreference)

def OnViewRightEdge(win, event):
    flag = win.document.GetEdgeMode()
    if flag == wx.stc.STC_EDGE_NONE:
        k = wx.stc.STC_EDGE_LINE
    else:
        k = wx.stc.STC_EDGE_NONE
    win.document.SetEdgeMode(k)
Mixin.setMixin('mainframe', 'OnViewRightEdge', OnViewRightEdge)

def OnViewLineNumber(win, event):
    win.document.show_linenumber = not win.document.show_linenumber
    win.document.setLineNumberMargin(win.document.show_linenumber)
Mixin.setMixin('mainframe', 'OnViewLineNumber', OnViewLineNumber)

def OnViewEndOfLineMark(win, event):
    win.document.SetViewEOL(not win.document.GetViewEOL())
Mixin.setMixin('mainframe', 'OnViewEndOfLineMark', OnViewEndOfLineMark)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if hasattr(win, 'document') and win.document and win.document.CanView():
        if eid in [win.IDM_VIEW_TAB, win.IDM_VIEW_INDENTATION_GUIDES, win.IDM_VIEW_RIGHT_EDGE]:
            event.Enable(True)
        if eid == win.IDM_VIEW_TAB:
            stat = win.document.GetViewWhiteSpace()
            if stat == wx.stc.STC_WS_INVISIBLE:
                event.Check(False)
            elif stat == wx.stc.STC_WS_VISIBLEALWAYS:
                event.Check(True)
        elif eid == win.IDM_VIEW_INDENTATION_GUIDES:
            event.Check(win.document.GetIndentationGuides())
        elif eid == win.IDM_VIEW_RIGHT_EDGE:
            flag = win.document.GetEdgeMode()
            if flag == wx.stc.STC_EDGE_NONE:
                event.Check(False)
            else:
                event.Check(True)
        elif eid == win.IDM_VIEW_ENDOFLINE_MARK:
            event.Check(win.document.GetViewEOL())
        elif eid == win.IDM_VIEW_LINE_NUMBER:
            event.Check(win.document.show_linenumber)

    else:
        if eid in [win.IDM_VIEW_TAB, win.IDM_VIEW_INDENTATION_GUIDES, win.IDM_VIEW_RIGHT_EDGE, win.IDM_VIEW_ENDOFLINE_MARK]:
#        if eid in [win.IDM_VIEW_TAB, win.IDM_VIEW_INDENTATION_GUIDES, win.IDM_VIEW_RIGHT_EDGE]:
            event.Enable(False)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (800, '|'),
        (810, 'viewtab'),
    ])

    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'viewtab':(wx.ITEM_CHECK, 'IDM_VIEW_TAB', 'images/format.gif', tr('Toggle Whitespace'), tr('Shows or hides whitespace indicators.'), 'OnViewTab'),
    })
Mixin.setPlugin('mainframe', 'add_tool_list', add_tool_list)

def on_modified(win):
    win.setLineNumberMargin(win.show_linenumber)
Mixin.setPlugin('editor', 'on_modified', on_modified)

def afteropenfile(win, filename):
    win.setLineNumberMargin(win.show_linenumber)
Mixin.setPlugin('editor', 'afteropenfile', afteropenfile)
