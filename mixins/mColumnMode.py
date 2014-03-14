import wx
from modules import Mixin
from modules.Debug import error

def editor_init(win):
    win.MarkerDefine(1, wx.stc.STC_MARK_VLINE, "black", "black")
    win.marker_columnmode = 1
    win.columnmode_lines = None
    win.column_mode = False
Mixin.setPlugin('editor', 'init', editor_init)

def add_editor_menu(popmenulist):
    popmenulist.extend([ (None, #parent menu id
        [
            (245, 'IDPM_COLUMN_MODE', tr('Column Mode') +'\tAlt+C', wx.ITEM_CHECK, 'OnColumnMode', tr('Marks Column Mode region.')),
        ]),
    ])
Mixin.setPlugin('editor', 'add_menu', add_editor_menu)

def OnColumnMode(win, event):
    if win.column_mode:
        win.ClearColumnModeRegion()
        win.column_mode = False
    else:
        win.column_mode = True
        auto_column_mode(win)
Mixin.setMixin('editor', 'OnColumnMode', OnColumnMode)

def define_column_mode_region(win, startline, endline):
    win.columnmode_lines = startline, endline
    i = startline
    while i <= endline:
        win.MarkerAdd(i, win.marker_columnmode)
        i += 1
    pos = win.GetCurrentPos()
    win.SetSelection(pos, pos)

def selectmultiline(win):
    start, end = win.GetSelection()
    startline = win.LineFromPosition(start)
    endline = win.LineFromPosition(end)
    return start != end

def auto_column_mode(win):
    if win.GetSelectedText() and selectmultiline(win):
        start, end = win.GetSelection()
        startline = win.LineFromPosition(start)
        endline = win.LineFromPosition(end)
        curline = win.GetCurrentLine()
        
        col = win.GetColumn(win.GetCurrentPos())
        if endline == curline and col == 0:
            endline -= 1
            curline = endline
            
        if win.columnmode_lines: #judge if need to expand
            b, e = win.columnmode_lines
            #expand upward or expand downward
            if (curline < b and endline == b) or (curline > e and startline == e):
                startline = min(startline, b)
                endline = max(endline, e)
        win.ClearColumnModeRegion()
        define_column_mode_region(win, startline, endline)

def ClearColumnModeRegion(win, event=None):
    win.MarkerDeleteAll(win.marker_columnmode)
Mixin.setMixin('editor', 'ClearColumnModeRegion', ClearColumnModeRegion)

def editor_init(win):
    wx.EVT_UPDATE_UI(win, win.IDPM_COLUMN_MODE, win.OnUpdateUI)
Mixin.setPlugin('editor', 'init', editor_init)

def editor_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDPM_COLUMN_MODE:
        event.Check(win.column_mode)
Mixin.setPlugin('editor', 'on_update_ui', editor_updateui)

def InColumnModeRegion(win, line):
    if win.columnmode_lines and (win.columnmode_lines[0] <= line <= win.columnmode_lines[1]):
        return True
    else:
        return False
Mixin.setMixin('editor', 'InColumnModeRegion', InColumnModeRegion)

def on_key_up(win, event):
    key = event.GetKeyCode()
    shift = event.ShiftDown()
    if win.column_mode and key in (wx.WXK_DOWN, wx.WXK_UP) and shift:
        auto_column_mode(win)
    return False
Mixin.setPlugin('editor', 'on_key_up', on_key_up)

def on_mouse_up(win, event):
    if win.column_mode:
        auto_column_mode(win)
    return False
Mixin.setPlugin('editor', 'on_mouse_up', on_mouse_up)

def ColumnEditAction(win, event, col, begin, end, in_key_down=False):
    """if dealed then return True"""
    char = event.GetKeyCode()
    alt = event.AltDown()
    shift = event.ShiftDown()
    ctrl = event.ControlDown()
    line = win.GetCurrentLine()
    f = None
    if in_key_down:
        if not alt and not shift and not ctrl:
            if char == wx.WXK_RETURN:
                return True
            elif char == wx.WXK_DELETE:
                def func(win, line):
                    if win.GetCurrentPos() < win.GetLineEndPosition(line) and win.GetLineEndPosition(line) > 0:
                        win.execute_key('DEL')
                f = func
            elif char == wx.WXK_TAB:
                def func(win, line):
                    win.execute_key('TAB')
                f = func
            elif char == wx.WXK_BACK:
                def func(win, line):
                    col = win.GetCurrentPos() - win.PositionFromLine(line)
                    if col == 0:
                        if win.GetLineEndPosition(line) > 0:
                            win.execute_key('DEL')
                    else:
                        win.execute_key(wx.stc.STC_CMD_DELETEBACK)
                f = func
            else:
                return False
        else:
            return False
    else:
        if not ((31 <char < 127) or char > wx.WXK_PAGEDOWN):
            return False
    i = 0
    win.BeginUndoAction()
    try:
        lastline = win.GetCurrentLine()
        while begin+i <= end:
            delta = win.PositionFromLine(begin+i) + col - win.GetLineEndPosition(begin+i)
            if delta > 0:
                win.GotoPos(win.GetLineEndPosition(begin+i))
                win.AddText(' '*delta)
            else:
                win.GotoPos(win.PositionFromLine(begin+i) + col)
            if f:
                f(win, begin+i)
            else:
                if 31 <char < 127:
                    win.AddText(chr(char))
                else:
                    try:
                        win.AddText(unichr(char))
                    except:
                        error.error("Conver %d to unichar failed" % char)
                        error.traceback()
                        break
            if begin + i == lastline:
                lastpos = win.GetCurrentPos()
            i += 1
        win.GotoPos(lastpos)
    finally:
        win.EndUndoAction()
    return True

def on_key_down(win, event):
    key = event.GetKeyCode()
    ctrl = event.ControlDown()
    alt = event.AltDown()
    shift = event.ShiftDown()
    lastpos = win.GetCurrentPos()
    if win.column_mode and win.InColumnModeRegion(win.GetCurrentLine()):
        col = lastpos - win.PositionFromLine(win.GetCurrentLine())
        return ColumnEditAction(win, event, col, win.columnmode_lines[0], win.columnmode_lines[1], True)
    elif ctrl and key == wx.WXK_DELETE:
        if win.GetSelectedText():
            win.ReplaceSelection('')
        pos = win.GetCurrentPos()
        #then delete all the leading blanks of the next line and join the next line
        flag = False
        while chr(win.GetCharAt(pos)) in ['\r', '\n', ' ', '\t']:
            win.execute_key('DEL')
            flag = True
        if flag:
            return True
        else:
            return False
    elif shift and key == wx.WXK_RETURN:
        win.execute_key('END')
        return False
    else:
        return False
Mixin.setPlugin('editor', 'on_key_down', on_key_down, nice=0)

def on_char(win, event):
    key = event.GetKeyCode()
    ctrl = event.ControlDown()
    alt = event.AltDown()
    shift = event.ShiftDown()
    lastpos = win.GetCurrentPos()
    if win.column_mode and win.InColumnModeRegion(win.GetCurrentLine()):
        col = win.GetCurrentPos() - win.PositionFromLine(win.GetCurrentLine())
        return ColumnEditAction(win, event, col, win.columnmode_lines[0], win.columnmode_lines[1])
    else:
        return False
Mixin.setPlugin('editor', 'on_char', on_char)

def add_mainframe_menu(menulist):
    menulist.extend([
        ('IDM_EDIT', #parent menu id
        [
            (275, 'IDM_EDIT_COLUMN_MODE', tr('Column Mode') +'\tE=Alt+C', wx.ITEM_CHECK, 'OnEditColumnMode', tr('Marks Column Mode region.')),

        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_COLUMN_MODE, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDM_EDIT_COLUMN_MODE:
        if hasattr(win, 'document') and win.document:
            event.Enable(True)
            event.Check(win.document.column_mode)
        else:
            event.Enable(False)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def OnEditColumnMode(win, event):
    try:
        win.document.OnColumnMode(event)
    except:
        error.traceback()
Mixin.setMixin('mainframe', 'OnEditColumnMode', OnEditColumnMode)
