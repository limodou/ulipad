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
#   $Id: mFolder.py 1897 2007-02-03 10:33:43Z limodou $

import wx
import wx.stc
from modules import Mixin

def pref_init(pref):
    pref.use_folder = True
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('Document'), 130, 'check', 'use_folder', tr('Show code folding margin'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def savepreference(mainframe, pref):
    for document in mainframe.editctrl.getDocuments():
        if document.enablefolder:
            if pref.use_folder:
                document.SetMarginWidth(2, 16)
            else:
                document.SetMarginWidth(2, 0)
Mixin.setPlugin('prefdialog', 'savepreference', savepreference)

def editor_init(win):
    win.enablefolder = False
    win.SetMarginType(2, wx.stc.STC_MARGIN_SYMBOL) #margin 2 for symbols
    win.SetMarginMask(2, wx.stc.STC_MASK_FOLDERS)  #set up mask for folding symbols
    win.SetMarginSensitive(2, True)           #this one needs to be mouse-aware
#       win.SetMarginWidth(2, 16)                 #set margin 2 16 px wide


    #define folding markers
    win.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEREND,     wx.stc.STC_MARK_BOXPLUSCONNECTED,  "white", "black")
    win.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEROPENMID, wx.stc.STC_MARK_BOXMINUSCONNECTED, "white", "black")
    win.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERMIDTAIL, wx.stc.STC_MARK_TCORNER,  "white", "black")
    win.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERTAIL,    wx.stc.STC_MARK_LCORNER,  "white", "black")
    win.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERSUB,     wx.stc.STC_MARK_VLINE,    "white", "black")
    win.MarkerDefine(wx.stc.STC_MARKNUM_FOLDER,        wx.stc.STC_MARK_BOXPLUS,  "white", "black")
    win.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEROPEN,    wx.stc.STC_MARK_BOXMINUS, "white", "black")
Mixin.setPlugin('editor', 'init', editor_init)

def colourize(win):
    if win.enablefolder:
        if hasattr(win, 'pref'):
            if win.pref.use_folder:
                win.SetMarginWidth(2, 16)
                return
    win.SetMarginWidth(2, 0)    #used as folder

Mixin.setPlugin('lexerbase', 'colourize', colourize)

def OnMarginClick(win, event):
    # fold and unfold as needed
    if event.GetMargin() == 2:
        if event.GetControl() and event.GetShift():
            FoldAll(win)
        else:
            lineClicked = win.LineFromPosition(event.GetPosition())
            if win.GetFoldLevel(lineClicked) & wx.stc.STC_FOLDLEVELHEADERFLAG:
                if event.GetShift():
                    win.SetFoldExpanded(lineClicked, True)
                    Expand(win, lineClicked, True, True, 1)
                elif event.GetControl():
                    if win.GetFoldExpanded(lineClicked):
                        win.SetFoldExpanded(lineClicked, False)
                        Expand(win, lineClicked, False, True, 0)
                    else:
                        win.SetFoldExpanded(lineClicked, True)
                        Expand(win, lineClicked, True, True, 100)
                else:
                    win.ToggleFold(lineClicked)
Mixin.setPlugin('editor', 'on_margin_click', OnMarginClick)

def FoldAll(win):
    lineCount = win.GetLineCount()
    expanding = True

    # find out if we are folding or unfolding
    for lineNum in range(lineCount):
        if win.GetFoldLevel(lineNum) & wx.stc.STC_FOLDLEVELHEADERFLAG:
            expanding = not win.GetFoldExpanded(lineNum)
            break;

    lineNum = 0
    while lineNum < lineCount:
        level = win.GetFoldLevel(lineNum)
        if level & wx.stc.STC_FOLDLEVELHEADERFLAG and \
           (level & wx.stc.STC_FOLDLEVELNUMBERMASK) == wx.stc.STC_FOLDLEVELBASE:

            if expanding:
                win.SetFoldExpanded(lineNum, True)
                lineNum = Expand(win, lineNum, True)
                lineNum = lineNum - 1
            else:
                lastChild = win.GetLastChild(lineNum, -1)
                win.SetFoldExpanded(lineNum, False)
                if lastChild > lineNum:
                    win.HideLines(lineNum+1, lastChild)

        lineNum = lineNum + 1

def Expand(win, line, doExpand, force=False, visLevels=0, level=-1):
    lastChild = win.GetLastChild(line, level)
    line = line + 1
    while line <= lastChild:
        if force:
            if visLevels > 0:
                win.ShowLines(line, line)
            else:
                win.HideLines(line, line)
        else:
            if doExpand:
                win.ShowLines(line, line)

        if level == -1:
            level = win.GetFoldLevel(line)

        if level & wx.stc.STC_FOLDLEVELHEADERFLAG:
            if force:
                if visLevels > 1:
                    win.SetFoldExpanded(line, True)
                else:
                    win.SetFoldExpanded(line, False)
                line = Expand(win, line, doExpand, force, visLevels-1)

            else:
                if doExpand and win.GetFoldExpanded(line):
                    line = Expand(win, line, True, force, visLevels-1)
                else:
                    line = Expand(win, line, False, force, visLevels-1)
        else:
            line = line + 1;

    return line
