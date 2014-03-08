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
from modules.Debug import error
import StringIO
import re

class UnicodeError(Exception):
    pass

def unicodetext(text, defaultencoding='utf-8'):
    encoding = None
    begin = 0
    
    if text.startswith('\xEF\xBB\xBF'):
        begin = 3
        encoding = 'utf-8'
    if text.startswith('\xFF\xFE'):
        begin = 2
        encoding = 'utf-16'

    if not encoding:
        r = re.compile(r'coding[=:]\s*([-\w.]+)')
        
        buf = StringIO.StringIO(text[begin:])
        while 1:
            line = buf.readline()
            if not line: break
            line = line.rstrip()
            if line.startswith('#!'):
                continue
            if line.startswith('#'):
                b = r.search(line[1:])
                if b:
                    encoding = b.groups()[0]
                    break
            if not line:
                continue
            else:
                break
    
    if not encoding:
        if defaultencoding:
            encoding = defaultencoding
        else:
            encoding = common.defaultencoding
    
    try:
        s = unicode(text[begin:], encoding)
    except:
        encoding = common.defaultencoding
        try:
            s = unicode(text[begin:], encoding, 'replace')
        except:
            error.traceback()
            raise UnicodeError('Unicode error')
    return s, encoding
    