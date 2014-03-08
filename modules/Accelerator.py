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
#   $Id: Accelerator.py 1634 2006-10-21 09:55:44Z limodou $

import wx
import Id
from Debug import error, debug

keylist = {
'BS'        :wx.WXK_BACK,
'TAB'       :wx.WXK_TAB,
'ENTER'     :wx.WXK_RETURN,
'ESC'       :wx.WXK_ESCAPE,
'PACE'      :wx.WXK_SPACE,
'DEL'       :wx.WXK_DELETE,
'PGUP'      :wx.WXK_PAGEUP,
'PGDN'      :wx.WXK_PAGEDOWN,
'CAP'       :wx.WXK_CAPITAL,
'END'       :wx.WXK_END,
'HOME'      :wx.WXK_HOME,
'LEFT'      :wx.WXK_LEFT,
'UP'        :wx.WXK_UP,
'RIGHT'     :wx.WXK_RIGHT,
'DOWN'      :wx.WXK_DOWN,
'PRINT'     :wx.WXK_PRINT,
'INS'       :wx.WXK_INSERT,
'HELP'      :wx.WXK_HELP,
'NUMPAD0'   :wx.WXK_NUMPAD0,
'NUMPAD1'   :wx.WXK_NUMPAD1,
'NUMPAD2'   :wx.WXK_NUMPAD2,
'NUMPAD3'   :wx.WXK_NUMPAD3,
'NUMPAD4'   :wx.WXK_NUMPAD4,
'NUMPAD5'   :wx.WXK_NUMPAD5,
'NUMPAD6'   :wx.WXK_NUMPAD6,
'NUMPAD7'   :wx.WXK_NUMPAD7,
'NUMPAD8'   :wx.WXK_NUMPAD8,
'NUMPAD9'   :wx.WXK_NUMPAD9,
'ADD'       :wx.WXK_ADD,
'SEPARATOR' :wx.WXK_SEPARATOR,
'SUBTRACT'  :wx.WXK_SUBTRACT,
'MULTIPLY'  :wx.WXK_MULTIPLY,
'DIVIDE'    :wx.WXK_DIVIDE,
'F1'        :wx.WXK_F1,
'F2'        :wx.WXK_F2,
'F3'        :wx.WXK_F3,
'F4'        :wx.WXK_F4,
'F5'        :wx.WXK_F5,
'F6'        :wx.WXK_F6,
'F7'        :wx.WXK_F7,
'F8'        :wx.WXK_F8,
'F9'        :wx.WXK_F9,
'F10'       :wx.WXK_F10,
'F11'       :wx.WXK_F11,
'F12'       :wx.WXK_F12,
'F13'       :wx.WXK_F13,
'F14'       :wx.WXK_F14,
'F15'       :wx.WXK_F15,
'F16'       :wx.WXK_F16,
'F17'       :wx.WXK_F17,
'F18'       :wx.WXK_F18,
'F19'       :wx.WXK_F19,
'F20'       :wx.WXK_F20,
'F21'       :wx.WXK_F21,
'F22'       :wx.WXK_F22,
'F23'       :wx.WXK_F23,
'F24'       :wx.WXK_F24,
'NUMLOCK'   :wx.WXK_NUMLOCK,
}

def create_key(keystr, keylist=keylist):
    f = wx.ACCEL_NORMAL
    ikey=0
    for k in keystr.split('+'):
        uk = k.strip().upper()
        if uk == 'CTRL':
            f |= wx.ACCEL_CTRL
        elif uk == 'ALT':
            f |= wx.ACCEL_ALT
        elif uk == 'SHIFT':
            f |= wx.ACCEL_SHIFT
        elif uk == 'CMD' and hasattr(wx, 'ACCEL_CMD'):
            f |= wx.ACCEL_CMD
        elif keylist.has_key(uk):
            ikey = keylist[uk]
        elif len(uk) == 1:
            ikey = ord(uk)
        else:
            error.error("[accelerator] Error: Undefined char [%s]" % uk)
    return f, ikey

def get_keystring(fkey, keylist=keylist):
    f, ikey = fkey
    s = []
    if f & wx.ACCEL_CTRL:
        s.append('Ctrl')
    if f & wx.ACCEL_SHIFT:
        s.append('Shift')
    if f & wx.ACCEL_ALT:
        s.append('Alt')
    if hasattr(wx, 'ACCEL_CMD')  and f & wx.ACCEL_CMD:
        s.append('Cmd')
       
    key = ''
    for k, v in keylist.items():
        if v == ikey:
            key = k
            break
    if not key:
        key = chr(ikey)
    s.append(key)
    return '+'.join(s)
    
def initaccelerator(win, acceleratorlist):
    ikey = 0

    accelist = []
    debug.info('[accelerator] listing ...')
    for idname, value in acceleratorlist.items():
        keys, func = value
        if not keys:
            continue
        debug.info('%s\t%s' % (keys, idname))
        f, ikey = create_key(keys)
        id = Id.makeid(win, idname)
        accelist.append((f, ikey, id))

    aTable = wx.AcceleratorTable(accelist)
    win.SetAcceleratorTable(aTable)

def getkeycodes(acceleratorlist, klist):
    for idname, value in acceleratorlist.items():
        keys, func = value
        if not keys:
            continue
        
        f, ikey = create_key(keys)
        klist[(f, ikey)] = (idname, func)
