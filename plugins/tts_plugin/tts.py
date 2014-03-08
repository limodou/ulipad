#coding=utf-8
#parse cninese word and englist word

def maketext(text):
    import string

    buf = []
    cn_b = '<VOICE REQUIRED="language=804">'
    cn_e = '</VOICE>'
    en_b = '<VOICE REQUIRED="language=409">'
    en_e = '</VOICE>'
    flag = None
    if not text: return
    i = text[0]
    if ord(i) > 127:
        buf.append(cn_b)
        flag = 'cn'
    else:
        buf.append(en_b)
        flag = 'en'
    for i in text:
        if i == '&':
            if flag == 'cn':
                buf.append(cn_e)
                buf.append(en_b)
                flag = 'en'
            buf.append('&amp;')
        elif i == '<':
            buf.append('&lt;')
        elif i == '>':
            buf.append('&gt;')
        elif i.isdigit():
            buf.append(str(i))
        elif ord(i) < 127:
            if i in string.ascii_letters:
                if flag == 'cn':
                    buf.append(cn_e)
                    buf.append(en_b)
                    flag = 'en'
            buf.append(str(i))
        else:
            try:
                t = i.encode('gbk')
                if flag == 'en':
                    buf.append(en_e)
                    buf.append(cn_b)
                buf.append(t)
                flag = 'cn'
            except:
                pass
    if flag == 'cn':
        buf.append(cn_e)
    else:
        buf.append(en_e)
    return ''.join(buf)

if __name__ == '__main__':
    a = u'中国english天上'
    print maketext(a)
