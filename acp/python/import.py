import sys
import re
from modules import PyParse

re_as = re.compile('\s+as(\s+|$)')
re_match = re.compile('import\s*$|,\s*$')
def fromimport(win, matchobj):
    n = {}
    try:
        b = re_as.search(matchobj.group())
        if b:
            return 'blank', ''
        b = re_match.search(matchobj.group())
        if not b:
            return 'blank', ''
        module = matchobj.groups()[0]
        if sys.modules.has_key(module):
            keys = dir(sys.modules[module])
        else:
            exec('import ' + module) in n
            keys = dir(sys.modules[module])
        return 'append', keys
    except:
#        error.error('Execute code error: import ' + matchobj.groups()[0])
#        error.traceback()
        return 'blank', ''

import import_utils
def calltip(win, word, syncvar):
    return import_utils.get_calltip(win, word, syncvar)

def autodot(win, word, syncvar):
    return import_utils.autoComplete(win, word, syncvar)

def analysis(win, syncvar):
    try:
        win
    except:
        return
    line = win.GetCurrentLine()
    root = PyParse.parseString(win.getRawText(), syncvar)
    if not syncvar.empty or not root:
        return
    win.lock.acquire()
    win.syntax_info = root
    win.lock.release()
    
def locals(win, line, word, syncvar):
    if hasattr(win, 'syntax_info') and win.syntax_info:
        return import_utils.get_locals(win, line, word, syncvar)
    else:
        return None, []
