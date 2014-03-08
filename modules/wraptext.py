#!/usr/bin/env python
#coding=utf-8
#
# Copyleft 2008 limodou@gmail.com
# License BSD
# Version 0.1
#
# 说明
#    本程序用来进行文本的折行处理，支持中文和英文，可以处理Unicode和普通字符串
#
# 参数说明
#    text       待处理的文本，可以是unicode或str
#    width      处理宽度
#    encoding   字符串编码，只当text不是unicode时有效
#    cr         换行符，如果为None则自动从文本中判断，自动设定为找到的第一个换
#               行符，如果找不到缺省为'\n'，如果不为None，则使用设定的换行符
#    indent     非首行缩近量
#    firstindent首行缩近量
#    skipchar   行首忽略字符，如果存在则在处理前会清除每前开始前有skipchar的文本
#    remove_tailingchar   行尾忽略字符，如果存在则在处理前会清除每行行尾匹配的文本
#    add_tailingchar   添加行尾字符，如果存在则在处理后每行最后添加此文本
#
# 功能描述
#  1.支持unicode和非unicode文本，如果为非unicode文本，则会使用encoding指定的编
#    码对文本转换为unicode，在返回时，会根据原文本是unicode还是非unicode进行转
#    换并输出。
#  2.支持段落概念。两个以上连续的回车为段落分隔，其中如果一行只包括空白(空格或
#    制表符的行)将视为空行。最终的结果段落间只保存一个空行。如果只存在单个换行
#    则相邻的行视为同一段落。支持'\n', '\r\n', '\r'三种形式的换行符。可以自动
#    使用文本中的回车符或指定转换后的回车符。
#  3.自动处理亚洲文字和半角字符，自动处理空白，多个空白(包括制表符)将自动合并
#    成一个。亚洲文字和英文之间以空格分隔。对于亚洲文字中间的空白自动删除。
#  4.支持缩近设置，首行缩近和非首行缩近。缩近量可以是数值，则为空格*数值，可以
#    是字符串。如果firstindent没有设置将缺省为indent的值。
#  5.可以设置每行行首要忽略的字符，如注释行的'#'，在处理时将先删除匹配的行首字
#    符。
#
# 示例
#  msg = '''中文 中文hello, world'''
#  wraptext(msg, 10)

def wraptext(text, width=75, encoding='utf-8', cr=None, indent='', 
    firstindent=None, skipchar=None, remove_tailingchar='', add_tailingchar=''):
    import unicodedata
    import re
    if isinstance(text, unicode):
        unicode_flag = True
    else:
        unicode_flag = False
        text = unicode(text, encoding)
        
    if text[-1] in ('\r', '\n'):
        enter_flag = True
    else:
        enter_flag = False
        
    if not cr:
        if text.find('\r\n') > -1:
            cr = '\r\n'
        elif text.find('\r') > -1:
            cr = '\r'
        else:
            cr = '\n'
            
    text = text.replace('\r\n', '\n')
    text = re.sub(r'\s+$', '\n', text)
    if skipchar:
        text = re.sub(r'(?m)^%s' % skipchar, '', text)
    if remove_tailingchar:
        _r = re.compile('%s\n' % re.escape(remove_tailingchar), re.MULTILINE)
        text = _r.sub('\n', text)
        
    lines = re.split(r'(\n\s*\n+|\r\r+)', text)
    rx = re.compile(u"[\u2e80-\uffff]+", re.UNICODE)
    
    if isinstance(indent, int):
        indent = ' ' * indent
    if firstindent is None:
        firstindent = indent
    if isinstance(firstindent, int):
        firstindent = ' ' * firstindent
    
    def _add_line(line, buf, tailing=add_tailingchar):
        line.append(buf + tailing)
        
    def _wrap(text, width, indent, firstindent):
        if not text:
            return ''
        text = text.strip()
        s = []
        pos = 0
        for i in rx.finditer(text):
            if i.start() > pos:
                s.extend(text[pos:i.start()].split())
            s.append(i.group())
            pos = i.end()
        if pos < len(text):
            s.extend(text[pos:].split())
        
        ss = [s[0]]
        #get first element character is asian char flag
        flag = unicodedata.east_asian_width(s[0][0]) != 'Na'
        for i in range(1, len(s)):
            f = unicodedata.east_asian_width(s[i][0]) != 'Na'
            if f and f == flag:
                ss[-1] = ss[-1] + s[i]
            else:
                ss.append(s[i])
            flag = f
        
        s = ss
        
        t = []
        y = 0
        buf = []
        x = 0
        while s:
            i = s.pop(0)
            if unicodedata.east_asian_width(i[0]) != 'Na':
                factor = 2
            else:
                factor = 1
                
            if x == 0:
                w = width - len(firstindent)
                step = firstindent
            else:
                w = width - len(indent)
                step = indent
            length = y + len(i)*factor + len(buf)
#            print 'length', length, s[0].encode('gbk')
            if length == w:
                buf.append(i)
                _add_line(t, step + ' '.join(buf))
#                t.append(step + ' '.join(buf))
                x = 1
                buf = []
                y = 0
            elif length > w:
                if factor == 2 or (factor==1 and len(i) * factor >= w):
                    buf_len = len(buf)
                    rest = w-y-buf_len
                    buf.append(i[:rest/factor])
#                    print '----', w, y, buf_len, (w-y-buf_len-1), buf
                    _add_line(t, step + ' '.join(buf))
#                    t.append(step + ' '.join(buf))
                    x = 1
                    s.insert(0, i[rest/factor:])
                    buf = []
                    y = 0
                    continue
                else:
                    _add_line(t, step + ' '.join(buf))
#                    t.append(step + ' '.join(buf))
                    x = 1
                    s.insert(0, i)
                    buf = []
                    y = 0
                    continue
                    
            else:
                buf.append(i)
                y += factor * len(i)
                
        if buf:
            _add_line(t, step + ' '.join(buf), '')
#            t.append(step + ' '.join(buf))
        return cr.join(t)
    
    s = []
    for line in lines:
        if not line.strip():
            s.append(indent)
        else:
            s.append(_wrap(line, width, indent, firstindent))
       
    if enter_flag:
        s.append('')
    text = cr.join(s)
    if not unicode_flag:
        text = text.encode(encoding)
    return text
        
def test():
    msg =u"""首先这个框架是一个试验品，或者说是主要是个人使用，因此我将有完全的控制权，这一点很重要。我可以用它学到许多框架的知识。以前只是使用，学习，象学过：cherrypy, Karrigell, snakelets等，不过没有做过什么开发；zope则是我学得最早了，不过也早就放弃了；django投入的精力最多，也开发了不少东西；再后来就是 web2py了，不过重用搞得我很不爽，而且有些想法不被认同。但这些更多的还是集中在开发方面，对于框架本身了解有限，这次造轮是一个好机会。"""
    print wraptext(msg, 75, indent='', skipchar='#', remove_tailingchar='', 
        add_tailingchar='\\').encode('gbk')

if __name__ == '__main__':
#    from timeit import Timer
#    t = Timer("test()", "from __main__ import test")
#    print t.timeit(1000)
    test()
    