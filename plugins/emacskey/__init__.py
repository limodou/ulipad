#   Programmer: wlvong


import wx
from modules import Mixin

inPartialShortcut = False
currentPartialMatch = ''
mark_positions = []

def keyDown(editor, event):
    global inPartialShortcut
    global currentPartialMatch

    scs = assembleShortcutString(event)
    if scs in shortcuts:
        if shortcuts[scs][0] == True:
            editor.CmdKeyExecute(shortcuts[scs][1])
            return True
        else:
            shortcuts[scs][1](editor, event)
            return True
    if matchPartial(scs, shortcuts):
        inPartialShortcut = True
        currentPartialMatch = scs
        return True

    # Allow for '<'
    if scs == 'shift+,':
        return False

    if len(scs.split(',')) > 1 and scs != ',': # multi-key shortcut reach here
                                # means invalid key
        return True

    return False
Mixin.setPlugin('editor', 'on_first_keydown', keyDown, nice=0)


def matchPartial(scs, shortcuts):
    for key in shortcuts.keys():
        if scs == key.split(',')[0]:
            return True
    return False


def assembleShortcutString(event):
    global inPartialShortcut
    global currentPartialMatch

    key = event.GetKeyCode()
    sc = ''
    #print event.GetModifiers()
    if event.ControlDown():
        sc = 'ctrl'

    if event.AltDown():
        if len(sc) > 0:
            sc = sc + '+'
        sc = sc + 'alt'

    if event.ShiftDown():
        if len(sc) > 0:
            sc = sc + '+'
        sc = sc + 'shift'

    if len(sc) > 0:
        sc = sc + '+'

    if ord(' ') <= key < 127:
        sc = sc + chr(key).lower()

        if inPartialShortcut is True and len(currentPartialMatch) > 0:
            sc = currentPartialMatch + ',' + sc
            inPartialShortcut = False
            currentPartialMatch = ''
    return sc

def getSelection(editor):
    '''Return the selection.

    If the user has highlighted a selection then use that.  Otherwise use the
    mark.

    If there are no marks, and there is no selection, then None, None is
    returned.  Otherwise either the selection end points or the mark, current
    position are returned.

    # No selection and no marks.
    getSelection(editor) -> (None, None)

    # Either selection or mark, current pos
    getSelection(editor) -> (1, 3)
    '''
    sel = editor.GetSelection()
    if sel[0] != sel[1]:
        start, stop = sel
    else:
        # No marks, nothing to cut.
        if len(mark_positions) == 0:
            return None, None
        start = mark_positions.pop()
        stop = editor.GetCurrentPos()

    return start, stop

def onCut(editor, event):
    start, stop = getSelection(editor)
    if start is None:
        return
    editor.SetSelection(start, stop)
    editor.CmdKeyExecute(wx.stc.STC_CMD_CUT)

def onCopy(editor, event):
    start, stop = getSelection(editor)
    if start is None:
        return
    editor.SetSelection(start, stop)
    editor.CmdKeyExecute(wx.stc.STC_CMD_COPY)
    editor.SetSelection(editor.GetCurrentPos(), editor.GetCurrentPos())

def setMark(editor, event):
    mark_positions.append(editor.GetCurrentPos())

def pressDelete(editor, event):
    event.m_keyCode = wx.WXK_DELETE
    event.m_controlDown = False
    editor.GetEventHandler().AddPendingEvent(event)

def closeCurrentDoc(editor, event):
    editor.SetEvtHandlerEnabled(False)
    editor.mainframe.CloseFile(editor)
    editor.SetEvtHandlerEnabled(True)

def cancelAllCommand(editor, event):
    global inPartialShortcut
    global partialMatch
    inPartialShortcut = False
    partialMatch = ''

# Maps keyboard shortcuts to "handlers".  Keep this at the bottom of the module.
# The tuple is a (bool, obj) tuple.  If bool is True, then the stc command will
# be sent to the control.  If false, then obj should be a callable that handles
# the event.  The callable accepts two parameters - editor, event.
shortcuts = {
    'ctrl+a':(True, wx.stc.STC_CMD_VCHOME),
    'ctrl+b':(True, wx.stc.STC_CMD_CHARLEFT),
    'ctrl+d':(False, pressDelete),
    'ctrl+g':(False, cancelAllCommand),
    'ctrl+h':(True, wx.stc.STC_CMD_DELETEBACK),
    'ctrl+u':(True, wx.stc.STC_CMD_DELLINELEFT),
    'ctrl+f':(True, wx.stc.STC_CMD_CHARRIGHT),
    'ctrl+e':(True, wx.stc.STC_CMD_LINEEND),
    'ctrl+p':(True, wx.stc.STC_CMD_LINEUP),
    'ctrl+n':(True, wx.stc.STC_CMD_LINEDOWN),
    'ctrl+v':(True, wx.stc.STC_CMD_PAGEDOWN),
    'ctrl+w':(False, onCut),
    'ctrl+y':(True, wx.stc.STC_CMD_PASTE),
    'alt+b':(True, wx.stc.STC_CMD_WORDLEFT),
    'alt+f':(True, wx.stc.STC_CMD_WORDRIGHT),
    'alt+d':(True, wx.stc.STC_CMD_DELWORDRIGHT),
    'alt+v':(True, wx.stc.STC_CMD_PAGEUP),
    'alt+w':(False, onCopy),
    'ctrl+x,k':(False, closeCurrentDoc),
    'ctrl+ ':(False, setMark),
    'ctrl+/':(True, wx.stc.STC_CMD_UNDO)
}
