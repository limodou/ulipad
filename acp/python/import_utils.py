import sys
import re
import inspect
import wx.py.introspect as intro
from modules.common import pout
from mixins.InputAssistant import StopException

try:
    set
except:
    from sets import Set as set

INDENT = ' '*4
getattributes = intro.getAttributeNames
namespace = {}

def get_calltip(win, word, syncvar):
    if not hasattr(win, 'syntax_info') or not win.syntax_info:
        return []
    
    pout('-'*50)
    pout('get_calltip', word)
    
    flag, object = guessWordObject(win, word, False, syncvar)

    pout(INDENT, 'ready to output:', flag, object)
    if object:
        if flag == 'obj':
            signature = getargspec(win,object)
            doc = object.__doc__
            return filter(None, [signature, doc])
        else:
            if object.type == 'function':
                return unicode('\n'.join([object.info, object.docstring]), 'utf8')
            elif object.type == 'class':
                s = []
                s.append(object.docstring)
                t = object.get_local_name('__init__')
                c = object.get_local_name('__call__')
                if  t:
                    _obj = t[1]
                    s.append("\n")
                    s.append(_obj.info)
                    s.append(_obj.docstring)
                if  c:
                    _obj1 = c[1]
                    s.append("\n")
                    s.append(_obj1.info)
                    s.append(_obj1.docstring)
                return unicode('\n'.join(s), 'utf8')
                
    pout(INDENT, 'return:', None)
    return None
    
def getWordObject(win, word=None, whole=None):
    if not word:
        word = getWord(win, whole=whole)
    try:
        return evaluate(win, word)
    except:
#        error.traceback()
        return None

def getWord(win, whole=None):
    pos=win.GetCurrentPos()
    line = win.GetCurrentLine()
    linePos=win.PositionFromLine(line)
    txt = win.GetLine(line)
    start=win.WordStartPosition(pos,1)
    i = start - 1
    while i >= 0:
        if win.getChar(i) in win.mainframe.getWordChars() + '.':
            start -= 1
            i -= 1
        else:
            break
    if whole:
        end=win.WordEndPosition(pos,1)
    else:
        end=pos
    return txt[start-linePos:end-linePos]


def evaluate(win, word, syncvar=None):
#    from modules.callinmainthread import CallFunctionOnMainThread
#    
#    _import = CallFunctionOnMainThread(import_document)
    try:
        obj = eval(word, namespace)
        return obj
    except:
        try:
            import_document(win, syncvar)
#            _import(win, syncvar)
            obj = eval(word, namespace)
            return obj
        except:
            try:
                exec('import %s' % word) in namespace
                obj = eval(word, namespace)
                return obj
            except:
                return None

def getargspec(win, func):
    """Get argument specifications"""
    if  inspect.isclass(func):
        s = []
        # Get the __init__ method function for the class.
        constructor = getConstructor(func)
        init_docstring = inspect.getdoc(constructor)
        if  constructor:
            v = getargspec(win, constructor)
            s.append('\n' + v + '\n')
        if  init_docstring:
            s.append(init_docstring)
        call_docstring = None
        v1 = None
        # Handle  the __call__ method function for the class.
        try:
            call = func.__call__.im_func
            v1 = getargspec(win, call)
            call_docstring = inspect.getdoc(call)
        except AttributeError:
            pass
        if  v1:
            s.append('\n' + v1 + '\n')
        if  call_docstring:
            s.append(call_docstring)
  
        return '\n'.join(s)
    try:
        func=func.im_func
    except:
#        error.traceback()
        pass
    try:
        tt = inspect.getargspec(func)
        if  win.pref.inputass_func_parameter_autocomplete:
            win.function_parameter.extend(tt[0])
        return func.func_name + inspect.formatargspec(*tt)
    except:
#        error.traceback()
        pass
    try:
        return func.func_name + inspect.formatargvalues(*inspect.getargvalues(func))
    except:
#        error.traceback()
        return ''
    
def getConstructor(object):
    """Return constructor for class object, or None if there isn't one."""
    try:
        return object.__init__.im_func
    except AttributeError:
        for base in object.__bases__:
            constructor = getConstructor(base)
            if constructor is not None:
                return constructor
    return None

def import_document(win, syncvar):
    root = win.syntax_info
    if not root:
        return
    
    lineno = win.GetCurrentLine() + 1
    result = root.get_imports(lineno)
    pout('import_document')
    for importline, line in result:
        if syncvar and not syncvar.empty:
            raise StopException
        
        pout('import', importline, line)
        if importline.startswith('from'):
            try:
                exec(importline) in namespace
            except:
                #error.traceback()
                pass
        elif importline.startswith('import'):
            try:
                exec(importline) in namespace
            except:
#                error.traceback()
                pass

def autoComplete(win, word=None, syncvar=None):
    if not word:
        word = getWord(win)
    words = getAutoCompleteList(win, word, syncvar)
    if words:
        return words
    else:
        if not word.startswith('self.'):
            words = getWords(win, word, syncvar)
            return words
    
def getAutoCompleteList(win, command='', syncvar=None):
    from modules.callinmainthread import CallFunctionOnMainThread
    
    _getattributes = CallFunctionOnMainThread(getattributes)
#    if not hasattr(win, 'syntax_info') or not win.syntax_info:
#        return []

    if hasattr(win, 'syntax_info') and win.syntax_info:
        root = win.syntax_info
        r_idens = _get_filter_list(win, command, root.idens)
    else:
        r_idens = []
        
    pout('-'*50)
    pout('getAutoCompleteList', command)

    v = guessWordObject(win, command, True, syncvar)
    flag, object = v
    pout(INDENT, 'ready to output:', flag, object)
    if object:
        if flag == 'obj':
            return _getattributes(object) + r_idens
        else:
            if object.type == 'class':
                return getClassAttributes(win, object, syncvar) + r_idens
    pout(INDENT, 'return:', '***')
    return r_idens

def guessWordObject(win, command, striplast=True, syncvar=None):
    '''
    Guess command's type, if striplast is True, then don't care the last
    word. command will be splitted into list according to '.'
    '''
    root = win.syntax_info
    attributes = []
    # Get the proper chunk of code from the command.
    flag = None
    object = None
#    while command.endswith('.'):
#        command = command[:-1]
    
    if syncvar and not syncvar.empty:
        raise StopException
    
    lineno = win.GetCurrentLine() + 1
    attributes = command.split('.')
    if command == 'self.':    #process self.
        if not root:
            return flag, object
        cls = root.guess_class(lineno)
        if cls:
            return 'source', cls
    elif command.startswith('self.'):   #process self.a. then treat self.a as a var
        if len(attributes) == 2:    #self.xxx
            pass
        else:
            key = attributes[0] + '.' + attributes[1]
            del attributes[0]
            attributes[0] = key
    else:
        if root:
            result = root.guess_type(lineno, command)
            if result:
                attributes = [command]
        
    if syncvar and not syncvar.empty:
        raise StopException
   
    #deal first word
    firstword = attributes[0]
    del attributes[0]
    pout(INDENT, 'attributes:', attributes, 'firstword:', firstword)
    if root:
        result = root.guess_type(lineno, firstword)
    else:
        result = None
    pout(INDENT, 'guess [%s] result:' % firstword, result)
    
    if syncvar and not syncvar.empty:
        raise StopException
    
    if striplast:
        if attributes:
            del attributes[-1]
            
    if result:
        t, v = result
        pout(INDENT, 'begin try_get_obj_type:', t, v, attributes)
        flag, object = try_get_obj_type(win, t, v, lineno)
        pout(INDENT, 'result:', flag, object, attributes)
        
        if syncvar and not syncvar.empty:
            raise StopException
        
        if not attributes or attributes[0] == '':
            return flag, object
        
        if flag == 'source' or attributes:
            #deal other rest
            flag, object = try_get_obj_attribute(win, firstword, flag, object, attributes)
            pout(INDENT, 'result:', flag, 'object=', object)
    else:
        if firstword.startswith('self.'):
            word = firstword.split('.', 1)[1]
            if root:
                cls = root.guess_class(lineno)
            else:
                cls = None
            
            if syncvar and not syncvar.empty:
                raise StopException
            
            if cls:
                for b in cls.bases:
                    if syncvar and not syncvar.empty:
                        raise StopException
                    
                    obj = getObject(win, b, syncvar)
                    if obj:
                        if hasattr(obj, word):
                            object = getattr(obj, word)
                            flag = 'obj'
        else:
            flag = 'obj'
            object = getObject(win, firstword, syncvar)
            if object:
                s = []
                for a in attributes:
                    if not a:
                        break
                    pout(INDENT*2, 'get attribute', a)
                    s.append(a)
                    if hasattr(object, a):
                        object = getattr(object, a)
                        pout(INDENT*2, 'found', firstword, s)
                    else:
                        pout(INDENT*2, 'unfound', 'try to get', '.'.join([firstword]+s))
                        object = getObject(win, '.'.join([firstword]+s), syncvar)
                        if not object:
                            break

    if syncvar and not syncvar.empty:
        raise StopException
    
    return flag, object

def getWords(win, word=None, whole=None):
    if not word:
        word = getWord(whole=whole)
    if not word:
        return []
    else:
        word = word.replace('.', r'\.')
        words = list(set([x for x in re.findall(r"\b" + word + r"(\w+)\b", win.GetText())]))
        words.sort(lambda x, y:cmp(x.upper(), y.upper()))
        return words

re_match = re.compile('^\s*from\s+')
def getObject(win, word, syncvar=None):
    pout(INDENT, 'getObject:', word)
    object = None
    line = win.GetLine(win.GetCurrentLine())

    if syncvar and not syncvar.empty:
        raise StopException
    
    if re_match.match(line):
        if sys.modules.has_key(word):
            object = sys.modules[word]
        else:
            try:
                object = __import__(word, [], [], [''])
            except:
                pass
    else:
        object = evaluate(win, word, syncvar)
#        try:
#            object = eval(word, namespace)
#            if syncvar and not syncvar.empty:
#                raise StopException
#        except:
#            try:
#                import_document(win, syncvar)
#                if syncvar and not syncvar.empty:
#                    raise StopException
#                
#                object = eval(word, namespace)
#            except:
#                try:
#                    pout(INDENT*2, 'import %s' % word)
#                    exec('import %s' % word) in namespace
#                    object = eval(word, namespace)
#                except:
#                    pass
    pout(INDENT, 'getObject result [%s]:' % word, object)
    return object
    
def getClassAttributes(win, cls, syncvar):
    s = set([])
    root = win.syntax_info
    if cls and root:
        s = set(cls.locals)
        for b in cls.bases:
            if syncvar and not syncvar.empty:
                raise StopException
            
            c = root.search_name(cls.lineno, b)
            if c:
                _cls = root.guess_class(c[2])
                if _cls:
                    s.update(_cls.locals)
                    continue
            obj = getObject(win, b, syncvar)
            if obj:
                s.update(getattributes(obj))
#    pout(INDENT, "getClassAttributes", s)
    return list(s)

def try_get_obj_type(win, t, v, lineno):
    pout(INDENT, "try_get_obj_type", t, v, lineno)
    flag = 'obj'
    node = None
    if t in ('class', 'function'):
        node = v
        flag = 'source'
    elif t not in ('reference', 'import'):
        node = v
    else:
        node = getObject(win, v)
    return flag, node
    
def try_get_obj_attribute(win, firstword, flag, object, attributes):
    pout(INDENT, "try_get_obj_attribute", firstword, flag, object, attributes)
    root = win.syntax_info
    if object:
        if flag == 'obj':
            if len(attributes) > 1 and attributes[:-1] == '':
                attrs = attributes[:-1]
            else:
                attrs = attributes
            s = []
            for a in attrs:
                if not a:
                    break
                pout(INDENT*2, 'get attribute', a)
                s.append(a)
                if hasattr(object, a):
                    object = getattr(object, a)
                    pout(INDENT*2, 'found', firstword, s)
                else:
                    pout(INDENT*2, 'unfound', 'try to get', '.'.join([firstword]+s))
                    object = getObject(win, '.'.join([firstword]+s))
                    if not object:
                        break
        else:
            if not root:
                return flag, None
            
            o = attributes[0]
            del attributes[0]
            r = object.get_local_name(o)
            if r:
                t, v, line = r
                if t == 'reference':
                    gt = root.guess_type(line, v)
                    if gt:
                        t, v = gt
                
                flag, object = try_get_obj_type(win, t, v, line)
                if attributes:
                    return try_get_obj_attribute(win, firstword, flag, object, attributes)
                else:
                    return flag, object
            else:
                for b in object.bases:
                    c = root.search_name(object.lineno, b)
                    if c:
                        cls = root.guess_class(c[2])
                        gr = cls.get_local_name(o)
                        if gr:
                           t, v, line = gr
                           if t == 'reference':
                               gt = root.guess_type(line, v)
                               if gt:
                                   t, v = gt
                           flag, object = try_get_obj_type(win, t, v, line)
                           if attributes:
                               return try_get_obj_attribute(win, firstword, flag, object, attributes)
                           else:
                               return flag, object
                    else:
                        flag = 'obj'
                        obj = getObject(win, b)
                        if hasattr(obj, o):
                            return flag, getattr(obj, o)
                
                object = None
    return flag, object

#getlocals
import __builtin__
import keyword
import types

def default_identifier(win):
    return keyword.kwlist + [x for x in dir(__builtin__) if isinstance(getattr(__builtin__, x), (types.BuiltinFunctionType, type))] + ['None', 'as', 'True', 'False', 'self']

def _get_filter_list(win, word, words):
    if not win.pref.inputass_full_identifier:
        return []

    if not word:
        return []
    r = set([])
    if '.' in word:
        base, left = word.rsplit('.', 1)
        base += '.'
        _len = len(base)
        for w in words:
            wleft = w[_len:]
            if w.startswith(base) and len(wleft) > 1:
                if '.' in wleft:
                    wleft = wleft.split('.', 1)[0]
                r.add(wleft)
    else:
        ch = word[0].upper()
        for w in list(words):
            if ch == w[0].upper():
                if '.' in w:
                    w = w.split('.', 1)[0]
                r.add(w)
    return list(r)

def get_locals(win, lineno, word, syncvar):
    root = win.syntax_info
    if root:
        r_idens = _get_filter_list(win, word, root.idens)
    else:
        r_idens = []
    if '.' in word:
        if word.endswith('.'):
#            word = word[:-1]
            length = 0
        else:
            w, ext = word.rsplit('.', 1)
            length = len(ext)
        return length, getAutoCompleteList(win, word)
    else:
        if root:
            r = root.get_locals(lineno)
        else:
            r = []
        d = {}
        for i in r + default_identifier(win):
            if syncvar and not syncvar.empty:
                raise StopException
            
            if len(i) <= 1:
                continue
            k = i[0].upper()
            s = d.setdefault(k, [])
            if i not in s:
                s.append(i)
        for k, v in d.items():
            d[k].sort(lambda x, y:cmp(x.upper(), y.upper()))
         
        if len(word) > 0 and (d.has_key(word[0].upper()) or r_idens):
            words = d.get(word[0].upper(), []) + r_idens
            if words:
                for i in words:
                    if syncvar and not syncvar.empty:
                        raise StopException
                    
                    if i.startswith(word):
                        return len(word), words
        
        return None, []
