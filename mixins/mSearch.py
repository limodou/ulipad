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
#   $Id: mSearch.py 2036 2007-03-19 02:19:30Z limodou $

"""Search process"""

import wx
from modules import Mixin

def add_mainframe_menu(menulist):
    menulist.extend([ (None, #parent menu id
        [
            (400, 'IDM_SEARCH', tr('Search'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDM_SEARCH', #parent menu id
        [
            (100, 'wx.ID_FIND', tr('Find...') + '\tE=Ctrl+F', wx.ITEM_NORMAL, 'OnSearchFind', tr('Shows the Find pane.')),
            (110, 'IDM_SEARCH_DIRECTFIND', tr('Directly Find') + '\tE=F4', wx.ITEM_NORMAL, 'OnSearchDirectFind', tr('Jumps to the next occurrence of selected text.')),
            (120, 'wx.ID_REPLACE', tr('Find And Replace...') + '\tE=Ctrl+H', wx.ITEM_NORMAL, 'OnSearchReplace', tr('Shows the Find And Replace pane.')),
            (130, 'wx.ID_BACKWARD', tr('Find Previous') + '\tE=Shift+F3', wx.ITEM_NORMAL, 'OnSearchFindPrev', tr('Finds the previous occurence of text.')),
            (140, 'wx.ID_FORWARD', tr('Find Next') + '\tE=F3', wx.ITEM_NORMAL, 'OnSearchFindNext', tr('Finds the next occurence of text.')),
            (150, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (160, 'IDM_SEARCH_GOTO_LINE', tr('Go To Line...') + '\tE=Ctrl+G', wx.ITEM_NORMAL, 'OnSearchGotoLine', tr('Jumps to the specified line in the current document.')),
            (170, 'IDM_SEARCH_LAST_MODIFY', tr('Go To Last Modification') + '\tE=Ctrl+B', wx.ITEM_NORMAL, 'OnSearchLastModify', tr('Jumps to the position of the last modification.')),

        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_mainframe_menu_image_list(imagelist):
    imagelist.update({
        'wx.ID_FIND':'images/find.gif',
        'wx.ID_REPLACE':'images/replace.gif',
        'wx.ID_FORWARD':'images/findnext.gif',
    })
Mixin.setPlugin('mainframe', 'add_menu_image_list', add_mainframe_menu_image_list)

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (220, 'find'),
        (230, 'replace'),
        (240, '|'),
    ])

    toolbaritems.update({
        'find':(wx.ITEM_NORMAL, 'wx.ID_FIND', 'images/find.gif', tr('Find'), tr('Shows the Find pane.'), 'OnSearchFind'),
        'replace':(wx.ITEM_NORMAL, 'wx.ID_REPLACE', 'images/replace.gif', tr('Find And Replace'), tr('Shows the Find And Replace pane.'), 'OnSearchReplace'),
    })
Mixin.setPlugin('mainframe', 'add_tool_list', add_tool_list)

def afterinit(win):
    import FindReplace

    win.finder = FindReplace.Finder()
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def on_set_focus(win, event):
    win.mainframe.finder.setWindow(win)
Mixin.setPlugin('editor', 'on_set_focus', on_set_focus)

def on_document_enter(win, document):
    win.mainframe.finder.setWindow(document)
Mixin.setPlugin('editctrl', 'on_document_enter', on_document_enter)

def OnSearchFind(win, event):
    name = 'findpanel'
    if not win.documentarea.sizer.is_shown(name):
        import FindReplace

        panel = FindReplace.FindPanel(win.documentarea, name)
        win.documentarea.sizer.add(panel,
            name=name, flag=wx.EXPAND|wx.ALL, border=2)
    else:
        panel = win.documentarea.sizer.find(name)
        if panel:
            panel = panel.get_obj()
    panel.reset(win.finder)
Mixin.setMixin('mainframe', 'OnSearchFind', OnSearchFind)

def OnSearchDirectFind(win, event):
    text = win.document.GetSelectedText()
    if len(text) > 0:
        win.finder.findtext = text
        win.finder.find(0)
Mixin.setMixin('mainframe', 'OnSearchDirectFind', OnSearchDirectFind)

def OnSearchReplace(win, event):
    name = 'findpanel'
    if not win.documentarea.sizer.is_shown(name):
        import FindReplace

        panel = FindReplace.FindPanel(win.documentarea, name)
        win.documentarea.sizer.add(panel,
            name=name, flag=wx.EXPAND|wx.ALL, border=2)
    else:
        panel = win.documentarea.sizer.find(name)
        if panel:
            panel = panel.get_obj()
    panel.reset(win.finder, replace=True)
Mixin.setMixin('mainframe', 'OnSearchReplace', OnSearchReplace)

def OnSearchFindNext(win, event):
    win.finder.find(0)
Mixin.setMixin('mainframe', 'OnSearchFindNext', OnSearchFindNext)

def OnSearchFindPrev(win, event):
    win.finder.find(1)
Mixin.setMixin('mainframe', 'OnSearchFindPrev', OnSearchFindPrev)

#def add_pref(preflist):
#    preflist.extend([
#        (tr('General'), 120, 'num', 'max_number', tr('Max number of saved items:'), None)
#    ])
#Mixin.setPlugin('preference', 'add_pref', add_pref)

def pref_init(pref):
    pref.max_number  = 20
    pref.findtexts = []
    pref.replacetexts = []
Mixin.setPlugin('preference', 'init', pref_init)

def OnSearchGotoLine(win, event):
    from modules import Entry
    document = win.document

    line = document.GetCurrentLine() + 1
    dlg = Entry.MyTextEntry(win, tr("Go To Line"), tr("Enter the line number:"), str(line))
    answer = dlg.ShowModal()
    if answer == wx.ID_OK:
        try:
            line = int(dlg.GetValue())
        except:
            return
        else:
            document.goto(line)
Mixin.setMixin('mainframe', 'OnSearchGotoLine', OnSearchGotoLine)

def pref_init(pref):
    pref.smart_nav_last_position = None
Mixin.setPlugin('preference', 'init', pref_init)

def on_modified(win):
    if hasattr(win, 'multiview') and win.multiview:
        return
    win.pref.smart_nav_last_position = win.getFilename(), win.save_state()
    win.pref.save()
Mixin.setPlugin('editor', 'on_modified', on_modified)

#this function will replace the one in mSearch.py
def OnSearchLastModify(win, event=None):
    if win.pref.smart_nav_last_position:
        filename, status = win.pref.smart_nav_last_position
        document = win.editctrl.new(filename)
        if document.getFilename() == filename:
            document.restore_state(status)
        else:
            win.pref.smart_nav_last_position = None
Mixin.setMixin('mainframe', 'OnSearchLastModify', OnSearchLastModify)
