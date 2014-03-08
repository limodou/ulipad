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
#   $Id: LexerFactory.py 1457 2006-08-23 02:12:12Z limodou $

__doc__ = 'Lexer control'

from modules import Mixin

class LexerFactory(Mixin.Mixin):
    __mixinname__ = 'lexerfactory'

    lexers = [] #(name, filewildchar, stxfile, lexerclass)
    lexnames = []
    lexshownames = []

    def __init__(self, mainframe):
        self.initmixin()

        self.mainframe = mainframe
        self.pref = mainframe.pref
        self.lexobjs = []

        #@add_lexer name, filewildchar, stxfile, lexerclass
        self.callplugin_once('add_lexer', LexerFactory.lexers)

        self.lexers.sort(lambda x, y: cmp(x[1].lower(), y[1].lower()))
        s = []
        for name, filewildchar, syntaxtype, stxfile, lexerclass in self.lexers:
            lexobj = lexerclass(name, filewildchar, syntaxtype, stxfile)
            self.lexobjs.append(lexobj)
            n = filewildchar.split('|', 1)[0]
            LexerFactory.lexnames.append((n, name))
            s.append(lexobj.getFilewildchar())
        self.mainframe.filewildchar.extend(s)

    def reset(self):
        for obj in self.lexobjs:
            obj.init()
            
    def items(self):
        return self.lexobjs

    def getDefaultLexer(self):
        obj = None
        for i, v in enumerate(self.lexnames):
            n, name = v
            if name == self.pref.default_lexer:
                obj = self.lexobjs[i]
                break
        
        if not obj:
            obj = self.lexobjs[self.lexnames.index('text')]
            self.pref.default_lexer = 'text'
            self.pref.save()

        return obj

    def getNamedLexer(self, name):
        obj = None
        for i, v in enumerate(self.lexnames):
            n, lexername = v
            if name == lexername:
                obj = self.lexobjs[i]
                break
        return obj
    
    def getLexerNames(self):
        s = []
        for v in self.lexnames:
            n, name = v
            s.append(n)
        s.sort(lambda x, y: cmp(x.lower(), y.lower()))
        return s