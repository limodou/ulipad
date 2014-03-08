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
#   $Id: mPrint.py 1723 2006-11-20 06:07:51Z limodou $

__doc__ = 'print'

import wx
from modules import Mixin

def add_mainframe_menu(menulist):
    menulist.extend([('IDM_FILE',
        [
            (200, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (210, 'IDM_FILE_PRINT_MENU', tr('Print'), wx.ITEM_NORMAL, '', None),
        ]),
        ('IDM_FILE_PRINT_MENU',
        [
            (100, 'wx.ID_PRINT_SETUP', tr('Page Setup...'), wx.ITEM_NORMAL, 'OnFilePageSetup', tr('Selects a printer and printer connection.')),
            (105, 'IDM_FILE_PRINT_LINENUMBER', tr('Print Line Numbers'), wx.ITEM_CHECK, 'OnFilePrintLineNumber', tr('Prints the line numbers.')),
#            (110, 'IDM_FILE_PRINTER_SETUP', tr('Printer Setup...'), wx.ITEM_NORMAL, 'OnFilePrinterSetup', tr('Selects a printer and printer connection.')),
            (120, 'wx.ID_PREVIEW', tr('Print Preview...'), wx.ITEM_NORMAL, 'OnFilePrintPreview', tr('Displays the document on the screen as it would appear printed.')),
            (130, 'wx.ID_PRINT', tr('Print'), wx.ITEM_NORMAL, 'OnFilePrint', tr('Prints a document.')),
            (140, 'IDM_FILE_HTML', tr('HTML Document'), wx.ITEM_NORMAL, '', None),
        ]),
        ('IDM_FILE_HTML',
        [
            (100, 'IDM_FILE_HTML_PRINT_PREVIEW', tr('HTML Document Preview...'), wx.ITEM_NORMAL, 'OnFileHtmlPreview', tr('Displays the HTML document on the screen as it would appear printed.')),
            (110, 'IDM_FILE_HTML_PRINT', tr('Print HTML Document'), wx.ITEM_NORMAL, 'OnFileHtmlPrint', tr('Prints the current HTML document.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (125, 'print'),
    ])

    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'print':(wx.ITEM_NORMAL, 'wx.ID_PRINT', 'images/printer.gif', tr('Print'), tr('Prints a document.'), 'OnFilePrint'),
    })
Mixin.setPlugin('mainframe', 'add_tool_list', add_tool_list)

def pref_init(pref):
    pref.print_line_number = True
Mixin.setPlugin('preference', 'init', pref_init)

def mainframe_init(win):
    win.printer = None
Mixin.setPlugin('mainframe', 'init', mainframe_init)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_FILE_PRINT_LINENUMBER, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if hasattr(win, 'document') and win.document:
        if eid == win.IDM_FILE_PRINT_LINENUMBER:
            event.Check(win.pref.print_line_number)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

last_printer_type = None
def get_printer(win, t=None):
    global last_printer_type
    if win.printer:
        if t != last_printer_type:
            win.printer.Destroy()
        else:
            return win.printer
    if not t:
        from Print import SimpleDocPrinter
        win.printer = SimpleDocPrinter(win)
    elif t == 'html':
        from Print import MyPrinter
        win.printer = MyPrinter(win)
    last_printer_type = t
        
    return win.printer

def OnFilePrintLineNumber(win, event):
    win.pref.print_line_number = not win.pref.print_line_number
    win.pref.save()
Mixin.setMixin('mainframe', 'OnFilePrintLineNumber', OnFilePrintLineNumber)
    
def OnFilePageSetup(win, event):
    if get_printer(win):
        win.printer.PageSetup()
Mixin.setMixin('mainframe', 'OnFilePageSetup', OnFilePageSetup)

def OnFilePrint(win, event):
    if get_printer(win):
        win.printer.Print(win.document.GetText(), win.document.filename)
Mixin.setMixin('mainframe', 'OnFilePrint', OnFilePrint)

def OnFilePrintPreview(win, event):
    if get_printer(win):
        win.printer.PrintPreview(win.document.GetText(), win.document.filename)
Mixin.setMixin('mainframe', 'OnFilePrintPreview', OnFilePrintPreview)

#def OnFilePrinterSetup(win, event):
#       win.printer.PrinterSetup()
#Mixin.setMixin('mainframe', 'OnFilePrinterSetup', OnFilePrinterSetup)

def OnFileHtmlPreview(win, event):
    if get_printer(win, 'html'):
        win.printer.PreviewText(win.document.GetText(), win.document.filename)
Mixin.setMixin('mainframe', 'OnFileHtmlPreview', OnFileHtmlPreview)

def OnFileHtmlPrint(win, event):
    if get_printer(win, 'html'):
        win.printer.Print(win.document.GetText(), win.document.filename)
Mixin.setMixin('mainframe', 'OnFileHtmlPrint', OnFileHtmlPrint)
