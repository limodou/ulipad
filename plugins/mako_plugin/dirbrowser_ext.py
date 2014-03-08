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

from modules import common
from modules import Mixin

project_names = ['mako']
Mixin.setMixin('dirbrowser', 'project_names', project_names)

def set_project(ini, projectnames):
    if 'mako' in projectnames:
        common.set_acp_highlight(ini, '.mko', ['html.acp', 'makohtml.acp'], 'makotmp')
Mixin.setPlugin('dirbrowser', 'set_project', set_project)

def remove_project(ini, projectnames):
    if 'mako' in projectnames:
        common.remove_acp_highlight(ini, '.mko', ['html.acp', 'makohtml.acp'], 'makotmp')
Mixin.setPlugin('dirbrowser', 'remove_project', remove_project)
