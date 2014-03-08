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

from EasyUtils import EasyException

class IElement(object):
    def __init__(self, parent, type, message='', externinfo=None, size=None, enabledflag=None):
        """create the control"""
        self.parent = parent
        self.type = type
        self.obj = None
        self.enabledflag = enabledflag
        if self.enabledflag is not None:
            self.enabled = self.enabledflag
        else:
            self.enabled = None
        self.externinfo = externinfo
        self.checkbox = None

    def getType(self):
        return self.type

    def setValue(self, value):
        raise EasyException, "Not implemented!"

    def getValue(self):
        raise EasyException, "Not implemented!"

    def isLarge(self):
        return False

    def getObject(self):
        return self.obj

    def getContainer(self):
        return self.obj

    def getAlignFlag(self, flag):
        return flag

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return repr(self.getValue())

    def setEnabled(self, flag):
        if flag is not None:
            self.enabled = flag
            self.obj.Enable(flag)

    def getEnabled(self):
        return self.enabled

    def getEnabledFlag(self):
        return self.enabledflag is not None
