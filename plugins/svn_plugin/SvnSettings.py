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
#   $Id$

import os
import wx
from modules import meide as ui
from modules import Globals
from modules import common
from modules import dict4ini

GLOBAL_IGNORES = '*.pyc *.pyo *.tmp *.bak *.o'
class SVNSettings(wx.Dialog):
    def __init__(self, parent, title=tr('SVN Settings'), size=(450, -1)):
        self.pref = Globals.pref
        try:
            v = self._get_info()
        except:
            raise
        
        wx.Dialog.__init__(self, parent, -1, title=title, size=size)
        
        self.sizer = sizer = ui.VBox(namebinding='widget').create(self).auto_layout()
        box = sizer.add(ui.SimpleGrid)
        box.add(tr('Global ignores'), ui.Text, name='svn_global_ignores')\
            .tooltip(tr('Multiple ignores should be delimeted by space'))
        
        sizer.add(ui.Check(False, tr('Enable proxy server')), name='proxy')\
            .bind('check', self.OnEnable)
        box = sizer.add(ui.VGroup(tr('Proxy settings')))
        grid = box.add(ui.Grid(growablecol=1))
        
        grid.add((0, 0), ui.Label(tr('Server Address')+':'))
        grid.add((0, 1), ui.Text, name='server')
        grid.add((0, 2), ui.Label(tr('Port')+':'))
        grid.add((0, 3), ui.Int(0, size=(40, -1)), name='port')
        grid.add((1, 0), ui.Label(tr('Username')+':'))
        grid.add((1, 1), ui.Text, name='username')
        grid.add((2, 0), ui.Label(tr('Password')+':'))
        grid.add((2, 1), ui.Password, name='password')
        grid.add((3, 0), ui.Label(tr('Proxy timeout in seconds')+':'))
        grid.add((3, 1), ui.Int, name='timeout')
        
        sizer.add(ui.simple_buttons(), flag=wx.ALIGN_CENTER|wx.BOTTOM)
        sizer.bind('btnOk', 'click', self.OnOk)
        self.btnOk.SetDefault()
        
        sizer.auto_fit(1)

        sizer.SetValue(v)
        self.OnEnable(None)

    def OnEnable(self, event=None):
        flag = self.proxy.GetValue()
        self.server.Enable(flag)
        self.port.Enable(flag)
        self.username.Enable(flag)
        self.password.Enable(flag)
        self.timeout.Enable(flag)
    
    def OnOk(self, event):
        self._save_info()
        event.Skip()
        
    def _save_info(self):
        v = self.sizer.GetValue()
        self.pref.svn_proxy_server = v['server']
        self.pref.svn_proxy_port = v['port']
        self.pref.svn_proxy_password = v['password']
        self.pref.svn_proxy_username = v['username']
        self.pref.svn_proxy_timeout = v['timeout']
        self.pref.save()
        
        if wx.Platform == '__WXMSW__':
            from modules import winreg
            try:
                _key = winreg.Key(winreg.HKCU, r'Software\Tigris.org\Subversion\Config')
                if 'miscellany' not in _key:
                    key = _key.add('miscellany')
                else:
                    key = _key['miscellany']
            except:
                common.warn(tr("Maybe your subversion doesn't be installed or installed uncorrectly."))
                raise
            key.values.set('global-ignores', v['svn_global_ignores'])
            
            try:
                key = winreg.Key(winreg.HKCU, r'Software\Tigris.org\Subversion\Servers\global')
            except:
                common.warn(tr("Maybe your subversion doesn't be installed or installed uncorrectly."))
                raise
            
            if v['proxy']:
                key.values.set('http-proxy-host', v['server'])
                key.values.set('http-proxy-port', str(v['port']))
                key.values.set('http-proxy-username', v['username'])
                key.values.set('http-proxy-password', v['password'])
                key.values.set('http-proxy-timeout', str(v['timeout']))
            else:
                for i in range(len(key.values)-1, -1, -1):
                    key.values[i].delete()
        else:
            path = os.path.join(common.getHomeDir(), '.subversion')
            if os.path.exists(path):
                config = os.path.join(path, 'config')
                servers = os.path.join(path, 'servers')
                if os.path.exists(config) and os.path.exists(servers):
                    ini = dict4ini.DictIni(config, normal=True)
                    ini.miscellany['global-ignores'] = v['svn_global_ignores']
                    ini.save()
                    ini = dict4ini.DictIni(servers, normal=True)
                    if v['proxy']:
                        ini['global']['http-proxy-host'] = v['server']
                        ini['global']['http-proxy-port'] = v['port']
                        ini['global']['http-proxy-username'] = v['username']
                        ini['global']['http-proxy-password'] = v['password']
                        ini.save()
                    else:
                        ini['global'] = {}
                        ini.save()
            else:
                common.warn(tr("Maybe your subversion doesn't be installed or installed uncorrectly."))
            
    def _get_info(self):
        v = {}
        v['proxy'] = False
        v['server'] = self.pref.svn_proxy_server
        v['port'] = self.pref.svn_proxy_port
        v['password'] = self.pref.svn_proxy_password
        v['timeout'] = self.pref.svn_proxy_timeout
        v['username'] = self.pref.svn_proxy_username

        if wx.Platform == '__WXMSW__':
            from modules import winreg
            try:
                _key = winreg.Key(winreg.HKCU, r'Software\Tigris.org\Subversion\Config')
                if 'miscellany' not in _key:
                    key = _key.add('miscellany')
                else:
                    key = _key['miscellany']
            except:
                common.warn(tr("Maybe your subversion doesn't be installed or installed uncorrectly."))
                raise
            if 'global-ignores' in key.values:
                v['svn_global_ignores'] = key.values['global-ignores'].getvalue()
            else:
                key.values.set('global-ignores', GLOBAL_IGNORES)
                v['svn_global_ignores'] = key.values['global-ignores'].getvalue()
            
            try:
                key = winreg.Key(winreg.HKCU, r'Software\Tigris.org\Subversion\Servers\global')
            except:
                common.warn(tr("Maybe your subversion doesn't be installed or installed uncorrectly."))
                raise
            
            if 'http-proxy-host' in key.values:
                v['proxy'] = True
                self.pref.svn_proxy_server = v['server'] = key.values['http-proxy-host'].getvalue()
                self.pref.svn_proxy_port = v['port'] = int(key.values['http-proxy-port'].getvalue())
                self.pref.svn_proxy_password = v['password'] = key.values['http-proxy-password'].getvalue()
                self.pref.svn_proxy_timeout = v['timeout'] = int(key.values['http-proxy-timeout'].getvalue())
                self.pref.svn_proxy_username = v['username'] = key.values['http-proxy-username'].getvalue()
                self.pref.save()
        
        else:
            path = os.path.join(common.getHomeDir(), '.subversion')
            if os.path.exists(path):
                config = os.path.join(path, 'config')
                servers = os.path.join(path, 'servers')
                if os.path.exists(config) and os.path.exists(servers):
                    ini = dict4ini.DictIni(config, normal=True)
                    v['svn_global_ignores'] = ini.miscellany.get('global-ignores', GLOBAL_IGNORES)
                    ini = dict4ini.DictIni(servers, normal=True)
                    if ini['global']:
                        v['proxy'] = True
                        self.pref.svn_proxy_server = v['server'] = ini['global'].get('http-proxy-host', '')
                        self.pref.svn_proxy_port = v['port'] = int(ini['global'].get('http-proxy-port', 0))
                        self.pref.svn_proxy_password = v['password'] = ini['global'].get('http-proxy-password', '')
                        self.pref.svn_proxy_username = v['username'] = ini['global'].get('http-proxy-username', '')
                        self.pref.save()
            
        return v
    
def get_global_ignore():
    v = GLOBAL_IGNORES
    if wx.Platform == '__WXMSW__':
        from modules import winreg
        try:
            _key = winreg.Key(winreg.HKCU, r'Software\Tigris.org\Subversion\Config')
            if 'miscellany' not in _key:
                key = _key.add('miscellany')
            else:
                key = _key['miscellany']
        except:
            common.warn(tr("Maybe your subversion doesn't be installed or installed uncorrectly."))
            raise
        if 'global-ignores' in key.values:
            v = key.values['global-ignores'].getvalue()
    
    else:
        path = os.path.join(common.getHomeDir(), '.subversion')
        if os.path.exists(path):
            config = os.path.join(path, 'config')
            servers = os.path.join(path, 'servers')
            if os.path.exists(config) and os.path.exists(servers):
                ini = dict4ini.DictIni(config, normal=True)
                v = ini.miscellany.get('global-ignores', GLOBAL_IGNORES)
    return v