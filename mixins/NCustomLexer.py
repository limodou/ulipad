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
#   $Id$

from LexerBase import *
import re

STYLE_DEFAULT = 1
STYLE_KEYWORD = 2
STYLE_COMMENT = 3
STYLE_INTEGER = 4
STYLE_STRING = 5
STYLE_CUSTOM = 20

PATTERN_NUMBER = r'(\b|[+-]?)(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?\b'
PATTERN_INT = r'(\b|[+-])\d+\b'
PATTERN_DOUBLE_STRING = r'"((?:\\.|[^"])*)?"'
PATTERN_SINGLE_STRING = r"'((?:\\.|[^'])*)?'"
PATTERN_STRING = r'"((?:\\.|[^"])*)?"|\'((?:\\.|[^\'])*)?\''
PATTERN_IDEN = r'\b\w+\b'
PATTERN_EMAIL = r'\b[\w\-_/]+@[\w\-_]+(\.[\w\-_]+)+\b'
PATTERN_URL = r'\b(https?://|ftp://|file://|mailto:)\S+?(?=[^a-zA-Z/0-9.:=&\-%#?_!])'

class TokenList(list):
    def __init__(self, tokens):
        super(TokenList, self).__init__(self._init_tokens(tokens))
        
    def _init_tokens(self, tokens):
        r = []
        for p, s in tokens:
            if isinstance(p, (str, unicode)):
                p_r = re.compile(p, re.DOTALL)
            else:
                p_r = p
            r.append((p_r, s))
        return r

def is_keyword(group=0, style=STYLE_KEYWORD, keywords=[], casesensitive=False):
    def r(win, begin, end, text, matchobj):
        key = matchobj.group(group)
        span = matchobj.span(group)
        if not casesensitive:
            key = key.lower()
        if key in keywords:
            b = matchobj.start()
            return [(span[0]-b, span[1]-b, style)]
        else:
            return STYLE_DEFAULT
    return r
    
class CustomLexer(LexerBase):
    metaname = 'ncustom'
    casesensitive = True
    
    tokens = []
    backstyles = []
    comment_pattern = ''
    comment_begin = '#'
    comment_end = ''
    string_type = 'all' #others can be 'double' and 'single'
    
    def loadToken(self):
        if not self.comment_pattern:
            c_p = re.compile(r'^(%s.*?)%s$' % (self.comment_begin, self.comment_end), re.M)
        else:
            if isinstance(self.comment_pattern, (str, unicode)):
                c_p = re.compile(self.comment_pattern, re.DOTALL)
            else:
                c_p = self.comment_pattern
        if self.string_type == 'all':
            s_p = PATTERN_STRING
        elif self.string_type == 'double':
            s_p = PATTERN_DOUBLE_STRING
        else:
            s_p = PATTERN_STRING
        return TokenList([
            (c_p, STYLE_COMMENT),
            (s_p, STYLE_STRING),
            (PATTERN_NUMBER, STYLE_INTEGER),
            (PATTERN_IDEN, self.is_keyword()),
        ])
    
    def pre_colourize(self, win):
        pass
    
    def load(self):
        super(CustomLexer, self).load()
        if not self.casesensitive:
            self.keywords = [x.lower() for x in self.keywords]
        if not self.backstyles:
            self.backstyles = self.initbackstyle()
    
    def initSyntaxItems(self):
        self.addSyntaxItem('r_default', 'Default',  STYLE_DEFAULT,  self.STC_STYLE_TEXT)
        self.addSyntaxItem('keyword',   'Keyword',  STYLE_KEYWORD,  self.STC_STYLE_KEYWORD1)
        self.addSyntaxItem('comment',   'Comment',  STYLE_COMMENT,  self.STC_STYLE_COMMENT)
        self.addSyntaxItem('integer',   'Integer',  STYLE_INTEGER,  self.STC_STYLE_NUMBER)
        self.addSyntaxItem('string',    'String',   STYLE_STRING,   self.STC_STYLE_STRING)
                                                                    
    def is_keyword(self, group=0, style=STYLE_KEYWORD, keywords=None, casesensitive=None):
        if keywords is None:
            keywords = self.keywords
        if casesensitive is None:
            casesensitive = self.casesensitive
        return is_keyword(group, STYLE_KEYWORD, keywords, casesensitive)
        
    def initbackstyle(self):
        '''
        The element should be (style, matchstring)
        '''
        return []
    
    def _get_begin_pos(self, win):
        '''
        Get a suitable position of beginning
        '''
        begin = win.GetEndStyled()
        
        for i in range(begin, -1, -1):
            style = win.GetStyleAt(i)
            if style:
                begin = i
                break
        
        for i in range(begin, -1, -1):
            es = win.GetStyleAt(i)
            for ls, match in self.backstyles:
                if es == ls:
                    if match:
                        text = win.GetTextRange(i, begin+1).encode('utf-8')
                        if isinstance(match, str):
                            if text.startswith(match):
                                return i
                        elif match.match(text):
                            return i

        begin = win.PositionFromLine(win.LineFromPosition(win.GetEndStyled()))

        return begin
    
    def styleneeded(self, win, pos):
        begin = self._get_begin_pos(win)
        text = win.GetTextRange(begin, pos).encode('utf-8')
        if not text:
            return
        
        if self.tokens:
            tokens = self.tokens
        else:
            tokens = self.loadToken()
        self.render(win, begin, pos, text, tokens)
        
    def render(self, win, begin, end, text, tokens):
        def _process_result(s, win, begin, end, text, matchobj=None):
            step = end - begin
            if not callable(s):
                if isinstance(s, int):
                    self.set_comp_style(win, begin, end, s)
                elif isinstance(s, TokenList):
                    self.render(win, begin, end, text, s)
                elif isinstance(s, (list, tuple)):
                    t = []
                    b = matchobj.start()
                    for group, _s in s:
                        span = matchobj.span(group)
                        _process_result(_s, win, begin+span[0]-b, 
                            begin+span[1]-b, matchobj.group(group))
                        t.append((span[0]-b, span[1]-b, 0))
                    self.set_comp_style(win, begin, end, t)
            else:
                a = s(win, begin, end, text, matchobj)
                self.set_comp_style(win, begin, end, a)
          
        i = 0
        last_begin = -1
        while begin + i < end:
            flag = False
            for p, s in tokens:
                r = p.match(text, i)
                if r:
                    if last_begin > -1:
                        self.set_comp_style(win, last_begin, begin + i, STYLE_DEFAULT)
                        last_begin = -1
                        
                    flag = True
                    step = r.end() - r.start()
                    _process_result(s, win, begin+r.start(), begin+r.end(), 
                        r.group(), r)
                    last_begin = begin+r.end()
                    break
                    
            if not flag:
                if last_begin == -1:
                    last_begin = begin + i
                step = 1
            
            i += step
        
        if last_begin > -1:
            self.set_comp_style(win, last_begin, end, STYLE_DEFAULT)
            
    def set_style(self, win, start, end, style):
        win.StartStyling(start, 0xff)
        win.SetStyling(end - start, style)
        
    def set_comp_style(self, win, begin, end, pos_array):
        if isinstance(pos_array, int):
            if pos_array:
                self.set_style(win, begin, end, pos_array)
            return
        
        pos_array.sort(lambda (aStart, aEnd, aStyle), (bStart, bEnd, bStyle): cmp(aStart, bStart))
        start = begin
        styledEnd = begin
        for (styledStart, styledEnd, style) in pos_array:
            if styledStart + begin > start:
                self.set_style(win, start, styledStart + begin, STYLE_DEFAULT)
                
            #if style==0, then skip, user should execute the render work
            if style:
                self.set_style(win, styledStart + begin, styledEnd + begin, style)
            start = styledEnd + begin + 1
        
        if styledEnd + begin < end:   
            self.set_style(win, styledEnd + begin, end, STYLE_DEFAULT)         
