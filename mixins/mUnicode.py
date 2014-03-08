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
#   $Id: mUnicode.py 2081 2007-06-12 08:31:48Z limodou $

__doc__ = 'encoding selection and unicode support'

import re
import StringIO
from modules import Mixin
from MyUnicodeException import MyUnicodeException
from modules.Debug import error
from modules import common

def pref_init(pref):
    pref.auto_detect_utf8 = True
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('Document')+'/'+tr('Edit'), 130, 'check', 'auto_detect_utf8', tr('Autodetect UTF-8 encoding'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def editor_init(win):
    win.locale = win.defaultlocale
Mixin.setPlugin('editor', 'init', editor_init)

def openfileencoding(win, filename, stext, encoding):
    text = stext[0]
    begin = 0
    if text.startswith('\xEF\xBB\xBF'):
        begin = 3
        encoding = 'UTF-8'
    elif text.startswith('\xFF\xFE'):
        begin = 2
        encoding = 'UTF-16'
    if not encoding:
        if filename:
            if win.mainframe.pref.auto_detect_utf8:
                encoding = 'UTF-8'
            else:
                encoding = win.defaultlocale
        else:
            if not encoding and hasattr(win.pref, 'custom_encoding'):
                encoding = win.pref.custom_encoding
            if not encoding and hasattr(win.pref, 'default_encoding'):
                encoding = win.pref.default_encoding
            if not encoding:
                encoding = common.defaultencoding

    try:
        s = unicode(text[begin:], encoding)
        win.locale = encoding
    except:
        if win.mainframe.pref.auto_detect_utf8 and encoding == 'UTF-8':
            encoding = win.defaultlocale
            try:
                s = unicode(text[begin:], encoding, 'replace')
                win.locale = encoding
            except:
                error.traceback()
                raise MyUnicodeException(win, tr("Can't convert file encoding [%s] to unicode!\nThe file can't be opened!") % encoding, tr("Unicode Error"))
        else:
            error.traceback()
            raise MyUnicodeException(win, tr("Can't convert file encoding [%s] to unicode!\nThe file can't be opened!") % encoding, tr("Unicode Error"))
    stext[0] = s
Mixin.setPlugin('editor', 'openfileencoding', openfileencoding)

def savefileencoding(win, stext, encoding):
    text = stext[0]

    if not encoding:
        encoding = win.locale

    if win.languagename == 'python':
        r = re.compile(r'\s*coding\s*[=:]\s*([-\w.]+)')

        buf = StringIO.StringIO(text)
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

    oldencoding = win.locale
    if encoding:
        try:
            s = text.encode(encoding)
            win.locale = encoding
        except:
            error.traceback()
            try:
                s = text.encode(encoding, 'replace')
            except:
                raise MyUnicodeException(win, tr("Can't convert file to [%s] encoding!\nThe file can't be saved!") % encoding,
                    tr("Unicode Error"))
    else:
        s = text
    stext[0] = s
Mixin.setPlugin('editor', 'savefileencoding', savefileencoding)
