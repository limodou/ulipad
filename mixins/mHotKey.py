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
#   $Id: mHotKey.py 1566 2006-10-09 04:44:08Z limodou $

from modules import Mixin
from modules import common
from modules.Debug import error

def init_accelerator(win, accellist, editoraccellist):
    ini = common.get_config_file_obj(onelevel=True)
    
    keylist = {}
    for mid, v in accellist.items():
        keys, func = v
        if not keys:
            continue
        if not keys in keylist:
            keylist[keys] = (mid, 'main')
        else:
            error.error('There is already %s defined! Please check.' % keys)

    for mid, v in editoraccellist.items():
        keys, func = v
        if not keys in keylist:
            keylist[keys] = (mid, 'editor')
        else:
            error.error('There is already %s defined! Please check.' % keys)
    
    #mid can be a mainframe menu ID or a mainframe function name
    #which should only has one parameter
    for mid, hotkey in ini.main_hotkey.items():
        _id, _t = keylist.get(hotkey, ('', ''))
        if _id:
            if _t == 'main':
                keys, func = accellist[_id]
                accellist[_id] = ('', func)
            else:
                keys, func = editoraccellist[_id]
                editoraccellist[_id] = ('', func)
            
        if mid in editoraccellist:
            keys, func = editoraccellist[mid]
            del editoraccellist[mid]
            accellist[mid] = (hotkey, func)
        elif mid in accellist:
            keys, func = accellist[mid]
            accellist[mid] = (hotkey, func)

    #mid can be a editor menu ID or a editor function name
    #which should only has one parameter
    for mid, hotkey in ini.editor_hotkey.items():
        _id, _t = keylist.get(hotkey, ('', ''))
        if _id:
            if _t == 'main':
                keys, func = accellist[_id]
                accellist[_id] = ('', func)
            else:
                keys, func = editoraccellist[_id]
                editoraccellist[_id] = ('', func)
            
        if accellist.has_key(mid):
            keys, func = accellist[mid]
            del accellist[mid]
            editoraccellist[mid] = (hotkey, func)
        elif editoraccellist.has_key(mid):
            keys, func = editoraccellist[mid]
            editoraccellist[mid] = (hotkey, func)
Mixin.setPlugin('mainframe', 'init_accelerator', init_accelerator)
