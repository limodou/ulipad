#   Programmer: limodou
#   E-mail:     limodou@gmail.com
#
#   Copyleft 2006 limodou
#
#   Distributed under the terms of the GPL (GNU Public License)
#
#   NewEdit is free software; you can redistribute it and/or modify
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

class EasyException(Exception):pass

class EMPTY_CLASS:pass

import wx

import locale
import types

def str_object(obj, encoding=None):
    if not encoding:
        encoding = locale.getdefaultlocale()[1]
    if isinstance(obj, (int, float, bool)):
        return str(obj)
    elif isinstance(obj, str):
        return obj
    elif isinstance(obj, unicode):
        return obj.encode(encoding)
    elif isinstance(obj, tuple):
        return tuple(str_object(list(obj), encoding))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            obj[i] = str_object(v, encoding)
        return obj
    elif isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = str_object(value, encoding)
        return obj
    else:
        return obj  #can't deal class instance

def getimage(imageobj):
    if isinstance(imageobj, (str, unicode)):
        image = wx.Image(imageobj).ConvertToBitmap()
    elif isinstance(imageobj, types.FunctionType):
        image = imageobj()
    else:
        image = imageobj
    return image
