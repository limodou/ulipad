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
#
#   $Id$

import wx
from modules import Casing
from modules import common
from modules.Debug import error

def wrap_run(func, callback=None, begin_msg=tr('Processing...'), end_msg='', finish_msg='Finished!', result=None):
    def f():
        common.setmessage(begin_msg)
        try:
            try:
                func()
                if callback:
                    callback()
            except Exception, e:
                error.traceback()
                common.showerror(str(e))
        finally:
            if result:
                wx.CallAfter(result.finish)
            common.setmessage(end_msg)
    Casing.Casing(f).start_thread()
    
import threading
class CallFunctionOnMainThread:
    def __init__(self, function):
        self.function = function

        self.cv = threading.Condition()
        self.result = None

    def __call__(self, *args):
        self.cv.acquire()

        wx.CallAfter(self._onMainThread, *args)

        self.cv.wait()
        self.cv.release()

        return self.result

    def _onMainThread(self, *args):
        try:
            self.result = self.function(*args)
        finally:
            pass
        
        self.cv.acquire()
        self.cv.notify()
        self.cv.release()
