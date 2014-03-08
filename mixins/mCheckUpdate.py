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
#   $Id$

import wx
from modules import Mixin
from modules import Version
from modules import common
from modules.HyperLinksCtrl import HyperLinkCtrl, EVT_HYPERLINK_LEFT
from modules import Globals
from modules import meide as ui

def pref_init(pref):
    pref.check_update = True
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('Update'), 100, 'check', 'check_update', tr('Check for updates at startup'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

class UpdateDialog(wx.Dialog):
    homepage = 'http://code.google.com/p/ulipad/downloads/list'

    def __init__(self, parent, version):
        wx.Dialog.__init__(self, parent, -1, size = (400, 340), style = wx.DEFAULT_DIALOG_STYLE, title = tr('Check Update'))

        box = ui.VBox(padding=6, namebinding='widget').create(self).auto_layout()
        h = box.add(ui.HBox)
        h.add(ui.Label(tr('There is new version %s of UliPad.') % version))

        self.ID_HOMEPAGE = wx.NewId()
        self.homepage = HyperLinkCtrl(self, self.ID_HOMEPAGE, tr("Goto Download page"), URL=self.homepage)
        h.add(self.homepage).bind(EVT_HYPERLINK_LEFT, self.OnDownload)

        box.add(ui.Check(Globals.pref.check_update, tr("Check for updates at startup")), name='chkCheck').bind('check', self.OnCheck)

        box.add(ui.Button(tr("OK"), id=wx.ID_OK), name='btnOk', flag=wx.ALIGN_CENTER|wx.ALL, border=10)
        self.btnOk.SetDefault()

        box.auto_fit(2)

    def OnDownload(self, event):
        common.webopen(self.homepage)

    def OnCheck(self, event):
        Globals.pref.check_update = self.chkCheck.GetValue()

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_HELP', #parent menu id
        [
            (800, 'IDM_HELP_UPDATE', tr('Check For Updates'), wx.ITEM_NORMAL, 'OnHelpCheckUpdate', tr('Check if where is new version of UliPad.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def check_update(force=False):
    from modules import Casing
    import urllib2

    def f():
        from xmlrpclib import ServerProxy, Transport, loads

        class UrllibTransport(Transport):
            def __init__(self, proxy, verbose=0):
                self.proxy = proxy
                self.verbose = verbose
                self.opener = opener = urllib2.OpenerDirector()
                if proxy:
                    opener.add_handler(urllib2.ProxyHandler({'http':self.proxy}))
                else:
                    opener.add_handler(urllib2.ProxyHandler())
                opener.add_handler(urllib2.UnknownHandler())
                opener.add_handler(urllib2.HTTPHandler())
                opener.add_handler(urllib2.HTTPDefaultErrorHandler())
                opener.add_handler(urllib2.HTTPSHandler())
                opener.add_handler(urllib2.HTTPErrorProcessor())

            def request(self, host, handler, request_body, verbose=1):
                f = self.opener.open('http://'+host+handler, request_body)
                u, f = loads(f.read())
                return u

        pref = Globals.pref
        if pref.use_proxy:
            if pref.proxy_user and pref.proxy_password:
                auth = pref.proxy_user + ':' + pref.proxy_password + '@'
            else:
                auth = ''
            proxy = auth + pref.proxy + ':' + str(pref.proxy_port)
        else:
            proxy = None
        try:
            server = ServerProxy("http://ulipad.appspot.com/XMLRPC", transport=UrllibTransport(proxy))
            version = server.version()
            def _f():
                if version > Version.version:
                    dlg = UpdateDialog(Globals.mainframe, version)
                    dlg.ShowModal()
                    dlg.Destroy()
                else:
                    if force:
                        common.showmessage(tr("There is no newer version."))
            wx.CallAfter(_f)
        except Exception, e:
            if force:
                wx.CallAfter(common.showerror, e)

    if not force:
        d = Casing.Casing(f)
        d.start_thread()
    else:
        f()
def OnHelpCheckUpdate(win, event):
    check_update(True)
Mixin.setMixin('mainframe', 'OnHelpCheckUpdate', OnHelpCheckUpdate)

def on_show(win):
    if not Globals.pref.check_update:
        return
    wx.FutureCall(1000, check_update())
Mixin.setPlugin('mainframe', 'show', on_show)