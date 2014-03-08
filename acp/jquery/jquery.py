import os
import wx.stc
from modules import dict4ini
from modules import Globals

_fmtime = None
_ini = None
_ini_filename = os.path.join(Globals.workpath, 'acp/jquery/jquery.tag')

# Lookups to determine what the current line-ending is.
_eols = { wx.stc.STC_EOL_CR : '\r',
          wx.stc.STC_EOL_CRLF : '\r\n',
          wx.stc.STC_EOL_LF : '\n' }

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

    # Only autodot when following a $ or a $(...)
    pos = win.GetCurrentPos()
    prev_char = win.getChar(pos - 2)
    if prev_char == '$':
        return ini.default.dots

    if following_jquery_func(win):
        return ini.default.dots

    # No hit.
    return ''

def at_eol(win, pos):
    'Return True if pos is pointing to the end of a line.'
    char = win.getChar(pos)

    eol_type = _eols[win.GetEOLMode()]
    if len(eol_type) == 1:
        return char == eol_type

    prev_char = win.getChar(pos - 1)
    return prev_char + char == eol_type

def backwards_match(txt, win, pos):
    'Returns true if txt is found at win, pos going backwards.'
    if win.FindText(pos - len(txt), pos, txt, 0) != -1:
        # Deselect what FindText selects.
        win.SetSelection(-1,-1)
        return True
    return False

def following_jquery_func(win):
    'Returns true if the cursor is following a jquery function call $(...).'
    # Try searching for $(...).  Only search up 5 lines.
    MAX_LINE_SEARCH = 5
    prev_char_pos = win.GetCurrentPos() - 2
    if prev_char_pos < 0 or win.getChar(prev_char_pos) != ')':
        return False

    # OK, start scanning backwards looking for a matching '('
    lines_searched = 0
    pos = prev_char_pos
    while lines_searched < MAX_LINE_SEARCH and prev_char_pos > 0:
        pos -= 1
        char = win.getChar(prev_char_pos)
        if at_eol(win, pos):
            lines_searched += 1
            continue

        if backwards_match('$(', win, pos):
            return True
    return False
