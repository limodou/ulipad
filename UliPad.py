#!/usr/bin/env python
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
#   $Id: UliPad.py 2009 2007-03-06 00:38:09Z limodou $

__appname__ = 'UliPad'
__author__ = 'limodou'

import getopt
import sys
import wx
import os
from modules import common
from modules import Debug
from modules import i18n
from modules import Globals

DEBUG = True

workpath = os.path.dirname(os.path.realpath(sys.argv[0]))
confpath = os.path.join(workpath, 'conf')
sys.path.insert(0, workpath)
sys.path.insert(0, os.path.join(workpath, 'modules'))
sys.path.insert(0, os.path.join(workpath, 'plugins'))
sys.path.insert(0, os.path.join(workpath, 'packages'))
curpath = os.getcwd()
os.chdir(workpath)
Globals.workpath = workpath
Globals.confpath = confpath

ini = common.get_config_file_obj()
debugflag = ini.default.get('debug', False)

#add pythonpath settings
if ini.default.has_key('pythonpath'):
    pythonpath = ini.default.pythonpath
    if isinstance(pythonpath, list):
        sys.path = pythonpath + sys.path
    elif isinstance(pythonpath, (str, unicode)):
        sys.path.insert(0, pythonpath)
    else:
        print 'The pythonpath should be a string list or a string.'

common.print_time('begin...', DEBUG)

Debug.debug = Debug.Debug(os.path.join(workpath, 'debug.txt'), debugflag)
Debug.error = Debug.Debug(os.path.join(workpath, 'error.txt'), True)

#hook global exception
def myexcepthook(type, value, tb):
    Debug.error.traceback((type, value, tb))
sys.excepthook = myexcepthook

#install i18n package
i18n = i18n.I18n('./lang', keyfunc='tr')
#ini = dict4ini.DictIni(os.path.join(workpath, 'config.ini'))
if ini.language.get('default', None) is not None:
    i18n.install(ini.language.default)

from modules import Mixin

Mixin.setlog(Debug.error)

#import mixins
try:
    import mixins
except:
    Debug.error.traceback()
    print "There are some errors as importing mimxins, Please see the error.txt."
    sys.exit(0)

class wxApp(wx.App):
    def OnInit(self):
        return True

app = None

class App(Mixin.Mixin):
    __mixinname__ = 'app'

    def __init__(self):
        global app

        app = self
        import __builtin__
        __builtin__.__dict__['app'] = app

        self.initmixin()

        self.appname = __appname__
        self.author = __author__

        Globals.app = self

        self.wxApp = wxApp(0)

        self.frame = self.init()

        self.frame.Show()
        self.wxApp.SetTopWindow(self.frame)

        common.print_time('end...', DEBUG)

        self.wxApp.MainLoop()

    def init(self, showSplash=True, load=True):

        #add modules path to sys.path
        self.workpath = workpath
        self.confpath = confpath
        self.curpath = curpath
        self.i18n = i18n

        self.processCommandLineArguments()

        if self.psycoflag:
            try:
                import psyco
                psyco.full()
            except:
                pass

        #change workpath
        self.userpath = self.workpath
        if self.multiuser:
            self.userpath = common.getHomeDir()

        #set globals variable
        Globals.userpath = self.userpath

        self.CheckPluginDir()

        Mixin.ENABLE = True
        try:
            import plugins
        except:
            Debug.error.traceback()
            common.showerror(None, tr('There was something wrong with importing plugins.'))

        #before running gui
        self.callplugin("beforegui", self)

        Mixin.ENABLE = False
        #-----------------------------------------------------------------------------

        if Debug.DEBUG:
            Mixin.printMixin()

        return self.execplugin('getmainframe', self, self.files)

    def processCommandLineArguments(self):
        #process command line
        try:
            opts, args = getopt.getopt(sys.argv[1:], "e:E:vuhnsfm", [])
        except getopt.GetoptError:
            self.Usage()
            sys.exit(2)
#        self.defaultencoding = common.defaultencoding   #defaultencoding in common.py

        self.ddeflag = True
        self.psycoflag = False
        self.skipsessionfile = False
        self.multiuser = False

        for o, a in opts:
            if o == '-e':       #encoding
                common.defaultencoding = a
                common.defaultfilesystemencoding = a
            elif o == '-E':       #encoding
                common.defaultfilesystemencoding = a
            elif o == '-v':     #version
                self.Version()
                sys.exit()
            elif o == '-u' or o == '-h':     #usage
                self.Usage()
                sys.exit()
            elif o == '-n':     #no dde
                self.ddeflag = False
            elif o == '-s':
                self.psycoflag = True
            elif o == '-f':
                self.skipsessionfile = True
            elif o == '-m':
                self.multiuser = True
        files = args

        self.files = [common.decode_string(os.path.join(self.curpath, f)) for f in files]
        self.callplugin('dde', self, self.files)

    def quit(self):
        self.wxApp.ProcessIdle()
        self.wxApp.Exit()

    def Usage(self):
        print """Usage %s -u|-v|-n|[-e encoding]|-s|-f|-m files ...

        -u Show this message
        -v Show version information
        -n Disable DDE support
        -e encoding Set default encoding which will be used in UliPad
        -E encoding Set default system encoding which will be used in UliPad
        -s Enable psyco speed support
        -f Skip last session files
        -m Multi user mode, data file will be saved in user home directory
    """ % sys.argv[0]

    def Version(self):
        from modules import Version

        print """%s Copyleft GPL
Author: %s
Version: %s""" % (__appname__, __author__, Version.version)

    def CheckPluginDir(self):
        pluginpath = os.path.join(self.workpath, 'plugins')
        if not os.path.exists(pluginpath):
            os.mkdir(pluginpath)
        if not os.path.exists(os.path.join(pluginpath, '__init__.py')):
            file(os.path.join(pluginpath, '__init__.py'), 'w').write("""#   Programmer: limodou
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

__doc__ = 'Plugins __init__.py'

""")

if __name__ == '__main__':
    App()
