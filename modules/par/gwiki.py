from pyPEG import *
import re
import types
from __init__ import SimpleVisitor

_ = re.compile

class WikiGrammar(dict):
    def __init__(self):
        peg, self.root = self._get_rules()
        self.update(peg)
        
    def _get_rules(self):
        #basic
        def ws(): return _(r'\s+')
        def space(): return _(r'[ \t]+')
        def eol(): return _(r'\r\n|\r|\n')
        def seperator(): return _(r'[\.,!?\-$ \t\^]')
    
        #hr
        def hr(): return _(r'\-{4,}'), -2, blankline
    
        #paragraph
        def blankline(): return 0, space, eol
        def identifer(): return _(r'[a-zA-Z_][a-zA-Z_0-9]*', re.U)
        def literal(): return _(r'u?r?"[^"\\]*(?:\\.[^"\\]*)*"', re.I|re.DOTALL)
        def literal1(): return _(r"u?r?'[^'\\]*(?:\\.[^'\\]*)*'", re.I|re.DOTALL)
        def escape_string(): return _(r'\\'), _(r'.')
        def op_string(): return _(r'\*|_|~~|\^|,,')
        def op(): return [(-1, seperator, op_string), (op_string, -1, seperator)]
        def string(): return _(r'[^\\\*_\^~ \t\r\n`,]+', re.U)
        def code_string_short(): return _(r'`'), _(r'[^`]*'), _(r'`')
        def code_string(): return _(r'\{\{\{'), _(r'[^\}\r\n$]*'), _(r'\}\}\}')
        def default_string(): return _(r'\S+', re.U)
        def word(): return [literal, literal1, escape_string, code_string, code_string_short, op, link, string, default_string]
        def words(): return word, -1, [space, word]
        def line(): return words, eol
        def paragraph(): return -2, line, -1, blankline
    
        #pre
        def pre_b(): return _(r'\{\{\{')
        def pre_e(): return _(r'\}\}\}')
        def pre_alt(): return _(r'<code>'), _(r'.+?(?=</code>)', re.M|re.DOTALL), _(r'</code>'), -2, blankline
        def pre_normal(): return pre_b, 0, space, eol, _(r'.+?(?=\}\}\})', re.M|re.DOTALL), pre_e, -2, blankline
        def pre(): return [pre_alt, pre_normal]
    
        
        #subject
        def title_text(): return _(r'.+(?= =)', re.U)
#        def subject(): return _(r'\s*.*'), eol, _(r'(?:=|-){4,}'), -2, eol
        def title1(): return _(r'= '), title_text, _(r' ='), -2, eol
        def title2(): return _(r'== '), title_text, _(r' =='), -2, eol
        def title3(): return _(r'=== '), title_text, _(r' ==='), -2, eol
        def title4(): return _(r'==== '), title_text, _(r' ===='), -2, eol
        def title5(): return _(r'===== '), title_text, _(r' ====='), -2, eol
        def title6(): return _(r'====== '), title_text, _(r' ======'), -2, eol
        def title(): return [title6, title5, title4, title3, title2, title1]
    
        #table
        def table_column(): return -2, [space, escape_string, code_string_short, code_string, op, link, _(r'[^\\\*_\^~ \t\r\n`,\|]+', re.U)], _(r'\|\|')
        def table_line(): return _(r'\|\|'), -2, table_column, eol
        def table(): return -2, table_line, -1, blankline
    
        #lists
        def list_leaf_content(): return words, eol
        def list_indent(): return space
        def bullet_list_item(): return list_indent, _(r'\*'), space, list_leaf_content
        def number_list_item(): return list_indent, _(r'#'), space, list_leaf_content
        def list_item(): return [bullet_list_item, number_list_item]
        def list(): return -2, list_item, -1, blankline
    
        #quote
        def quote_line(): return space, line
        def quote(): return -2, quote_line, -1, blankline
            
        #links
        def protocal(): return [_(r'http://'), _(r'https://'), _(r'ftp://')]
        def direct_link(): return protocal, _(r'[\w\-\.,@\?\^=%&:/~+#]+')
        def image_link(): return protocal, _(r'.*?(?:\.png|\.jpg|\.gif|\.jpeg)', re.I)
        def alt_direct_link(): return _(r'\['), 0, space, direct_link, space, _(r'[^\]]+'), 0, space, _(r'\]')
        def alt_image_link(): return _(r'\['), 0, space, direct_link, space, image_link, 0, space, _(r'\]')
        def mailto(): return 'mailto:', _(r'[a-zA-Z_0-9-@/\.]+')
        def link(): return [alt_image_link, alt_direct_link, image_link, direct_link, mailto], -1, space
        
        #article
        def article(): return 0, ws, -1, [hr, title, pre, table, list, quote, paragraph]
    
        peg_rules = {}
        for k, v in ((x, y) for (x, y) in locals().items() if isinstance(y, types.FunctionType)):
            peg_rules[k] = v
        return peg_rules, article
    
    def parse(self, text, root=None, skipWS=False, **kwargs):
        if not text:
            text = '\n'
        if text[-1] not in ('\r', '\n'):
            text = text + '\n'
        text = re.sub('\r\n|\r', '\n', text)
        return parseLine(text, root or self.root, skipWS=skipWS, **kwargs)
        
class WikiHtmlVisitor(SimpleVisitor):
    op_maps = {
        '*':['<b>', '</b>'],
        '_':['<i>', '</i>'],
        '~~':['<span style="text-decoration: line-through">', '</span>'],
        '^':['<sup>', '</sup>'],
        ',,':['<sub>', '</sub>'],
        '`':['<code>', '</code>'],
    }
    tag_class = {}
    
#    default_template="""<!DOCTYPE html>
#<html>
#<head>
#<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
#<link rel="stylesheet" type="text/css" href="bootstrap.min.css"/>
#<link rel="stylesheet" type="text/css" href="example.css"/>
#<title>%(title)s</title>
#</head>
#<body>
#%(body)s</body>
#</html>
#"""
    
    def __init__(self, template=None, tag_class=None, grammar=None, title='Untitled', block_callback=None, init_callback=None):
        self._template = template or '%(body)s'
        self.title = title
        self.titles = []
        self.titles_ids = {}
        self.ops = {}
        self.tag_class = tag_class or self.__class__.tag_class
        self.grammar = grammar
        self.block_callback = block_callback or {}
        self.init_callback = init_callback
        
    def __str__(self):
        return self.template()
    
    def template(self, node):
        body = self.visit(node, self.grammar or self.grammar.root)
        if self.init_callback:
            self.init_callback(self)
        if self._template:
            return self._template % {'title':self.title, 'body':body}
        else:
            return body
    
    def parse_text(self, text, peg=None):
        g = self.grammar
        if isinstance(peg, (str, unicode)):
            peg = g[peg]
        resultSoFar = []
        result, rest = g.parse(text, root=peg, resultSoFar=resultSoFar, 
            skipWS=False, block_callback=self.block_callback, 
            init_callback=self.init_callback)
        v = self.__class__('', self.tag_class, g)
        return v.visit(result, peg)
    
    def tag(self, tag, child='', enclose=0, newline=True, **kwargs):
        """
        enclose:
            0 => <tag>
            1 => <tag/>
            2 => <tag></tag>
        """
        kw = kwargs.copy()
        if '_class' in kw:
            kw['class'] = kw.pop('_class')
        _class = self.tag_class.get(tag, '')
        if _class:
            #if tag_class definition starts with '+', and combine it with original value
            if _class.startswith('+'):
                kw['class'] = _class[1:] + ' ' + kw.get('class', '')
            else:
                kw['class'] = _class
        
        #process inner and outter link
        if tag == 'a':
            if kw['href'].startswith('http:') or kw['href'].startswith('https:') or kw['href'].startswith('ftp:'):
                _cls = 'outter'
            else:
                _cls = 'inner'
            if kw.get('class'):
                kw['class'] = kw['class'] + ' ' + _cls
            else:
                kw['class'] = _cls
            
        attrs = ' '.join(['%s="%s"' % (x, y) for x, y in kw.items() if y])
        if attrs:
            attrs = ' ' + attrs
        nline = '\n' if newline else ''
        if child:
            enclose = 2
        if enclose == 1:
            return '<%s%s/>%s' % (tag, attrs, nline)
        elif enclose == 2:
            return '<%s%s>%s</%s>%s' % (tag, attrs, child, tag, nline)
        else:
            return '<%s%s>%s' % (tag, attrs, nline)
    
    def get_title_id(self, level, begin=1):
        x = self.titles_ids.setdefault(level, 0) + 1
        self.titles_ids[level] = x
        _ids = []
        for x in range(begin, level+1):
            y = self.titles_ids.setdefault(x, 0)
            _ids.append(y)
        return 'title_%s' % '-'.join(map(str, _ids))
    
    def visit_eol(self, node):
        return '\n'
    
    def visit_subject(self, node):
        self.subject = node[0].strip()
        return self.tag('h1', self.subject)
    
    def visit_title1(self, node):
        self.subject = node[1].text
        return self.tag('h1', node[1].text)
    
    def visit_title2(self, node):
        _id = self.get_title_id(2)
        self.titles.append((2, _id, node[1].text))
        return self.tag('h2', node[1].text, id=_id)

    def visit_title3(self, node):
        _id = self.get_title_id(3)
        self.titles.append((3, _id, node[1].text))
        return self.tag('h3', node[1].text, id=_id)

    def visit_title4(self, node):
        _id = self.get_title_id(4)
        self.titles.append((4, _id, node[1].text))
        return self.tag('h4', node[1].text, id=_id)
    
    def visit_title5(self, node):
        _id = self.get_title_id(5)
        self.titles.append((5, _id, node[1].text))
        return self.tag('h5', node[1].text, id=_id)

    def visit_title6(self, node):
        _id = self.get_title_id(6)
        self.titles.append((6, _id, node[1].text))
        return self.tag('h6', node[1].text, id=_id)

    def visit_paragraph(self, node):
        return self.tag('p', self.visit(node).rstrip())
    
    def visit_op_string(self, node):
        c = node.text
        index = (self.ops.setdefault(c, 1) + 1)%2
        self.ops[c] = index
        return self.op_maps[c][index]
        
    def visit_escape_string(self, node):
        return node[1]
    
    def to_html(self, text):
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        return text
    
    def visit_pre_alt(self, node):
        return self.tag('pre', self.to_html(node[1].strip()))

    def visit_pre_normal(self, node):
        return self.tag('pre', self.to_html(self.visit(node).strip()))
    
    def visit_pre_b(self, node):
        return ''
    
    def visit_pre_e(self, node):
        return ''

    def visit_code_string(self, node):
        return self.tag('code', self.to_html(node[1].strip()), newline=False)
    
    def visit_code_string_short(self, node):
        return self.tag('code', self.to_html(node[1].strip()), newline=False)

    def visit_hr(self, node):
        return self.tag('hr', enclose=1)
    
    def visit_table_begin(self, node):
        return self.tag('table')
    
    def visit_table_end(self, node):
        return '</table>\n'
    
    def visit_table_line(self, node):
        return self.tag('tr', self.visit(node[1:]))
    
    def visit_table_column(self, node):
        return self.tag('td', self.visit(node[:-1]), newline=False)
    
    def visit_list_begin(self, node):
        self.lists = []
        return ''
        
    def visit_list_end(self, node):
        def create_list(index, lists):
            buf = []
            old = None
            old_indent = None
            parent = None
            i = index
            while i<len(lists):
                _type, indent, txt = lists[i]
                i += 1
                #find sub_list
                if old_indent and indent > old_indent:
                    _t, i = create_list(i-1, lists)
                    buf.append(_t)
                    continue
                if old_indent and indent < old_indent:
                    buf.append('</' + parent + '>\n')
                    return ''.join(buf), i-1
                if _type == old:
                    buf.append(txt)
                else:
                    #find another list
                    if parent:
                        buf.append('</' + parent + '>\n')
                    if _type == 'b':
                        parent = 'ul'
                    else:
                        parent = 'ol'
                    buf.append(self.tag(parent))
                    buf.append(txt)
                    old_indent = indent
                    old = _type
            if buf:
                buf.append('</' + parent + '>\n')
            return ''.join(buf), i
    
        return create_list(0, self.lists)[0]
        
    def visit_bullet_list_item(self, node):
        self.lists.append(('b', len(node[0].text), self.visit([node[3]])))
        return ''
        
    def visit_number_list_item(self, node):
        self.lists.append(('n', len(node[0].text), self.visit([node[3]])))
        return ''
        
    def visit_list_leaf_content(self, node):
        return self.tag('li', self.visit(node.what).strip())
    
    def visit_quote_begin(self, node):
        return '<blockquote>'
    
    def visit_quote_end(self, node):
        return '</blockquote>'
    
    def visit_mailto(self, node):
        text = node[0]
        return '<a href="mailto:%s">%s</a>' % (text, text)
    
    def visit_direct_link(self, node):
        return '<a href="%s%s">%s%s</a>' % (node[0].text, node[1], node[0].text, node[1])
    
    def visit_alt_direct_link(self, node):
        return '<a href="%s">%s</a>' % (node[1].text, node[3].strip())
    
    def visit_alt_image_link(self, node):
        return '<a href="%s">%s</a>' % (node[1].text, self.visit_direct_link(node[3]))

    def visit_image_link(self, node):
        return '<img src="%s%s"/>' % (node[0].text, node[1])
    
    def visit_block(self, node):
        items = []
        name = None
        for n in node.find_all('block_item'):
            x = {}
            x['name'] = name = n.find('block_name').text.strip()
            x['kwargs'] = y = {}
            for t in n.find_all('block_kwargs'):
                k = t.find('block_kwargs_key').text.strip()
                v_node = t.find('block_kwargs_value')
                if v_node:
                    v = v_node.text.strip()
                else:
                    v = ''
                y[k] = v
            x['body'] = self.visit(n.find('block_body'))
            items.append(x)
        func = self.block_callback.get(name)
        if func:
            return func(self, items)
        else:
            return node.text
        
def parseHtml(text, template=None, tag_class=None, block_callback=None, init_callback=None):
    template = template or ''
    tag_class = tag_class or {}
    g = WikiGrammar()
    resultSoFar = []
    result, rest = g.parse(text, resultSoFar=resultSoFar, skipWS=False, block_callback=block_callback, init_callback=init_callback)
    v = WikiHtmlVisitor(template, tag_class, g)
    return v.template(result)

def parseText(text):
    g = WikiGrammar()
    resultSoFar = []
    result, rest = g.parse(text, resultSoFar=resultSoFar, skipWS=False)
    v = SimpleVisitor(g)
    return v.visit(result)
