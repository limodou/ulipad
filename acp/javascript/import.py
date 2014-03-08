import os
from modules import dict4ini
from modules import Globals

_fmtime = None
_ini = None
_ini_filename = os.path.join(Globals.workpath, 'acp/javascript/javascript.tag')

def get_newest_ini():
    global _ini
    if _fmtime and _ini:
        if _fmtime < os.path.getmtime(_ini_filename):
            _ini = dict4ini.DictIni(_ini_filename)
    else:
        _ini = dict4ini.DictIni(_ini_filename)
    return _ini

def default_identifier(win):
    ini = get_newest_ini()
    return ini.default.identifiers

def calltip(win, word, syncvar):
    ini = get_newest_ini()
    pos = word.rfind('.')
    if pos != -1:
        word = word[pos+1:]
    if not word:
        pos=win.GetCurrentPos()
        if win.getChar(pos-1) == '(':
            pos -= 1
        line = win.GetCurrentLine()
        linePos=win.PositionFromLine(line)
        if pos > linePos:
            word = win.getChar(pos - 1)       
    return ini.functions.get(word, '')

def autodot(win, word, syncvar):
    ini = get_newest_ini()
    if word.endswith('.'):
        word = word[:-1]
    return ini.dots[word]

