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
#   $Id: PyParse.py 1908 2007-02-07 00:45:02Z limodou $


import tokenize # Python tokenizer
import token
import StringIO
import re
import sys

try:
    set
except:
    from sets import Set as set
    
INDENT = ' '*4
ONLY_ONE_NAME = True    #if there are many identifier definition, when ONLY_ONE_NAME is True, only one will add to locals

class Node(object):
    def __init__(self, parent=None, name='', type='', info='', lineno=-1, span=[]):
        self.parent = parent
        self.name = name
        self.type = type
        self.lineno = lineno
        self.info = info
        if span:
            self.span = span
        else:
            self.span = [lineno]
        self.items = []
        self.values = []
        self.lines = []
        self.locals = []
        self.local_types = []
        self.importlines = []

    def set_lines(self, lines):
        self.lines = lines

    def add(self, name, value):
        self.items.append(name)
        self.values.append(value)
        return value

    def find(self, name):
        try:
            index = self.items.index(name)
        except ValueError:
            index = -1
        if index > -1:
            return self.values[index]
        else:
            return None

    def get_text(self):
        obj = self
        while obj.parent:
            obj = obj.parent
        lines = obj.lines
        if len(self.span) == 1:
            return lines[self.span[0]-1]
        else:
            return '\n'.join(lines[self.span[0]-1:self.span[1]-1])

    def is_in(self, lineno):
        if len(self.span) == 2:
            return self.span[0] <= lineno < self.span[1]
        else:
            return self.lineno == lineno

    def guess_class(self, lineno, name=''):
        nodes = self.guess(lineno)
        for n in nodes:
            if n.type == 'class':
                if name:
                    if n.name == name:
                        return n
                else:
                    return n
        return None
    
    def guess_function(self, lineno, name=''):
        nodes = self.guess(lineno)
        for n in nodes:
            if n.type == 'function':
                if name:
                    if n.name == name:
                        return n
                else:
                    return n
        return None

    def search_name(self, lineno, word):
        if not word:
            return
        nodes = []
        if word.startswith('self.'):
            word = word[5:]
            node = self.guess_class(lineno)
            if node:
                nodes.append(node)
                for n in node.bases:
                    r = self.search_name(node.lineno, n)
                    if r:
                        t, v, line = r
                        cls = self.guess_class(line)
                        if cls:
                            nodes.append(cls)
                    
        else:
            ns = self.guess(lineno)
            if not ns or ns[-1] is not self:
                ns.append(self)
            for n in ns:
                if word in n.locals:
                    nodes.append(n)
                    break
        if nodes:
            for node in nodes:
                t, v, line = None, None, None
                flag = False
                for i in range(len(node.locals)-1, -1, -1):
                    w = node.locals[i]
                    if w == word:
                        t, v, line = node.local_types[i]
                        if t == 'reference' and w == v: #name is not be the same in locals
                            break
                        else:
                            flag = True
                            break
                if flag and t:
                    return t, v, line
        else:
            return None
        
    def guess(self, lineno):
        nodes = []
        if self.is_in(lineno):
            nodes.append(self)
        for obj in self.values:
            if hasattr(obj, 'guess') and callable(obj.guess):
                nodes.extend(obj.guess(lineno))
        nodes.reverse()
        return nodes
    
    def guess_type(self, lineno, word, stack=None):
        if not stack:
            stack = []
        else:
            for k, line, t, v in stack:
                if k == word:
                    return t, v
        if word == 'self': #it's a class
            cls = self.guess_class(lineno)
            if cls:
                return cls.type, cls
            else:
                return None
        
        r = self.search_name(lineno, word)
        if r:
            t, v, line = r
            if t == 'reference':    #need to find others
                if v == 'self': #it's a class
                    cls = self.guess_class(line)
                    if cls:
                        return cls.type, cls
                    else:
                        return None
                stack.append((word, line, t, v))
                gt = self.guess_type(lineno, v, stack)
                if not gt:
                    return t, v
                else:
                    return gt
            else:
                return t, v
        return None
    
    def get_locals(self, lineno):
        nodes = self.guess(lineno)
        if not nodes or nodes[-1] is not self:
            nodes.append(self)
        s = []
        for n in nodes:
            if n.type == 'class':
                continue
            for i in n.locals:
                if i not in s:
                    s.append(i)
        return s
    
    def get_local_name(self, name):
        for i in range(len(self.locals)-1, -1, -1):
            w = self.locals[i]
            if w == name:
                t, v, line = self.local_types[i]
                return t, v, line
        return None

    def __str__(self):
        s = []
        s.append("[name=%s,type=%s,span=%r,info=%s]" % (self.name, self.type, self.span, self.info))
        return ''.join(s)
    
    def add_local(self, name, type=None, value=None, lineno=None):
        if ONLY_ONE_NAME:
            if not self.get_local_name(name):
                self.locals.append(name)
                self.local_types.append((type, value, lineno))
        
    def add_import(self, info, lineno):
        self.importlines.append((info, lineno))
        
    def output(self, indent=''):
        if self.name:
            print indent, '-'*50
            print indent, '# ', self.type, ':', self.name, '(', self.info, self.span, ')'
            print indent, '-'*50
        if self.locals:
            print indent, 'locals:'
            for i, n in enumerate(self.locals):
                print indent+INDENT, n, '(', ', '.join(map(str, self.local_types[i])), ')'
        for v in self.values:
            if hasattr(v, 'output'):
                v.output(indent+INDENT)
            else:
                print v
            
    def get_imports(self, lineno):
        nodes = self.guess(lineno)
        if not nodes or nodes[-1] is not self:
            nodes.append(self)
        s = []
        for n in nodes:
            s.extend(n.importlines)
        return s
        
 
r_fpara = re.compile(r'\((.*?)\)')
r_para = re.compile(r'([\w\d]+)')
r_value = re.compile(r'\s*=\s*(.*)')
r_indent = re.compile(r'[\w\d.]+')
class FuncNode(Node):
    def __init__(self, parent=None, name='root', type='root', info='', lineno=-1, span=[]):
        super(FuncNode, self).__init__(parent, name, type, info, lineno, span)
        self.parse_parameter()
        self.docstring = ''
        
    def parse_parameter(self):
        b = r_fpara.search(self.info)
        if not b:
            return
        paras = b.groups()[0].split(',')
        for p in paras:
            p = p.strip()
            if p == 'self':
                continue
            b = r_para.match(p)
            if b:
                v = b.groups()[0]
                valuetype = None
                vvalue = None
                t = p[b.end():]
                #analysis parameter
                if t:
                    b = r_value.search(t)
                    if b:
                        value = b.groups()[0]
                        if value:
                            if value.isdigit():
                                valuetype = 'int'
                                vvalue = int
                            elif value[0] in ('"', "'"):
                                valuetype = 'str'
                                vvalue = str
                            elif value[:2] in ('u"', "u'", 'r"', "r'"):
                                valuetype = 'str'
                                vvalue = str
                            elif value[0] == '[':
                                valuetype = 'list'
                                vvalue = list
                            elif value[0] == '(':
                                valuetype = 'tuple'
                                vvalue = tuple
                            elif value[0] == '{':
                                valuetype = 'dict'
                                vvalue = dict
                            elif value in ('True', 'False'):
                                valuetype = 'bool'
                                vvalue = bool
                            else:
                                b = r_indent.match(value)
                                if b:
                                    valuetype = 'reference'
                                    vvalue = b.group()
                self.add_local(v, valuetype, vvalue, self.lineno)

    def __str__(self):
        s = []
        s.append("[name=%s,type=%s,span=%r,info=%s,docstring=%s]" % (self.name, self.type, self.span, self.info, self.docstring))
        return ''.join(s)
    
class ClassNode(Node):
    def __init__(self, parent=None, name='', type='', info='', lineno=-1, span=[]):
        super(ClassNode, self).__init__(parent, name, type, info, lineno, span)
        self.parse_bases()
        self.docstring = ''
    
    def parse_bases(self):
        self.bases = []
        b = r_fpara.search(self.info)
        if not b:
            return
        self.bases = b.groups()[0].split(',')
 
    def __str__(self):
        s = []
        s.append("[name=%s,type=%s,span=%r,info=%s,docstring=%s]" % (self.name, self.type, self.span, self.info, self.docstring))
        return ''.join(s)
    
def parseFile(filename, syncvar=None):
    text = open(filename, 'rU').read()
    return parseString(text, syncvar)

def parseString(text, syncvar=None):
    if text.find('\n') == -1:
        text = text.replace('\r', '\n')
    parser = PyParser(text)
    return parser.parse(syncvar)

class PyParser(object):
    def __init__(self, string):
        self.stack = [] # stack of (class, indent) pairs

        f = StringIO.StringIO(string)

        self.g = tokenize.generate_tokens(f.readline)

        self.root = root = Node()
    #    root.set_lines(buf.splitlines())

        self.func_nodes = root.add('function', Node(root))
        self.class_nodes = root.add('class', Node(root))
        self.import_nodes = root.add('import', Node(root))
        self.importline_nodes = root.add('importline', Node(root))
        self.idens = root.idens = set([])

        self.last_node = None
        
        self.dispatcher = [self.do_indent, self.do_function, self.do_class,
            self.do_import, self.do_from, self.do_global, self.do_multi_identifer, 
            self.do_identifer, self.do_docstring]

    def close_span(self, stack, lineno):
        if stack:
            last_node = stack.pop(-1)[0]
            if last_node.type in ('class', 'function'):
                last_node.span.append(lineno)

    def parse(self, syncvar=None):
        g = self.g
        stack = self.stack
        root = self.root
        flag = True
        judge_indent = False
        self.lastnode = None
        while 1:
            if syncvar and not syncvar.empty:
                return None
            
            r = self.read_line()
            if not r:
                break
#            self.print_line_buf(*r)
            lineinfo, linebuf = r
            lineno, indent = lineinfo
            while stack and stack[-1][1] >= indent:
                self.close_span(stack, lineno)
            for f in self.dispatcher:
                try:
                    v = f((x for x in linebuf))
                except:
                    break
                if v:
                    if isinstance(v, tuple):
                        self.lastnode = v[1]
                    else:
                        self.lastnode = None
                    break
            else:
                self.lastnode = None
                
        while stack:
            self.close_span(stack, sys.maxint)
        return root
    
    def read_line(self):
        g = self.g
        buf = []
        lasttoken = None
        lastword = None
        words = []
        while 1:
            try:
                v = g.next()
            except:
                if buf:
                    return buf[0][2], buf
                else:
                    return None
            tokentype, t, start, end, line = v
            if tokentype == token.NAME:
                if not lastword:
                    words = [t]
                    lasttoken = tokentype
                    lastword = t
                elif lastword == '.':
                    words.append(t)
                    lasttoken = tokentype
                    lastword = t
                else:
                    self._put_idens(words)
                    lasttoken = None
                    lastword = None
                    words = [t]
                    
            else:
                if t == '.' and lasttoken == token.NAME:
                    words.append('.')
                    lastword = t
                    lasttoken = tokentype
                else:
                    self._put_idens(words)
                    lasttoken = None
                    lastword = None
                    words = []
                    
            if tokentype == 54:
                continue
            if tokentype in (token.INDENT, token.DEDENT, tokenize.COMMENT):
                continue
            if tokentype != token.NEWLINE:
                buf.append(v)
            else:
                buf.append(v)
                return buf[0][2], buf
            
    def _put_idens(self, words):
        w = ''.join(words)
        if len(w) > 1:
            if w not in self.idens:
                self.idens.add(w)
            
    def print_line_buf(self, lineinfo, buf):
        for v in buf:
            tokentype, t, start, end, line = v
            print token.tok_name[tokentype], repr(t), start,
        print 
    
    def do_indent(self, g):
        stack = self.stack
        tokentype, t, start, end, line = g.next()
        if tokentype == token.DEDENT:
            lineno, thisindent = start
            # close nested classes and defs
            while stack and stack[-1][1] >= thisindent:
                self.close_span(stack, lineno)
            return True
        else:
            return False
        
    def do_function(self, g):
        tokentype, t, start, end, line = g.next()
        if t == 'def':
            lineno, thisindent = start
            tokentype, meth_name, start, end, line = g.next()
            if tokentype != token.NAME:
                return True # Syntax error
            info = meth_name
            while True: # get details
                tokentype, t, start, end, line = g.next()
                if t == ':':
                    break
                if tokentype != tokenize.COMMENT:
                    if t == ',':
                        t = ', '
                    info += t
            node = None
            if self.stack:
                obj = self.stack[-1][0]
                if obj.type == 'class' or obj.type == 'function':
                    # it's a method
                    node = obj.add(meth_name, FuncNode(obj, meth_name, 'function', info, lineno))
                    obj.add_local(meth_name, 'function', node, lineno)
                    self.stack.append((node, thisindent)) # Marker for nested fns
                # else it's a nested def
            else:
                # it's a function
                node = self.func_nodes.add(meth_name, FuncNode(self.func_nodes, meth_name, 'function', info, lineno))
                self.root.add_local(meth_name, 'function', node, lineno)
                self.stack.append((node, thisindent)) # Marker for nested fns
        
            return True, node
        else:
            return False
        
    def do_class(self, g):
        stack = self.stack
        root = self.root
        tokentype, t, start, end, line = g.next()
        if t == 'class':
            lineno, thisindent = start
            tokentype, class_name, start, end, line = g.next()
            if tokentype != token.NAME:
                return True # Syntax error
            info = class_name
            while True: # get details
                tokentype, t, start, end, line = g.next()
                if t == ':':
                    break
                if tokentype != tokenize.COMMENT:
                    if t == ',':
                        t = ', '
                    info += t
            if stack:
                obj = stack[-1][0]
                if obj.type == 'class' or obj.type == 'function':
                    # it's a method
                    node = obj.add(class_name, ClassNode(obj, class_name, 'class', info, lineno))
                    obj.add_local(class_name, 'class', node, lineno)
                    stack.append((node, thisindent)) # Marker for nested fns
            else:
                node = self.class_nodes.add(class_name, ClassNode(self.class_nodes, class_name, 'class', info, lineno))
                root.add_local(class_name, 'class', node, lineno)
                stack.append((node, thisindent))
            return True, node
        else:
            return False
        
    def do_import(self, g):
        root = self.root
        tokentype, t, start, end, line = g.next()
        stack = self.stack
        if t == 'import':
            info = t + ' '
            lineno, thisindent = start
            while True:
                tokentype, t, start, end, line = g.next()
                if tokentype == token.NEWLINE or tokentype == tokenize.COMMENT:
                    break
                if tokentype == token.OP and t in ('(', ')'):
                    continue
                if t == ',':
                    t = ', '
                if t == 'as':
                    t = ' as '
                info += t
            imports = self.parse_import(info)
            if stack:
                obj = stack[-1][0]
                if obj.type == 'class' or obj.type == 'function':
                    obj.add_import(info, lineno)
                    # it's a method
                    for n in imports:
                        node = obj.add(info, Node(obj, n, 'import', info, lineno))
                        obj.add_local(n, 'import', n, lineno)
            else:
                root.add_import(info, lineno)
                for n in imports:
                    node = self.import_nodes.add(info, Node(self.import_nodes, n, 'import', info, lineno))
                    root.add_local(n, 'import', n, lineno)
            return True
        else:
            return False
        
    def do_from(self, g):
        root = self.root
        tokentype, t, start, end, line = g.next()
        stack = self.stack
        if t == 'from':
            info = t + ' '
            lineno, thisindent = start
            while True:
                tokentype, t, start, end, line = g.next()
                if tokentype == token.NEWLINE or tokentype == tokenize.COMMENT:
                    break
                if tokentype == token.OP and t in ('(', ')'):
                    continue
                if t == 'import':
                    t = ' import '
                if t == ',':
                    t = ', '
                if t == 'as':
                    t = ' as '
                info += t
            imports = self.parse_import(info)
            if stack:
                obj = stack[-1][0]
                if obj.type == 'class' or obj.type == 'function':
                    obj.add_import(info, lineno)
                    # it's a method
                    for n in imports:
                        node = obj.add(info, Node(obj, n, 'import', info, lineno))
                        obj.add_local(n, 'import', n, lineno)
            else:
                root.add_import(info, lineno)
                for n in imports:
                    node = self.import_nodes.add(info, Node(self.import_nodes, n, 'import', info, lineno))
                    root.add_local(n, 'import', n, lineno)
            return True
        else:
            return False
        
    def do_docstring(self, g):
        tokentype, t, start, end, line = g.next()
        docstring = None
        if tokentype == token.STRING:
            s = t
            tokentype, t, start, end, line = g.next()
            if tokentype == token.NEWLINE:
                docstring = s
                if self.lastnode and self.lastnode.type in ('function', 'class'):
                    self.lastnode.docstring = docstring
                    self.parse_type(self.lastnode, docstring)
                    return True
        return False
        
    def do_global(self, g):
        root = self.root
        tokentype, t, start, end, line = g.next()
        stack = self.stack
        if t == 'global':
            info = t + ' '
            lineno, thisindent = start
            while True:
                tokentype, t, start, end, line = g.next()
                if tokentype == token.NEWLINE or tokentype == tokenize.COMMENT:
                    break
                if t == ',':
                    t = ', '
                info += t
            gs = self.parse_global(info)
            for n in gs:
                root.add_local(n, 'reference', n, lineno)
            return True
        else:
            return False

    def do_identifer(self, g):
        stack = self.stack
        root = self.root
        tokentype, t, start, end, line = g.next()
        text = line
        if tokentype == token.NAME:
            typeflag = None
            typevalue = None
            idenname = t
            tokentype, t, start, end, line = g.next()
            lineno, thisindent = start
            dotflag = True
            while dotflag and t == '.' or not dotflag and tokentype == token.NAME:
                idenname += t
                tokentype, t, start, end, line = g.next()
                dotflag = not dotflag
                
            if tokentype == token.OP and t == '=':
                tokentype, t, start, end, line = g.next()
#                print tokentype, t, start, end, line
                if tokentype == token.STRING:
                    typeflag = 'str'
                    typevalue = str
                elif tokentype == token.OP and t == '[':
                    typeflag = 'list'
                    typevalue = list
                elif tokentype == token.OP and t == '{':
                    typeflag = 'dict'
                    typevalue = dict
                elif tokentype == token.OP and t == '(':
                    typeflag = 'tuple'
                    typevalue = tuple
                elif tokentype == token.NAME and t == 'None':
                    typeflag = 'none'
                    typevalue = None
                elif tokentype == token.NUMBER:
                    typeflag = 'int'
                    typevalue = int
                else:
                    if tokentype == token.NAME:
                        classname = t
                        tokentype, t, start, end, line = g.next()
                        dotflag = True
                        while dotflag and t == '.' or not dotflag and tokentype == token.NAME:
                            classname += t
                            tokentype, t, start, end, line = g.next()
                            dotflag = not dotflag
                        if classname in ('True', 'False'):
                            typeflag = 'bool'
                            typevalue = bool
                        else:
                            typeflag = 'reference'
                            typevalue = classname
                        
                if stack:
                    obj = stack[-1][0]
                    if obj.type != 'class' and obj.type != 'function':
                        obj = None
                else:
                    obj = root
                if typeflag:
                    if idenname.startswith('self.'):    #class instance attribute
                        for i in range(len(stack)-1, -1, -1):
                            obj = stack[i][0]
                            if obj.type == 'class':
                                idenname = idenname[5:]
                                break
                        else:
                            obj = None
                        
                    if obj:
                        obj.add_local(idenname, typeflag, typevalue, lineno)
            return True
        else:
            return False

    def do_multi_identifer(self, g):
        stack = self.stack
        root = self.root
        tokentype, t, start, end, line = g.next()
        idenbuf = []
        while tokentype == token.NAME:
            idenname = t
            tokentype, t, start, end, line = g.next()
            lineno, thisindent = start
            dotflag = True
            while dotflag and t == '.' or not dotflag and tokentype == token.NAME:
                idenname += t
                tokentype, t, start, end, line = g.next()
                dotflag = not dotflag
            idenbuf.append((idenname, lineno))
            if tokentype == token.OP and ',' == t:
                tokentype, t, start, end, line = g.next()
                continue
            else:
                break
            
        if len(idenbuf) <= 1:
            return False
        
        if tokentype == token.OP and t == '=':
            if stack:
                obj = stack[-1][0]
                if obj.type != 'class' and obj.type != 'function':
                    obj = None
            else:
                obj = root
            for idenname, lineno in idenbuf:
                if idenname.startswith('self.'):    #class instance attribute
                    for i in range(len(stack)-1, -1, -1):
                        obj = stack[i][0]
                        if obj.type == 'class':
                            idenname = idenname[5:]
                            break
                    else:
                        obj = None
                if obj:
                    obj.add_local(idenname, 'reference', None, lineno)
            return True
                    
        return False
    
    r_import = re.compile('\s*import\s+(.*)')
    r_fromimport = re.compile('\s*from\s*.*?import\s+(.*)')
    def parse_import(self, info):
        buf = []
        b = self.r_import.match(info)
        if not b:
            b = self.r_fromimport.match(info)
        if b:
            s = b.groups()[0].split(',')
            for p in s:
                t = p.split()
                if len(t) > 1 and t[1] == 'as':
                    buf.append(t[2].strip())
                elif len(t) == 1:
                    buf.append(t[0].strip())
        return buf
    
    r_global = re.compile('\s*global\s+(.*)')
    def parse_global(self, info):
        buf = []
        b = self.r_global.match(info)
        if b:
            s = b.groups()[0].split(',')
            for p in s:
                buf.append(p.strip())
        return buf

    r_type = re.compile(r'^\s*@type\s+(\w+)\s*:\s*([\w\d.]+)', re.MULTILINE)
    def parse_type(self, funcnode, docstring):
        start = 0
        b = self.r_type.search(docstring, start)
        s = []
        while b:
            s.append(b.groups())
            start = b.end()
            b = self.r_type.search(docstring, start)
        for name, t in s:
            if t in ('str', 'string', 'unicode'):
                typeflag = 'str'
                typevalue = str
            elif t in ('int', 'integer'):
                typeflag = 'int'
                typevalue = int
            elif t in ('float',):
                typeflag = 'float'
                typevalue = float
            elif t in ('bool', 'False', 'True'):
                typeflag = 'bool'
                typevalue = bool
            elif t == 'list':
                typeflag = 'list'
                typevalue = list
            elif t == 'dict':
                typeflag = 'dict'
                typevalue = dict
            elif t == 'tuple':
                typeflag = 'tuple'
                typevalue = tuple
            elif t == 'none':
                typeflag = 'none'
                typevalue = None
            else:
                typeflag = 'reference'
                typevalue = t
            for i, n in enumerate(funcnode.locals):
                if n == name:
                    funcnode.local_types[i] = (typeflag, typevalue, funcnode.lineno)
                    break
            else:
                funcnode.locals.append(name)
                funcnode.local_types.append((typeflag, typevalue, funcnode.lineno))

def main():
    # Main program for testing.
    import sys
    file = sys.argv[1]

    s = parseFile(file)
#    s.output()
#    print s.idens
                
#    print s.get_imports(1)
#    print 'self.ppp', s.guess_type(51, 'self.ppp')
#    print 'a', s.guess_type(60, 'a')
#    print 'printf', s.guess_type(4, 'printf')
#    print s.guess_type(40, 'printf')
#    print 'a', s.guess(17)
#    print s.get_imports(34)
#    print s.get_imports(1)

if __name__ == "__main__":
    main()
