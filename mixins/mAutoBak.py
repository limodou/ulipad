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
#   $Id: mAutoBak.py 1897 2007-02-03 10:33:43Z limodou $

__doc__ = 'auto make bak file as open a file'

from modules import Mixin
from modules import common

def add_pref(preflist):
    preflist.extend([
        (tr('Document')+'/'+tr('Back-End'), 100, 'check', 'auto_make_bak', tr('Make file backup at opening a file'), None)
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def pref_init(pref):
    pref.auto_make_bak  = False
Mixin.setPlugin('preference', 'init', pref_init)

def openfile(win, filename):
    import shutil

    if filename and win.pref.auto_make_bak:
        bakfile = filename + '.bak'
        try:
            shutil.copyfile(filename, bakfile)
        except Exception, mesg:
            common.showerror(win, mesg)
Mixin.setPlugin('editor', 'openfile', openfile, Mixin.HIGH, 0)
