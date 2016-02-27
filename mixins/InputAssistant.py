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
#   $Id$

import os
import re
import wx
from modules import dict4ini
from modules.Debug import error
from modules import common
from modules import Mixin
import SnipMixin

try:
    set
except:
    from sets import Set as set

#mylocal = threading.local()
class DUMY_CLASS:pass

assistant = {}
assistant_objs = {}
KEYS = {'<space>':' ', '<equal>':'=', '<div>':'/', '<square>':'['}
CALLTIP_AUTOCOMPLETE = 2
class StopException(Exception):pass

list_type = 1

class InputAssistant(Mixin.Mixin):
    __mixinname__ = 'inputassistant'

    def __init__(self):
        self.initmixin()
        self.acpmodules = {}
        self.acpmodules_time = {}
        self.lasteditor = None
        self.lastlanguage = None

    def run(self, editor, event, on_char=True, syncvar=None):
        if not editor.pref.input_assistant:
            return False

        if not hasattr(editor, 'lexer') or editor.lexer.cannot_expand(editor):
            return False

        if not syncvar.empty:
            return True

        self.syncvar = syncvar

        if wx.version().split('.')[:2] > ['2', '8']:
            key = event.KeyCode
            ctrl = event.controlDown
            alt = event.altDown
            shift = event.shiftDown
        else:
            key = event.GetKeyCode()
            ctrl = event.ControlDown()
            alt = event.AltDown()
            shift = event.ShiftDown()
            
        self.on_char = on_char
        self.oldpos = editor.GetCurrentPos()
        self.editor = editor
        self.language = editor.languagename
        if not hasattr(self.editor, 'default_auto_identifier'):
            self.editor.default_auto_identifier = {}
        if not hasattr(self.editor, 'input_calltip'):
            self.editor.input_calltip = []
        if not hasattr(self.editor, 'input_autodot'):
            self.editor.input_autodot = []
        if not hasattr(self.editor, 'input_locals'):
            self.editor.input_locals = []
        if not hasattr(self.editor, 'input_analysis'):
            self.editor.input_analysis = []

        if editor.hasSelection() and on_char and not ctrl and not alt and (31 < key < 127 or key > wx.WXK_PAGEDOWN):
            self.check_selection(editor)

        f = 0
        if not on_char:
            if ctrl:
                f |= wx.stc.STC_SCMOD_CTRL
            elif alt:
                f |= wx.stc.STC_SCMOD_ALT
            elif shift:
                f |= wx.stc.STC_SCMOD_SHIFT

        self.key = (f, key)
        if not self.install_acp(editor, self.language) and not self.editor.custom_assistant:
            return False

        try:
            return self._run()
        except StopException:
#            error.traceback()
            return True
        except:
            error.traceback()
            return False

    def install_acp(self, editor, language, changeflag=False):
#        changeflag = False
        filename = common.getConfigPathFile('%s.acp' % language)
        if not os.path.exists(filename):
            if assistant.has_key(language):
                del assistant[language]
                changeflag = True
        else:
            if not changeflag:
                changeflag = self.install_assistant(language, filename)
        self.editor = editor

        try:
            self.lasteditor
        except:
            error.traceback()
            self.lasteditor = None
            self.lastlanguage = None

        if changeflag or not self.lasteditor is editor or self.lastlanguage != editor.languagename:
            self.lasteditor = editor
            self.lastlanguage = editor.languagename
            #re cal all the default auto indentifier list
            editor.default_auto_identifier = {}
            editor.input_calltip = []
            editor.input_autodot = []
            editor.input_locals = []
            editor.input_analysis = []
            for obj in self.get_acp(language) + editor.custom_assistant:
                self.install_default_auto_identifier(obj)
                self.install_calltip(obj)
                self.install_autodot(obj)
                self.install_locals(obj)
                self.install_analysis(obj)
        return True

    def get_acp(self, language):
        return assistant.get(language, [])

    def get_all_acps(self):
        return self.get_acp(self.language) + self.editor.custom_assistant

    def _run(self):
        if not self.syncvar.empty:
            return True
        win = self.editor
        objs = self.get_all_acps()
        if not objs:
            return False
        else:
            #matching
            for obj in objs:
                if not self.syncvar.empty:
                    return True
                if obj.projectname and obj.projectname not in common.getProjectName(win.filename):
                    continue
                #autostring
                if obj.autostring.has_key(self.key):
                    s = obj.autostring[self.key]
                    for k, text in s:
                        if not self.syncvar.empty:
                            return True
                        word, start, end = self.getWord(k)
                        if k == word:
                            if self.parse_result(obj, text, start, end, self.key, matchtext=None):
                                return True
                            if win.AutoCompActive():
                                self.postcall(win.AutoCompCancel)
                            if not isinstance(text, list):
                                def f():
                                    win.BeginUndoAction()
                                    win.SetTargetStart(start)
                                    win.SetTargetEnd(end)
                                    win.ReplaceTarget('')
                                    win.GotoPos(start)
                                    self.settext(text)
                                    win.EndUndoAction()
                                self.postcall(f)
                                return True
                            else:
                                def f():
                                    win.BeginUndoAction()
#                                    win.inputassistant_obj = obj
                                    win.word_len = start, end + 1
                                    win.replace_strings = None
                                    win.UserListShow(list_type, " ".join(text))
                                    win.EndUndoAction()
                                self.postcall(f)
                                return True
                #autostring_append
                if obj.autostring_append.has_key(self.key):
                    s = obj.autostring_append[self.key]
                    for k, text in s:
                        word, start, end = self.getWord(k)
                        if k == word:
                            if self.parse_result(obj, text, start, end, self.key):
                                return True
                            if win.AutoCompActive():
                                self.postcall(win.AutoCompCancel)
                            if not isinstance(text, list):
                                def f():
                                    win.BeginUndoAction()
                                    self.settext(text)
                                    win.EndUndoAction()
                                self.postcall(f)
                                return True
                            else:
                                def f():
                                    win.BeginUndoAction()
#                                    win.inputassistant_obj = obj
                                    win.replace_strings = None
                                    win.word_len = win.GetCurrentPos(), -1
                                    win.UserListShow(list_type, " ".join(text))
                                    win.EndUndoAction()
                                self.postcall(f)
                                return True
                #autore
                if obj.autore.has_key(self.key):
                    line = win.GetCurrentLine()
                    txt = win.GetTextRange(win.PositionFromLine(line), win.GetCurrentPos())
                    txt = txt.encode('utf-8')
                    s = obj.autore[self.key]
                    length = len(txt)
                    flag = False
                    for k, text in s:
                        pos = 0
                        b = k.search(txt, pos)
                        while b:
                            if b.end() == length: #find
                                flag = True
                                break
                            else:
                                pos += 1
                                b = k.search(txt, pos)
                        if flag:
                            r = []
                            r.append(unicode(b.group(), 'utf-8'))
                            r.extend([unicode(x, 'utf-8') for x in b.groups()])
                            if self.parse_result(obj, text, 0, 0, self.key, matchtext=r, line=line, matchobj=b):
                                return True
                            if win.AutoCompActive():
                                self.postcall(win.AutoCompCancel)
                            if not isinstance(text, list):
                                m = []
                                for p in text:
                                    for i in range(len(r)):
                                        p = p.replace('\\' + str(i), r[i])
                                    m.append(p)
                                def f():
                                    win.BeginUndoAction()
                                    pos = win.PositionFromLine(line)
                                    win.SetTargetStart(pos + b.start())
                                    win.SetTargetEnd(pos + b.end())
                                    win.ReplaceTarget('')
                                    win.GotoPos(pos + b.start())
                                    self.settext(m)
                                    win.EndUndoAction()
                                self.postcall(f)
                                return True
                            else:
                                def f():
                                    win.BeginUndoAction()
#                                    win.inputassistant_obj = obj
                                    pos = win.PositionFromLine(line)
                                    win.replace_strings = r
                                    win.word_len = pos + b.start(), pos + b.end()
                                    win.UserListShow(list_type, " ".join(text))
                                    win.EndUndoAction()
                                self.postcall(f)
                                return True
                #autore_append
                if obj.autore_append.has_key(self.key):
                    line = win.GetCurrentLine()
                    txt = win.GetTextRange(win.PositionFromLine(line), win.GetCurrentPos())
                    txt = txt.encode('utf-8')
                    s = obj.autore_append[self.key]
                    length = len(txt)
                    flag = False
                    for k, text in s:
                        pos = 0
                        b = k.search(txt, pos)
                        while b:
                            if b.end() == length: #find
                                flag = True
                                break
                            else:
                                pos += 1
                                b = k.search(txt, pos)
                        if flag:
                            r = []
                            r.append(unicode(b.group(), 'utf-8'))
                            r.extend(unicode(x, 'utf-8') for x in b.groups())
                            if self.parse_result(obj, text, 0, 0, self.key, matchtext=r, line=line, matchobj=b):
                                return True
                            if win.AutoCompActive():
                                self.postcall(win.AutoCompCancel)
                            if not isinstance(text, list):
                                m = []
                                for p in text:
                                    for i in range(len(r)):
                                        p = p.replace('\\' + str(i), r[i])
                                    m.append(p)
                                def f():
                                    win.BeginUndoAction()
                                    self.settext(m)
                                    win.EndUndoAction()
                                self.postcall(f)
                                return True
                            else:
                                def f():
                                    win.BeginUndoAction()
#                                    win.inputassistant_obj = obj
                                    pos = win.PositionFromLine(line)
                                    win.replace_strings = r
                                    win.word_len = win.GetCurrentPos(), -1
                                    win.UserListShow(list_type, " ".join(text))
                                    win.EndUndoAction()
                                self.postcall(f)
                                return True

            else:
                if self.on_char: #in on_char event
                    #deal with auto identifiers
                    result = False
                    try:
                        if self.key[0] == 0 and self.key[1] == ord('('):
                            self.process_calltip_begin()
                            result = True
                        elif self.key[0] == 0 and self.key[1] == ord(')'):
                            self.process_calltip_end()
                            result = True
                        elif self.key[0] == 0 and self.key[1] == ord('.'):
                            self.process_autocomplete()
                            result = True
                        if not result:
                            return self.process_default()
                        else:
                            return True
                    except StopException:
                        pass
                    except:
                        error.traceback()
            return False

    def run_default(self, editor, syncvar):
        self.syncvar = syncvar
        self.oldpos = editor.GetCurrentPos()
        self.on_char = True
        try:
            return self.process_default(True, editor)
        except StopException:
            return False

    def process_default(self, skipkey=False, editor=None):
        if not editor:
            win = self.editor
        else:
            win = editor
        if win.AutoCompActive():
            return False
        if not win.pref.inputass_identifier:
            return False

        win = self.editor
        if not skipkey and self.key[1] > 127:
            return False

        if not self.syncvar.empty:
            return False

        word = _getWord(win)
        win.word_len = win.GetCurrentPos(), -1

        v = self.call_locals(win.GetCurrentLine() + 1, word, self.syncvar)
        if v:
            length, words = v
            if words:
                # function parameter autocomplete.
                words.extend(win.function_parameter)
                s = word[-1*length:].upper()
                slist = self._get_popup_list(word, words)
                if slist:
                    if not self.syncvar.empty:
                        return False
#                    def f():
#                        win.replace_strings = word
#                        win.word_len = win.GetCurrentPos(), -1
#                        win.UserListShow(list_type, " ".join(slist))
#                    self.postcall(f)

                    win.word_len = win.GetCurrentPos() - length, -1
                    self.postcall(win.AutoCompShow, length, ' '.join(slist))
                    win.AutoCompShow(length, ' '.join(slist))
                    return True

        if not word: return False
        d = win.default_auto_identifier
        if d.has_key(word[0].upper()):
            words = d.get(word[0].upper(), [])
            if words:
                s = word.upper()
                length = len(s)
                slist = self._get_popup_list(word, words)
                if slist:
                    if not self.syncvar.empty:
                        return False
#                    def f():
#                        win.replace_strings = word
#                        win.word_len = win.GetCurrentPos(), -1
#                        win.UserListShow(list_type, " ".join(slist))
#                    self.postcall(f)
#                    print 'end2 process_default', win.AutoCompActive()

                    win.word_len = win.GetCurrentPos() - length, -1
                    self.postcall(win.AutoCompShow, len(s), ' '.join(slist))
                    win.AutoCompShow(len(s), ' '.join(slist))
                    return True

        return False

    def _get_popup_list(self, word, words):
        r = []
        flag = False
        if words:
            if '.' in word:
                word = word.rsplit('.', 1)[1]
            s = word.upper()
            slen = len(s)
            r = set([x for x in words if len(x)>1])
            for w in r:
                if len(w) > 1 and w.upper().startswith(s) and slen < len(w):
                    flag = True
                    break

        if flag:
            r = list(r)
            r.sort(lambda x, y:cmp(x.upper(), y.upper()))
            return r

    def process_calltip_begin(self):
        win = self.editor
        if not win.pref.inputass_calltip:
            return False
        pos = win.GetCurrentPos()
        word = _getWord(win)
        pos = win.GetCurrentPos()
        r = self.call_calltip(word, self.syncvar)
        if r:
            if isinstance(r, (str, unicode)):
                r = [r]
            tip = '\n\n'.join(list(filter(None, r)) + [tr('(Press ESC to close)')])
            if win.calltip.active and CALLTIP_AUTOCOMPLETE:
                win.calltip.cancel()
            t = tip.replace('\r\n','\n')
            win.calltip_type = CALLTIP_AUTOCOMPLETE
            win.calltip_stack[pos-1] = t
            self.postcall(win.calltip.show, pos, t)
            #save position
            curpos = win.GetCurrentPos()
            win.calltip_column = win.GetColumn(curpos)
            win.calltip_line = win.GetCurrentLine()
            return True
        return False

    def postcall(self, f, *args):
        if self.on_char and not self.syncvar.empty or self.oldpos != self.editor.GetCurrentPos():
            raise StopException
        if self.editor.AutoCompActive():
            wx.CallAfter(self.editor.AutoCompCancel)
        #wx.CallAfter(f, *args)
        return

    def process_calltip_end(self):
        win = self.editor
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = win.GetCurrentPos()
        if caretPos > 0:
            charBefore = win.GetCharAt(caretPos - 1)
            styleBefore = win.GetStyleAt(caretPos - 1)
        # check before
        if charBefore and chr(charBefore) in ")":
            braceAtCaret = caretPos - 1
        if braceAtCaret >= 0:
            braceOpposite = win.BraceMatch(braceAtCaret)
        try:
            if  braceOpposite != -1:
                calltip_text = win.calltip_stack.get(braceOpposite, None)
                if  calltip_text is None:
                    return
                else:
                    klist = win.calltip_stack.keys()
                    klist.sort()
                    i = klist.index(braceOpposite)
                    s = klist[i-1]
                    ss = min(klist)
                    if  braceOpposite == ss:
                        wx.CallAfter(win.calltip.cancel)
                        win.calltip_stack.clear()
                        del win.function_parameter[:]
                        return
                    if  len(win.calltip_stack)>1:
                        del win.calltip_stack[braceOpposite]
                    calltip_text = win.calltip_stack.get(s, None)
                    if  calltip_text:
                        if win.calltip.active and CALLTIP_AUTOCOMPLETE:
                            win.calltip.cancel()
                        win.calltip_type = CALLTIP_AUTOCOMPLETE
                        pos = win.GetCurrentPos()
                        self.postcall(win.calltip.show, pos, calltip_text)
                        #save position
                        curpos = win.GetCurrentPos()
                        win.calltip_column = win.GetColumn(curpos)
                        win.calltip_line = win.GetCurrentLine()
        except:
            error.traceback()
        return False

    def process_autocomplete(self):
        win = self.editor
        if not win.pref.inputass_autocomplete:
            return False

        word = _getWord(win)
        result = self.call_autodot(word, self.syncvar)
        if result:
#            wx.CallAfter(win.AddText, '.')
            result = list(set(result))
            result.sort(lambda x, y:cmp(x.upper(), y.upper()))
            s = ' '.join(result)
#            win.replace_strings = ''
#            win.word_len = win.GetCurrentPos(), -1
#            self.postcall(win.UserListShow, list_type, s)
            win.word_len = win.GetCurrentPos(), -1
            self.postcall(win.AutoCompShow, 0, s)
            win.AutoCompShow(0, s)
            return True
        return False

    def parse_result(self, assistant_obj, text, start, end, key='', matchtext='', line=None, matchobj=None):
        """ return True if success
            return False is failed
        """
        win = self.editor
        text = text[0]
        if (text and text[0] == '@') or (assistant_obj.ini.has_key('auto_funcs') and assistant_obj.ini.auto_funcs.has_key(text)): #maybe a function
            if text[0] != '@':
                modstring = assistant_obj.auto_funcs.get(text)
            else:
                modstring = text
            func = self.get_function(modstring)
            if func:
                try:
                    flag, result = func(win, matchobj)
                    if isinstance(result, tuple):
                        result = list(result)
                        result.sort(lambda x, y:cmp(x.upper(), y.upper()))
                    elif isinstance(result, list):
                        result.sort(lambda x, y:cmp(x.upper(), y.upper()))
                except:
                    error.error('Execute %s.%s failed!' % (func.module_name, func.function_name))
                    error.traceback()
                    return False
                if flag == 'replace':
                    if win.AutoCompActive():
                        self.postcall(win.AutoCompCancel)
                    if isinstance(result, list):
                        def f():
                            win.BeginUndoAction()
#                            win.inputassistant_obj = assistant_obj
                            pos = win.PositionFromLine(line)
                            win.replace_strings = matchtext
                            win.word_len = pos + matchobj.start(), pos + matchobj.end()
                            win.UserListShow(list_type, " ".join(result))
                            win.EndUndoAction()
                        self.postcall(f)
                        return True

                    else:
                        def f():
                            win.BeginUndoAction()
                            win.SetTargetStart(start)
                            win.SetTargetEnd(end)
                            win.ReplaceTarget('')
                            win.GotoPos(start)
                            self.settext(result)
                            win.EndUndoAction()
                        self.postcall(f)
                        return True
                elif flag == 'append':
                    if win.AutoCompActive():
                        wx.CallAfter(win.AutoCompCancel)
                    if isinstance(result, list):
                        def f():
                            win.BeginUndoAction()
#                            win.inputassistant_obj = assistant_obj
                            win.replace_strings = matchtext
                            win.word_len = win.GetCurrentPos(), -1
                            win.UserListShow(list_type, " ".join(result))
                            win.EndUndoAction()
                        self.postcall(f)
                        return True
                    else:
                        def f():
                            win.BeginUndoAction()
                            self.settext(result)
                            win.EndUndoAction()
                        self.postcall(f)
                        return True
                elif flag == "blank":
                    return True
                else:
                    error.error("Can't recognize result type " + flag)
                    error.traceback()
                    return True

        return False


    def install_assistant(self, language, filename):
        flag = False
        if not assistant.has_key(language):
            flag = True
            assistant[language] = [self.get_assistant(filename)]
            obj = assistant[language][0]
            #install include files
            for f in obj.ini.include.values():
                fname = common.getConfigPathFile(f)
                if fname:
                    assistant[language].insert(-1, self.get_assistant(fname))
        else:
            objs = assistant[language]
            for i, obj in enumerate(objs):
                if os.path.getmtime(obj.filename) > obj.ftime:
                    del assistant[language]
                    self.install_assistant(language, filename)
                    flag = True
                    break
        return flag

    def get_assistant(self, filename):
        obj = assistant_objs.get(filename, None)
        if obj:
            if os.path.getmtime(obj.filename) > obj.ftime:
                del assistant_objs[filename]
                return self.get_assistant(filename)
            else:
                return assistant_objs[filename]
        else:
            obj = DUMY_CLASS()
            obj.ini = dict4ini.DictIni(filename, encoding='utf-8', onelevel=True)
            obj.filename = filename
            obj.ftime = os.path.getmtime(filename)
            #autostring is used to replace
            obj.autostring = self.install_keylist(obj.ini.ordereditems(obj.ini.autostring, ['autostring']), False)
            #autostring_append is used to append
            obj.autostring_append = self.install_keylist(obj.ini.ordereditems(obj.ini.autostring_append, ['autostring_append']), False)
            #autore is used to replace
            obj.autore = self.install_keylist(obj.ini.ordereditems(obj.ini.autore, ['autore']), True)
            #autore_replace is used to append
            obj.autore_append = self.install_keylist(obj.ini.ordereditems(obj.ini.autore_append, ['autore_append']), True)
            obj.projectname = obj.ini.default.get('projectname', '')
            assistant_objs[filename] = obj
            return obj

    def get_function(self, modstring):
        func = None
        if not isinstance(modstring, list) and modstring.startswith('@'):
            module, function = modstring[1:].rsplit('.', 1)
            if self.acpmodules.has_key(module):
                mod = self.acpmodules[module]
                if self.need_reinstall_module(mod):
                    mod = reload(mod)
                    self.set_modules_time(mod)
            else:
                try:
                    mod = __import__(module, [], [], [''])
                    self.set_modules_time(mod)
                except:
                    error.error("Can't load the module " + module)
                    error.traceback()
                    return False
                self.acpmodules[module] = mod
            func = getattr(mod, function, None)
            if not callable(func):
                func = None
            else:
                func.module_name = module
                func.function_name = function
        return func

    def install_default_auto_identifier(self, obj):
        if not obj.ini.has_key('auto_default'):
            return
        r = obj.ini.auto_default.values()
        if not r:
            return
        slist = []
        for i in r:
            func = self.get_function(i)
            if func:
                try:
                    result = func(self.editor)
                    if result:
                        slist.extend(result)
                except:
                    error.error('Execute %s.%s failed!' % (func.module_name, func.function_name))
                    error.traceback()
                    return False
            else:
                if not isinstance(i, list):
                    slist.append(i)
                else:
                    slist.extend(i)
        d = self.editor.default_auto_identifier
        for i in slist:
            if len(i) <= 1:
                continue
            k = i[0].upper()
            s = d.setdefault(k, [])
            if i not in s:
                s.append(i)
        for k, v in d.items():
            d[k].sort(lambda x, y:cmp(x.upper(), y.upper()))

    def install_calltip(self, obj):
        if not obj.ini.auto_complete.calltip:
            return
        func = self.get_function(obj.ini.auto_complete.calltip)
        if func:
            self.editor.input_calltip.append(func)

    def install_autodot(self, obj):
        if not obj.ini.auto_complete.autodot:
            return
        func = self.get_function(obj.ini.auto_complete.autodot)
        if func:
            self.editor.input_autodot.append(func)

    def install_locals(self, obj):
        if not obj.ini.auto_complete.locals:
            return
        func = self.get_function(obj.ini.auto_complete.locals)
        if func:
            self.editor.input_locals.append(func)

    def install_analysis(self, obj):
        if not obj.ini.auto_complete.analysis:
            return
        func = self.get_function(obj.ini.auto_complete.analysis)
        if func:
            self.editor.input_analysis.append(func)

    def call_calltip(self, word, syncvar):
        try:
            for f in self.editor.input_calltip:
                r = f(self.editor, word, syncvar)
                if r:
                    return r
        except StopException:
            pass
        except:
            error.traceback()

    def call_autodot(self, word, syncvar):
        result = []
        for f in self.editor.input_autodot:
            try:
                r = f(self.editor, word, syncvar)
                if r:
                    result.extend(r)
            except StopException:
                pass
            except:
                error.traceback()
        return result

    def call_locals(self, line, word, syncvar):
        try:
            if not self.editor:
                return
            result = []
            for f in self.editor.input_locals:
                r = f(self.editor, line, word, syncvar)
                if r:
#                    return r
                    result.extend(r[1])
            if result:
                return len(word), list(set(result))
            
        except StopException:
            pass
        except:
            error.traceback()

    def call_analysis(self, syncvar):
        try:
            if not self.editor:
                return
            for f in self.editor.input_analysis:
                r = f(self.editor, syncvar)
        except StopException:
            pass
        except:
            error.traceback()

    r_key = re.compile(r'(.*?)%(.*?)%$')
    def install_keylist(self, items, re_flag=False):
        d = {}
        for key, value in items:
            for k, v in KEYS.items():
                key = key.replace(k, v)
            b = self.r_key.search(key)
            if b:
                key = b.groups()[0]
                last_key = convert_key(b.groups()[1])
            else:
                last_key = (0, ord(key[-1]))
#                key = key[:-1]
            if re_flag:
                try:
                    r = re.compile(key)
                except:
                    error.info("key=%s, value=%s" % (key,value))
                    error.traceback()
                    continue
            else:
                r = key
            if d.has_key(last_key):
                d[last_key].append((r, self.gettext(value)))
            else:
                d[last_key] =[(r, self.gettext(value))]
        return d

    def getWord(self, key):
        win = self.editor
        end = win.GetCurrentPos()
        if not key:
            return '', end, end
        line = win.LineFromPosition(end)
        linestart = win.PositionFromLine(line)
        start = max(end - len(key), linestart)
        text = win.GetTextRange(start, end)
        return text, start, end

    def gettext(self, text):
        if isinstance(text, (str, unicode)):
            return tuple(filter(None, re.split(r'(\n|\t|!<)', text)))
        else:
            text.sort()
            return text

    def _split(self, text, delimeter):
        return filter(None, re.split(delimeter, text))

    def settext(self, text):
        win = self.editor
        start = win.GetCurrentPos()
        cur_pos = -1
        refline = win.GetCurrentLine()
        for t in text:
            pos = t.encode('utf-8').find('!^')
            if pos > -1:
                t = t.replace('!^', '')
                cur_pos = win.GetCurrentPos() + pos
            if t == '\n':
                if win.pref.autoindent:
                    n = win.GetLineIndentation(refline) / win.GetTabWidth()
                    win.AddText(win.getEOLChar() + win.getIndentChar() * n)
                else:
                    win.AddText(win.getEOLChar())
            elif t == r'!<':
                win.execute_key('Shift+TAB')
            elif t == '\t':
                win.AddText(win.getIndentChar())
            else:
                win.AddText(t)
        end = win.GetCurrentPos()
        if cur_pos > -1:
            win.GotoPos(cur_pos)
        win.EnsureCaretVisible()
        self.call_snippet(win.GetTextRange(start, end), start, end)

    def call_snippet(self, tpl, start, end):
        if self.editor.snippet:
            snippet = self.editor.snippet
        else:
            snippet = self.editor.snippet = SnipMixin.SnipMixin(self.editor)
        snippet.start(tpl, start, end)

    def check_selection(self, win):
        if win.GetSelectedText():
            win.ReplaceSelection('')

    def set_modules_time(self, mod):
        try:
            sfile = mod.__file__
            if os.path.exists(sfile):
                self.acpmodules_time[mod] = os.path.getmtime(sfile)
        except:
            error.traceback()

    def need_reinstall_module(self, mod):
        try:
            mfile = mod.__file__
            mainfile, ext = os.path.splitext(mfile)
            sfile = mainfile + '.py'
            if os.path.exists(sfile) and os.path.getmtime(sfile) > self.acpmodules_time.get(mod, 0):
                return True
            else:
                return False
        except:
            error.traceback()
            return False

from modules.Accelerator import keylist
def convert_key(s):
    f = 0
    key = 0
    for i in [x.upper() for x in s.split('+')]:
        if i == 'CTRL':
            f |= wx.stc.STC_SCMOD_CTRL
        elif i == 'ALT':
            f |= wx.stc.STC_SCMOD_ALT
        elif i == 'SHIFT':
            f |= wx.stc.STC_SCMOD_SHIFT
        elif keylist.has_key(i):
            key = keylist[i]
        elif KEYS.has_key(i):
            key = KEYS[i]
        else:
            key = ord(i)
    return f, key

def _getWord(win, whole=None):
    pos=win.GetCurrentPos()
    if win.getChar(pos-1) == '(':
        pos -= 1
    line = win.GetCurrentLine()
    linePos=win.PositionFromLine(line)
    txt = win.GetLine(line)
    start=win.WordStartPosition(pos,1)
    i = start - 1
    #skip the first '.'
    if win.getChar(pos) == '.':
        return ''
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






