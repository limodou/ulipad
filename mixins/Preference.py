#   Programmer: limodou
#   E-mail:     limodou@gmail.com
#
#   Copyleft 2008 limodou
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
#   $Id: Preference.py 1887 2007-02-01 14:03:10Z limodou $

import copy
import os.path
from modules import Mixin
from modules.Debug import debug, error
from modules.EasyGuider import obj2ini
from modules import Globals
import threading

_lock = threading.Lock()

class Preference(Mixin.Mixin):
    __mixinname__ = 'preference'
    preflist = []
    pages_order = {}

    def __init__(self):
        self.initmixin()
        #@add_pref preflist
        self.callplugin_once('add_pref_page', Preference.pages_order)
        self.callplugin_once('add_pref', Preference.preflist)
        self.callplugin('init', self)
        self.preflist.sort()
        
    def get_default_inifile(self):
        return os.path.join(Globals.workpath, 'ulipad.ini')
    
    def clone(self):
        return copy.copy(self)

    def save(self, filename=''):
        _lock.acquire()
        try:
            if not filename:
                filename = self.get_default_inifile()
            try:
                obj2ini.dump(self, filename, encoding='utf-8')
            except:
                try:
                    obj2ini.dump(self, filename)
                except:
                    error.traceback()
        finally:
            _lock.release()

    def load(self, filename=''):
        if not filename:
            filename = self.get_default_inifile()
        if os.path.exists(filename):
            try:
                obj2ini.load(filename, obj=self, encoding='utf-8')
            except:
                try:
                    obj2ini.load(filename, obj=self)
                except:
                    error.traceback()

    def printValues(self):
        debug.info("[preference] member variable...")
        for k, v in self.__dict__.items():
            debug.info('\t', k,'=', v)
        debug.info('[preference] preference dialog member...')
        for v in self.preflist:
            debug.info('\t',v)
