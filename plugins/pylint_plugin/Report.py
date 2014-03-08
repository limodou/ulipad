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

import wx
from pylint.reporters.text import TextReporter
from modules import Globals

_types = {'C':tr('Convention'), 'R':tr('Refactor'), 'W':tr('Warning'), 
    'E':tr('Error'), 'F':tr('Fatal')}
class Report(TextReporter):
    def __init__(self, pane):
        TextReporter.__init__(self)
        self.pane = pane

    def add_message(self, msg_id, location, msg):
        """manage message of different type and in the context of path"""
        module, obj, line = location[1:]
        if obj:
            obj = ':%s' % obj
#        if self.include_ids:
#            sigle = msg_id
#        else:
        sigle = msg_id[0]
            
        pref = Globals.pref
        flag = False
        if pref.pylint_convention and sigle == 'C':
            flag = True
        elif pref.pylint_refactor and sigle == 'R':
            flag = True
        elif pref.pylint_warning and sigle == 'W':
            flag = True
        elif pref.pylint_error and sigle == 'E':
            flag = True
        elif pref.pylint_fatal and sigle == 'F':
            flag = True
        
        if flag:
            wx.CallAfter(self.pane.addline, [location[0], _types.get(sigle, ''), str(line), msg])
