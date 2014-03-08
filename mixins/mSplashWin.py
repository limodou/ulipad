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
#   $Id: mSplashWin.py 1566 2006-10-09 04:44:08Z limodou $

import wx
from modules import common
from modules import Mixin

def add_pref(preflist):
    preflist.extend([
        (tr('General'), 140, 'check', 'splash_on_startup', tr('Show splash screen at startup'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def beforegui(app):
    splashimg = common.uni_work_file('images/splash.jpg')
    app.splashwin = None
    if app.pref.splash_on_startup:
        app.splashwin = wx.SplashScreen(wx.Image(splashimg).ConvertToBitmap(),
            wx.SPLASH_CENTRE_ON_SCREEN|wx.SPLASH_NO_TIMEOUT, 0, None, -1)
Mixin.setPlugin('app', 'beforegui', beforegui)

def init(pref):
    pref.splash_on_startup = True
Mixin.setPlugin('preference', 'init', init)

def show(mainframe):
    if mainframe.app.splashwin:
        wx.FutureCall(1000, mainframe.app.splashwin.Destroy)
Mixin.setPlugin('mainframe', 'show', show)
