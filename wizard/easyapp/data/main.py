from meteor import *

app = T('''#coding=<#encoding#>

import sys
import getopt
import os.path
import traceback
import wx

__appname__ = '<#appname#>'
__author__ = '<#author#>'
__version__ = '<#version#>'

class wxApp(wx.App):
    def OnInit(self):
        return True

class MainApp:
    def __init__(self):
        pass

    def run(self):
        self.initlog()
        self.wxApp = wxApp(0)
        self.processCommandLineArguments()
        self.frame = self.initframe()
        self.frame.Show()
        self.wxApp.SetTopWindow(self.frame)
        self.wxApp.mainframe = self.frame
        self.wxApp.log =  self.frame
        self.wxApp.MainLoop()

    def initframe(self):

        import MainFrame

        return MainFrame.MainFrame(u'<#mainframetitle#>')

    def initlog(self):
        import logging
        self.log = log = logging.getLogger('<#appname#>')
        hdlr = logging.FileHandler('<#appname#>.log')
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        hdlr.setFormatter(formatter)
        log.addHandler(hdlr)
        log.setLevel(logging.WARNING)

        def trace():
            message = traceback.format_exception(*sys.exc_info())
            log.error(''.join(message))

        log.traceback = trace

    def processCommandLineArguments(self):
        #process command line

        cmdstring = "Vu"

        try:
            opts, args = getopt.getopt(sys.argv[1:], cmdstring, [])
        except getopt.GetoptError:
            self.Usage()
            sys.exit(1)

        for o, a in opts:
            if o == '-V':       #version
                self.Version()
                sys.exit()
            elif o == '-u':       #version
                self.Usage()
                sys.exit()

    def Usage(self):
        print """Usage %s [options]

    -V      Show version
    -u      Show usage
    """ % sys.argv[0]

    def Version(self):
        print """%s Copyleft GPL
Author: %s
Version: %s""" % (__appname__, __author__, __version__)


main = MainApp()
main.run()
''')
