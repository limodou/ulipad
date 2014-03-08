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

import wx
try:
    set
except:
    from sets import Set as set

import os
import glob
from modules import Mixin
from modules.Debug import error
from modules import Globals
from modules import common
from modules import dict4ini

CALLTIP_AUTOCOMPLETE = 2

def mainframe_init(win):
    win.input_assistant = None
Mixin.setPlugin('mainframe', 'init', mainframe_init)

def editor_init(win):
    win.AutoCompSetIgnoreCase(True)
    win.AutoCompStops(' .,;:()[]{}\'"\\<>%^&+-=*/|`')
    win.AutoCompSetAutoHide(True)
    win.AutoCompSetCancelAtStart(False)

#    win.inputassistant_obj = None
    win.replace_strings = None
    win.word_len = 0
    win.custom_assistant = []
    win.function_parameter = []
    win.calltip_stack = {} # collecting nested calltip's text and pos.
    win.syntax_info = None
    win.auto_routin = None
    win.snippet = None
    win.modified_line = None
Mixin.setPlugin('editor', 'init', editor_init)

def _replace_text(win, start, end, text):
    if end == -1:
        end = win.GetCurrentPos()
    win.BeginUndoAction()
    win.SetTargetStart(start)
    win.SetTargetEnd(end)
    win.ReplaceTarget('')
    win.GotoPos(start)
    t = text
    for obj in win.mainframe.input_assistant.get_all_acps():
        if obj.ini.autovalues.has_key(text):
            t = obj.ini.autovalues[text]
            break
    txt = win.mainframe.input_assistant.gettext(t)
    if win.replace_strings:
        r = win.replace_strings
        m = []
        for p in txt:
            for i in range(len(r)):
                p = p.replace('\\' + str(i), r[i])
            m.append(p)
        txt = m
    win.mainframe.input_assistant.settext(txt)
    win.EndUndoAction()

def on_user_list_selction(win, list_type, text):
    t = list_type
    if t == 1:  #1 is used by input assistant
        start, end = win.word_len
        _replace_text(win, start, end, text)
Mixin.setPlugin('editor', 'on_user_list_selction', on_user_list_selction)

def on_auto_completion(win, pos, text):
    start, end = win.word_len
    wx.CallAfter(_replace_text, win, start, end, text)
Mixin.setPlugin('editor', 'on_auto_completion', on_auto_completion)

def get_inputassistant_obj(win):
    if not win.mainframe.input_assistant:
        from InputAssistant import InputAssistant

        win.mainframe.input_assistant = i = InputAssistant()
    else:
        i = win.mainframe.input_assistant
    return i

def after_char(win, event):
    win.mainframe.auto_routin_ac_action.put({'type':'normal', 'win':win,
        'event':event, 'on_char_flag':True})
Mixin.setPlugin('editor', 'after_char', after_char)

def on_key_down(win, event):
    key = event.GetKeyCode()
#    if key == ord(']') and event.ControlDown() and not event.AltDown() and not event.ShiftDown():
    if key == wx.WXK_TAB and not event.ControlDown() and not event.AltDown() and not event.ShiftDown():
        if win.snippet and win.snippet.snip_mode:
            if win.AutoCompActive():
                win.AutoCompCancel()

            win.calltip_stack.clear()
            del win.function_parameter[:]
            win.calltip.cancel()

            win.snippet.nextField(win.GetCurrentPos())
            return True
    if key == ord('Q') and event.AltDown() and not event.ControlDown() and not event.ShiftDown():
        if win.snippet and win.snippet.snip_mode:
            win.snippet.cancel()
            return True

    if key == wx.WXK_BACK and not event.AltDown() and not event.ControlDown() and not event.ShiftDown():
        if win.pref.input_assistant and win.pref.inputass_identifier:
            win.mainframe.auto_routin_ac_action.put({'type':'default', 'win':win, 'event':event})
    return False
Mixin.setPlugin('editor', 'on_key_down', on_key_down)

def on_first_keydown(win, event):
    if win.pref.input_assistant:
        win.mainframe.auto_routin_ac_action.put({'type':'normal', 'win':win,
            'event':event, 'on_char_flag':False})
    return False
Mixin.setPlugin('editor', 'on_first_keydown', on_first_keydown, nice=1)

def pref_init(pref):
    pref.input_assistant = True
    pref.inputass_calltip = True
    pref.inputass_autocomplete = True
    pref.inputass_identifier = True
    pref.inputass_full_identifier = True
    pref.inputass_func_parameter_autocomplete = True
    pref.inputass_typing_rate = 400
Mixin.setPlugin('preference', 'init', pref_init)

def _get(name):
    def _f(name=name):
        return getattr(Globals.pref, name)
    return _f

from modules import meide as ui

mInputAssistant_ia = ui.Check(_get('input_assistant'), tr('Enables input assistant'))
mInputAssistant_s1 = ui.Check(_get('inputass_calltip'), tr("Enables calltips"))
mInputAssistant_s2 = ui.Check(_get('inputass_autocomplete'), tr("Enables autocompletion"))
mInputAssistant_s3 = ui.Check(_get('inputass_identifier'), tr("Enables autoprompt identifiers"))
mInputAssistant_s4 = ui.Check(_get('inputass_full_identifier'), tr("Enables full identifiers search"))
mInputAssistant_s5 = ui.Check(_get('inputass_func_parameter_autocomplete'), tr("Enables function parameter autocomplete"))

def _toggle(event=None):
    ss = [mInputAssistant_s1, mInputAssistant_s2, mInputAssistant_s3, mInputAssistant_s4, mInputAssistant_s5]
    if mInputAssistant_ia.GetValue():
        for s in ss:
            s.get_widget().Enable()
    else:
        for s in ss:
            s.get_widget().Disable()

def aftercreate(dlg):
    _toggle()
Mixin.setPlugin('prefdialog', 'aftercreate', aftercreate)
    
def add_pref(preflist):
    def _get(name):
        def _f(name=name):
            from modules import Globals
            return getattr(Globals.pref, name)
        return _f
    
    mInputAssistant_ia.bind('check', _toggle)
    from modules import meide as ui
    box = ui.HBox()
    box.add(ui.Label(tr("Skip input assistance when typing rate faster than ")))
    box.add(ui.Int(_get('inputass_typing_rate'), size=(40, -1)), name='inputass_typing_rate')
    box.add(ui.Label(tr(" milliseconds")))
    
    preflist.extend([
        (tr('Input Assistant'), 100, mInputAssistant_ia, 'input_assistant', '', None),
        (tr('Input Assistant'), 110, mInputAssistant_s1, 'inputass_calltip', '', None),
        (tr('Input Assistant'), 120, mInputAssistant_s2, 'inputass_autocomplete', '', None),
        (tr('Input Assistant'), 130, mInputAssistant_s3, 'inputass_identifier', '', None),
        (tr('Input Assistant'), 140, mInputAssistant_s4, 'inputass_full_identifier', '', None),
        (tr('Input Assistant'), 150, mInputAssistant_s5, 'inputass_func_parameter_autocomplete', '', None),
        (tr('Input Assistant'), 160, box, '', '', {'span':True}),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def get_acp_files(win):
    i = get_inputassistant_obj(win)
    i.install_acp(win, win.languagename)

    files = []
    objs = i.get_acp(win.languagename)
    if objs:
        files = [obj.filename for obj in objs]

    b = glob.glob(os.path.join(Globals.workpath, '*.acp')) + glob.glob(os.path.join(Globals.confpath, '*.acp'))
    afiles = set(b)
    afiles.difference_update(files)
    afiles = list(afiles)
    afiles.sort()

    sfiles = [obj.filename for obj in win.custom_assistant]

    elements = [
    ('static', 'applied', '\n'.join(files), tr('Default acp files:'), None),
    ('multi', 'custom', sfiles, tr('Available acp files:'), afiles),
    ]
    from modules.EasyGuider import EasyDialog
    easy = EasyDialog.EasyDialog(win, title=tr('Acp Selector'), elements=elements)
    values = None
    if easy.ShowModal() == wx.ID_OK:
        values = easy.GetValue()
        win.custom_assistant = []
        for f in values['custom']:
            win.custom_assistant.append(i.get_assistant(f))
        i.install_acp(win, win.languagename, True)

    easy.Destroy()

def call_lexer(win, oldfilename, filename, language):
    i = get_inputassistant_obj(win)
#    i.install_acp(win, win.languagename)

    files = []
    objs = i.get_acp(win.languagename)
    if objs:
        files = [obj.filename for obj in objs]

    b = glob.glob(os.path.join(Globals.workpath, '*.acp')) + glob.glob(os.path.join(Globals.confpath, '*.acp'))
    afiles = set(b)
    afiles.difference_update(files)
    afiles = list(afiles)
    afiles.sort()

    prjfile = common.getProjectFile(filename)
    ini = dict4ini.DictIni(prjfile)
    ext = os.path.splitext(filename)[1]

    acps = ini.acp[ext]
    if acps:
        if isinstance(acps, str):
            acps = [acps]

        for f in acps:
            for acpf in afiles:
                if os.path.basename(acpf) == f:
                    win.custom_assistant.append(i.get_assistant(acpf))
                    
    i.install_acp(win, win.languagename)
Mixin.setPlugin('editor', 'call_lexer', call_lexer)

def add_mainframe_menu(menulist):
    menulist.extend([
        ('IDM_DOCUMENT', #parent menu id
        [
            (127, 'IDM_DOCUMENT_APPLYACP', tr('Apply Autocompleted Files'), wx.ITEM_NORMAL, 'OnDocumentApplyAcp', tr('Apply auto-complete files to current document.')),
        ]),
        (None, 
        [
            (800, 'IDM_CONFIG', tr('Config'), wx.ITEM_NORMAL, '', ''),
        ]),
        ('IDM_CONFIG',
        [
            (100, 'IDM_CONFIG_INPUTASSISTANT', tr('Input Assistant Enabled')+'\tAlt+A', wx.ITEM_CHECK, 'OnConfigInputAssistant', tr('Enable input assistant.')),
        ]),
        
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def OnDocumentApplyAcp(win, event):
    if hasattr(win, 'document') and win.document.edittype == 'edit':
       get_acp_files(win.document)
Mixin.setMixin('mainframe', 'OnDocumentApplyAcp', OnDocumentApplyAcp)

def add_editor_menu(popmenulist):
    popmenulist.extend([
        (None,
        [
            (270, 'IDPM_APPLYACP', tr('Apply Autocompleted Files'), wx.ITEM_NORMAL, 'OnApplyAcp', tr('Apply autocompleted files to current document.')),
        ]),
    ])
Mixin.setPlugin('editor', 'add_menu', add_editor_menu)

def OnApplyAcp(win, event):
    win.mainframe.OnDocumentApplyAcp(event)
Mixin.setMixin('editor', 'OnApplyAcp', OnApplyAcp)

###########################################################################
def on_kill_focus(win, event):
    if win.AutoCompActive():
        win.AutoCompCancel()
    if win.calltip and win.calltip.active:
        if hasattr(event,'FNB'):
            win.calltip.cancel()
            return
        if not win.have_focus:
            win.have_focus = True
        else:
            win.calltip.cancel()
Mixin.setPlugin('editor', 'on_kill_focus', on_kill_focus)

def on_key_down(win, event):
    key = event.GetKeyCode()
    control = event.ControlDown()
    #shift=event.ShiftDown()
    alt=event.AltDown()
    if key == wx.WXK_RETURN and not control and not alt:
        if not win.AutoCompActive():
            if win.calltip.active:
                pos = win.GetCurrentPos()
                # move calltip windown to next line
                # must be pos+2 not pos+1,the reason I don't konw.
                win.calltip.move(pos + 2)
##                win.calltip.cancel()
        else:
            event.Skip()
            return True
    elif key == wx.WXK_ESCAPE:
        # clear nested calltip state if something is wrong.
        win.calltip_stack.clear()
        del win.function_parameter[:]
        win.calltip.cancel()
##        statusbar = Globals.mainframe.statusbar
##        text = "press escape key to set calltip  state to normal, if you find the calltip state is wrong ,doing this can clear wrong state."
##        statusbar.show_panel('tips: '+text, color='#AAFFAA', font=wx.Font(10, wx.TELETYPE, wx.NORMAL, wx.BOLD, True))

Mixin.setPlugin('editor', 'on_key_down', on_key_down, Mixin.HIGH, 1)

def leaveopenfile(win, filename):
    if win.pref.input_assistant:
        i = get_inputassistant_obj(win)
        i.install_acp(win, win.languagename)
        win.mainframe.auto_routin_analysis.clear()
        win.mainframe.auto_routin_analysis.put(win)
Mixin.setPlugin('editor', 'leaveopenfile', leaveopenfile)

def beforeclosefile(editctrl, doc):
    Globals.mainframe.auto_routin_analysis.clear()
Mixin.setPlugin('editctrl', 'beforeclosefile', beforeclosefile)

def on_modified(win):
    win.mainframe.auto_routin_analysis.put(win)
Mixin.setPlugin('editor', 'on_modified', on_modified)

from modules import AsyncAction
def on_close(win, event):
    "when app close, keep thread from running do_action"
    AsyncAction.AsyncAction.STOP = True
Mixin.setPlugin('mainframe','on_close', on_close ,Mixin.HIGH, 1)

def on_close(win, event):
    win.auto_routin_analysis.join()
    win.auto_routin_ac_action.join()
Mixin.setPlugin('mainframe','on_close', on_close)

class InputAssistantAction(AsyncAction.AsyncAction):
    def do_action(self, obj):
        if not self.empty:
            return

        pref = Globals.pref

        action = obj['type']
        win = obj['win']
#        try:
#            win.lock.acquire()
        try:
            if not win: return
            i = get_inputassistant_obj(win)
            if action == 'default':
                i.run_default(win, self)
            else:
                event, on_char_flag = obj['event'], obj['on_char_flag']
                i.run(win, event, on_char_flag, self)
            return True
        except:
            Globals.mainframe.input_assistant = None
            error.traceback()
#        finally:
#            win.lock.release()

    def get_timestep(self):
        return float(Globals.pref.inputass_typing_rate)/1000

class Analysis(AsyncAction.AsyncAction):
    def do_action(self, obj):
        win = Globals.mainframe
        if not self.empty:
            return
        try:
            if not obj: return
            i = get_inputassistant_obj(obj)
            i.call_analysis(self)
            return True
        except:
            win.input_assistant = None
            error.traceback()

def main_init(win):
    win.auto_routin_analysis = Analysis(.2)
    win.auto_routin_analysis.start()
    win.auto_routin_ac_action = InputAssistantAction(float(win.pref.inputass_typing_rate)/1000)
    win.auto_routin_ac_action.start()
Mixin.setPlugin('mainframe', 'init', main_init)

def OnConfigInputAssistant(win, event):
    Globals.pref.input_assistant = not Globals.pref.input_assistant
    Globals.pref.save()
Mixin.setMixin('mainframe', 'OnConfigInputAssistant', OnConfigInputAssistant)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_CONFIG_INPUTASSISTANT, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDM_CONFIG_INPUTASSISTANT:
        event.Check(Globals.pref.input_assistant)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)
