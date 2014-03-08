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
#   $Id: mFtp.py 2120 2007-07-11 02:56:11Z limodou $

__doc__ = 'ftp manage'

import wx
from modules import Mixin
from modules.Debug import error
from modules import common

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_WINDOW',
        [
            (160, 'IDM_WINDOW_FTP', tr('FTP Window'), wx.ITEM_CHECK, 'OnWindowFtp', tr('Shows the FTP pane.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def afterinit(win):
    win.ftp_imagelist = {
    'close':            'images/folderclose.gif',
    'document':         'images/file.gif',
    'parentfold':       'images/parentfold.gif',
}
    win.ftp_resfile = common.uni_work_file('resources/ftpmanagedialog.xrc')
    win.ftp = None
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDM_WINDOW_FTP:
        event.Check(bool(win.panel.getPage('FTP')) and win.panel.BottomIsVisible)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_WINDOW_FTP, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def on_notebook_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDPM_FTPWINDOW:
        event.Check(bool(win.panel.getPage('FTP')) and win.panel.BottomIsVisible)
Mixin.setPlugin('notebook', 'on_update_ui', on_notebook_updateui)

def init(win):
    wx.EVT_UPDATE_UI(win, win.IDPM_FTPWINDOW, win.OnUpdateUI)
Mixin.setPlugin('notebook', 'init', init)

def add_editor_menu(popmenulist):
    popmenulist.extend([ (None,
        [
            (150, 'IDPM_FTPWINDOW', tr('FTP Window'), wx.ITEM_CHECK, 'OnFtpWindow', tr('Shows the FTP pane.')),
        ]),
    ])
Mixin.setPlugin('notebook', 'add_menu', add_editor_menu)

def createFtpWindow(win, side='bottom'):
    page = win.panel.getPage('FTP')
    if not page:
        from FtpClass import Ftp

        page = Ftp(win.panel.createNotebook(side), win)
        win.panel.addPage(side, page, 'FTP')
    win.ftp = page
Mixin.setMixin('mainframe', 'createFtpWindow', createFtpWindow)

def OnWindowFtp(win, event):
    if not win.panel.getPage('FTP'):
        win.createFtpWindow()
        win.panel.showPage('FTP')
    else:
        win.panel.closePage('FTP')
Mixin.setMixin('mainframe', 'OnWindowFtp', OnWindowFtp)

def OnFtpWindow(win, event):
    if not win.panel.getPage('FTP'):
        win.mainframe.createFtpWindow('bottom')
        win.panel.showPage('FTP')
    else:
        win.panel.closePage('FTP')
Mixin.setMixin('notebook', 'OnFtpWindow', OnFtpWindow)

def pref_init(pref):
    pref.ftp_sites = []
    pref.sites_info = {}
    pref.last_ftp_site = 0
    pref.remote_paths = []
Mixin.setPlugin('preference', 'init', pref_init)

def afterclosewindow(win):
    if win.ftp and win.ftp.alive:
        try:
            win.ftp.ftp.quit()
        except:
            error.traceback()
Mixin.setPlugin('mainframe', 'afterclosewindow', afterclosewindow)

def add_ftp_menu(popmenulist):
    popmenulist.extend([ (None, #parent menu id
        [
            (100, 'IDPM_OPEN', tr('Open'), wx.ITEM_NORMAL, 'OnOpen', tr('Opens a file or a directory.')),
            (110, 'IDPM_NEWFILE', tr('New File'), wx.ITEM_NORMAL, 'OnNewFile', tr('Creates a new file.')),
            (120, 'IDPM_NEWDIR', tr('New Directory'), wx.ITEM_NORMAL, 'OnNewDir', tr('Creates a new directory.')),
            (130, 'IDPM_DELETE', tr('Delete'), wx.ITEM_NORMAL, 'OnDelete', tr('Deletes the selected file or a directory.')),
            (140, 'IDPM_RENAME', tr('Rename'), wx.ITEM_NORMAL, 'OnRename', tr('Renames the selected file or a directory.')),
            (150, '-', '', wx.ITEM_SEPARATOR, '', ''),
            (160, 'IDPM_REFRESH', tr('Refresh'), wx.ITEM_NORMAL, 'OnRefresh', tr('Refreshes the current directory.')),
            (170, '-', '', wx.ITEM_SEPARATOR, '', ''),
            (180, 'IDPM_UPLOAD', tr('Upload'), wx.ITEM_NORMAL, 'OnUpload', tr('Uploads a file.')),
            (190, 'IDPM_DOWNLOAD', tr('Download'), wx.ITEM_NORMAL, 'OnDownload', tr('Downloads a file.')),
        ]),
    ])
Mixin.setPlugin('ftpclass', 'add_menu', add_ftp_menu)

def OnOpen(win, event):
    win.OnEnter(event)
Mixin.setMixin('ftpclass', 'OnOpen', OnOpen)

def OnNewFile(win, event):
    win.newfile()
Mixin.setMixin('ftpclass', 'OnNewFile', OnNewFile)

def OnNewDir(win, event):
    win.newdir()
Mixin.setMixin('ftpclass', 'OnNewDir', OnNewDir)

def OnDelete(win, event):
    win.delete()
Mixin.setMixin('ftpclass', 'OnDelete', OnDelete)

def OnRename(win, event):
    win.rename()
Mixin.setMixin('ftpclass', 'OnRename', OnRename)

def OnUpload(win, event):
    win.upload()
Mixin.setMixin('ftpclass', 'OnUpload', OnUpload)

def OnDownload(win, event):
    win.download()
Mixin.setMixin('ftpclass', 'OnDownload', OnDownload)

#ftp(siteno):fullpathfilename
def readfiletext(win, filename, stext):
    import re

    re_ftp = re.compile('^ftp\((\d+)\):')
    b = re_ftp.search(filename)
    if b:
        siteno = int(b.group(1))
        filename = filename.split(':', 1)[1]
        from FtpClass import readfile
        text = readfile(win.mainframe, filename, siteno)
        if text:
            win.needcheckfile = False
            if text is not None:
                stext.append(text)
            else:
                stext.append(None)
            return True, True
        else:
            return True, False
Mixin.setPlugin('editor', 'readfiletext', readfiletext)

def writefiletext(win, filename, text):
    import re

    re_ftp = re.compile('^ftp\((\d+)\):')
    b = re_ftp.search(filename)
    if b:
        siteno = int(b.group(1))
        filename = filename.split(':', 1)[1]
        from FtpClass import writefile
        flag = writefile(win.mainframe, filename, siteno, text)
        return True, True, flag
Mixin.setPlugin('editor', 'writefiletext', writefiletext)

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (127, 'ftp'),
    ])

    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'ftp':(wx.ITEM_CHECK, 'IDM_WINDOW_FTP', 'images/ftp.gif', tr('FTP'), tr('Shows the FTP pane.'), 'OnWindowFtp'),
    })
Mixin.setPlugin('mainframe', 'add_tool_list', add_tool_list)

def getShortFilename(win):
    import re
    import os.path

    if win.title:
        return win.title

    re_ftp = re.compile('^ftp\((\d+)\):')
    b = re_ftp.search(win.filename)
    if b:
        return os.path.basename(win.filename.split(':', 1)[1])
    else:
        return os.path.basename(win.getFilename())
Mixin.setMixin('editor', 'getShortFilename', getShortFilename)
