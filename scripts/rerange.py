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

from modules import common

def rerange(text):
    import re
    r_blank = re.compile(r'\s+')
    lines = text.splitlines(True)
    if len(lines) <= 1:
        return
    s = []
    flag = True
    pos = []
    for line in lines:
        line = line.rstrip()
        if not line: 
            s.append('')
            continue
        strings = ['']#strings
        #append leading blank
        b = r_blank.match(line)
        if b:
            p = b.end()
        else:
            p = 0
        if flag:
            pos.append(p)
        while 1:
            lastp = p
            b = feed(line, p)
            if b:
                p = p + common.string_width(b)
                strings.append(b)
            else:
                break
            b = r_blank.match(line[p:])
            if b:
                p = p + b.end()
            else:
                break
            if flag:
                pos.append(p - lastp)
           
        if flag:
            flag = False
            pos.append(0)
        s.append(''.join([common.hz_string_ljust(x, y) for x, y in zip(strings, pos)]))
    return s

def feed(text, pos):
    s = []
    i = pos
    while i < len(text):
        c = text[i]
        if c != ' ':
            s.append(c)
            if c == "'" or c == '"':
                i += 1
                while 1 or i<len(text):
                    k = text[i]
                    if k == '\\':
                        s.append(c)
                        s.append(text[i+1])
                        i += 2
                    elif k == c:
                        s.append(k)
                        i += 1
                        break
                    else:
                        s.append(k)
                        i += 1
            else:
                i += 1
        else:
            break
    return ''.join(s)

def run(win):
    text = win.document.GetSelectedText()
    if not text: return
    s = rerange(text)
    if s:
        status = win.document.save_state()
        win.document.BeginUndoAction()
        win.document.ReplaceSelection(win.document.getEOLChar().join(s) + win.document.getEOLChar())
        win.document.EndUndoAction()
        win.document.restore_state(status)
        
run(win)
    
if __name__ == '__main__':
    s = rerange("""        self.addSyntaxItem('regex',             'Regex',                wx.stc.STC_C_REGEX,                     self.STE_STYLE_REGEX)
        self.addSyntaxItem('commentlinedoc', 'Comment line doc', wx.stc.STC_C_COMMENTLINEDOC, self.STE_STYLE_COMMENTOTHER)
        """)
    print '\n'.join(s)