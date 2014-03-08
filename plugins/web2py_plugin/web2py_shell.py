#   Programmer: limodou
#   E-mail:     limodou@gmail.com
#
#   Copyleft 2008 limodou
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

import os
from mixins.ShellWindow import ShellWindow

class Web2pyShell(ShellWindow):
    def set_locals(self, dir, appname, reload=True):
#        os.chdir(dir)
        import shell
        import types
        
        locals = shell.env(appname, dir=dir)
        if reload:
            for k, v in locals.items():
                if isinstance(v, types.ModuleType):
                    reload(v)
        self.interp.locals = locals