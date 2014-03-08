#coding=cp936
#---------------------------------------------------
#                   UliPad script
# Author  :limodou
# Date    :2005/07/16
# Version :0.1
# Description:
#     Convert Html to Moin
#
#---------------------------------------------------
from sgmllib import SGMLParser
import htmlentitydefs
import tidy
import StringIO
import re

re_div = re.compile('</?div.*?>')
re_spe = re.compile('(__\w+__)')

class Converter(SGMLParser):
    def reset(self):
        SGMLParser.reset(self)
        self.text=[]
        self.ul = 0
        self.ol = 0
        self.pre = 0
        self.a_flag = False

    def start_a(self, attrs):
        for attr, value in attrs:
            if attr.lower() == "href":
                if value and value[0] != '#':
                    self.text.append('[' + value + ' ')
                    self.a_flag = True

    def end_a(self):
        if self.a_flag:
            self.text.append(']')
        self.a_flag = False

    def start_h1(self, attrs):
        self.text.append('= ')

    def end_h1(self):
        self.text.append(' =')

    def start_h2(self, attrs):
        self.text.append('== ')

    def end_h2(self):
        self.text.append(' ==')

    def start_h3(self, attrs):
        self.text.append('=== ')

    def end_h3(self):
        self.text.append(' ===')

    def start_h4(self, attrs):
        self.text.append('==== ')

    def end_h4(self):
        self.text.append(' ====')

    def start_h5(self, attrs):
        self.text.append('===== ')

    def end_h5(self):
        self.text.append(' =====')

    def start_pre(self, attrs):
        self.text.append('{{{#!python\n')
        self.pre = 1

    def end_pre(self):
        self.text.append('}}}')
        self.pre = 0

    def start_img(self, attrs):
        for attr, value in attrs:
            if attr.lower() == "src":
                self.text.append(value)

#    def end_img(self):
#        self.text.append("'''")
#
    def handle_data(self, text):
        if not self.pre:
            text = re_spe.sub('`\g<1>`', text)
        self.text.append(text)

    def output(self):
        def c(t):
            if not isinstance(t, unicode):
                return unicode(t)
            else:
                return t
        return ''.join([c(x) for x in self.text])

    def handle_entityref(self, ref):
        if ref == 'nbsp':
            self.text.append(' ')
        else:
            self.text.append(htmlentitydefs.entitydefs[ref])

    def start_ul(self, attrs):
        self.ul = 1

    def start_li(self, attrs):
        if self.ul:
            self.text.append(" * ")
        elif self.ol:
            self.text.append(" 1. ")

    def end_ul(self):
        self.ul = 0

    def start_ol(self, attrs):
        self.ol = 1

    def end_ol(self):
        self.ol = 0

    def start_strong(self, attrs):
        self.text.append("'''")

    def end_strong(self):
        self.text.append("'''")

    def start_em(self, attrs):
        self.text.append("'''")

    def end_em(self):
        self.text.append("'''")

    def do_hr(self, attrs):
        self.text.append("----\n")

    def parse_file(self, filename):
        text=file(filename).read()
        self.parse_string(text)

    def parse_string(self, text):
        self.feed(text)
        self.close()

def convert(text):
    unicodeflag = False
    if isinstance(text, unicode):
        text = text.encode('utf-8')
        unicodeflag = True
    text = re_div.sub('', text)
    options = dict(output_xhtml=1,add_xml_decl=0, indent='auto', tidy_mark=0,
        wrap=0,drop_empty_paras=1,logical_emphasis=1,lower_literals=1,
        show_body_only=1,char_encoding='utf8')
    dom = tidy.parseString(text, **options)
    buf = StringIO.StringIO()
    dom.write(buf)
    text = buf.getvalue()
    if unicodeflag:
        text = text.decode('utf-8')
    con = Converter()
    con.parse_string(text)
    text = con.output()
    return text

def run(win):
    text = win.document.GetText()
    text = convert(text)
    win.createMessageWindow()
    win.panel.showPage(tr('Message'))
    win.messagewindow.SetText(text)

run(win)
