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

from modules import Mixin

def pref_init(pref):
    pref.use_proxy = False
    pref.proxy = ''
    pref.proxy_port = 8000
    pref.proxy_user = ''
    pref.proxy_password = ''
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):

    def _get(name):
        def _f(name=name):
            from modules import Globals
            return getattr(Globals.pref, name)
        return _f

    from modules import meide as ui
    box = ui.VGroup(tr('Network'))
    grid = ui.SimpleGrid()
    grid.add('', ui.Check(_get('use_proxy'), tr('Use a proxy')), name='use_proxy', span=True)
    grid.add(tr('IP address:'), ui.Text(_get('proxy')), name='proxy')
    grid.add(tr('Port number:'), ui.Int(_get('proxy_port')), name='proxy_port')
    grid.add(tr('Username:'), ui.Text(_get('proxy_user')), name='proxy_user')
    grid.add(tr('Password:'), ui.Password(_get('proxy_password')), name='proxy_password')
    box.add(grid)
#    preflist.extend([
#        (tr('Network'), 100, 'check', 'use_proxy', tr('Use proxy'), None),
#        (tr('Network'), 110, 'text', 'proxy', tr('Proxy URL:'), None),
#        (tr('Network'), 120, 'text', 'proxy_user', tr('Proxy User:'), None),
#        (tr('Network'), 130, 'password', 'proxy_password', tr('Proxy Password:'), None),
#    ])
    preflist.extend([
        (tr('Network'), 100, box, '', '', {'span':True}),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)
