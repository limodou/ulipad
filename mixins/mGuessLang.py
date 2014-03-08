#   Programmer: limodou, zhangchunlin
#   E-mail:     limodou@gmail.com, zhangchunlin@gmail.com
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

import re
from modules import Mixin

r_lang = re.compile('^#!\s*/usr/bin/env\s+(\w+)')
def guess_language(win, language):
    l = win.GetLine(0).lower()
    lang = language
    if not lang and l[:2]=="#!":
        b = r_lang.search(l)
        if b:
            lang = b.groups()[0]

    return lang
Mixin.setPlugin('editor', 'guess_lang', guess_language)

