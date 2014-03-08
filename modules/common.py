#   Programmer:     limodou
#   E-mail:         limodou@gmail.com
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
#   $Id: common.py 1868 2007-01-27 07:19:29Z limodou $

"""Used to define commonly functions.
"""
import locale
import types
import os
import wx
import sys
import codecs
import Globals
import time

try:
    defaultencoding = locale.getdefaultlocale()[1]
except:
    defaultencoding = None

if not defaultencoding:
    defaultencoding = 'UTF-8'
try:
    codecs.lookup(defaultencoding)
except:
    defaultencoding = 'UTF-8'

try:
    defaultfilesystemencoding = sys.getfilesystemencoding()
except:
    defaultfilesystemencoding = None

if not defaultfilesystemencoding:
    defaultfilesystemencoding = 'ASCII'
try:
    codecs.lookup(defaultfilesystemencoding)
except:
    defaultfilesystemencoding = 'ASCII'

def unicode_path(path, encoding=defaultfilesystemencoding):
    """convert path to unicode
    """
    return decode_string(path, encoding)

def encode_path(path, encoding=defaultfilesystemencoding):
    return encode_string(path, encoding)

def unicode_abspath(path):
    """convert path to unicode
    """
    return decode_string(os.path.abspath(path), defaultfilesystemencoding)

def uni_join_path(*path):
    return decode_string(os.path.join(*path), defaultfilesystemencoding)

def uni_work_file(filename):
    return uni_join_path(Globals.workpath, filename)

def decode_string(string, encoding=None):
    """convert string to unicode

    If the second parameter encoding is omit, the default locale will be used.
    """
    if not encoding:
        encoding = defaultencoding
    if not isinstance(string, types.UnicodeType):
        return unicode(string, encoding)
    else:
        return string
unicode_string = decode_string

def encode_string(string, encoding=None):
    """convert unicode to string

    If the second parameter encoding is omit, the default locale will be used.
    """
    if not encoding:
        encoding = defaultencoding
    if isinstance(string, types.UnicodeType):
        return string.encode(encoding)
    else:
        return string

def get_app_filename(mainframe, filename):
    """concatenate app.workpath and filename
    """
    return decode_string(os.path.normpath(os.path.join(mainframe.app.workpath, filename)), defaultfilesystemencoding)

def showerror(*args):
    """show error message dialog

    win is parent window
    """
    if len(args) > 1:
        win, message = args
    else:
        win = Globals.mainframe
        message = args[0]
    if not isinstance(message, types.StringTypes):
        message = str(message)
    wx.MessageDialog(win, message, tr("Error"), wx.OK | wx.ICON_EXCLAMATION).ShowModal()

def showmessage(*args):
    """show message dialog

    win is parent window
    """
    if len(args) > 1:
        win, message = args
    else:
        win = Globals.mainframe
        message = args[0]
    if not isinstance(message, types.StringTypes):
        message = str(message)
    wx.MessageDialog(win, message, tr("Message"), wx.OK | wx.ICON_INFORMATION).ShowModal()

def setmessage(*args):
    """show message in main frame statusbar

    mainframe is main frame
    """
#    GenericDispatch.Dispatch(mainframe, mainframe.SetStatusText, message, 0)
    if len(args) > 1:
        win, message = args
    else:
        win = Globals.mainframe
        message = args[0]
    wx.CallAfter(win.SetStatusText, message, 0)

def getHomeDir():
    ''' Try to find user's home directory, otherwise return current directory.'''
    try:
        path1=os.path.expanduser("~")
    except:
        path1=""
    try:
        path2=os.environ["HOME"]
    except:
        path2=""
    try:
        path3=os.environ["USERPROFILE"]
    except:
        path3=""

    if os.path.exists(path1): return path1
    if os.path.exists(path2): return path2
    if os.path.exists(path3): return path3
    return os.getcwd()

def uni_prt(a, encoding=None):
    s = []
    if not encoding:
        encoding = defaultencoding
    if isinstance(a, (list, tuple)):
        if isinstance(a, list):
            s.append('[')
        else:
            s.append('(')
        for i, k in enumerate(a):
            s.append(uni_prt(k, encoding))
            if i<len(a)-1:
                s.append(', ')
        if isinstance(a, list):
            s.append(']')
        else:
            s.append(')')
    elif isinstance(a, dict):
        for i, k in enumerate(a.items()):
            key, value = k
            s.append('{%s: %s}' % (uni_prt(key, encoding), uni_prt(value, encoding)))
            if i<len(a.items())-1:
                s.append(', ')
    elif isinstance(a, str):
        s.append("%s" %a)
    elif isinstance(a, unicode):
        s.append("%s" % a.encode(encoding))
    else:
        s.append(str(a))
    return ''.join(s)

def getpngimage(filename):
    if isinstance(filename, (str, unicode)):
        if not os.path.exists(filename) and not os.path.isabs(filename):
            filename = os.path.normpath(os.path.join(Globals.workpath, filename))
        path, fname = os.path.split(filename)
        ini = get_config_file_obj()
        
        if path.endswith('images') and 'icontheme' in ini.default:
            files = []
            filename1 = os.path.join(path, 'theme', ini.default.icontheme, fname)
            files.append(filename1)
            if not filename1.endswith('.png'):
                filename2 = os.path.splitext(filename1)[0] + '.png'
                files.insert(0, filename2)
            for f in files:
                if os.path.exists(f):
                    filename = f
                    break
        fname, ext = os.path.splitext(decode_string(filename))
        if ext.lower() == '.ico':
            icon = wx.Icon(filename, wx.BITMAP_TYPE_ICO, 16, 16)
            bitmap = wx.EmptyBitmap(16, 16)
            bitmap.CopyFromIcon(icon)
            return bitmap
        if ext.lower() == '.png':
            f = filename
        else:
            f = fname + '.png'
            if not os.path.exists(f):
                f = filename
        image = wx.Image(f)
        if image.Ok():
            return image.ConvertToBitmap()
        else:
            return filename
    else:
        return filename

def getProjectName(filename):
    path = getProjectHome(filename)
    #found _project
    from modules import dict4ini
    ini = dict4ini.DictIni(os.path.normpath(os.path.join(path, '_project')))
    name = ini.default.get('projectname', [])
    if not isinstance(name, list):
        name = [name]
    return name

def getCurrentPathProjectName(filename):
    path = getCurrentPathProjectHome(filename)
    #found _project
    from modules import dict4ini
    ini = dict4ini.DictIni(os.path.join(os.path.join(path, '_project')))
    name = ini.default.get('projectname', [])
    if not isinstance(name, list):
        name = [name]
    return name

def getCurrentPathProjectHome(filename):
    if not filename:
        return ''
    if os.path.isfile(filename):
        path = os.path.dirname(os.path.abspath(filename))
    else:
        path = filename
    if not os.path.exists(os.path.join(path, '_project')):
        path = ''
    return os.path.normpath(path)

def getProjectHome(filename):
    if not filename:
        return ''
    if os.path.isfile(filename):
        path = os.path.dirname(os.path.abspath(filename))
    else:
        path = filename
    while not os.path.exists(os.path.join(path, '_project')):
        newpath = os.path.dirname(path)
        if newpath == path: #not parent path, so not found _project
            return ''
        path = newpath
    return os.path.normpath(path)

def getProjectFile(filename):
    if not filename:
        return ''
    if os.path.isfile(filename):
        path = os.path.dirname(os.path.abspath(filename))
    else:
        path = filename
    while not os.path.exists(os.path.join(path, '_project')):
        newpath = os.path.dirname(path)
        if newpath == path: #not parent path, so not found _project
            return ''
        path = newpath
    return os.path.normpath(os.path.join(path, '_project'))

def getConfigPathFile(f, prefix=''):
    filename = os.path.normpath(os.path.join(Globals.workpath, prefix, f))
    if os.path.exists(filename):
        return filename
    filename = os.path.normpath(os.path.join(Globals.confpath, prefix, f))
    if os.path.exists(filename):
        return filename
    return ''

_config_file = None
def get_config_file():
    global _config_file
    
    if not _config_file:
        _config_file = getConfigPathFile('config.ini')
        if not _config_file:
            _config_file = os.path.normpath(os.path.join(Globals.workpath, 'config.ini'))
            
    return _config_file

#_config_ini = None
def get_config_file_obj(*args, **kwargs):
#    global _config_ini
    
#    if not _config_ini:
    from modules import dict4ini
    _config_ini = dict4ini.DictIni(get_config_file(), *args, **kwargs)
        
    return _config_ini
    
def uni_file(filename):
    if isinstance(filename, str):
        return decode_string(filename, defaultfilesystemencoding)
    else:
        return filename

def normal_file(filename):
    if isinstance(filename, unicode):
        return encode_string(filename, defaultfilesystemencoding)
    else:
        return filename

def print_time(name, debug):
    if debug:
        print name, time.strftime("%H:%M:%S")


def getCurrentDir(filename):
    if os.path.isfile(filename):
        dir = os.path.dirname(filename)
    else:
        dir = filename
    return dir

def show_in_message_window(text):
    win = Globals.mainframe
    win.createMessageWindow()
    win.panel.showPage(tr('Message'))
    win.messagewindow.SetText(text)

def note(text):
    wx.CallAfter(Globals.mainframe.statusbar.note, text)
#    setmessage(Globals.mainframe, text)

def warn(text):
    wx.CallAfter(Globals.mainframe.statusbar.warn, text)
#    setmessage(Globals.mainframe, text)

def curry(*args, **kwargs):
    def _curried(*moreargs, **morekwargs):
        return args[0](*(args[1:]+moreargs), **dict(kwargs.items() + morekwargs.items()))
    return _curried

def set_acp_highlight(ini, suffix, acps, highlight):
    if acps:
        s = ini.acp.get(suffix, [])
        if not isinstance(s, list):
            s = [s]
        if not isinstance(acps, list):
            acps = [acps]
        for i in acps:
            if not i in s:
                s.append(i)
        ini.acp[suffix] = s
    if highlight:
        ini.highlight[suffix] = highlight
    
def remove_acp_highlight(ini, suffix, acps, highlight):
    if acps:
        s = ini.acp.get(suffix, [])
        if not isinstance(s, list):
            s = [s]
        if not isinstance(acps, list):
            acps = [acps]
        for i in acps:
            if i in s:
                s.remove(i)
        if not s:
            del ini.acp[suffix]
        else:
            ini.acp[suffix] = s
    if highlight:
        del ini.highlight[suffix]

def pout(head, *args):
    from Debug import debug
    if debug.is_debug():
        print head,
        for i in args:
            print i,
        print

if wx.Platform == '__WXMSW__':
    faces = { 'times': 'Times New Roman',
              'mono' : 'Courier New',
              'helv' : 'Arial',
              'other': 'Comic Sans MS',
              'size' : 12,
              'lnsize' : 10,
             }
elif wx.Platform == '__WXGTK__':
    faces = { 'times': 'Times',
              'mono' : 'Courier 10 Pitch',
              'helv' : 'Helvetica',
              'other': 'new century schoolbook',
              'size' : 12,
              'lnsize' : 10,
             }
else:
    faces = { 'times': 'Times',
              'mono' : 'Monaco',
              'helv' : 'Helvetica',
              'other': 'new century schoolbook',
              'size' : 12,
              'lnsize' : 10,
             }
    

def merge_bitmaps(image1, image2):
    #prepare blank bitmap
    bmp = wx.EmptyBitmap(16, 16)
    mem_dc = wx.MemoryDC()
    mem_dc.SelectObject(bmp)
    brush = wx.Brush('white', wx.SOLID)
    mem_dc.SetBackground(brush)
    mem_dc.Clear()
    
    mask = wx.Mask(image2, wx.WHITE)
    image2.SetMask(mask)
    
    mem_dc.DrawBitmap(getpngimage(image1), 0, 0, True)
    mem_dc.DrawBitmap(getpngimage(image2), 0, 0, True)
    
    return bmp

def who_called_me(show_filename=False, out=None, indent=' '):
    def _wrapper(fn):
        def _inner_wrapper(*args, **kwargs):
            import sys
            import inspect
            output = out or sys.stdout
            assert hasattr(output, 'write'), \
                'argument \'out\' of function \'who_called_me\' must have a write method'
            index = 0
            stack = inspect.stack()
            stack.reverse()
            # remove ourself from the stack list
            stack.pop()
            for record in stack:
                frame = record[0]
                line = frame.f_lineno
                func_name = frame.f_code.co_name
                if show_filename:
                    descr = frame.f_code.co_filename
                else:
                    descr = frame.f_globals["__name__"]
                print >>output, '%s%s@%s:%d' % (indent*index, descr, func_name, line)
                # to be safe explicitly delete the stack frame reference
                # @see http://docs.python.org/lib/inspect-stack.html
                del frame
                index += 1
            del stack
            if hasattr(output, 'flush'):
                output.flush()
            return fn(*args, **kwargs)
        return _inner_wrapper
    return _wrapper

def webopen(filename):
    import webbrowser

    o = webbrowser.get()
    if hasattr(o, 'args'):
        o.args = [arg.replace('"%s"', '%s') for arg in o.args]
    if not filename.startswith('http://') and not filename.startswith('mailto:'):
        o.open('file://'+filename, 1)
    else:
        o.open(filename)

def hz_string_ljust(s, length):
    l = string_width(s)
    return s.ljust(length - (l - len(s)))

def hz_string_rjust(s, length):
    l = string_width(s)
    return s.rjust(length - (l - len(s)))

def string_width(text):
    import unicodedata
    s = 0
    for ch in text:
        if isinstance(ch, unicode):
            if unicodedata.east_asian_width(ch) != 'Na':
                s += 2
            else:
                s += 1
        else:
            s += 1
    return s
            
def set_line_ending(ending):
    Globals.mainframe.SetStatusText(tr('Line ending: ') + ending, 4)
    
def set_encoding(encoding):
    Globals.mainframe.SetStatusText(tr('Encoding: ') + encoding, 5)
