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
#   $Id$

import os
import wx
import inspect
from modules import Globals
from modules.Debug import error
from modules import common
from modules import dict4ini

_commands = {} #key=command_id value={'caption': 'shortcut':, 'target':mainframe|editor|or others, 'command', 'commands', 'impact':}

_instance = None

_cmdfile = 'commands.ini'
_cmdfile_fmttime = None

def getinstance():
    global _instance, _cmdfile_fmttime
    filename = common.getConfigPathFile(_cmdfile)
    if not _instance or _cmdfile_fmttime < os.path.getmtime(filename):
        _instance = Commands(filename)
        _cmdfile_fmttime = os.path.getmtime(filename)
    return _instance

def _get_target(target):
    if target == 'mainframe':
        return Globals.mainframe
    if target == 'editor':
        return Globals.mainframe.document
   
def addcmd(target, cmd_id, caption, func, shortcut='', impact=''):
    if not cmd_id:
        cmd_id = caption
    _commands[cmd_id] = {'caption': caption, 'shortcut':shortcut, 'target':target, 'func':func, 'impact':impact}
    
def addcmds(cmd_id, caption, commands, impact=''):
    if not cmd_id:
        cmd_id = caption
    _commands[cmd_id] = {'caption': caption, 'shortcut':'', 'target':'', 'func':'', 'commands':commands, 'impact':impact}

class Commands(object):
    def __init__(self, filename):
        self.impacts = {}
        self.searchbuf = self.getdata(filename)
        self.searchbuf.sort()
        
    def getdata(self, filename):
        s = []
        ini = dict4ini.DictIni(filename)
        for k, v in ini.default.items():
            _commands[k] = dict(zip(['target', 'caption', 'shortcut', 'impact', 'func'], v))
        for k, v in ini.commands.items():
            _commands[k] = dict(zip(['caption', 'commands', 'impact'], [v[0], v[1].split('|'), v[2]]))
        for k, v in _commands.items():
            s.append((v['caption'], v['shortcut'], v['impact'], k))
            if v['impact']:
                self.impacts[v['impact']] = k
        return s
    
    def search(self, info):
        if not info:
            return self.searchbuf
        else:
            s = []
            for v in self.searchbuf:
                t = v[0] + v[1]
                p = strin(info, t)
                if p:
                    s.append((p, v))
            s.sort()
            s.reverse()
            s = [y for x, y in s]
            return s
        
    def impact_search(self, info):
        if not info:
            return self.searchbuf
        else:
            s = []
            for k, cmd_id in self.impacts.items():
                if k.startswith(info):
                    cmd = _commands[cmd_id]
                    s.append((cmd['caption'], cmd['shortcut'], cmd['impact'], cmd_id))
            s.sort()
            return s
            
    def run(self, cmd_id):
        v = _commands.get(cmd_id, None)
        if v:
            win = _get_target(v['target'])
            func = v['func']
            para = None
            if func.find(':') > -1:
                func, para = func.split(':', 1)
            f = getattr(win, func, None)
            if f:
                args = len(inspect.getargspec(f)[0])
                def fn():
                    try:
                        if args == 2:
                            f(para)
                        else:
                            f()
                        if v['target'] == 'editor':
                            win.EnsureCaretVisible()
                    except:
                        error.traceback()
                        common.warn("There is some wrong when run the command")
                wx.CallAfter(fn)
        
def strin(s, text):
    if not s:
        return
    result = []
    t = text.lower()
    s = s.lower()
    def f(s, t, r, pos=-1):
        k = pos
        while 1:
            k = t.find(s[0], k+1)
            if k > -1:
                if s[1:]:
                    f(s[1:], t, r+[k], k)
                else:   #finish
                    result.append(r+[k])
            else:
                return
    f(s, t, [])
    if not result:
        return
    def cal(p):
        maxlen = 1
        l = 1
        i = p[0]
        for k in p[1:]:
            if k == i+1:
                l += 1
                i = k
            else:
                i = k
                l = 1
            if l > maxlen:
                maxlen = l
        return maxlen
    maxlen = max(map(cal, result))
    return maxlen
