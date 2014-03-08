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
#   $Id$

import sys
import compiler
import wx
from modules.pyflakes import checker
from modules import common
from modules.EasyGuider import EasyList
from modules.Debug import error

def check(codeString, filename):
    message = []
    try:
        codeString = codeString.replace('\r\n', '\n')
        tree = compiler.parse(codeString)
    except (SyntaxError, IndentationError):
        value = sys.exc_info()[1]
        if isinstance(value, Exception):
            lineno = value.lineno
            offset = value.offset
            line = value.text
#            if line and line.endswith("\n"):
#                line = line[:-1]
            message.append((filename, lineno, value.msg))
    except:
        error.traceback()
        message.append((filename, -1, tr('There are some unknown errors, please check error.txt')))
    else:
        w = checker.Checker(tree, filename)
        w.messages.sort(lambda a, b: cmp(a.lineno, b.lineno))
        for warning in w.messages:
            message.append((filename, warning.lineno, warning.message % warning.message_args))

    return message

syntax_pagename = tr('Check Syntax')

def Check(mainframe, document):
    message = []
    if document.filename:
        message = check(document.GetText().encode(document.locale) + '\n\n',
            common.encode_string(document.filename, common.defaultfilesystemencoding))
    else:
        message = check(document.GetText().encode(document.locale) + '\n\n', '<stdin>')
    if mainframe.pref.auto_py_pep8_check:
        pep8check(document, message)
    message.sort()
    mainframe.createSyntaxCheckWindow()
    mainframe.syntaxcheckwindow.adddata(message)
    if message:
        mainframe.panel.showPage(syntax_pagename)
    else:
        mainframe.panel.closePage(syntax_pagename)
        
    wx.CallAfter(document.SetFocus)

class SyntaxCheckWindow(wx.Panel):
    def __init__(self, parent, mainframe):
        wx.Panel.__init__(self, parent, -1)

        self.mainframe = mainframe

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.chkPep8 = wx.CheckBox(self, -1, tr("Check syntax for PEP8-style at python program run"))
        self.chkPep8.SetValue(self.mainframe.pref.auto_py_pep8_check)
        self.sizer.Add(self.chkPep8, 0, wx.ALL, 2)
        self.list = EasyList.AutoWidthListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.list.InsertColumn(0, tr("File path"))
        self.list.InsertColumn(1, tr("Line number"))
        self.list.InsertColumn(2, tr("Description"))
        self.list.SetColumnWidth(0, 400)
        self.list.SetColumnWidth(1, 60)
        self.list.SetColumnWidth(2, 200)

        self.sizer.Add(self.list, 1, wx.EXPAND)

        wx.EVT_LIST_ITEM_ACTIVATED(self.list, self.list.GetId(), self.OnEnter)
        wx.EVT_CHECKBOX(self.chkPep8, self.chkPep8.GetId(), self.OnCheckPep8)

        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)

    def adddata(self, data):
        self.list.DeleteAllItems()
        for i in data:
            filename, lineno, desc = i
            lineno = str(lineno)
            desc = desc.strip()
            index = self.list.InsertStringItem(sys.maxint, filename)
            self.list.SetStringItem(index, 1, lineno)
            self.list.SetStringItem(index, 2, desc)

    def OnEnter(self, event):
        index = event.GetIndex()
        filename = self.list.GetItem(index, 0).GetText()
        lineno = self.list.GetItem(index, 1).GetText()
        self.mainframe.editctrl.new(filename)
        wx.CallAfter(self.mainframe.document.goto, int(lineno))
        
    def OnCheckPep8(self, event):
        self.mainframe.pref.auto_py_pep8_check = event.IsChecked()
        self.mainframe.pref.save()

    def canClose(self):
        return True

def pep8check(editor, message):
    """
    Parse command line options and run checks on Python source.
    """
    from modules import pep8
    from optparse import OptionParser
    import os
    from modules import Globals
    
    pref = Globals.pref
    
    class MyPep8(pep8.Checker):
        def report_error(self, line_number, offset, text, check):
            message.append((self.filename, line_number, text))
            
    options = None
    usage = "%prog [options] input ..."
    parser = OptionParser(usage)
    parser.add_option('-v', '--verbose', default=0, action='count',
                      help="print status messages, or debug with -vv")
    parser.add_option('-q', '--quiet', default=0, action='count',
                      help="report only file names, or nothing with -qq")
    parser.add_option('--exclude', metavar='patterns', default=pep8.default_exclude,
                      help="skip matches (default %s)" % pep8.default_exclude)
    parser.add_option('--filename', metavar='patterns',
                      help="only check matching files (e.g. *.py)")
    parser.add_option('--ignore', metavar='errors', default='',
                      help="skip errors and warnings (e.g. E4,W)")
    parser.add_option('--repeat', action='store_true',
                      help="show all occurrences of the same error")
    parser.add_option('--show-source', action='store_true',
                      help="show source code for each error")
    parser.add_option('--show-pep8', action='store_true',
                      help="show text of PEP 8 for each error")
    parser.add_option('--statistics', action='store_true',
                      help="count errors and warnings")
    parser.add_option('--benchmark', action='store_true',
                      help="measure processing speed")
    parser.add_option('--testsuite', metavar='dir',
                      help="run regression tests from dir")
    parser.add_option('--doctest', action='store_true',
                      help="run doctest on myself")
    options, args = parser.parse_args([editor.getFilename()])
    pep8.options = options
    if options.doctest:
        import doctest
        return doctest.testmod()
    if options.testsuite:
        args.append(options.testsuite)
    if len(args) == 0:
        parser.error('input not specified')
    options.prog = os.path.basename(sys.argv[0])
    options.exclude = options.exclude.split(',')
    for index in range(len(options.exclude)):
        options.exclude[index] = options.exclude[index].rstrip('/')
    if options.filename:
        options.filename = options.filename.split(',')
    if options.ignore:
        options.ignore = options.ignore.split(',')
    else:
        options.ignore = []
    options.counters = {}
    options.messages = {}
#    if pref.py_check_skip_long_line:
#        pep8.maximum_line_length = None
#    if pref.py_check_skip_tailing_whitespace:
#        pep8.trailing_whitespace = None
#    if pref.py_check_skip_blank_lines:
#        pep8.blank_lines = None
    MyPep8(editor.getFilename()).check_all()
