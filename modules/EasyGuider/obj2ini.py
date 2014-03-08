#coding=utf-8
# dump python object to ini format file
# Author: limodou (limodou@gmail.com)
# Copyleft GPL
# $Id: obj2ini.py,v 1.2 2005/04/21 15:42:39 limodou Exp $
#
# 2005/07/31
#            1. 增加变量的支持。
#            2. 修改输出的ini格式为第一行为#obj表示是对象，#var表示是变量。
#            同时为了兼容性，当第一行不是#var或#obj时默认为#obj。
#            3. 修改load方法的调用参数

import types
import sys
import locale
import codecs

def dump(obj, filename, encoding=None):
    encoding = __getdefaultencoding(encoding)

    from StringIO import StringIO
    
    f = StringIO()

    if hasattr(obj, '__dict__'):
        objects = {}
        f.write("#obj\n")
        f.write("[=%s.%s]\n" % (obj.__class__.__module__, obj.__class__.__name__))
        for key, value in vars(obj).items():
            if isinstance(value, types.InstanceType):
                objects[key] = value
            else:
                __write_var(f, key, value, encoding)
        for key, value in objects.items():
            __dumpsubobj(value, key, '', f, encoding)
    else:
        f.write("#var\n")
        f.write(__uni_prt(obj, encoding))
        
    if hasattr(filename, "write"):
        out = filename
    else:
        out = file(filename, "w")
        
    out.write(f.getvalue())
    out.close()

class EmptyClass:
    pass

def __getparentobjname(name):
    a = name.split('.')
    return '.'.join(a[:-1])

def __getmoduleandclass(name):
    a = name.split('.')
    return '.'.join(a[:-1]), a[-1]

def load(filename, obj=None, encoding=None):
    encoding = __getdefaultencoding(encoding)

    if hasattr(filename, "read"):
        f = filename
    else:
        f = file(filename, "r")

    firstline = f.readline()
    if firstline.startswith('#obj') or not firstline.startswith('#var'):
        if not firstline.startswith('#obj'):
            f.seek(0)
        objects = {}
        namespace = {}
        if not obj:
            obj = EmptyClass()
        currentobj = obj
        parentobj = obj
        for line in f:
            line = line.strip()
            if not line: continue
            if line[0] in ('#', ';'): continue
            if line.startswith('[') and line.endswith(']'): #sub object
                #set original class
                classname, classinfo = line[1:-1].split('=')
                module, _class = __getmoduleandclass(classinfo)
                __import__(module)
                mod = sys.modules[module]
                _klass = getattr(mod, _class)
                if classname:
                    sub = EmptyClass()
                    parentname = __getparentobjname(classname)
                    setattr(parentobj, classname, sub)
                else:
                    sub = currentobj
                    parentname = ''
                sub.__class__ = _klass
                if parentname:
                    parentobj = objects[parentname]
                else:
                    parentobj = currentobj
                objects[classname] = sub
                currentobj = sub
            else:
                if line.find('='):
                    delimeter = '='
                else:
                    delimeter = ':'
                key, value = line.split(delimeter, 1)
                key = key.strip()
                exec __filter(line, encoding) in namespace
                setattr(currentobj, key, namespace[key])
        return obj
    else:
        line = f.readline()
        namespace = {}
        exec __filter('var='+line, encoding) in namespace
        return namespace['var']

def __dumpsubobj(obj, objname, parentname, filename, encoding=None):
    if hasattr(filename, "write"):
        f = filename
    else:
        f = file(filename, "w")

    if parentname:
        f.write("\n[%s.%s=%s.%s]\n" % (parentname, objname, obj.__class__.__module__, obj.__class__.__name__))
    else:
        f.write("\n[%s=%s.%s]\n" % (objname, obj.__class__.__module__, obj.__class__.__name__))
    objects = {}
    for key, value in vars(obj).items():
        if isinstance(value, types.InstanceType):
            objects[key] = value
        else:
            __write_var(f, key, value, encoding)
    for key, value in objects.items():
        __dumpsubobj(value, key, objname, f, encoding)

def __write_var(f, key, var, encoding):
    f.write("%s=%s\n" % (key, __uni_prt(var, encoding)))

def __getdefaultencoding(encoding):
    if not encoding:
        encoding = locale.getdefaultlocale()[1]
    try:
        codecs.lookup(encoding)
    except:
        encoding = 'utf-8'
    return encoding

def __uni_prt(a, encoding=None):
    escapechars = [("\\", "\\\\"), ("'", r"\'"), ('\"', r'\"'), ('\b', r'\b'),
        ('\t', r"\t"), ('\r', r"\r"), ('\n', r"\n")]
    s = []
    encoding = __getdefaultencoding(encoding)
    if isinstance(a, (list, tuple)):
        if isinstance(a, list):
            s.append('[')
        else:
            s.append('(')
        for i, k in enumerate(a):
            s.append(__uni_prt(k, encoding))
            if i<len(a)-1:
                s.append(', ')
        if isinstance(a, list):
            s.append(']')
        else:
            s.append(')')
    elif isinstance(a, dict):
        s.append('{')
        for i, k in enumerate(a.items()):
            key, value = k
            s.append('%s: %s' % (__uni_prt(key, encoding), __uni_prt(value, encoding)))
            if i<len(a.items())-1:
                s.append(', ')
        s.append('}')
    elif isinstance(a, str):
        t = a
        for i in escapechars:
            t = t.replace(i[0], i[1])
        s.append("'%s'" % t)
    elif isinstance(a, unicode):
        t = a
        for i in escapechars:
            t = t.replace(i[0], i[1])
        try:
            s.append("u'%s'" % t.encode(encoding))
        except:
            import traceback
            traceback.print_exc()
    else:
        s.append(str(a))
    return ''.join(s)

def __filter(s, encoding):
    import StringIO
    import tokenize
    import token

    f = StringIO.StringIO(s)
    g = tokenize.generate_tokens(f.readline)
    slist = []
    namespace = {}
    for tokentype, t, start, end, line in g:
        if tokentype == token.STRING:
            if t[0] == 'u':
                exec "v=" + t[1:] in namespace
                slist.append(repr(unicode(namespace["v"], encoding)))
            else:
                slist.append(t)
        else:
            slist.append(t)
    return ''.join(slist)

if __name__ == '__main__':
    class A:
        a = 1
        def __init__(self):
            self.b = 1
            self.c = unicode("中\\'国", 'utf-8')
            self.d = (self.c, self.b)
            self.e = [self.b, self.c, self.d]
            self.f = {self.b:self.c, self.d:self.e}

    a = A()
    #f = sys.stdout
    f = "test1.ini"
    b = A()
    b.s = "aa\ba\"a\ns'ss\tsdd\r"
    c = A()
    a.obj = b
    a.obj.obj = c
    dump(a, f)

    s = load(f)
    print vars(s)
    print s.__class__.__name__

#    f = sys.stdout
#    dump(s, f)

    a = ['a', 'b',(1,2), '中文', {'a':[1,2,3]}]
    dump(a, 'test2.ini')
    b = load('test2.ini')
    print b
