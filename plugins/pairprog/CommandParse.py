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

import pickle

class CommandParse(object):
    def call_dumps(funcname, *args, **kwargs):
        buf = [funcname + '\t']
        d = {'tuple':args, 'dict':kwargs}
        s = pickle.dumps(d)
        buf.append(s)
        length = len(funcname) + 1 + len(s)
        buf.insert(0, "%08d" % length)
        return ''.join(buf)
    call_dumps = staticmethod(call_dumps)
    
    def parse_call(s):
        commandname, parameter = s.split('\t', 1)
        d = pickle.loads(parameter)
        return commandname, d
    parse_call = staticmethod(parse_call)