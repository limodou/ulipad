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


#-----------------------  mMainFrame.py ------------------

from modules import Mixin
from modules import Globals

def getmainframe(app, filenames):
    from MainFrame import MainFrame
    Globals.starting = True

    app.mainframe = frame = MainFrame(app, filenames)

    frame.workpath = app.workpath
    frame.userpath = app.userpath
    frame.afterinit()
    frame.editctrl.openPage()
    Globals.starting = False
    return frame
Mixin.setPlugin('app', 'getmainframe', getmainframe)



#-----------------------  mPreference.py ------------------

import wx
from modules import Mixin

def add_mainframe_menu(menulist):
    menulist.extend([
        ('IDM_EDIT',
        [
            (300, '-', '', wx.ITEM_SEPARATOR, '', ''),
            (310, 'wx.ID_PREFERENCES', tr('Preferences...'), wx.ITEM_NORMAL, 'OnOptionPreference', tr('Opens the Preferences window.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def beforegui(win):
    import Preference
    from modules import Globals

    win.pref = Preference.Preference()
    win.pref.load()
    win.pref.printValues()
    Globals.pref = win.pref
Mixin.setPlugin('app', 'beforegui', beforegui, Mixin.HIGH)

def OnOptionPreference(win, event):
    import PrefDialog

    dlg = PrefDialog.PrefDialog(win)
    dlg.ShowModal()
Mixin.setMixin('mainframe', 'OnOptionPreference', OnOptionPreference)

def add_pref_page(pages_order):
    pages_order.update({
        tr('General'):100,
        tr('Document'):110,
    }
    )
Mixin.setPlugin('preference', 'add_pref_page', add_pref_page)



#-----------------------  mMainSubFrame.py ------------------

from modules import Mixin
import MyPanel

class MainSubFrame(MyPanel.SashPanel, Mixin.Mixin):

    __mixinname__ = 'mainsubframe'

    def __init__(self, parent, mainframe):
        self.initmixin()
        self.parent = parent
        self.mainframe = mainframe
        self.mainframe.panel = self

        MyPanel.SashPanel.__init__(self, parent)

        self.callplugin('init', self)

def init(win):
    return MainSubFrame(win, win)
Mixin.setPlugin('mainframe', 'init', init)



#-----------------------  mEditorCtrl.py ------------------

import wx
import os.path
from modules.wxctrl import FlatNotebook as FNB
from modules import Globals
from modules import Mixin

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_FILE',
        [
            (100, 'IDM_FILE_NEW', tr('New') + '\tCtrl+N', wx.ITEM_NORMAL, 'OnFileNew', tr('Creates a new document.')),
            (105, 'IDM_FILE_NEWMORE', tr('New') + '...', wx.ITEM_NORMAL, None, None),
            (110, 'IDM_FILE_OPEN', tr('Open...') + '\tCtrl+O', wx.ITEM_NORMAL, 'OnFileOpen', tr('Opens an existing document.')),
            (120, 'IDM_FILE_REOPEN', tr('Reopen') + '\tE=Ctrl+Shift+O', wx.ITEM_NORMAL, 'OnFileReOpen', tr('Reopens the current document.')),
            (140, 'IDM_FILE_CLOSE', tr('Close') + '\tCtrl+F4', wx.ITEM_NORMAL, 'OnFileClose', tr('Closes an opened document.')),
            (150, 'IDM_FILE_CLOSE_ALL', tr('Close All'), wx.ITEM_NORMAL, 'OnFileCloseAll', tr('Closes all document windows.')),
            (160, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (170, 'IDM_FILE_SAVE', tr('Save') + '\tE=Ctrl+S', wx.ITEM_NORMAL, 'OnFileSave', tr('Saves an opened document using the same filename.')),
            (180, 'IDM_FILE_SAVEAS', tr('Save As...'), wx.ITEM_NORMAL, 'OnFileSaveAs', tr('Saves an opened document to a specified filename.')),
            (190, 'IDM_FILE_SAVE_ALL', tr('Save All'), wx.ITEM_NORMAL, 'OnFileSaveAll', tr('Saves all documents.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_editctrl_menu(popmenulist):
    popmenulist.extend([ (None,
        [
            (100, 'IDPM_CLOSE', tr('Close') + '\tCtrl+F4', wx.ITEM_NORMAL, 'OnPopUpMenu', tr('Closes an opened document.')),
            (110, 'IDPM_CLOSE_ALL', tr('Close All'), wx.ITEM_NORMAL, 'OnPopUpMenu', tr('Closes all document windows.')),
            (120, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (130, 'IDPM_SAVE', tr('Save') + '\tCtrl+S', wx.ITEM_NORMAL, 'OnPopUpMenu', tr('Saves an opened document using the same filename.')),
            (140, 'IDPM_SAVEAS', tr('Save As...'), wx.ITEM_NORMAL, 'OnPopUpMenu', tr('Saves an opened document to a specified file name.')),
            (150, 'IDPM_FILE_SAVE_ALL', tr('Save All'), wx.ITEM_NORMAL, 'OnPopUpMenu', tr('Saves all documents.')),
            (155, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (156, 'IDPM_FILE_COPY_FILENAME', tr('Copy Filename To Clipboard'), wx.ITEM_NORMAL, 'OnCopyFilenameToClipboard', tr('Copies the filename of the current document to the clipboard.')),
            (160, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (170, 'IDPM_OPEN_CMD_WINDOW', tr('Open Command Window Here'), wx.ITEM_NORMAL, 'OnOpenCmdWindow', ''),
            (180, 'IDPM_OPEN_CMD_EXPLORER', tr('Open Explorer Window Here'), wx.ITEM_NORMAL, 'OnOpenCmdExplorerWindow', ''),
        ]),
    ])
Mixin.setPlugin('editctrl', 'add_menu', add_editctrl_menu)

def add_mainframe_menu_image_list(imagelist):
    imagelist.update({
        'IDM_FILE_NEW':'images/new.gif',
        'IDM_FILE_OPEN':'images/open.gif',
        'IDM_FILE_CLOSE':'images/close.gif',
        'IDM_FILE_SAVE':'images/save.gif',
        'IDM_FILE_SAVEALL':'images/saveall.gif',
    })
Mixin.setPlugin('mainframe', 'add_menu_image_list', add_mainframe_menu_image_list)

def add_editctrl_menu_image_list(imagelist):
    imagelist = {
        'IDPM_CLOSE':'images/close.gif',
        'IDPM_SAVE':'images/save.gif',
        'IDPM_FILE_SAVEALL':'images/saveall.gif',
    }
Mixin.setPlugin('editctrl', 'add_menu_image_list', add_editctrl_menu_image_list)

def neweditctrl(win):
    from EditorFactory import EditorFactory

    win.notebook = EditorFactory(win, Globals.mainframe)
    return win.notebook
Mixin.setPlugin('documentarea', 'init', neweditctrl)

def on_close(win, event):
    if event.CanVeto():
        for document in win.editctrl.getDocuments():
            r = win.CloseFile(document, True)
            if r == wx.ID_CANCEL:
                return True
        if win.execplugin('closewindow', win) == wx.ID_CANCEL:
            return True
Mixin.setPlugin('mainframe', 'on_close', on_close)

def OnFileNew(win, event):
    win.editctrl.new()
Mixin.setMixin('mainframe', 'OnFileNew', OnFileNew)

def OnFileOpen(win, event):
    dlg = wx.FileDialog(win, tr("File List"), win.pref.last_dir, "", '|'.join(win.filewildchar), wx.OPEN|wx.MULTIPLE)
    dlg.SetFilterIndex(getFilterIndex(win))
    if dlg.ShowModal() == wx.ID_OK:
        encoding = win.execplugin('getencoding', win, win)
        for filename in dlg.GetPaths():
            win.editctrl.new(filename, encoding)
        dlg.Destroy()
Mixin.setMixin('mainframe', 'OnFileOpen', OnFileOpen)

def getFilterIndex(win):
    if hasattr(win, 'document') and win.document:
        doc = win.document
        if doc.languagename:
            w = None
            for wildchar, lang in win.filenewtypes:
                if lang == doc.languagename:
                    w = wildchar
                    break
            if w:
                for i, v in enumerate(win.filewildchar):
                    s = v.split('|')[0]
                    if s.startswith(w):
                        return i

    if len(win.pref.recent_files) > 0:
        filename = win.pref.recent_files[0]
        ext = os.path.splitext(filename)[1]
        for i, v in enumerate(win.filewildchar):
            s = v.split('|')[1]
            for wildchar in s.split(';'):
                if wildchar.endswith(ext):
                    return i
            else:
                continue
    return 0
Mixin.setMixin('mainframe', 'getFilterIndex', getFilterIndex)

def OnFileReOpen(win, event):
    if win.document.isModified():
        document = findDocument(win.document)
        dlg = wx.MessageDialog(win, tr("The document has been modified.\nDo you really want to reopen it and discard the modification?"), tr("Reopening Confirmation"), wx.YES_NO|wx.ICON_QUESTION)
        answer = dlg.ShowModal()
        dlg.Destroy()
        if answer != wx.ID_YES:
            return
        state = document.save_state()
        document.openfile(document.filename)
        document.editctrl.switch(document)
        document.restore_state(state)
Mixin.setMixin('mainframe', 'OnFileReOpen', OnFileReOpen)

def OnFileClose(win, event):
    document = findDocument(win.document)
    win.CloseFile(document)
    if len(win.editctrl.getDocuments()) == 0:
        win.editctrl.new()
Mixin.setMixin('mainframe', 'OnFileClose', OnFileClose)

def OnFileCloseAll(win, event):
    i = len(win.editctrl.getDocuments()) - 1
    while i > -1:
        document = win.editctrl.getDoc(i)
        if not document.opened:
            win.editctrl.skip_closing = True
            win.editctrl.skip_page_change = True
            win.editctrl.DeletePage(i)
        i -= 1

    k = len(win.editctrl.getDocuments())
    for i in range(k):
        document = win.editctrl.getDoc(0)
        r = win.CloseFile(document)
        if r == wx.ID_CANCEL:
            break
    if win.editctrl.GetPageCount() == 0:
        win.editctrl.new()
Mixin.setMixin('mainframe', 'OnFileCloseAll', OnFileCloseAll)

def CloseFile(win, document, checkonly = False):
    answer = wx.ID_YES
    if document.isModified():
        d = wx.MessageDialog(win, tr("Would you like to save %s?") % document.getFilename(),
            tr("Saving Confirmation"), wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
        answer = d.ShowModal()
        d.Destroy()
        if answer == wx.ID_YES:
            win.SaveFile(document)
        elif answer == wx.ID_CANCEL:
            return answer

    if checkonly == False:
        win.editctrl.lastdocument = None
        win.callplugin('closefile', win, document, document.filename)
        win.editctrl.closefile(document)
    return answer
Mixin.setMixin('mainframe', 'CloseFile', CloseFile)

def OnFileSave(win, event):
    document = findDocument(win.document)
    r = win.SaveFile(document)
    #if saving file failed, then invoke SaveAs
    if not r:
        win.SaveFile(document, True)
    document.SetFocus()
Mixin.setMixin('mainframe', 'OnFileSave', OnFileSave)

def OnFileSaveAll(win, event):
    for ctrl in win.editctrl.getDocuments():
        if ctrl.opened:
            r = win.SaveFile(ctrl)
Mixin.setMixin('mainframe', 'OnFileSaveAll', OnFileSaveAll)

def OnFileSaveAs(win, event):
    win.SaveFile(win.document, True)
Mixin.setMixin('mainframe', 'OnFileSaveAs', OnFileSaveAs)

def SaveFile(win, ctrl, issaveas=False):
    encoding = None
    if not ctrl.cansavefile():
        return True

    if issaveas or len(ctrl.filename)<=0:
        encoding = win.execplugin('getencoding', win, win)
        filename = get_suffix_filename(ctrl, ctrl.getFilename())
        dlg = wx.FileDialog(win, tr("Save Document As..."), win.pref.last_dir, filename, '|'.join(win.filewildchar), wx.SAVE|wx.OVERWRITE_PROMPT)
        dlg.SetFilterIndex(getFilterIndex(win))
        if (dlg.ShowModal() == wx.ID_OK):
            filename = dlg.GetPath()
            dlg.Destroy()

            #check if the filename has been opened, if opened then fail
            for document in win.editctrl.getDocuments():
                if (not ctrl is document ) and (filename == document.filename):
                    wx.MessageDialog(win, tr("The document %s is already opened.\nPlease choose a different name for the document.") % document.getFilename(),
                        tr("Error"), wx.OK|wx.ICON_EXCLAMATION).ShowModal()
                    return False
        else:
            return True
    else:
        filename = ctrl.filename

    return win.editctrl.savefile(ctrl, filename, encoding)
Mixin.setMixin('mainframe', 'SaveFile', SaveFile)

def get_suffix_filename(editor, filename):
    fname, ext = os.path.splitext(filename)
    if not ext:
        if hasattr(editor, 'lexer'):
            wildchar = editor.lexer.getFilewildchar()
            pos = wildchar.find('|')
            if pos > -1:
                suffix = wildchar[pos+1:].split(';', 1)[0]
                suffix = suffix.replace('*', '')
                if suffix:
                    if not suffix.startswith('.'):
                        suffix = '.' + suffix
                    return fname + suffix
    return filename

def pref_init(pref):
    pref.last_dir = ''
    pref.notebook_direction = 0
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('Document'), 170, 'choice', 'notebook_direction', tr('Document tabs placement:'), [tr('Top'), tr('Bottom')])
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def savepreference(mainframe, pref):
    style = mainframe.editctrl.GetWindowStyleFlag()
    if pref.notebook_direction:
        style |= FNB.FNB_BOTTOM
    else:
        if style & FNB.FNB_BOTTOM:
            style ^= FNB.FNB_BOTTOM

    mainframe.editctrl.SetWindowStyleFlag(style)
    mainframe.editctrl.Refresh()
Mixin.setPlugin('prefdialog', 'savepreference', savepreference)

def findDocument(document):
    if hasattr(document, 'multiview') and document.multiview and hasattr(document, 'document'):
        return document.document
    else:
        return document

def OnOpenCmdWindow(win, event=None):
    filename = win.getCurDoc().getFilename()
    if not filename:
        filename = Globals.userpath
    else:
        filename = os.path.dirname(filename)
    if wx.Platform == '__WXMSW__':
        os.spawnl(os.P_NOWAIT, win.pref.command_line,r" /k %s && cd %s" % (os.path.split(filename)[0][:2], filename))
    else:
        cmdline = win.pref.command_line.replace('{path}', filename)
        wx.Execute(cmdline)
Mixin.setMixin('editctrl', 'OnOpenCmdWindow', OnOpenCmdWindow)

def OnOpenCmdExplorerWindow(win, event=None):
    filename = win.getCurDoc().getFilename()
    if not filename:
        filename = Globals.userpath
    else:
        filename = os.path.dirname(filename)
    wx.Execute(r"explorer.exe /e, %s" % filename)
Mixin.setMixin('editctrl', 'OnOpenCmdExplorerWindow', OnOpenCmdExplorerWindow)

def OnCopyFilenameToClipboard(win, event):
    filename = win.getCurDoc().getFilename()
    do = wx.TextDataObject()
    do.SetText(filename)
    if wx.TheClipboard.Open():
        wx.TheClipboard.SetData(do)
        wx.TheClipboard.Close()
Mixin.setMixin('editctrl', 'OnCopyFilenameToClipboard', OnCopyFilenameToClipboard)



#-----------------------  mEditor.py ------------------

from modules import Mixin
import wx
from modules import Globals

def add_panel_list(panellist):
    from TextPanel import TextPanel
    panellist['texteditor'] = TextPanel
Mixin.setPlugin('editctrl', 'add_panel_list', add_panel_list)

def on_first_keydown(win, event):
    key = event.GetKeyCode()
    alt = event.AltDown()
    shift = event.ShiftDown()
    ctrl = event.ControlDown()
    if ctrl and key == wx.WXK_TAB:
        if not shift:
            win.editctrl.Navigation(True)
            wx.CallAfter(Globals.mainframe.editctrl.getCurDoc().SetFocus)
        else:
            win.editctrl.Navigation(False)
            wx.CallAfter(Globals.mainframe.editctrl.getCurDoc().SetFocus)
Mixin.setPlugin('editor', 'on_first_keydown', on_first_keydown)

def on_modified_routin(win):
    win.mainframe.auto_onmodified.put(win)
Mixin.setPlugin('editor', 'on_modified_routin', on_modified_routin)

def on_modified(win):
    if win.edittype == 'edit':
        if not win.isModified():
            win.SetSavePoint()
        if win.editctrl:
            wx.CallAfter(win.editctrl.showTitle, win)
            wx.CallAfter(win.editctrl.showPageTitle, win)
Mixin.setPlugin('editor', 'on_modified', on_modified)

from modules import Globals
from modules.Debug import error
from modules import AsyncAction
class OnModified(AsyncAction.AsyncAction):
    def do_action(self, obj):
        win = Globals.mainframe
        if not self.empty:
            return
        try:
            if not obj: return
            wx.CallAfter(obj.callplugin, 'on_modified', obj)
            return True
        except:
            error.traceback()

def main_init(win):
    win.auto_onmodified = OnModified(.5)
    win.auto_onmodified.start()
Mixin.setPlugin('mainframe', 'init', main_init)

def on_close(win, event):
    win.auto_onmodified.join()
Mixin.setPlugin('mainframe','on_close', on_close)



#-----------------------  mComEdit.py ------------------

__doc__ = 'Common edit menu. Redo, Undo, Cut, Paste, Copy'

import wx
from modules import Mixin

def add_editor_menu(popmenulist):
    popmenulist.extend([ (None, #parent menu id
        [
            (100, 'IDPM_UNDO', tr('Undo') + '\tCtrl+Z', wx.ITEM_NORMAL, 'OnPopupEdit', tr('Reverses previous editing operation.')),
            (110, 'IDPM_REDO', tr('Redo') + '\tCtrl+Y', wx.ITEM_NORMAL, 'OnPopupEdit', tr('Reverses previous undo operation.')),
            (120, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (130, 'IDPM_CUT', tr('Cut') + '\tCtrl+X', wx.ITEM_NORMAL, 'OnPopupEdit', tr('Deletes text from the document and moves it to the clipboard.')),
            (140, 'IDPM_COPY', tr('Copy') + '\tCtrl+C', wx.ITEM_NORMAL, 'OnPopupEdit', tr('Copies text from the document to the clipboard.')),
            (150, 'IDPM_PASTE', tr('Paste') + '\tCtrl+V', wx.ITEM_NORMAL, 'OnPopupEdit', tr('Pastes text from the clipboard into the document.')),
            (160, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (170, 'IDPM_SELECTION', tr('Selection'), wx.ITEM_NORMAL, None, ''),

        ]),
        ('IDPM_SELECTION',
        [
            (100, 'IDPM_SELECTION_SELECT_WORD', tr('Select Word') + '\tCtrl+W', wx.ITEM_NORMAL, 'OnSelectionWord', tr('Selects the current word.')),
            (200, 'IDPM_SELECTION_SELECT_WORD_EXTEND', tr('Select Extended Word') + '\tCtrl+Shift+W', wx.ITEM_NORMAL, 'OnSelectionWordExtend', tr('Selects the current word, including the dot.')),
            (300, 'IDPM_SELECTION_SELECT_PHRASE', tr('Match Select (Left First)') + '\tCtrl+E', wx.ITEM_NORMAL, 'OnSelectionMatchLeft', tr('Selects the text enclosed by () [] {} <> "" \'\', matching left first.')),
            (400, 'IDPM_SELECTION_SELECT_PHRASE_RIGHT', tr('Match Select (Right First)') + '\tCtrl+Shift+E', wx.ITEM_NORMAL, 'OnSelectionMatchRight', tr('Selects the text enclosed by () [] {} <> "" \'\', matching right first.')),
            (500, 'IDPM_SELECTION_SELECT_ENLARGE', tr('Enlarge Selection') + '\tCtrl+Alt+E', wx.ITEM_NORMAL, 'OnSelectionEnlarge', tr('Enlarges the selection.')),
            (600, 'IDPM_SELECTION_SELECT_LINE', tr('Select Line') + '\tCtrl+R', wx.ITEM_NORMAL, 'OnSelectionLine', tr('Selects the current phrase.')),
            (700, 'IDPM_SELECTION_SELECTALL', tr('Select All') + '\tCtrl+A', wx.ITEM_NORMAL, 'OnPopupEdit', tr('Selects the entire document.')),
            (800, 'IDPM_SELECTION_BEGIN', tr('Set Start Of Selection'), wx.ITEM_NORMAL, 'OnSelectionBegin', tr('Sets selection beginning.')),
            (900, 'IDPM_SELECTION_END', tr('Set End Of Selection'), wx.ITEM_NORMAL, 'OnSelectionEnd', tr('Sets selection end.')),
        ]),
    ])
Mixin.setPlugin('editor', 'add_menu', add_editor_menu)

def add_editor_menu_image_list(imagelist):
    imagelist.update({
        'IDPM_UNDO':'images/undo.gif',
        'IDPM_REDO':'images/redo.gif',
        'IDPM_CUT':'images/cut.gif',
        'IDPM_COPY':'images/copy.gif',
        'IDPM_PASTE':'images/paste.gif',
    })
Mixin.setPlugin('editor', 'add_menu_image_list', add_editor_menu_image_list)

def OnPopupEdit(win, event):
    eid = event.GetId()
    if eid == win.IDPM_UNDO:
        win.Undo()
    elif eid == win.IDPM_REDO:
        win.Redo()
    elif eid == win.IDPM_CUT:
        win.Cut()
    elif eid == win.IDPM_COPY:
        win.Copy()
    elif eid == win.IDPM_PASTE:
        win.Paste()
    elif eid == win.IDPM_SELECTION_SELECTALL:
        win.SelectAll()
Mixin.setMixin('editor', 'OnPopupEdit', OnPopupEdit)

def add_mainframe_menu(menulist):
    menulist.extend([ (None, #parent menu id
        [
            (200, 'IDM_EDIT', tr('Edit'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDM_EDIT', #parent menu id
        [
            (201, 'IDM_EDIT_UNDO', tr('Undo') +'\tE=Ctrl+Z', wx.ITEM_NORMAL, 'DoSTCBuildIn', tr('Reverses previous editing operation.')),
            (202, 'IDM_EDIT_REDO', tr('Redo') +'\tE=Ctrl+Y', wx.ITEM_NORMAL, 'DoSTCBuildIn', tr('Reverses previous undo operation.')),
            (203, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (204, 'IDM_EDIT_CUT', tr('Cut') + '\tE=Ctrl+X', wx.ITEM_NORMAL, 'DoSTCBuildIn', tr('Deletes text from the document and moves it to the clipboard.')),
            (205, 'IDM_EDIT_COPY', tr('Copy') + '\tE=Ctrl+C', wx.ITEM_NORMAL, 'DoSTCBuildIn', tr('Copies text from the document to the clipboard.')),
            (206, 'IDM_EDIT_PASTE', tr('Paste') + '\tE=Ctrl+V', wx.ITEM_NORMAL, 'DoSTCBuildIn', tr('Pastes text from the clipboard into the document.')),
            (210, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (215, 'IDM_EDIT_SELECTION', tr('Selection'), wx.ITEM_NORMAL, None, ''),

        ]),
        ('IDM_EDIT_SELECTION',
        [
            (100, 'IDM_EDIT_SELECTION_SELECT_WORD', tr('Select Word') + '\tE=Ctrl+W', wx.ITEM_NORMAL, 'OnEditSelectionWord', tr('Selects the current word.')),
            (200, 'IDM_EDIT_SELECTION_SELECT_WORD_EXTEND', tr('Select Extended Word') + '\tE=Ctrl+Shift+W', wx.ITEM_NORMAL, 'OnEditSelectionWordExtend', tr('Selects the current word, including the dot.')),
            (300, 'IDM_EDIT_SELECTION_SELECT_PHRASE', tr('Match Select (Left First)') + '\tE=Ctrl+E', wx.ITEM_NORMAL, 'OnEditSelectionMatchLeft', tr('Selects the text enclosed by () [] {} <> "" \'\', matching left first.')),
            (400, 'IDM_EDIT_SELECTION_SELECT_PHRASE_RIGHT', tr('Match Select (Right First)') + '\tE=Ctrl+Shift+E', wx.ITEM_NORMAL, 'OnEditSelectionMatchRight', tr('Selects the text enclosed by () [] {} <> "" \'\', matching right first.')),
            (500, 'IDM_EDIT_SELECTION_SELECT_ENLARGE', tr('Enlarge Selection') + '\tE=Ctrl+Alt+E', wx.ITEM_NORMAL, 'OnEditSelectionEnlarge', tr('Enlarges the selection.')),
            (600, 'IDM_EDIT_SELECTION_SELECT_LINE', tr('Select Line') + '\tE=Ctrl+R', wx.ITEM_NORMAL, 'OnEditSelectionLine', tr('Selects the current phrase.')),
            (700, 'IDM_EDIT_SELECTION_SELECTALL', tr('Select All') + '\tE=Ctrl+A', wx.ITEM_NORMAL, 'DoSTCBuildIn', tr('Selects the entire document.')),
            (800, 'IDM_EDIT_SELECTION_BEGIN', tr('Select Begin'), wx.ITEM_NORMAL, 'OnEditSelectionBegin', tr('Sets selection beginning.')),
            (900, 'IDM_EDIT_SELECTION_END', tr('Select End'), wx.ITEM_NORMAL, 'OnEditSelectionEnd', tr('Sets selection end.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_mainframe_menu_image_list(imagelist):
    imagelist.update({
        'IDM_EDIT_UNDO':'images/undo.gif',
        'IDM_EDIT_REDO':'images/redo.gif',
        'IDM_EDIT_CUT':'images/cut.gif',
        'IDM_EDIT_COPY':'images/copy.gif',
        'IDM_EDIT_PASTE':'images/paste.gif',
    })
Mixin.setPlugin('mainframe', 'add_menu_image_list', add_mainframe_menu_image_list)

def DoSTCBuildIn(win, event):
    eid = event.GetId()
    doc = win.document
    if eid == win.IDM_EDIT_UNDO:
        doc.Undo()
    elif eid == win.IDM_EDIT_REDO:
        doc.Redo()
    elif eid == win.IDM_EDIT_CUT:
        doc.Cut()
    elif eid == win.IDM_EDIT_COPY:
        doc.Copy()
    elif eid == win.IDM_EDIT_PASTE:
        doc.Paste()
    elif eid == win.IDM_EDIT_SELECTION_SELECTALL:
        doc.SelectAll()
Mixin.setMixin('mainframe', 'DoSTCBuildIn', DoSTCBuildIn)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_CUT, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_COPY, win.OnUpdateUI)
    if wx.Platform == '__WXMSW__':
        wx.EVT_UPDATE_UI(win, win.IDM_EDIT_PASTE, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_UNDO, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_REDO, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if hasattr(win, 'document') and win.document and win.document.edittype == 'edit':
        if eid in [win.IDM_EDIT_CUT, win.IDM_EDIT_COPY]:
            event.Enable(len(win.document.GetSelectedText()) > 0)
        elif eid == win.IDM_EDIT_PASTE:
            event.Enable(bool(win.document.CanPaste()))
        elif eid == win.IDM_EDIT_UNDO:
            event.Enable(bool(win.document.CanUndo()))
        elif eid == win.IDM_EDIT_REDO:
            event.Enable(bool(win.document.CanRedo()))
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def editor_init(win):
    wx.EVT_UPDATE_UI(win, win.IDPM_CUT, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDPM_COPY, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDPM_PASTE, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDPM_UNDO, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDPM_REDO, win.OnUpdateUI)
    wx.EVT_LEFT_DCLICK(win, win.OnDClick)
Mixin.setPlugin('editor', 'init', editor_init)

def editor_updateui(win, event):
    eid = event.GetId()
    if eid in [win.IDPM_CUT, win.IDPM_COPY]:
        event.Enable(len(win.GetSelectedText()) > 0)
    elif eid == win.IDPM_PASTE:
        event.Enable(win.CanPaste())
    elif eid == win.IDPM_UNDO:
        event.Enable(win.CanUndo())
    elif eid == win.IDPM_REDO:
        event.Enable(win.CanRedo())
Mixin.setPlugin('editor', 'on_update_ui', editor_updateui)

def OnDClick(win, event):
    if event.ControlDown():
        win.mainframe.OnEditSelectionWordExtend(event)
    else:
        event.Skip()
Mixin.setMixin('editor', 'OnDClick', OnDClick)

def OnSelectionWord(win, event):
    win.mainframe.OnEditSelectionWord(event)
Mixin.setMixin('editor', 'OnSelectionWord', OnSelectionWord)

def OnEditSelectionWord(win, event):
    pos = win.document.GetCurrentPos()
    start = win.document.WordStartPosition(pos, True)
    end = win.document.WordEndPosition(pos, True)
    win.document.SetSelection(start, end)
Mixin.setMixin('mainframe', 'OnEditSelectionWord', OnEditSelectionWord)

def OnSelectionWordExtend(win, event):
    win.mainframe.OnEditSelectionWordExtend(event)
Mixin.setMixin('editor', 'OnSelectionWordExtend', OnSelectionWordExtend)

def OnEditSelectionWordExtend(win, event):
    pos = win.document.GetCurrentPos()
    start = win.document.WordStartPosition(pos, True)
    end = win.document.WordEndPosition(pos, True)
    if end > start:
        i = start - 1
        while i >= 0:
            if win.document.getChar(i) in win.getWordChars() + '.':
                start -= 1
                i -= 1
            else:
                break
        i = end
        length = win.document.GetLength()
        while i < length:
            if win.document.getChar(i) in win.getWordChars()+ '.':
                end += 1
                i += 1
            else:
                break
    win.document.SetSelection(start, end)
Mixin.setMixin('mainframe', 'OnEditSelectionWordExtend', OnEditSelectionWordExtend)

def OnEditSelectionLine(win, event):
    win.document.SetSelection(*win.document.getLinePositionTuple())
Mixin.setMixin('mainframe', 'OnEditSelectionLine', OnEditSelectionLine)

def OnSelectionLine(win, event):
    win.mainframe.OnEditSelectionLine(event)
Mixin.setMixin('editor', 'OnSelectionLine', OnSelectionLine)

def OnEditSelectionMatchLeft(win, event):
    pos = win.document.GetCurrentPos()
    text = win.document.getRawText()

    token = [('\'', '\''), ('"', '"'), ('(', ')'), ('[', ']'), ('{', '}'), ('<', '>'), ('`', '`')]
    start, match = findLeft(text, pos, token)
    if start > -1:
        end, match = findRight(text, pos, token, match)
        if end > -1:
            win.document.SetSelection(start, end)
Mixin.setMixin('mainframe', 'OnEditSelectionMatchLeft', OnEditSelectionMatchLeft)

def OnSelectionMatchLeft(win, event):
    event.SetId(win.mainframe.IDM_EDIT_SELECTION_SELECT_PHRASE)
    win.mainframe.OnEditSelectionMatchLeft(event)
Mixin.setMixin('editor', 'OnSelectionMatchLeft', OnSelectionMatchLeft)

def OnEditSelectionMatchRight(win, event):
    pos = win.document.GetCurrentPos()
    text = win.document.getRawText()

    token = [('\'', '\''), ('"', '"'), ('(', ')'), ('[', ']'), ('{', '}'), ('<', '>')]
    end, match = findRight(text, pos, token)
    if end > -1:
        start, match = findLeft(text, pos, token, match)
        if start > -1:
            win.document.SetSelection(end, start)
Mixin.setMixin('mainframe', 'OnEditSelectionMatchRight', OnEditSelectionMatchRight)

def OnSelectionMatchRight(win, event):
    win.mainframe.OnEditSelectionMatchRight(event)
Mixin.setMixin('editor', 'OnSelectionMatchRight', OnSelectionMatchRight)

def findLeft(text, pos, token, match=None):
    countleft = {}
    countright = {}
    leftlens = {}
    rightlens = {}
    for left, right in token:
        countleft[left] = 0
        countright[right] = 0
        leftlens[left] = len(left)
        rightlens[right] = len(right)
    i = pos
    while i >= 0:
        for left, right in token:
            if text.endswith(left, 0, i):
                if countright[right] == 0:
                    if (not match) or (match and (match == right)):
                        return i, left
                    else:
                        i -= leftlens[left]
                        break
                else:
                    countright[right] -= 1
                    i -= leftlens[left]
                    break
            elif text.endswith(right, 0, i):
                countright[right] += 1
                i -= rightlens[right]
                break
        else:
            i -= 1
    return -1, ''

def findRight(text, pos, token, match=None):
    countleft = {}
    countright = {}
    leftlens = {}
    rightlens = {}
    for left, right in token:
        countleft[left] = 0
        countright[right] = 0
        leftlens[left] = len(left)
        rightlens[right] = len(right)
    i = pos
    length = len(text)
    while i < length:
        for left, right in token:
            if text.startswith(right, i):
                if countleft[left] == 0:
                    if (not match) or (match and (match == left)):
                        return i, right
                    else:
                        i += rightlens[right]
                        break
                else:
                    countleft[left] -= 1
                    i += rightlens[right]
                    break
            elif text.startswith(left, i):
                countleft[left] += 1
                i += leftlens[left]
                break
        else:
            i += 1
    return -1, ''

def OnEditSelectionEnlarge(win, event):
    start, end = win.document.GetSelection()
    if end - start > 0:
        if win.document.GetCharAt(start-1) < 127:
            start -= 1
        if win.document.GetCharAt(end + 1) < 127:
            end += 1
        win.document.SetSelection(start, end)
Mixin.setMixin('mainframe', 'OnEditSelectionEnlarge', OnEditSelectionEnlarge)

def OnSelectionEnlarge(win, event):
    win.mainframe.OnEditSelectionEnlarge(event)
Mixin.setMixin('editor', 'OnSelectionEnlarge', OnSelectionEnlarge)

def editor_init(win):
    win.MarkerDefine(2, wx.stc.STC_MARK_SMALLRECT, "red", "red")
    win.selection_mark = 2
    win.select_anchor = -1
Mixin.setPlugin('editor', 'init', editor_init)

def OnSelectionBegin(win, event):
    win.select_anchor = win.GetCurrentPos()
    win.MarkerAdd(win.GetCurrentLine(), win.selection_mark)
    if win.GetSelectedText():
        win.dselect()
Mixin.setMixin('editor', 'OnSelectionBegin', OnSelectionBegin)

def OnEditSelectionBegin(win, event):
    win.document.OnSelectionBegin(event)
Mixin.setMixin('mainframe', 'OnEditSelectionBegin', OnEditSelectionBegin)

def OnSelectionEnd(win, event):
    win.MarkerDeleteAll(win.selection_mark)
    if win.select_anchor > 0:
        win.SetSelection(win.select_anchor, win.GetCurrentPos())
    win.select_anchor = -1
Mixin.setMixin('editor', 'OnSelectionEnd', OnSelectionEnd)

def OnEditSelectionEnd(win, event):
    win.document.OnSelectionEnd(event)
Mixin.setMixin('mainframe', 'OnEditSelectionEnd', OnEditSelectionEnd)



#-----------------------  mToolbar.py ------------------

import wx
from modules import Mixin
from modules import maketoolbar

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (100, 'new'),
        (110, 'open'),
        (120, 'save'),
        (121, 'saveall'),
        (130, '|'),
        (140, 'cut'),
        (150, 'copy'),
        (160, 'paste'),
        (170, '|'),
        (180, 'undo'),
        (190, 'redo'),
        (200, '|'),
        (400, 'preference'),
        (900, '|'),
    ])

    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'new':(wx.ITEM_NORMAL, 'IDM_FILE_NEW', 'images/new.gif', tr('New Document'), tr('Creates a new document.'), 'OnFileNew'),
        'open':(wx.ITEM_NORMAL, 'IDM_FILE_OPEN', 'images/open.gif', tr('Open Document'), tr('Opens an existing document.'), 'OnFileOpen'),
        'save':(wx.ITEM_NORMAL, 'IDM_FILE_SAVE', 'images/save.gif', tr('Save Document'), tr('Saves an opened document using the same filename.'), 'OnFileSave'),
        'saveall':(wx.ITEM_NORMAL, 'IDM_FILE_SAVE_ALL', 'images/saveall.gif', tr('Save All Documents'), tr('Saves all documents.'), 'OnFileSaveAll'),
        'cut':(wx.ITEM_NORMAL, 'IDM_EDIT_CUT', 'images/cut.gif', tr('Cut'), tr('Deletes text from the document and moves it to the clipboard.'), 'DoSTCBuildIn'),
        'copy':(wx.ITEM_NORMAL, 'IDM_EDIT_COPY', 'images/copy.gif', tr('Copy'), tr('Copies text from the document to the clipboard.'), 'DoSTCBuildIn'),
        'paste':(wx.ITEM_NORMAL, 'IDM_EDIT_PASTE', 'images/paste.gif', tr('Paste'), tr('Pastes text from the clipboard into the document.'), 'DoSTCBuildIn'),
        'undo':(wx.ITEM_NORMAL, 'IDM_EDIT_UNDO', 'images/undo.gif', tr('Undo'), tr('Reverse previous editing operation.'), 'DoSTCBuildIn'),
        'redo':(wx.ITEM_NORMAL, 'IDM_EDIT_REDO', 'images/redo.gif', tr('Redo'), tr('Reverse previous undo operation.'), 'DoSTCBuildIn'),
        'preference':(wx.ITEM_NORMAL, 'wx.ID_PREFERENCES', 'images/prop.gif', tr('Preferences'), tr('Opens the Preferences window.'), 'OnOptionPreference'),
    })
Mixin.setPlugin('mainframe', 'add_tool_list', add_tool_list)

def beforeinit(win):
    maketoolbar.maketoolbar(win, win.toollist, win.toolbaritems)
Mixin.setPlugin('mainframe', 'beforeinit', beforeinit)



#-----------------------  mIcon.py ------------------

import wx
from modules import Mixin
from modules import common

def init(win):
    icon = wx.EmptyIcon()
    iconfile = common.uni_work_file('ulipad.ico')
    bmp = common.getpngimage(iconfile)
    win.SetIcon(wx.Icon(iconfile, wx.BITMAP_TYPE_ICO))
Mixin.setPlugin('mainframe', 'init', init)



#-----------------------  mRecentFile.py ------------------

import wx
import os
from modules import Mixin
from modules import common
from modules import Globals

def add_mainframe_menu(menulist):
    menulist.extend([('IDM_FILE',
        [
            (130, 'IDM_FILE_RECENTFILES', tr('Recent Files...')+'\tAlt+R', wx.ITEM_NORMAL, 'OnOpenRecentFiles', 'Shows recently opened files in a pop-up menu.'),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def pref_init(pref):
    pref.recent_files = []
    pref.recent_files_num = 20
Mixin.setPlugin('preference', 'init', pref_init)

def afteropenfile(win, filename):
    if Globals.starting:
        return
    if filename:
        #deal recent files
        if filename in win.pref.recent_files:
            win.pref.recent_files.remove(filename)
        win.pref.recent_files.insert(0, filename)
        win.pref.recent_files = win.pref.recent_files[:win.pref.recent_files_num]
        win.pref.last_dir = os.path.dirname(filename)


        #save pref
        win.pref.save()
Mixin.setPlugin('editor', 'afteropenfile', afteropenfile)
Mixin.setPlugin('editor', 'aftersavefile', afteropenfile)

def OnOpenRecentFiles(win, event=None):
    menu = wx.Menu()
    pref = win.pref
    for index, filename in enumerate(pref.recent_files):
        def OnFunc(event, index=index):
            open_recent_files(win, index)

        _id = wx.NewId()
        item = wx.MenuItem(menu, _id, filename, filename)
        wx.EVT_MENU(win, _id, OnFunc)
        menu.AppendItem(item)
    win.PopupMenu(menu)
Mixin.setMixin('mainframe', 'OnOpenRecentFiles', OnOpenRecentFiles)

def add_pref(preflist):
    preflist.extend([
        (tr('Document'), 200, 'num', 'recent_files_num', tr('Maximum number of recent files:'), None)
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)


def open_recent_files(win, index):
    filename = win.pref.recent_files[index]
    try:
        f = file(filename)
        f.close()
    except:
        common.showerror(win, tr("Can't open the file %s.") % filename)
        del win.pref.recent_files[index]
        win.pref.save()
        return
    win.editctrl.new(filename)




#-----------------------  mSearch.py ------------------

"""Search process"""

import wx
from modules import Mixin

def add_mainframe_menu(menulist):
    menulist.extend([ (None, #parent menu id
        [
            (400, 'IDM_SEARCH', tr('Search'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDM_SEARCH', #parent menu id
        [
            (100, 'wx.ID_FIND', tr('Find...') + '\tE=Ctrl+F', wx.ITEM_NORMAL, 'OnSearchFind', tr('Shows the Find pane.')),
            (110, 'IDM_SEARCH_DIRECTFIND', tr('Directly Find') + '\tE=F4', wx.ITEM_NORMAL, 'OnSearchDirectFind', tr('Jumps to the next occurrence of selected text.')),
            (120, 'wx.ID_REPLACE', tr('Find And Replace...') + '\tE=Ctrl+H', wx.ITEM_NORMAL, 'OnSearchReplace', tr('Shows the Find And Replace pane.')),
            (130, 'wx.ID_BACKWARD', tr('Find Previous') + '\tE=Shift+F3', wx.ITEM_NORMAL, 'OnSearchFindPrev', tr('Finds the previous occurence of text.')),
            (140, 'wx.ID_FORWARD', tr('Find Next') + '\tE=F3', wx.ITEM_NORMAL, 'OnSearchFindNext', tr('Finds the next occurence of text.')),
            (150, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (160, 'IDM_SEARCH_GOTO_LINE', tr('Go To Line...') + '\tE=Ctrl+G', wx.ITEM_NORMAL, 'OnSearchGotoLine', tr('Jumps to the specified line in the current document.')),
            (170, 'IDM_SEARCH_LAST_MODIFY', tr('Go To Last Modification') + '\tE=Ctrl+B', wx.ITEM_NORMAL, 'OnSearchLastModify', tr('Jumps to the position of the last modification.')),

        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_mainframe_menu_image_list(imagelist):
    imagelist.update({
        'wx.ID_FIND':'images/find.gif',
        'wx.ID_REPLACE':'images/replace.gif',
        'wx.ID_FORWARD':'images/findnext.gif',
    })
Mixin.setPlugin('mainframe', 'add_menu_image_list', add_mainframe_menu_image_list)

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (220, 'find'),
        (230, 'replace'),
        (240, '|'),
    ])

    toolbaritems.update({
        'find':(wx.ITEM_NORMAL, 'wx.ID_FIND', 'images/find.gif', tr('Find'), tr('Shows the Find pane.'), 'OnSearchFind'),
        'replace':(wx.ITEM_NORMAL, 'wx.ID_REPLACE', 'images/replace.gif', tr('Find And Replace'), tr('Shows the Find And Replace pane.'), 'OnSearchReplace'),
    })
Mixin.setPlugin('mainframe', 'add_tool_list', add_tool_list)

def afterinit(win):
    import FindReplace

    win.finder = FindReplace.Finder()
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def on_set_focus(win, event):
    win.mainframe.finder.setWindow(win)
Mixin.setPlugin('editor', 'on_set_focus', on_set_focus)

def on_document_enter(win, document):
    win.mainframe.finder.setWindow(document)
Mixin.setPlugin('editctrl', 'on_document_enter', on_document_enter)

def OnSearchFind(win, event):
    name = 'findpanel'
    if not win.documentarea.sizer.is_shown(name):
        import FindReplace

        panel = FindReplace.FindPanel(win.documentarea, name)
        win.documentarea.sizer.add(panel,
            name=name, flag=wx.EXPAND|wx.ALL, border=2)
    else:
        panel = win.documentarea.sizer.find(name)
        if panel:
            panel = panel.get_obj()
    panel.reset(win.finder)
Mixin.setMixin('mainframe', 'OnSearchFind', OnSearchFind)

def OnSearchDirectFind(win, event):
    text = win.document.GetSelectedText()
    if len(text) > 0:
        win.finder.findtext = text
        win.finder.find(0)
Mixin.setMixin('mainframe', 'OnSearchDirectFind', OnSearchDirectFind)

def OnSearchReplace(win, event):
    name = 'findpanel'
    if not win.documentarea.sizer.is_shown(name):
        import FindReplace

        panel = FindReplace.FindPanel(win.documentarea, name)
        win.documentarea.sizer.add(panel,
            name=name, flag=wx.EXPAND|wx.ALL, border=2)
    else:
        panel = win.documentarea.sizer.find(name)
        if panel:
            panel = panel.get_obj()
    panel.reset(win.finder, replace=True)
Mixin.setMixin('mainframe', 'OnSearchReplace', OnSearchReplace)

def OnSearchFindNext(win, event):
    win.finder.find(0)
Mixin.setMixin('mainframe', 'OnSearchFindNext', OnSearchFindNext)

def OnSearchFindPrev(win, event):
    win.finder.find(1)
Mixin.setMixin('mainframe', 'OnSearchFindPrev', OnSearchFindPrev)


def pref_init(pref):
    pref.max_number  = 20
    pref.findtexts = []
    pref.replacetexts = []
Mixin.setPlugin('preference', 'init', pref_init)

def OnSearchGotoLine(win, event):
    from modules import Entry
    document = win.document

    line = document.GetCurrentLine() + 1
    dlg = Entry.MyTextEntry(win, tr("Go To Line"), tr("Enter the line number:"), str(line))
    answer = dlg.ShowModal()
    if answer == wx.ID_OK:
        try:
            line = int(dlg.GetValue())
        except:
            return
        else:
            document.goto(line)
Mixin.setMixin('mainframe', 'OnSearchGotoLine', OnSearchGotoLine)

def pref_init(pref):
    pref.smart_nav_last_position = None
Mixin.setPlugin('preference', 'init', pref_init)

def on_modified(win):
    if hasattr(win, 'multiview') and win.multiview:
        return
    win.pref.smart_nav_last_position = win.getFilename(), win.save_state()
    win.pref.save()
Mixin.setPlugin('editor', 'on_modified', on_modified)

def OnSearchLastModify(win, event=None):
    if win.pref.smart_nav_last_position:
        filename, status = win.pref.smart_nav_last_position
        document = win.editctrl.new(filename)
        if document.getFilename() == filename:
            document.restore_state(status)
        else:
            win.pref.smart_nav_last_position = None
Mixin.setMixin('mainframe', 'OnSearchLastModify', OnSearchLastModify)



#-----------------------  mPosition.py ------------------

import wx
from modules import Mixin

def on_key_up(win, event):
    if win.edittype == 'edit':
        win.mainframe.SetStatusText(tr("Line: %d") % (win.GetCurrentLine()+1), 1)
        win.mainframe.SetStatusText(tr("Column: %d") % (win.GetColumn(win.GetCurrentPos())+1), 2)
Mixin.setPlugin('editor', 'on_key_up', on_key_up)

def on_mouse_up(win, event):
    if win.edittype == 'edit':
        win.mainframe.SetStatusText(tr("Line: %d") % (win.GetCurrentLine()+1), 1)
        win.mainframe.SetStatusText(tr("Column: %d") % (win.GetColumn(win.GetCurrentPos())+1), 2)
Mixin.setPlugin('editor', 'on_mouse_up', on_mouse_up)

def on_document_enter(win, document):
    if document.edittype == 'edit':
        win.mainframe.SetStatusText(tr("Line: %d") % (document.GetCurrentLine()+1), 1)
        win.mainframe.SetStatusText(tr("Column: %d") % (document.GetColumn(document.GetCurrentPos())+1), 2)
Mixin.setPlugin('editctrl', 'on_document_enter', on_document_enter)

def on_update_ui(win, event):
    win.mainframe.SetStatusText(tr("Selected: %d") % len(win.GetSelectedText()), 3)
Mixin.setPlugin('editor', 'on_update_ui', on_update_ui)




#-----------------------  mLineending.py ------------------

import wx
from modules import Mixin
from modules import common

eolmess = [tr(r"Unix mode (\n)"), tr(r"DOS/Windows mode (\r\n)"), tr(r"Mac mode (\r)")]

def beforeinit(win):
    win.lineendingsaremixed = False
    win.eolmode = win.pref.default_eol_mode
    win.eols = {0:wx.stc.STC_EOL_LF, 1:wx.stc.STC_EOL_CRLF, 2:wx.stc.STC_EOL_CR}
    win.eolstr = {0:r'\n', 1:r'\r\n', 2:r'\r'}
    win.eolstring = {0:'\n', 1:'\r\n', 2:'\r'}
    win.eolmess = eolmess
    win.SetEOLMode(win.eols[win.eolmode])
Mixin.setPlugin('editor', 'init', beforeinit)

def add_pref(preflist):
    preflist.extend([
        (tr('Document'), 140, 'choice', 'default_eol_mode', tr('Default line ending used in the document:'), eolmess)
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def pref_init(pref):
    if wx.Platform == '__WXMSW__':
        pref.default_eol_mode = 1
    else:
        pref.default_eol_mode = 0
Mixin.setPlugin('preference', 'init', pref_init)

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_DOCUMENT',
        [
            (120, 'IDM_DOCUMENT_EOL_CONVERT', tr('Convert Line Ending'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDM_DOCUMENT_EOL_CONVERT',
        [
            (100, 'IDM_DOCUMENT_EOL_CONVERT_PC', tr('Convert To Windows Format'), wx.ITEM_NORMAL, 'OnDocumentEolConvertWin', tr('Converts line ending to Windows format.')),
            (200, 'IDM_DOCUMENT_EOL_CONVERT_UNIX', tr('Convert To Unix Format'), wx.ITEM_NORMAL, 'OnDocumentEolConvertUnix', tr('Converts line ending to Unix format.')),
            (300, 'IDM_DOCUMENT_EOL_CONVERT_MAX', tr('Convert To Mac Format'), wx.ITEM_NORMAL, 'OnDocumentEolConvertMac', tr('Converts line ending to Mac format.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def setEOLMode(win, mode, convert=True):
    win.lineendingsaremixed = False
    win.eolmode = mode
    if convert:
        win.ConvertEOLs(win.eols[mode])
    win.SetEOLMode(win.eols[mode])
    common.set_line_ending(win.eolstr[mode])

def OnDocumentEolConvertWin(win, event):
    setEOLMode(win.document, 1)
Mixin.setMixin('mainframe', 'OnDocumentEolConvertWin', OnDocumentEolConvertWin)

def OnDocumentEolConvertUnix(win, event):
    setEOLMode(win.document, 0)
Mixin.setMixin('mainframe', 'OnDocumentEolConvertUnix', OnDocumentEolConvertUnix)

def OnDocumentEolConvertMac(win, event):
    setEOLMode(win.document, 2)
Mixin.setMixin('mainframe', 'OnDocumentEolConvertMac', OnDocumentEolConvertMac)

def check_mixed(text):
    lineendingsaremixed = False

    eollist = "".join(map(getEndOfLineCharacter, text))

    len_win = eollist.count('\r\n')
    len_unix = eollist.count('\n')
    len_mac = eollist.count('\r')
    eolmode = -1
    if len_mac > 0 and len_unix == 0:
        eolmode = 2
    elif len_win == len_unix == len_mac:
        eolmode = 1
    elif len_unix > 0 and len_win == 0 and len_mac == 0:
        eolmode = 0
    else:
        lineendingsaremixed = True

    return eolmode, lineendingsaremixed

def fileopentext(win, stext):
    text = stext[0]
    win.eolmode, win.lineendingsaremixed = check_mixed(text)
Mixin.setPlugin('editor', 'openfiletext', fileopentext)

def confirm_eol(win):
    eolmodestr = "MIX"
    d = wx.MessageDialog(win,
        tr('%s is currently mixed.\nWould you like to change it to default?\nThe default is: %s')
        % (win.filename, win.eolmess[win.pref.default_eol_mode]),
        tr("Mixed Line Ending"), wx.YES_NO | wx.ICON_QUESTION)
    if d.ShowModal() == wx.ID_YES:
        setEOLMode(win, win.pref.default_eol_mode)
        return True
    else:
        return False

def afteropenfile(win, filename):
    if win.lineendingsaremixed:
        wx.CallAfter(confirm_eol, win)
    else:
        eolmodestr = win.eolstr[win.eolmode]
        common.set_line_ending(eolmodestr)
        setEOLMode(win, win.eolmode, convert=False)
Mixin.setPlugin('editor', 'afteropenfile', afteropenfile)


def savefile(win, filename):
    text = win.GetText()
    win.eolmode, win.lineendingsaremixed = check_mixed(text)
    if win.lineendingsaremixed:
        confirm_eol(win)
Mixin.setPlugin('editor', 'savefile', savefile)

def on_document_enter(win, document):
    if document.edittype == 'edit':
        if document.lineendingsaremixed:
            eolmodestr = "MIX"
        else:
            eolmodestr = document.eolstr[document.eolmode]
        common.set_line_ending(eolmodestr)
Mixin.setPlugin('editctrl', 'on_document_enter', on_document_enter)

def getEndOfLineCharacter(character):
    if character == '\r' or character == '\n':
        return character
    return ""


def add_pref(preflist):
    preflist.extend([
        (tr('Document')+'/'+tr('Edit'), 180, 'check', 'edit_linestrip', tr('Strip line ending at file saving'), eolmess)
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def pref_init(pref):
    pref.edit_linestrip = False
Mixin.setPlugin('preference', 'init', pref_init)

def savefile(win, filename):
    if win.pref.edit_linestrip:
        status = win.save_state()
        try:
    #        if not win.lineendingsaremixed:
    #            setEOLMode(win, win.eolmode)
            win.mainframe.OnEditFormatChop(None)
        finally:
            win.restore_state(status)
Mixin.setPlugin('editor', 'savefile', savefile)




#-----------------------  mView.py ------------------

import wx
from modules import Mixin

def add_mainframe_menu(menulist):
    menulist.extend([ (None,
        [
            (300, 'IDM_VIEW', tr('View'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDM_VIEW', #parent menu id
        [
            (100, 'IDM_VIEW_TAB', tr('Tabs And Spaces'), wx.ITEM_CHECK, 'OnViewTab', tr('Shows or hides whitespace indicators.')),
            (110, 'IDM_VIEW_INDENTATION_GUIDES', tr('Indentation Guides'), wx.ITEM_CHECK, 'OnViewIndentationGuides', tr('Shows or hides indentation guides.')),
            (120, 'IDM_VIEW_RIGHT_EDGE', tr('Long-Line Indicator'), wx.ITEM_CHECK, 'OnViewRightEdge', tr('Shows or hides the long-line indicator.')),
            (130, 'IDM_VIEW_LINE_NUMBER', tr('Line Numbers'), wx.ITEM_CHECK, 'OnViewLineNumber', tr('Shows or hides line numbers.')),
            (131, 'IDM_VIEW_ENDOFLINE_MARK', tr('End-Of-Line Marker'), wx.ITEM_CHECK, 'OnViewEndOfLineMark', tr('Shows or hides the end-of-line marker.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_VIEW_TAB, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_VIEW_INDENTATION_GUIDES, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_VIEW_RIGHT_EDGE, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_VIEW_LINE_NUMBER, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_VIEW_ENDOFLINE_MARK, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def editor_init(win):
    #show long line indicator
    if win.mainframe.pref.startup_show_longline:
        win.SetEdgeMode(wx.stc.STC_EDGE_LINE)
    else:
        win.SetEdgeMode(wx.stc.STC_EDGE_NONE)
        win.SetEdgeColour(wx.Colour(200,200,200))

    #long line width
    win.SetEdgeColumn(win.mainframe.pref.edge_column_width)

    #show tabs
    if win.mainframe.pref.startup_show_tabs:
        win.SetViewWhiteSpace(wx.stc.STC_WS_VISIBLEALWAYS)
    else:
        win.SetViewWhiteSpace(wx.stc.STC_WS_INVISIBLE)

    #show indentation guides
    win.SetIndentationGuides(win.mainframe.pref.startup_show_indent_guide)

    win.mwidth = 0     #max line number
    win.show_linenumber = win.mainframe.pref.startup_show_linenumber
Mixin.setPlugin('editor', 'init', editor_init)

def OnViewTab(win, event):
    stat = win.document.GetViewWhiteSpace()
    if stat == wx.stc.STC_WS_INVISIBLE:
        win.document.SetViewWhiteSpace(wx.stc.STC_WS_VISIBLEALWAYS)
    elif stat == wx.stc.STC_WS_VISIBLEALWAYS:
        win.document.SetViewWhiteSpace(wx.stc.STC_WS_INVISIBLE)
Mixin.setMixin('mainframe', 'OnViewTab', OnViewTab)

def OnViewIndentationGuides(win, event):
    win.document.SetIndentationGuides(not win.document.GetIndentationGuides())
Mixin.setMixin('mainframe', 'OnViewIndentationGuides', OnViewIndentationGuides)

def pref_init(pref):
    pref.edge_column_width = 79
    pref.startup_show_tabs = False
    pref.startup_show_indent_guide = False
    pref.startup_show_longline = True
    pref.startup_show_linenumber = True
Mixin.setPlugin('preference', 'init', pref_init)

tab_startup = tr('Document') + '/' + tr('Startup')
tab_view = tr('Document') + '/' + tr('View')
tab_edit = tr('Document') + '/' + tr('Edit')
tab_backend = tr('Document') + '/' + tr('Backend')
def add_pref_page(pages_order):
    pages_order.update({
        tab_startup:100,
        tab_view:110,
        tab_edit:120,
        tab_backend:130,
    }
    )
Mixin.setPlugin('preference', 'add_pref_page', add_pref_page)

def add_pref(preflist):
    preflist.extend([
        (tab_startup, 110, 'check', 'startup_show_tabs', tr('Show whitespace indicators at startup'), None),
        (tab_startup, 120, 'check', 'startup_show_indent_guide', tr('Make indentation guides visible at startup'), None),
        (tab_startup, 130, 'check', 'startup_show_longline', tr('Make long-line indicator visible at startup'), None),
        (tab_startup, 140, 'check', 'startup_show_linenumber', tr('Show line numbers at startup'), None),
        (tr('Document'), 100, 'num', 'edge_column_width', tr('Long-line indicator column position:'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def savepreference(mainframe, pref):
    for document in mainframe.editctrl.getDocuments():
        if document.CanView():
            document.SetEdgeColumn(mainframe.pref.edge_column_width)
Mixin.setPlugin('prefdialog', 'savepreference', savepreference)

def OnViewRightEdge(win, event):
    flag = win.document.GetEdgeMode()
    if flag == wx.stc.STC_EDGE_NONE:
        k = wx.stc.STC_EDGE_LINE
    else:
        k = wx.stc.STC_EDGE_NONE
    win.document.SetEdgeMode(k)
Mixin.setMixin('mainframe', 'OnViewRightEdge', OnViewRightEdge)

def OnViewLineNumber(win, event):
    win.document.show_linenumber = not win.document.show_linenumber
    win.document.setLineNumberMargin(win.document.show_linenumber)
Mixin.setMixin('mainframe', 'OnViewLineNumber', OnViewLineNumber)

def OnViewEndOfLineMark(win, event):
    win.document.SetViewEOL(not win.document.GetViewEOL())
Mixin.setMixin('mainframe', 'OnViewEndOfLineMark', OnViewEndOfLineMark)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if hasattr(win, 'document') and win.document and win.document.CanView():
        if eid in [win.IDM_VIEW_TAB, win.IDM_VIEW_INDENTATION_GUIDES, win.IDM_VIEW_RIGHT_EDGE]:
            event.Enable(True)
        if eid == win.IDM_VIEW_TAB:
            stat = win.document.GetViewWhiteSpace()
            if stat == wx.stc.STC_WS_INVISIBLE:
                event.Check(False)
            elif stat == wx.stc.STC_WS_VISIBLEALWAYS:
                event.Check(True)
        elif eid == win.IDM_VIEW_INDENTATION_GUIDES:
            event.Check(win.document.GetIndentationGuides())
        elif eid == win.IDM_VIEW_RIGHT_EDGE:
            flag = win.document.GetEdgeMode()
            if flag == wx.stc.STC_EDGE_NONE:
                event.Check(False)
            else:
                event.Check(True)
        elif eid == win.IDM_VIEW_ENDOFLINE_MARK:
            event.Check(win.document.GetViewEOL())
        elif eid == win.IDM_VIEW_LINE_NUMBER:
            event.Check(win.document.show_linenumber)

    else:
        if eid in [win.IDM_VIEW_TAB, win.IDM_VIEW_INDENTATION_GUIDES, win.IDM_VIEW_RIGHT_EDGE, win.IDM_VIEW_ENDOFLINE_MARK]:
            event.Enable(False)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (800, '|'),
        (810, 'viewtab'),
    ])

    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'viewtab':(wx.ITEM_CHECK, 'IDM_VIEW_TAB', 'images/format.gif', tr('Toggle Whitespace'), tr('Shows or hides whitespace indicators.'), 'OnViewTab'),
    })
Mixin.setPlugin('mainframe', 'add_tool_list', add_tool_list)

def on_modified(win):
    win.setLineNumberMargin(win.show_linenumber)
Mixin.setPlugin('editor', 'on_modified', on_modified)

def afteropenfile(win, filename):
    win.setLineNumberMargin(win.show_linenumber)
Mixin.setPlugin('editor', 'afteropenfile', afteropenfile)



#-----------------------  mFormat.py ------------------

import wx.stc
from modules import Mixin
from modules import common
from modules import Globals

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_EDIT',
        [
            (250, 'IDM_EDIT_FORMAT', tr('Format'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDM_EDIT_FORMAT',
        [
            (100, 'IDM_EDIT_FORMAT_CHOP', tr('Trim Trailing Whitespace'), wx.ITEM_NORMAL, 'OnEditFormatChop', tr('Trims the trailing whitespace.')),
            (110, 'IDM_EDIT_FORMAT_SPACETOTAB', tr('Leading Spaces To Tabs'), wx.ITEM_NORMAL, 'OnEditFormatSpaceToTab', tr('Converts leading spaces to tabs.')),
            (120, 'IDM_EDIT_FORMAT_TABTOSPACE', tr('Leading Tabs To Spaces'), wx.ITEM_NORMAL, 'OnEditFormatTabToSpace', tr('Converts leading tabs to spaces.')),
            (125, 'IDM_EDIT_FORMAT_ALLTABTOSPACE', tr('All Tabs To Spaces'), wx.ITEM_NORMAL, 'OnEditFormatAllTabToSpace', tr('Converts all tabs to spaces.')),
            (130, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (140, 'IDM_EDIT_FORMAT_INDENT', tr('Increase Indent'), wx.ITEM_NORMAL, 'OnEditFormatIndent', tr('Increases the indentation of current line or selected block.')),
            (150, 'IDM_EDIT_FORMAT_UNINDENT', tr('Decrease Indent'), wx.ITEM_NORMAL, 'OnEditFormatUnindent', tr('Decreases the indentation of current line or selected block.')),
            (160, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (170, 'IDM_EDIT_FORMAT_COMMENT', tr('Line Comment...') + '\tE=Ctrl+/', wx.ITEM_NORMAL, 'OnEditFormatComment', tr('Inserts comment sign at the beginning of line.')),
            (180, 'IDM_EDIT_FORMAT_UNCOMMENT', tr('Line Uncomment...') + '\tE=Ctrl+\\', wx.ITEM_NORMAL, 'OnEditFormatUncomment', tr('Removes comment sign from the beginning of line.')),
            (190, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (200, 'IDM_EDIT_FORMAT_QUOTE', tr('Text Quote...') + '\tE=Ctrl+\'', wx.ITEM_NORMAL, 'OnEditFormatQuote', tr('Quotes selected text.')),
            (210, 'IDM_EDIT_FORMAT_UNQUOTE', tr('Text Unquote...') + '\tE=Ctrl+Shift+\'', wx.ITEM_NORMAL, 'OnEditFormatUnquote', tr('Unquotes selected text.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_editor_menu(popmenulist):
    popmenulist.extend([ (None, #parent menu id
        [
            (220, 'IDPM_FORMAT', tr('Format'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDPM_FORMAT',
        [
            (100, 'IDPM_FORMAT_CHOP', tr('Trim Trailing Whitespace'), wx.ITEM_NORMAL, 'OnFormatChop', tr('Trims the trailing whitespace.')),
            (110, 'IDPM_FORMAT_SPACETOTAB', tr('Convert Leading Spaces To Tabs'), wx.ITEM_NORMAL, 'OnFormatSpaceToTab', tr('Converts leading spaces to tabs.')),
            (120, 'IDPM_FORMAT_TABTOSPACE', tr('Convert Leading Tabs To Spaces'), wx.ITEM_NORMAL, 'OnFormatTabToSpace', tr('Converts leading tabs to spaces.')),
            (125, 'IDPM_FORMAT_ALLTABTOSPACE', tr('Convert All Tabs To Spaces'), wx.ITEM_NORMAL, 'OnFormatAllTabToSpace', tr('Converts all tabs to spaces.')),
            (130, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (140, 'IDPM_FORMAT_INDENT', tr('Increase Indent'), wx.ITEM_NORMAL, 'OnFormatIndent', tr('Increases the indentation of current line or selected block.')),
            (150, 'IDPM_FORMAT_UNINDENT', tr('Decrease Indent'), wx.ITEM_NORMAL, 'OnFormatUnindent', tr('Decreases the indentation of current line or selected block.')),
            (160, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (170, 'IDPM_FORMAT_COMMENT', tr('Line Comment...') + '\tCtrl+/', wx.ITEM_NORMAL, 'OnFormatComment', tr('Inserts comment sign at the beginning of line.')),
            (180, 'IDPM_FORMAT_UNCOMMENT', tr('Line Uncomment...') + '\tCtrl+\\', wx.ITEM_NORMAL, 'OnFormatUncomment', tr('Removes comment sign from the beginning of line.')),
            (190, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (200, 'IDPM_FORMAT_QUOTE', tr('Text Quote...') + '\tCtrl+\'', wx.ITEM_NORMAL, 'OnFormatQuote', tr('Quotes selected text.')),
            (210, 'IDPM_FORMAT_UNQUOTE', tr('Text Unquote...') + '\tCtrl+Shift+\'', wx.ITEM_NORMAL, 'OnFormatUnquote', tr('Unquotes selected text.')),
        ]),
    ])
Mixin.setPlugin('editor', 'add_menu', add_editor_menu)

def add_mainframe_menu_image_list(imagelist):
    imagelist.update({
        'IDM_EDIT_FORMAT_INDENT':'images/indent.gif',
        'IDM_EDIT_FORMAT_UNINDENT':'images/unindent.gif',
    })
Mixin.setPlugin('mainframe', 'add_menu_image_list', add_mainframe_menu_image_list)

def add_editor_menu_image_list(imagelist):
    imagelist.update({
        'IDPM_FORMAT_INDENT':'images/indent.gif',
        'IDPM_FORMAT_UNINDENT':'images/unindent.gif',
    })
Mixin.setPlugin('editor', 'add_menu_image_list', add_editor_menu_image_list)

def OnEditFormatIndent(win, event):
    OnFormatIndent(win.document, event)
Mixin.setMixin('mainframe', 'OnEditFormatIndent', OnEditFormatIndent)

def OnEditFormatUnindent(win, event):
    OnFormatUnindent(win.document, event)
Mixin.setMixin('mainframe', 'OnEditFormatUnindent', OnEditFormatUnindent)

def OnFormatIndent(win, event):
    win.CmdKeyExecute(wx.stc.STC_CMD_TAB)
Mixin.setMixin('editor', 'OnFormatIndent', OnFormatIndent)

def OnFormatUnindent(win, event):
    win.CmdKeyExecute(wx.stc.STC_CMD_BACKTAB)
Mixin.setMixin('editor', 'OnFormatUnindent', OnFormatUnindent)

def OnFormatQuote(win, event):
    win.mainframe.OnEditFormatQuote(event)
Mixin.setMixin('editor', 'OnFormatQuote', OnFormatQuote)

def OnFormatUnquote(win, event):
    win.mainframe.OnEditFormatUnquote(event)
Mixin.setMixin('editor', 'OnFormatUnquote', OnFormatUnquote)

def pref_init(pref):
    pref.tabwidth = 4
    pref.last_comment_chars = '#'
    pref.show_comment_chars_dialog = False
Mixin.setPlugin('preference', 'init', pref_init)

tab_edit = tr('Document')+'/'+tr('Edit')
def add_pref(preflist):
    preflist.extend([
        (tr('Document'), 110, 'num', 'tabwidth', tr('Tab width in spaces:'), None),
        (tab_edit, 160, 'check', 'show_comment_chars_dialog', tr('Show comment dialog if adding a comment'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def editor_init(win):
    #set tab width
    win.SetTabWidth(win.mainframe.pref.tabwidth)

    wx.EVT_UPDATE_UI(win, win.IDPM_FORMAT_QUOTE, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDPM_FORMAT_UNQUOTE, win.OnUpdateUI)
Mixin.setPlugin('editor', 'init', editor_init)

def savepreference(mainframe, pref):
    for document in mainframe.editctrl.getDocuments():
        document.SetTabWidth(mainframe.pref.tabwidth)
Mixin.setPlugin('prefdialog', 'savepreference', savepreference)

import re
r_lineending = re.compile(r'\s+$')
def strip_lineending(document):
    status = document.save_state()
    document.BeginUndoAction()
    try:
        for i in range(document.GetLineCount()):
            start = document.PositionFromLine(i)
            end = document.GetLineEndPosition(i)
            text = document.GetTextRange(start, end).encode('utf-8')
            b = r_lineending.search(text)
            if b:
                document.SetTargetStart(start+b.start())
                document.SetTargetEnd(start+b.end())
                document.ReplaceTarget('')
    finally:
        document.restore_state(status)
        document.EndUndoAction()

def OnEditFormatStripLineending(win, event):
    strip_lineending(win.document)
Mixin.setMixin('mainframe', 'OnEditFormatStripLineending', OnEditFormatStripLineending)

def OnFormatStripLineending(win, event):
    strip_lineending(win)
Mixin.setMixin('editor', 'OnFormatStripLineending', OnFormatStripLineending)

def OnEditFormatChop(win, event):
    strip_lineending(win.document)
Mixin.setMixin('mainframe', 'OnEditFormatChop', OnEditFormatChop)

def OnFormatChop(win, event):
    win.mainframe.OnEditFormatChop(event)
Mixin.setMixin('editor', 'OnFormatChop', OnFormatChop)

def get_document_comment_chars(editor):
    chars = {
        'c':'//',
        'python':'#',
        'ruby':'#',
        'perl':'#',
        'java':'//',
        'js':'//',
        'html':'//',
        'css':'//',
        'default':'#',
    }
    lang = editor.languagename
    x = common.get_config_file_obj(values={'comment_chars':chars})
    cchar = ''
    if x.comment_chars.has_key(lang):
        cchar = x.comment_chars[lang]
    if not cchar:
        if x.comment_chars.has_key('default'):
            cchar = x.comment_chars.default
    if not cchar:
        cchar = Globals.pref.last_comment_chars
    return cchar
Mixin.setMixin('editor', 'get_document_comment_chars', get_document_comment_chars)

def OnEditFormatComment(win, event):
    if win.pref.show_comment_chars_dialog:
        from modules import Entry

        dlg = Entry.MyTextEntry(win, tr("Comment Writer"), tr("Comment:"), get_document_comment_chars(win.document))
        answer = dlg.ShowModal()
        if answer == wx.ID_OK:
            commentchar = dlg.GetValue()
            if len(commentchar) == 0:
                return
        else:
            return
    else:
        commentchar = get_document_comment_chars(win.document)
    win.pref.last_comment_chars = commentchar
    win.pref.save()
    win.document.BeginUndoAction()
    for i in win.document.getSelectionLines():
        start = win.document.PositionFromLine(i)
        win.document.InsertText(start, commentchar)
    win.document.EndUndoAction()
Mixin.setMixin('mainframe', 'OnEditFormatComment', OnEditFormatComment)

def OnFormatComment(win, event):
    win.mainframe.OnEditFormatComment(event)
Mixin.setMixin('editor', 'OnFormatComment', OnFormatComment)

def OnEditFormatUncomment(win, event):
    if win.pref.show_comment_chars_dialog:
        from modules import Entry

        dlg = Entry.MyTextEntry(win, tr("Comment..."), tr("Comment Char:"), get_document_comment_chars(win.document))
        answer = dlg.ShowModal()
        if answer == wx.ID_OK:
            commentchar = dlg.GetValue()
            if len(commentchar) == 0:
                return
        else:
            return
    else:
        commentchar = get_document_comment_chars(win.document)
    win.pref.last_comment_chars = commentchar
    win.pref.save()
    win.document.BeginUndoAction()
    len_cm = len(commentchar)
    for i in win.document.getSelectionLines():
        start = win.document.PositionFromLine(i)
        text = win.document.getLineText(i)
        if text.startswith(commentchar):
            win.document.removeText(start, len_cm)
    win.document.EndUndoAction()
Mixin.setMixin('mainframe', 'OnEditFormatUncomment', OnEditFormatUncomment)

def OnFormatUncomment(win, event):
    win.mainframe.OnEditFormatUncomment(event)
Mixin.setMixin('editor', 'OnFormatUncomment', OnFormatUncomment)

def OnEditFormatSpaceToTab(win, event):
    win.document.BeginUndoAction()
    for i in win.document.getSelectionLines():
        tabwidth = win.document.GetTabWidth()
        text = win.document.getLineText(i).expandtabs(tabwidth)
        k = 0
        for ch in text:
            if ch == ' ':
                k += 1
            else:
                break
        n, m = divmod(k, tabwidth)
        newtext = '\t'*n + ' '*m + text[k:]
        win.document.replaceLineText(i, newtext)
    win.document.EndUndoAction()
    win.document.SetUseTabs(True)
    win.document.usetab = True
Mixin.setMixin('mainframe', 'OnEditFormatSpaceToTab', OnEditFormatSpaceToTab)

def OnFormatSpaceToTab(win, event):
    win.mainframe.OnEditFormatSpaceToTab(event)
Mixin.setMixin('editor', 'OnFormatSpaceToTab', OnFormatSpaceToTab)

def OnEditFormatAllTabToSpace(win, event):
    win.document.BeginUndoAction()
    for i in win.document.getSelectionLines():
        tabwidth = win.document.GetTabWidth()
        text = win.document.getLineText(i).expandtabs(tabwidth)
        win.document.replaceLineText(i, text)
    win.document.EndUndoAction()
    win.document.SetUseTabs(False)
    win.document.usetab = False
Mixin.setMixin('mainframe', 'OnEditFormatAllTabToSpace', OnEditFormatAllTabToSpace)

def OnFormatAllTabToSpace(win, event):
    win.mainframe.OnEditFormatAllTabToSpace(event)
Mixin.setMixin('editor', 'OnFormatAllTabToSpace', OnFormatAllTabToSpace)

def OnEditFormatTabToSpace(win, event):
    win.document.BeginUndoAction()
    for i in win.document.getSelectionLines():
        tabwidth = win.document.GetTabWidth()
        text = win.document.getLineText(i)
        k = 0
        for j, ch in enumerate(text):
            if ch == '\t':
                k += 1
            else:
                break
        text = ' '*k*tabwidth + text[j:]
        win.document.replaceLineText(i, text)
    win.document.EndUndoAction()
    win.document.SetUseTabs(False)
    win.document.usetab = False
Mixin.setMixin('mainframe', 'OnEditFormatTabToSpace', OnEditFormatTabToSpace)

def OnFormatTabToSpace(win, event):
    win.mainframe.OnEditFormatTabToSpace(event)
Mixin.setMixin('editor', 'OnFormatTabToSpace', OnFormatTabToSpace)

def mainframe_init(win):
    win.quote_user = False
    win.quote_index = 0
    win.quote_start = ''
    win.quote_end = ''
    win.quoteresfile = common.uni_work_file('resources/quotedialog.xrc')

    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_FORMAT_QUOTE, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_FORMAT_UNQUOTE, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'init', mainframe_init)

def OnEditFormatQuote(win, event):
    from modules import Resource
    import QuoteDialog
    from modules import i18n

    text = win.document.GetSelectedText()
    if len(text) > 0:
        filename = i18n.makefilename(win.quoteresfile, win.app.i18n.lang)
        dlg = Resource.loadfromresfile(filename, win, QuoteDialog.MyQuoteDialog, 'QuoteDialog', win)
        answer = dlg.ShowModal()
        dlg.Destroy()
        if answer == wx.ID_OK:
            if win.quote_user:
                start = win.quote_start
                end = win.quote_end
            else:
                start, end = QuoteDialog.quote_string[win.quote_index]
            win.document.BeginUndoAction()
            win.document.ReplaceSelection(start + text + end)
            win.document.EndUndoAction()
Mixin.setMixin('mainframe', 'OnEditFormatQuote', OnEditFormatQuote)

def OnEditFormatUnquote(win, event):
    from modules import Resource
    import QuoteDialog
    from modules import i18n

    text = win.document.GetSelectedText()
    if len(text) > 0:
        filename = i18n.makefilename(win.quoteresfile, win.app.i18n.lang)
        dlg = Resource.loadfromresfile(filename, win, QuoteDialog.MyQuoteDialog, 'QuoteDialog', win)
        answer = dlg.ShowModal()
        dlg.Destroy()
        if answer == wx.ID_OK:
            if win.quote_user:
                start = win.quote_start
                end = win.quote_end
            else:
                start, end = QuoteDialog.quote_string[win.quote_index]
            win.document.BeginUndoAction()
            win.document.ReplaceSelection(text[len(start):-len(end)])
            win.document.EndUndoAction()
Mixin.setMixin('mainframe', 'OnEditFormatUnquote', OnEditFormatUnquote)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDM_EDIT_FORMAT_QUOTE:
        event.Enable(win.document and win.document.GetSelectedText and len(win.document.GetSelectedText()) > 0)
    elif eid == win.IDM_EDIT_FORMAT_UNQUOTE:
        event.Enable(win.document and win.document.GetSelectedText and len(win.document.GetSelectedText()) > 0)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def on_editor_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDPM_FORMAT_QUOTE:
        event.Enable(len(win.GetSelectedText()) > 0)
    elif eid == win.IDPM_FORMAT_UNQUOTE:
        event.Enable(len(win.GetSelectedText()) > 0)
Mixin.setPlugin('editor', 'on_update_ui', on_editor_updateui)



#-----------------------  mCase.py ------------------

__doc__ = 'uppercase and lowercase processing'

import wx
from modules import Mixin

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_EDIT',
        [
            (260, 'IDM_EDIT_CASE', tr('Case'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDM_EDIT_CASE',
        [
            (100, 'IDM_EDIT_CASE_UPPER_CASE', tr('Uppercase') + '\tE=Ctrl+U', wx.ITEM_NORMAL, 'OnEditCaseUpperCase', tr('Changes the selected text to upper case.')),
            (200, 'IDM_EDIT_CASE_LOWER_CASE', tr('Lowercase') + '\tE=Ctrl+Shift+U', wx.ITEM_NORMAL, 'OnEditCaseLowerCase', tr('Changes the selected text to lower case.')),
            (300, 'IDM_EDIT_CASE_INVERT_CASE', tr('Invert Case'), wx.ITEM_NORMAL, 'OnEditCaseInvertCase', tr('Inverts the case of the selected text.')),
            (400, 'IDM_EDIT_CASE_CAPITALIZE', tr('Capitalize'), wx.ITEM_NORMAL, 'OnEditCaseCapitalize', tr('Capitalizes all words of the selected text.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_editor_menu(popmenulist):
    popmenulist.extend([ (None, #parent menu id
        [
            (230, 'IDPM_CASE', tr('Case'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDPM_CASE',
        [
            (100, 'IDPM_CASE_UPPER_CASE', tr('Uppercase') + '\tCtrl+U', wx.ITEM_NORMAL, 'OnCaseUpperCase', tr('Changes the selected text to upper case.')),
            (200, 'IDPM_CASE_LOWER_CASE', tr('Lowercase') + '\tCtrl+Shift+U', wx.ITEM_NORMAL, 'OnCaseLowerCase', tr('Changes the selected text to lower case.')),
            (300, 'IDPM_CASE_INVERT_CASE', tr('Invert Case'), wx.ITEM_NORMAL, 'OnCaseInvertCase', tr('Inverts the case of the selected text.')),
            (400, 'IDPM_CASE_CAPITALIZE', tr('Capitalize'), wx.ITEM_NORMAL, 'OnCaseCapitalize', tr('Capitalizes all words of the selected text.')),
        ]),
    ])
Mixin.setPlugin('editor', 'add_menu', add_editor_menu)

def OnEditCaseUpperCase(win, event):
    text = win.document.GetSelectedText()
    if len(text) > 0:
        text = text.upper()
        win.document.BeginUndoAction()
        win.document.ReplaceSelection(text)
        win.document.EndUndoAction()
Mixin.setMixin('mainframe', 'OnEditCaseUpperCase', OnEditCaseUpperCase)

def OnEditCaseLowerCase(win, event):
    text = win.document.GetSelectedText()
    if len(text) > 0:
        text = text.lower()
        win.document.BeginUndoAction()
        win.document.ReplaceSelection(text)
        win.document.EndUndoAction()
Mixin.setMixin('mainframe', 'OnEditCaseLowerCase', OnEditCaseLowerCase)

def OnEditCaseInvertCase(win, event):
    text = win.document.GetSelectedText()
    if len(text) > 0:
        text = text.swapcase()
        win.document.BeginUndoAction()
        win.document.ReplaceSelection(text)
        win.document.EndUndoAction()
Mixin.setMixin('mainframe', 'OnEditCaseInvertCase', OnEditCaseInvertCase)

def OnEditCaseCapitalize(win, event):
    text = win.document.GetSelectedText()
    if len(text) > 0:
        s=[]
        word = False
        for ch in text:
            if 'a' <= ch.lower() <= 'z':
                if word == False:
                    ch = ch.upper()
                    word = True
            else:
                if word == True:
                    word = False
            s.append(ch)
        text = ''.join(s)
        win.document.BeginUndoAction()
        win.document.ReplaceSelection(text)
        win.document.EndUndoAction()
Mixin.setMixin('mainframe', 'OnEditCaseCapitalize', OnEditCaseCapitalize)

def OnCaseUpperCase(win, event):
    event.SetId(win.mainframe.IDM_EDIT_CASE_UPPER_CASE)
    OnEditCaseUpperCase(win.mainframe, event)
Mixin.setMixin('editor', 'OnCaseUpperCase', OnCaseUpperCase)

def OnCaseLowerCase(win, event):
    event.SetId(win.mainframe.IDM_EDIT_CASE_LOWER_CASE)
    OnEditCaseLowerCase(win.mainframe, event)
Mixin.setMixin('editor', 'OnCaseLowerCase', OnCaseLowerCase)

def OnCaseInvertCase(win, event):
    event.SetId(win.mainframe.IDM_EDIT_CASE_INVERT_CASE)
    OnEditCaseInvertCase(win.mainframe, event)
Mixin.setMixin('editor', 'OnCaseInvertCase', OnCaseInvertCase)

def OnCaseCapitalize(win, event):
    event.SetId(win.mainframe.IDM_EDIT_CASE_CAPITALIZE)
    OnEditCaseCapitalize(win.mainframe, event)
Mixin.setMixin('editor', 'OnCaseCapitalize', OnCaseCapitalize)

def mainframe_init(win):
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_CASE_CAPITALIZE, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'init', mainframe_init)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDM_EDIT_CASE_CAPITALIZE:
        event.Enable(win.document.GetSelectedText and len(win.document.GetSelectedText()) > 0)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def editor_init(win):
    wx.EVT_UPDATE_UI(win, win.IDPM_CASE_CAPITALIZE, win.OnUpdateUI)
Mixin.setPlugin('editor', 'init', editor_init)

def on_editor_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDPM_CASE_CAPITALIZE:
        event.Enable(len(win.GetSelectedText()) > 0)
Mixin.setPlugin('editor', 'on_update_ui', on_editor_updateui)



#-----------------------  mDocument.py ------------------

import wx
import StringIO
from modules import Mixin

def add_mainframe_menu(menulist):
    menulist.extend([ (None,
        [
            (500, 'IDM_DOCUMENT', tr('Document'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDM_DOCUMENT', #parent menu id
        [
            (100, 'IDM_DOCUMENT_WORDWRAP', tr('Word Wrap'), wx.ITEM_NORMAL, 'OnDocumentWordWrap', tr('Toggles the word wrap feature of the current document.')),
            (110, 'IDM_DOCUMENT_AUTOINDENT', tr('Autoindent'), wx.ITEM_CHECK, 'OnDocumentAutoIndent', tr('Toggles the autoindent feature of the current document.')),
            (115, 'IDM_DOCUMENT_TABINDENT', tr('Switch To Space Indent'), wx.ITEM_NORMAL, 'OnDocumentTabIndent', tr('Uses tab as indent char or uses space as indent char.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_mainframe_menu_image_list(imagelist):
    imagelist.update({
        'IDM_DOCUMENT_WORDWRAP':'images/wrap.gif',
    })
Mixin.setPlugin('mainframe', 'add_menu_image_list', add_mainframe_menu_image_list)

def pref_init(pref):
    pref.autoindent = True
    pref.usetabs = False
    pref.wordwrap = False
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('Document')+'/'+tr('Edit'), 100, 'check', 'autoindent', tr('Autoindent'), None),
        (tr('Document')+'/'+tr('Edit'), 110, 'check', 'usetabs', tr('Use tabs'), None),
        (tr('Document')+'/'+tr('Edit'), 120, 'check', 'wordwrap', tr('Automatically word wrap'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def savepreference(mainframe, pref):
    for document in mainframe.editctrl.getDocuments():
        if mainframe.pref.wordwrap:
            document.SetWrapMode(wx.stc.STC_WRAP_WORD)
        else:
            document.SetWrapMode(wx.stc.STC_WRAP_NONE)
Mixin.setPlugin('prefdialog', 'savepreference', savepreference)

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (805, 'wrap'),
    ])

    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'wrap':(wx.ITEM_CHECK, 'IDM_DOCUMENT_WORDWRAP', 'images/wrap.gif', tr('Toggle Wrap Mode'), tr('Toggles the word wrap feature of the current document.'), 'OnDocumentWordWrap'),
    })
Mixin.setPlugin('mainframe', 'add_tool_list', add_tool_list)

def editor_init(win):
    win.SetUseTabs(win.mainframe.pref.usetabs)
    win.usetab = win.mainframe.pref.usetabs
    if win.pref.wordwrap:
        win.SetWrapMode(wx.stc.STC_WRAP_WORD)
    else:
        win.SetWrapMode(wx.stc.STC_WRAP_NONE)
Mixin.setPlugin('editor', 'init', editor_init)

def OnKeyDown(win, event):
    if event.GetKeyCode() == wx.WXK_RETURN:
        if win.GetSelectedText():
            win.CmdKeyExecute(wx.stc.STC_CMD_NEWLINE)
            return True
        if win.pref.autoindent:
            line = win.GetCurrentLine()
            text = win.GetTextRange(win.PositionFromLine(line), win.GetCurrentPos())
            if text.strip() == '':
                win.AddText(win.getEOLChar() + text)
                win.EnsureCaretVisible()
                return True

            n = win.GetLineIndentation(line) / win.GetTabWidth()
            win.AddText(win.getEOLChar() + win.getIndentChar() * n)
            win.EnsureCaretVisible()
            return True
        else:
            win.AddText(win.getEOLChar())
            win.EnsureCaretVisible()
            return True
Mixin.setPlugin('editor', 'on_key_down', OnKeyDown, Mixin.LOW)

def OnDocumentWordWrap(win, event):
    mode = win.document.GetWrapMode()
    if mode == wx.stc.STC_WRAP_NONE:
        win.document.SetWrapMode(wx.stc.STC_WRAP_WORD)
    else:
        win.document.SetWrapMode(wx.stc.STC_WRAP_NONE)
Mixin.setMixin('mainframe', 'OnDocumentWordWrap', OnDocumentWordWrap)

def OnDocumentAutoIndent(win, event):
    win.pref.autoindent = not win.pref.autoindent
    win.pref.save()
Mixin.setMixin('mainframe', 'OnDocumentAutoIndent', OnDocumentAutoIndent)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_DOCUMENT_WORDWRAP, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_DOCUMENT_AUTOINDENT, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_DOCUMENT_TABINDENT, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if hasattr(win, 'document') and win.document:
        if eid == win.IDM_DOCUMENT_WORDWRAP:
            if win.document.GetWrapMode:
                event.Enable(True)
                mode = win.document.GetWrapMode()
                if mode == wx.stc.STC_WRAP_NONE:
                    event.Check(False)
                else:
                    event.Check(True)
            else:
                event.Enable(False)
        elif eid == win.IDM_DOCUMENT_AUTOINDENT:
            if win.document.canedit:
                event.Enable(True)
                event.Check(win.pref.autoindent)
            else:
                event.Enable(False)
        elif eid == win.IDM_DOCUMENT_TABINDENT:
            if win.document.canedit:
                event.Enable(True)
                from modules import makemenu
                menu = makemenu.findmenu(win.menuitems, 'IDM_DOCUMENT_TABINDENT')
                if win.document.usetab:
                    menu.SetText(tr('Switch To Space Indent'))
                else:
                    menu.SetText(tr('Switch To Tab Indent'))
            else:
                event.Enable(False)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def openfiletext(win, stext):
    pos = 0
    text = stext[0]

    buf = StringIO.StringIO(text)
    while 1:
        line = buf.readline()
        if line:
            if line[0] == ' ':
                win.SetUseTabs(False)
                win.usetab = False
                return
            elif line[0] == '\t':
                win.SetUseTabs(True)
                win.usetab = True
                return
        else:
            break
    win.SetUseTabs(win.mainframe.pref.usetabs)
    win.usetab = win.mainframe.pref.usetabs
Mixin.setPlugin('editor', 'openfiletext', openfiletext)

def OnDocumentTabIndent(win, event):
    win.document.usetab = not win.document.usetab
    win.document.SetUseTabs(win.document.usetab)
Mixin.setMixin('mainframe', 'OnDocumentTabIndent', OnDocumentTabIndent)



#-----------------------  mUnicode.py ------------------

__doc__ = 'encoding selection and unicode support'

import re
import StringIO
from modules import Mixin
from MyUnicodeException import MyUnicodeException
from modules.Debug import error
from modules import common

def pref_init(pref):
    pref.auto_detect_utf8 = True
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('Document')+'/'+tr('Edit'), 130, 'check', 'auto_detect_utf8', tr('Autodetect UTF-8 encoding'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def editor_init(win):
    win.locale = win.defaultlocale
Mixin.setPlugin('editor', 'init', editor_init)

def openfileencoding(win, filename, stext, encoding):
    text = stext[0]
    begin = 0
    if text.startswith('\xEF\xBB\xBF'):
        begin = 3
        encoding = 'UTF-8'
    elif text.startswith('\xFF\xFE'):
        begin = 2
        encoding = 'UTF-16'
    if not encoding:
        if filename:
            if win.mainframe.pref.auto_detect_utf8:
                encoding = 'UTF-8'
            else:
                encoding = win.defaultlocale
        else:
            if not encoding and hasattr(win.pref, 'custom_encoding'):
                encoding = win.pref.custom_encoding
            if not encoding and hasattr(win.pref, 'default_encoding'):
                encoding = win.pref.default_encoding
            if not encoding:
                encoding = common.defaultencoding

    try:
        s = unicode(text[begin:], encoding)
        win.locale = encoding
    except:
        if win.mainframe.pref.auto_detect_utf8 and encoding == 'UTF-8':
            encoding = win.defaultlocale
            try:
                s = unicode(text[begin:], encoding, 'replace')
                win.locale = encoding
            except:
                error.traceback()
                raise MyUnicodeException(win, tr("Can't convert file encoding [%s] to unicode!\nThe file can't be opened!") % encoding, tr("Unicode Error"))
        else:
            error.traceback()
            raise MyUnicodeException(win, tr("Can't convert file encoding [%s] to unicode!\nThe file can't be opened!") % encoding, tr("Unicode Error"))
    stext[0] = s
Mixin.setPlugin('editor', 'openfileencoding', openfileencoding)

def savefileencoding(win, stext, encoding):
    text = stext[0]

    if not encoding:
        encoding = win.locale

    if win.languagename == 'python':
        r = re.compile(r'\s*coding\s*[=:]\s*([-\w.]+)')

        buf = StringIO.StringIO(text)
        while 1:
            line = buf.readline()
            if not line: break
            line = line.rstrip()
            if line.startswith('#!'):
                continue
            if line.startswith('#'):
                b = r.search(line[1:])
                if b:
                    encoding = b.groups()[0]
                    break
            if not line:
                continue
            else:
                break

    oldencoding = win.locale
    if encoding:
        try:
            s = text.encode(encoding)
            win.locale = encoding
        except:
            error.traceback()
            try:
                s = text.encode(encoding, 'replace')
            except:
                raise MyUnicodeException(win, tr("Can't convert file to [%s] encoding!\nThe file can't be saved!") % encoding,
                    tr("Unicode Error"))
    else:
        s = text
    stext[0] = s
Mixin.setPlugin('editor', 'savefileencoding', savefileencoding)



#-----------------------  mBookmark.py ------------------

import wx
from modules import Mixin

def editor_init(win):
    win.SetMarginWidth(0, 20)
    win.SetMarginType(0, wx.stc.STC_MARGIN_SYMBOL)

    win.SetMarginMask(0, ~wx.stc.STC_MASK_FOLDERS)
    win.MarkerDefine(0, wx.stc.STC_MARK_SHORTARROW, "blue", "blue")
Mixin.setPlugin('editor', 'init', editor_init)

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_SEARCH',
        [
            (180, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (190, 'IDM_SEARCH_BOOKMARK_TOGGLE', tr('Toggle Marker') + '\tE=F9', wx.ITEM_NORMAL, 'OnSearchBookmarkToggle', tr('Set and clear marker at current line.')),
            (200, 'IDM_SEARCH_BOOKMARK_CLEARALL', tr('Clear All Markers') + '\tE=Ctrl+Shift+F9', wx.ITEM_NORMAL, 'OnSearchBookmarkClearAll', tr('Clears all markers from the current document.')),
            (210, 'IDM_SEARCH_BOOKMARK_PREVIOUS', tr('Previous Marker') + '\tE=Shift+F8', wx.ITEM_NORMAL, 'OnSearchBookmarkPrevious', tr('Goes to previous marker position.')),
            (220, 'IDM_SEARCH_BOOKMARK_NEXT', tr('Next Marker') + '\tE=F8', wx.ITEM_NORMAL, 'OnSearchBookmarkNext', tr('Goes to next marker position.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def OnSearchBookmarkToggle(win, event):
    line = win.document.GetCurrentLine()
    marker = win.document.MarkerGet(line)
    if marker & 1:
        win.document.MarkerDelete(line, 0)
    else:
        win.document.MarkerAdd(line, 0)
Mixin.setMixin('mainframe', 'OnSearchBookmarkToggle', OnSearchBookmarkToggle)

def OnSearchBookmarkClearAll(win, event):
    win.document.MarkerDeleteAll(0)
Mixin.setMixin('mainframe', 'OnSearchBookmarkClearAll', OnSearchBookmarkClearAll)

def OnSearchBookmarkNext(win, event):
    line = win.document.GetCurrentLine()
    marker = win.document.MarkerGet(line)
    if marker & 1:
        line += 1
    f = win.document.MarkerNext(line, 1)
    if f > -1:
        win.document.goto(f + 1)
    else:
        f = win.document.MarkerNext(0, 1)
        if f > -1:
            win.document.goto(f + 1)
Mixin.setMixin('mainframe', 'OnSearchBookmarkNext', OnSearchBookmarkNext)

def OnSearchBookmarkPrevious(win, event):
    line = win.document.GetCurrentLine()
    marker = win.document.MarkerGet(line)
    if marker & 1:
        line -= 1
    f = win.document.MarkerPrevious(line, 1)
    if f > -1:
        win.document.goto(f + 1)
    else:
        f = win.document.MarkerPrevious(win.document.GetLineCount()-1, 1)
        if f > -1:
            win.document.goto(f + 1)
Mixin.setMixin('mainframe', 'OnSearchBookmarkPrevious', OnSearchBookmarkPrevious)



#-----------------------  mFolder.py ------------------

import wx
import wx.stc
from modules import Mixin

def pref_init(pref):
    pref.use_folder = True
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('Document'), 130, 'check', 'use_folder', tr('Show code folding margin'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def savepreference(mainframe, pref):
    for document in mainframe.editctrl.getDocuments():
        if document.enablefolder:
            if pref.use_folder:
                document.SetMarginWidth(2, 16)
            else:
                document.SetMarginWidth(2, 0)
Mixin.setPlugin('prefdialog', 'savepreference', savepreference)

def editor_init(win):
    win.enablefolder = False
    win.SetMarginType(2, wx.stc.STC_MARGIN_SYMBOL) #margin 2 for symbols
    win.SetMarginMask(2, wx.stc.STC_MASK_FOLDERS)  #set up mask for folding symbols
    win.SetMarginSensitive(2, True)           #this one needs to be mouse-aware


    #define folding markers
    win.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEREND,     wx.stc.STC_MARK_BOXPLUSCONNECTED,  "white", "black")
    win.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEROPENMID, wx.stc.STC_MARK_BOXMINUSCONNECTED, "white", "black")
    win.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERMIDTAIL, wx.stc.STC_MARK_TCORNER,  "white", "black")
    win.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERTAIL,    wx.stc.STC_MARK_LCORNER,  "white", "black")
    win.MarkerDefine(wx.stc.STC_MARKNUM_FOLDERSUB,     wx.stc.STC_MARK_VLINE,    "white", "black")
    win.MarkerDefine(wx.stc.STC_MARKNUM_FOLDER,        wx.stc.STC_MARK_BOXPLUS,  "white", "black")
    win.MarkerDefine(wx.stc.STC_MARKNUM_FOLDEROPEN,    wx.stc.STC_MARK_BOXMINUS, "white", "black")
Mixin.setPlugin('editor', 'init', editor_init)

def colourize(win):
    if win.enablefolder:
        if hasattr(win, 'pref'):
            if win.pref.use_folder:
                win.SetMarginWidth(2, 16)
                return
    win.SetMarginWidth(2, 0)    #used as folder

Mixin.setPlugin('lexerbase', 'colourize', colourize)

def OnMarginClick(win, event):
    # fold and unfold as needed
    if event.GetMargin() == 2:
        if event.GetControl() and event.GetShift():
            FoldAll(win)
        else:
            lineClicked = win.LineFromPosition(event.GetPosition())
            if win.GetFoldLevel(lineClicked) & wx.stc.STC_FOLDLEVELHEADERFLAG:
                if event.GetShift():
                    win.SetFoldExpanded(lineClicked, True)
                    Expand(win, lineClicked, True, True, 1)
                elif event.GetControl():
                    if win.GetFoldExpanded(lineClicked):
                        win.SetFoldExpanded(lineClicked, False)
                        Expand(win, lineClicked, False, True, 0)
                    else:
                        win.SetFoldExpanded(lineClicked, True)
                        Expand(win, lineClicked, True, True, 100)
                else:
                    win.ToggleFold(lineClicked)
Mixin.setPlugin('editor', 'on_margin_click', OnMarginClick)

def FoldAll(win):
    lineCount = win.GetLineCount()
    expanding = True

    # find out if we are folding or unfolding
    for lineNum in range(lineCount):
        if win.GetFoldLevel(lineNum) & wx.stc.STC_FOLDLEVELHEADERFLAG:
            expanding = not win.GetFoldExpanded(lineNum)
            break;

    lineNum = 0
    while lineNum < lineCount:
        level = win.GetFoldLevel(lineNum)
        if level & wx.stc.STC_FOLDLEVELHEADERFLAG and \
           (level & wx.stc.STC_FOLDLEVELNUMBERMASK) == wx.stc.STC_FOLDLEVELBASE:

            if expanding:
                win.SetFoldExpanded(lineNum, True)
                lineNum = Expand(win, lineNum, True)
                lineNum = lineNum - 1
            else:
                lastChild = win.GetLastChild(lineNum, -1)
                win.SetFoldExpanded(lineNum, False)
                if lastChild > lineNum:
                    win.HideLines(lineNum+1, lastChild)

        lineNum = lineNum + 1

def Expand(win, line, doExpand, force=False, visLevels=0, level=-1):
    lastChild = win.GetLastChild(line, level)
    line = line + 1
    while line <= lastChild:
        if force:
            if visLevels > 0:
                win.ShowLines(line, line)
            else:
                win.HideLines(line, line)
        else:
            if doExpand:
                win.ShowLines(line, line)

        if level == -1:
            level = win.GetFoldLevel(line)

        if level & wx.stc.STC_FOLDLEVELHEADERFLAG:
            if force:
                if visLevels > 1:
                    win.SetFoldExpanded(line, True)
                else:
                    win.SetFoldExpanded(line, False)
                line = Expand(win, line, doExpand, force, visLevels-1)

            else:
                if doExpand and win.GetFoldExpanded(line):
                    line = Expand(win, line, True, force, visLevels-1)
                else:
                    line = Expand(win, line, False, force, visLevels-1)
        else:
            line = line + 1;

    return line



#-----------------------  mCheckBrace.py ------------------

from modules import Mixin

def on_editor_updateui(win, event):
    # check for matching braces
    braceAtCaret = -1
    braceOpposite = -1
    charBefore = None
    caretPos = win.GetCurrentPos()
    if caretPos > 0:
        charBefore = win.GetCharAt(caretPos - 1)
        styleBefore = win.GetStyleAt(caretPos - 1)

    # check before
    if charBefore and chr(charBefore) in "[]{}()": # and styleBefore == wx.stc.STC_P_OPERATOR:
        braceAtCaret = caretPos - 1

    # check after
    if braceAtCaret < 0:
        charAfter = win.GetCharAt(caretPos)
        styleAfter = win.GetStyleAt(caretPos)
        if charAfter and chr(charAfter) in "[]{}()": # and styleAfter == wx.stc.STC_P_OPERATOR:
            braceAtCaret = caretPos

    if braceAtCaret >= 0:
        braceOpposite = win.BraceMatch(braceAtCaret)

    if braceAtCaret != -1  and braceOpposite == -1:
        win.BraceBadLight(braceAtCaret)
    else:
        win.BraceHighlight(braceAtCaret, braceOpposite)
Mixin.setPlugin('editor', 'on_update_ui', on_editor_updateui)



#-----------------------  mZoom.py ------------------

import wx
from modules import Mixin
from modules import common

def add_mainframe_menu(menulist):
    menulist.extend([
        ('IDM_VIEW', #parent menu id
        [
            (170, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (185, 'IDM_VIEW_ZOOM_IN', tr('Zoom In'), wx.ITEM_NORMAL, 'OnViewZoomIn', tr('Increases the font size of the document.')),
            (190, 'IDM_VIEW_ZOOM_OUT', tr('Zoom Out'), wx.ITEM_NORMAL, 'OnViewZoomOut', tr('Decreases the font size of the document.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_mainframe_menu_image_list(imagelist):
    imagelist.update({
        'IDM_VIEW_ZOOM_IN':'images/large.gif',
        'IDM_VIEW_ZOOM_OUT':'images/small.gif',
    })
Mixin.setPlugin('mainframe', 'add_menu_image_list', add_mainframe_menu_image_list)

def OnViewZoomIn(win, event):
    win.document.ZoomIn()
Mixin.setMixin('mainframe', 'OnViewZoomIn', OnViewZoomIn)

def OnViewZoomOut(win, event):
    win.document.ZoomOut()
Mixin.setMixin('mainframe', 'OnViewZoomOut', OnViewZoomOut)




#-----------------------  mSession.py ------------------

import os
import wx
from modules import Mixin
from modules.Debug import error
from modules import common
from modules import Globals
from modules import makemenu

def pref_init(pref):
    pref.load_session = True
    pref.sessions = []
    pref.last_tab_index = -1
    pref.screen_lines = 0
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('Document') + '/' + tr('Startup'), 150, 'check', 'load_session', tr('Load files of last session at startup'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def save_session(win):
    if Globals.starting: return
    win.pref.sessions, win.pref.last_tab_index = [], -1
    if win.pref.load_session:
        win.pref.sessions, win.pref.last_tab_index = gather_status()
    win.pref.save()

def afterclosewindow(win):
    save_session(win)
Mixin.setPlugin('mainframe', 'afterclosewindow', afterclosewindow)

def afterclosefile(win, *args):
    save_session(win)
Mixin.setPlugin('editctrl', 'afterclosefile', afterclosefile)

def afternewfile(win, *args):
    save_session(win.mainframe)
Mixin.setPlugin('editctrl', 'afternewfile', afternewfile)

def gather_status():
    sessions = []
    last_tab_index = -1
    win = Globals.mainframe
    for document in win.editctrl.getDocuments():
        if document.documenttype != 'texteditor':
            continue
        if document.filename and document.savesession:
            sessions.append(document.get_full_state())
    last_tab_index = win.editctrl.GetSelection()
    return sessions, last_tab_index

def openPage(win):
    n = 0
    if win.mainframe.pref.load_session and not win.mainframe.app.skipsessionfile:
        for v in win.mainframe.pref.sessions:
            if len(v) == 4:
                filename, row, col, bookmarks = v
                state = row
            else:
                filename, state, bookmarks = v
            document = win.new(filename, delay=True)
            if document:
                n += 1
        index = win.mainframe.pref.last_tab_index
        if index < 0:
            index = 0
        elif index >= len(win.getDocuments()):
            index = len(win.getDocuments()) -1
        if index > -1 and index < len(win.getDocuments()):
            wx.CallAfter(win.switch, win.getDoc(index), delay=False)
    return n > 0
Mixin.setPlugin('editctrl', 'openpage', openPage)

def pref_init(pref):
    pref.recent_sessions = []
    pref.last_session_dir = ''
Mixin.setPlugin('preference', 'init', pref_init)

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_FILE', #parent menu id
        [
            (202, 'IDM_FILE_SESSION_OPEN', tr('Open Session...'), wx.ITEM_NORMAL, 'OnFileSessionOpen', tr('Opens an existing session file.')),
            (203, 'IDM_FILE_SESSION_SAVE', tr('Save Session...'), wx.ITEM_NORMAL, 'OnFileSessionSave', tr('Saves opened documents to a session file.')),
            (204, 'IDM_FILE_SESSION_RECENT', tr('Open Recent Session'), wx.ITEM_NORMAL, '', ''),
            (205, '', '-', wx.ITEM_SEPARATOR, None, ''),
        ]),
        ('IDM_FILE_SESSION_RECENT',
        [
            (100, 'IDM_FILE_SESSION_RECENT_ITEMS', tr('(Empty)'), wx.ITEM_NORMAL, '', tr('There is no recent session.')),
        ]),

    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

from modules.EasyGuider import obj2ini

def OnFileSessionOpen(win, event=None, filename=None):
    if not filename:
        dlg = wx.FileDialog(win, tr("Choose A Session File"), win.pref.last_session_dir, "", 'UliPad Session File (*.ses)|*.ses', wx.OPEN)
        filename = None
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetPath()
        dlg.Destroy()
    if filename:
        try:
            get_recent_session_file(win, filename)
            d = obj2ini.load(filename)
            sessions, last_file = d['sessions'], d['last_file']
            win.pref.sessions.extend(sessions)
            for v in sessions:
                win.editctrl.new(v[0], delay=True)
            for document in win.editctrl.getDocuments():
                if document.documenttype == 'texteditor' and document.filename == last_file:
                    wx.CallAfter(win.editctrl.switch, document, delay=False)
        except:
            error.traceback()
            common.warn(tr('There was something wrong with loading the session file.'))
Mixin.setMixin('mainframe', 'OnFileSessionOpen', OnFileSessionOpen)

def OnFileSessionSave(win, event=None):
    dlg = wx.FileDialog(win, tr("Save To Session File"), win.pref.last_session_dir, "", 'UliPad Session File (*.ses)|*.ses', wx.SAVE|wx.OVERWRITE_PROMPT)
    filename = None
    if dlg.ShowModal() == wx.ID_OK:
        filename = dlg.GetPath()
    dlg.Destroy()
    if filename:
        try:
            get_recent_session_file(win, filename)
            sessions, last_index = gather_status()
            last_file = win.editctrl.getDoc(last_index).filename
            obj2ini.dump({'sessions':sessions, 'last_file':last_file}, filename)
        except:
            error.traceback()
            common.warn(tr('There was something wrong with saving the session file.'))
Mixin.setMixin('mainframe', 'OnFileSessionSave', OnFileSessionSave)

def afterinit(win):
    win.recentsession_ids = [win.IDM_FILE_SESSION_RECENT_ITEMS]
    create_recent_session_menu(win)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def create_recent_session_menu(win):
    menu = makemenu.findmenu(win.menuitems, 'IDM_FILE_SESSION_RECENT')

    for id in win.recentsession_ids:
        menu.Delete(id)

    win.recentsession_ids = []
    if len(win.pref.recent_sessions) == 0:
        id = win.IDM_FILE_SESSION_RECENT_ITEMS
        menu.Append(id, tr('(Empty)'))
        menu.Enable(id, False)
        win.recentsession_ids = [id]
    else:
        for i, filename in enumerate(win.pref.recent_sessions):
            id = wx.NewId()
            win.recentsession_ids.append(id)
            menu.Append(id, "%d %s" % (i+1, filename))
            wx.EVT_MENU(win, id, win.OnOpenRecentSession)

def OnOpenRecentSession(win, event):
    eid = event.GetId()
    index = win.recentsession_ids.index(eid)
    filename = win.pref.recent_sessions[index]
    try:
        f = file(filename)
        f.close()
    except:
        common.showerror(win, tr("Can't open the file %s.") % filename)
        del win.pref.recent_sessions[index]
        win.pref.save()
        create_recent_session_menu(win)
        return
    win.OnFileSessionOpen(filename=filename)
Mixin.setMixin('mainframe', 'OnOpenRecentSession', OnOpenRecentSession)

def get_recent_session_file(win, filename):
    if filename:
        #deal recent files
        if filename in win.pref.recent_sessions:
            win.pref.recent_sessions.remove(filename)
        win.pref.recent_sessions.insert(0, filename)
        win.pref.recent_sessions = win.pref.recent_sessions[:10]
        win.pref.last_session_dir = os.path.dirname(filename)

        #save pref
        win.pref.save()

        #create menus
        create_recent_session_menu(win)



#-----------------------  mLastStatus.py ------------------

__doc__ = "Saveing last window status, including position, size, and Maximized or Iconized."

import wx
from modules import Mixin

def pref_init(pref):
    pref.save_current_status = True
    if wx.Platform == '__WXMAC__':
        pref.status_position = wx.DefaultPosition
    else:
        pref.status_position = (0, 0)
    pref.status_size = (600, 400)
    pref.status = 3     #1 Iconized 2 Maximized 3 normal
    pref.status_panels = {'left':20, 'right':10, 'bottom':20}
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('General'), 110, 'check', 'save_current_status', tr('Save current status at application exit'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def afterclosewindow(win):
    if win.pref.save_current_status:
        if win.IsMaximized():
            win.pref.status = 2
        else:
            win.pref.status = 3
            saveWindowPosition(win)
        win.pref.status_panels = {'left':win.panel.leftsize, 'right':win.panel.rightsize, 'bottom':win.panel.bottomsize}
        win.pref.save()
Mixin.setPlugin('mainframe', 'afterclosewindow', afterclosewindow)

def beforeinit(win):
    if win.pref.save_current_status:
        x, y = win.pref.status_position
        w, h = win.pref.status_size
        win.SetDimensions(x, y, w, h)
        if win.pref.status == 2:
            wx.CallAfter(win.Maximize)
Mixin.setPlugin('mainframe', 'beforeinit', beforeinit)

def mainframe_init(win):
    wx.EVT_MAXIMIZE(win, win.OnMaximize)
    wx.EVT_ICONIZE(win, win.OnIconize)
Mixin.setPlugin('mainframe', 'init', mainframe_init)

def OnMaximize(win, event):
    saveWindowPosition(win)
    event.Skip()
Mixin.setMixin('mainframe', 'OnMaximize', OnMaximize)

def OnIconize(win, event):
    saveWindowPosition(win)
    event.Skip()
Mixin.setMixin('mainframe', 'OnIconize', OnIconize)

def saveWindowPosition(win):
    if win.IsIconized() == False and win.IsMaximized() == False:
        win.pref.status_position = win.GetPositionTuple()
        win.pref.status_size = win.GetSizeTuple()
        win.pref.save()

def mainframe_afterinit(win):
    if win.pref.save_current_status:
        p = win.pref.status_panels
        panel = win.panel
        panel.leftsize, panel.rightsize, panel.bottomsize = p['left'], p['right'], p['bottom']
Mixin.setPlugin('mainframe', 'afterinit', mainframe_afterinit)



#-----------------------  mDuplicate.py ------------------

__doc__ = 'Duplicate char, word, line'

from modules import Mixin
import wx
from modules import Calltip

CALLTIP_DUPLICATE = 1

def pref_init(pref):
    pref.duplicate_extend_mode = False
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('Document')+'/'+tr('Edit'), 140, 'check', 'duplicate_extend_mode', tr("Use duplication extend mode and treat a dot as a normal character"), None)
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def add_editor_menu(popmenulist):
    popmenulist.extend([ (None,
        [
            (190, 'IDPM_DUPLICATE', tr('Duplication'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDPM_DUPLICATE', #parent menu id
        [
            (90, 'IDPM_DUPLICATE_MODE', tr('Duplicate Extend Mode') + '\tF10', wx.ITEM_CHECK, 'OnDuplicateMode', tr('Toggle duplication extend mode.')),
            (100, 'IDPM_DUPLICATE_CURRENT_LINE', tr('Duplicate Current Line') + '\tCtrl+J', wx.ITEM_NORMAL, 'OnDuplicateCurrentLine', tr('Duplicates current line.')),
            (400, 'IDPM_DUPLICATE_WORD', tr('Duplicate Previous Word') + '\tCtrl+P', wx.ITEM_NORMAL, 'OnDuplicateWord', tr('Copies a word from previous matched line.')),
            (500, 'IDPM_DUPLICATE_NEXT_WORD', tr('Duplicate Next Word') + '\tCtrl+Shift+P', wx.ITEM_NORMAL, 'OnDuplicateNextWord', tr('Copies a word from next matched line.')),
            (600, 'IDPM_DUPLICATE_LINE', tr('Duplicate Previous Line') + '\tCtrl+L', wx.ITEM_NORMAL, 'OnDuplicateLine', tr('Copies a line from next matched line.')),
            (700, 'IDPM_DUPLICATE_NEXT_LINE', tr('Duplicate Next Line') + '\tCtrl+Shift+L', wx.ITEM_NORMAL, 'OnDuplicateNextLine', tr('Copies a line from next matched line.')),
        ]),
    ])
Mixin.setPlugin('editor', 'add_menu', add_editor_menu)

def editor_init(win):
    win.calltip = Calltip.MyCallTip(win)
    win.calltip_type = -1

    wx.EVT_UPDATE_UI(win, win.IDPM_DUPLICATE_MODE, win.OnUpdateUI)
Mixin.setPlugin('editor', 'init', editor_init)

def getWordChars(win):
    wordchars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
    if win.pref.duplicate_extend_mode:
        return wordchars + '.'
    else:
        return wordchars
Mixin.setMixin('mainframe', 'getWordChars', getWordChars)

def OnDuplicateCurrentLine(win, event):
    win.mainframe.OnEditDuplicateCurrentLine(event)
Mixin.setMixin('editor', 'OnDuplicateCurrentLine', OnDuplicateCurrentLine)


def OnDuplicateWord(win, event):
    win.mainframe.OnEditDuplicateWord(event)
Mixin.setMixin('editor', 'OnDuplicateWord', OnDuplicateWord)

def OnDuplicateNextWord(win, event):
    win.mainframe.OnEditDuplicateNextWord(event)
Mixin.setMixin('editor', 'OnDuplicateNextWord', OnDuplicateNextWord)

def OnDuplicateLine(win, event):
    win.mainframe.OnEditDuplicateLine(event)
Mixin.setMixin('editor', 'OnDuplicateLine', OnDuplicateLine)

def OnDuplicateNextLine(win, event):
    win.mainframe.OnEditDuplicateNextLine(event)
Mixin.setMixin('editor', 'OnDuplicateNextLine', OnDuplicateNextLine)

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_EDIT', #parent menu id
        [
            (230, 'IDM_EDIT_DUPLICATE', tr('Duplication'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDM_EDIT_DUPLICATE', #parent menu id
        [
            (90, 'IDM_EDIT_DUPLICATE_MODE', tr('Duplicate Extend Mode') + '\tF10', wx.ITEM_CHECK, 'OnEditDuplicateMode', tr('Toggle duplication extend mode.')),
            (100, 'IDM_EDIT_DUPLICATE_CURRENT_LINE', tr('Duplicate Current Line') + '\tE=Ctrl+J', wx.ITEM_NORMAL, 'OnEditDuplicateCurrentLine', tr('Duplicates current line.')),
            (400, 'IDM_EDIT_DUPLICATE_WORD', tr('Duplicate Previous Word') + '\tE=Ctrl+P', wx.ITEM_NORMAL, 'OnEditDuplicateWord', tr('Copies a word from previous matched line.')),
            (500, 'IDM_EDIT_DUPLICATE_NEXT_WORD', tr('Duplicate Next Word') + '\tE=Ctrl+Shift+P', wx.ITEM_NORMAL, 'OnEditDuplicateNextWord', tr('Copies a word from next matched line.')),
            (600, 'IDM_EDIT_DUPLICATE_LINE', tr('Duplicate Previous Line') + '\tE=Ctrl+L', wx.ITEM_NORMAL, 'OnEditDuplicateLine', tr('Copies a line from next matched line.')),
            (700, 'IDM_EDIT_DUPLICATE_NEXT_LINE', tr('Duplicate Next Line') + '\tE=Ctrl+Shift+L', wx.ITEM_NORMAL, 'OnEditDuplicateNextLine', tr('Copies a line from next matched line.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def on_editor_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDPM_DUPLICATE_MODE:
        event.Check(win.pref.duplicate_extend_mode)
Mixin.setPlugin('editor', 'on_update_ui', on_editor_updateui)

def mainframe_init(win):
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_DUPLICATE_MODE, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'init', mainframe_init)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDM_EDIT_DUPLICATE_MODE:
        event.Check(win.pref.duplicate_extend_mode)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def OnDuplicateMode(win, event):
    win.mainframe.OnEditDuplicateMode(event)
Mixin.setMixin('editor', 'OnDuplicateMode', OnDuplicateMode)

def OnEditDuplicateMode(win, event):
    win.pref.duplicate_extend_mode = not win.pref.duplicate_extend_mode
    win.pref.save()
Mixin.setMixin('mainframe', 'OnEditDuplicateMode', OnEditDuplicateMode)

def OnEditDuplicateCurrentLine(win, event):
    line = win.document.GetCurrentLine()
    text = win.document.getLineText(line)
    pos = win.document.GetCurrentPos() - win.document.PositionFromLine(line)
    start = win.document.GetLineEndPosition(line)
    win.document.InsertText(start, win.document.getEOLChar() + text)
    win.document.GotoPos(win.document.PositionFromLine(line + 1) + pos)
Mixin.setMixin('mainframe', 'OnEditDuplicateCurrentLine', OnEditDuplicateCurrentLine)


def findPreviousWordPos(text, pos, word, word_chars):
    while pos >= 0:
        if pos == 0:
            ch = ''
        else:
            ch = text[pos - 1]
        if (not ch) or (not (ch in word_chars)):
            if text.startswith(word, pos):
                return pos
        pos -= 1
    return -1

def findLeftWord(text, pos, word_chars):
    """if just left char is '.' or '(', etc. then continue to search, other case stop searching"""
    edge_chars = '.[('
    chars = []
    leftchar = text[pos - 1]
    if leftchar in edge_chars:
        chars.append(leftchar)
        pos -= 1

    while pos > 0:
        leftchar = text[pos - 1]
        if leftchar in word_chars:
            pos -= 1
            chars.append(leftchar)
        else:
            break
    chars.reverse()
    return ''.join(chars)


def findNextWordPos(text, pos, word, word_chars):
    length = len(text)
    while pos < length:
        if pos - 1 == 0:
            ch = ''
        else:
            ch = text[pos - 1]
        if (not ch) or (not (ch in word_chars)):
            if text.startswith(word, pos):
                return pos
        pos += 1
    return -1

def OnKeyDown(win, event):
    if win.findflag:
        key = event.GetKeyCode()
        if key in (wx.WXK_RETURN, wx.WXK_SPACE):
            win.calltip.cancel()
            win.findflag = 0
            if win.calltip_type == CALLTIP_DUPLICATE:#duplicate mode
                win.AddText(win.duplicate_match_text)
        elif key == wx.WXK_ESCAPE:
            win.calltip.cancel()
            win.findflag = 0
        elif key in ('L', 'P') and event.ControlDown():
            return False
        return True
Mixin.setPlugin('editor', 'on_key_down', OnKeyDown, Mixin.HIGH, 0)

def getMatchWordPos(text, start, word, word_chars):
    pos = start + len(word)
    length = len(text)
    while pos < length:
        if not (text[pos] in word_chars):
            return pos
        pos += 1
    return -1

def init(win):
    win.findflag = 0
Mixin.setPlugin('editor', 'init', init)

def OnEditDuplicateWord(win, event):
    duplicateMatch(win, 1)
Mixin.setMixin('mainframe', 'OnEditDuplicateWord', OnEditDuplicateWord)

def OnEditDuplicateNextWord(win, event):
    duplicateMatch(win, 2)
Mixin.setMixin('mainframe', 'OnEditDuplicateNextWord', OnEditDuplicateNextWord)

def OnEditDuplicateLine(win, event):
    duplicateMatch(win, 3)
Mixin.setMixin('mainframe', 'OnEditDuplicateLine', OnEditDuplicateLine)

def OnEditDuplicateNextLine(win, event):
    duplicateMatch(win, 4)
Mixin.setMixin('mainframe', 'OnEditDuplicateNextLine', OnEditDuplicateNextLine)

def duplicateMatch(win, kind):
    text = win.document.getRawText()
    length = win.document.GetLength()
    if win.document.findflag == 0:
        win.document.duplicate_pos = win.document.GetCurrentPos()
        win.document.duplicate_word = findLeftWord(text, win.document.duplicate_pos, win.getWordChars())
        win.document.duplicate_length = len(win.document.duplicate_word)
        if win.document.duplicate_length == 0:
            return
        if kind in (1, 3):
            findstart = win.document.duplicate_pos - win.document.duplicate_length - 1
        else:
            findstart = win.document.duplicate_pos + 1  #-1 means skip the char before the word
    else:
        if kind in (1, 3):
            findstart = win.document.duplicate_start - 1
        else:
            findstart = win.document.duplicate_start + win.document.duplicate_match_len
    while (kind in (1, 3) and (findstart >= 0)) or (kind in (2, 4) and (findstart < length)) :
        if kind in (1, 3):
            start = findPreviousWordPos(text, findstart, win.document.duplicate_word, win.getWordChars())
        else:
            start = findNextWordPos(text, findstart, win.document.duplicate_word, win.getWordChars())
        if start > -1:
            end = getMatchWordPos(text, start, win.document.duplicate_word, win.getWordChars())
            if end - start > win.document.duplicate_length:
                if kind in (1, 2) and win.document.findflag:
                    if win.document.duplicate_calltip == text[start:end]:
                        if kind == 1:
                            findstart = start - 1
                        else:
                            findstart = start + 1
                        continue
                win.document.findflag = 1
                win.document.duplicate_start = start
                if kind in (3, 4):
                    line = win.document.LineFromPosition(start)
                    line_end = win.document.GetLineEndPosition(line)
                    win.document.duplicate_calltip = win.document.getLineText(line).expandtabs(win.document.GetTabWidth())
                    win.document.duplicate_match_len = line_end - start - win.document.duplicate_length
                    win.document.duplicate_match_text = win.document.GetTextRange(start + win.document.duplicate_length , line_end)
                else:
                    win.document.duplicate_calltip = text[start:end]
                    win.document.duplicate_match_len = end - start - win.document.duplicate_length
                    win.document.duplicate_match_text = win.document.GetTextRange(start + win.document.duplicate_length , end)
                win.document.calltip.cancel()
                win.document.calltip_type = CALLTIP_DUPLICATE
                win.document.calltip.show(win.document.duplicate_pos, win.document.duplicate_calltip)
                return
            else:
                if kind in (1, 3):
                    findstart = start - 1
                else:
                    findstart = start + 1
        else:
            return



#-----------------------  mHelp.py ------------------

import os
import wx
from modules import Mixin
from modules import Version
from modules import common
from modules.HyperLinksCtrl import HyperLinkCtrl, EVT_HYPERLINK_LEFT
from modules import Globals
from modules import meide as ui

homepage = 'http://code.google.com/p/ulipad/'
blog = 'http://www.donews.net/limodou'
email = 'limodou@gmail.com'
ulispot = 'http://ulipad.appspot.com'
author = 'Limodou'
maillist = 'http://groups.google.com/group/ulipad'

class AboutDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, size = (400, 340), style = wx.DEFAULT_DIALOG_STYLE, title = tr('About'))

        box = ui.VBox(padding=6, namebinding='widget').create(self).auto_layout()
        box.add(ui.Label(tr('UliPad %s') % Version.version), name='version', flag=wx.ALIGN_CENTER|wx.ALL)
        font = self.version.GetFont()
        font.SetPointSize(20)
        self.version.SetFont(font)
        box.add(ui.Label(tr('Author: %s (%s)') % (author, email)))
        box.add(ui.Label(tr('If you have any questions, please contact me.')))

        self.ID_HOMEPAGE = wx.NewId()
        self.homepage = HyperLinkCtrl(self, self.ID_HOMEPAGE, "The UliPad project homepage", URL=homepage)
        box.add(self.homepage).bind(EVT_HYPERLINK_LEFT, self.OnLink)

        self.ID_MAILLIST = wx.NewId()
        self.maillist = HyperLinkCtrl(self, self.ID_MAILLIST, "The UliPad maillist", URL=maillist)
        box.add(self.maillist).bind(EVT_HYPERLINK_LEFT, self.OnLink)

        self.ID_ULISPOT = wx.NewId()
        self.ulispot = HyperLinkCtrl(self, self.ID_ULISPOT, "The UliPad Snippets Site", URL=ulispot)
        box.add(self.ulispot).bind(EVT_HYPERLINK_LEFT, self.OnLink)

        self.ID_BLOG = wx.NewId()
        self.blog = HyperLinkCtrl(self, self.ID_BLOG, "My Blog", URL=blog)
        box.add(self.blog)

        self.ID_EMAIL = wx.NewId()
        self.email = HyperLinkCtrl(self, self.ID_EMAIL, "Contact me", URL='mailto:'+email)
        box.add(self.email)

        box.add(ui.Button(tr("OK"), id=wx.ID_OK), name='btnOk', flag=wx.ALIGN_RIGHT|wx.ALL, border=10)
        self.btnOk.SetDefault()

        box.auto_fit(2)

    def OnLink(self, event):
        eid = event.GetId()
        mainframe = Globals.mainframe
        if eid == self.ID_HOMEPAGE:
            mainframe.OnHelpProject(event)
        elif eid == self.ID_MAILLIST:
            mainframe.OnHelpMaillist(event)
        elif eid == self.ID_ULISPOT:
            mainframe.OnHelpUlispot(event)
        elif eid == self.ID_BLOG:
            mainframe.OnHelpMyBlog(event)
        elif eid == self.ID_EMAIL:
            mainframe.OnHelpEmail(event)

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_HELP', #parent menu id
        [
            (100, 'wx.ID_HELP', tr('UliPad Help Document') + '\tF1', wx.ITEM_NORMAL, 'OnHelpIndex', tr('UliPad help document.')),
            (200, '-', '', wx.ITEM_SEPARATOR, '', ''),
            (210, 'wx.ID_HOME', tr('Visit Project Homepage'), wx.ITEM_NORMAL, 'OnHelpProject', tr('Visit Project Homepage: %s.') % homepage),
            (220, 'IDM_HELP_MAILLIST', tr('Visit Mail List'), wx.ITEM_NORMAL, 'OnHelpMaillist', tr('Visit Project Mail List: %s.') % maillist),
            (230, 'IDM_HELP_MYBLOG', tr('Visit My Blog'), wx.ITEM_NORMAL, 'OnHelpMyBlog', tr('Visit My blog: %s.') % blog),
            (240, 'IDM_HELP_ULISPOT', tr('Visit UliPad Snippets Site'), wx.ITEM_NORMAL, 'OnHelpUlispot', tr('Visit UliPad snippets site: %s.') % ulispot),
            (250, 'IDM_HELP_EMAIL', tr('Contact Me'), wx.ITEM_NORMAL, 'OnHelpEmail', tr('Send email to me mailto:%s.') % email),
            (900, 'wx.ID_ABOUT', tr('About...'), wx.ITEM_NORMAL, 'OnHelpAbout', tr('About this program.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def OnHelpIndex(win, event):
    lang = 'en'
    if Globals.app.i18n.lang:
        lang = Globals.app.i18n.lang
    filename = common.get_app_filename(win, 'doc/%s/index.htm' % lang)
    if not os.path.exists(filename):
        filename = common.get_app_filename(win, 'doc/%s/index.htm' % 'en')
    common.webopen(filename)
Mixin.setMixin('mainframe', 'OnHelpIndex', OnHelpIndex)

def OnHelpAbout(win, event):
    AboutDialog(win).ShowModal()
Mixin.setMixin('mainframe', 'OnHelpAbout', OnHelpAbout)

def OnHelpProject(win, event):
    common.webopen(homepage)
Mixin.setMixin('mainframe', 'OnHelpProject', OnHelpProject)

def OnHelpMaillist(win, event):
    common.webopen(maillist)
Mixin.setMixin('mainframe', 'OnHelpMaillist', OnHelpMaillist)

def OnHelpEmail(win, event):
    common.webopen('mailto:%s' % email)
Mixin.setMixin('mainframe', 'OnHelpEmail', OnHelpEmail)

def OnHelpMyBlog(win, event):
    common.webopen(blog)
Mixin.setMixin('mainframe', 'OnHelpMyBlog', OnHelpMyBlog)

def OnHelpUlispot(win, event):
    common.webopen(ulispot)
Mixin.setMixin('mainframe', 'OnHelpUlispot', OnHelpUlispot)



#-----------------------  mClassBrowser.py ------------------

import wx
from modules import Mixin
from modules import Globals
from modules.Debug import error

def pref_init(pref):
    pref.python_classbrowser_show = False
    pref.python_classbrowser_refresh_as_save = True
    pref.python_classbrowser_show_docstring = False
    pref.python_classbrowser_sort = True
    pref.python_classbrowser_show_side = 'RIGHT'
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        ('Python', 100, 'check', 'python_classbrowser_show', tr('Show class browser window when opening python source file'), None),
        ('Python', 105, 'check', 'python_classbrowser_refresh_as_save', tr('Refresh class browser window when saving python source file'), None),
        ('Python', 106, 'check', 'python_classbrowser_show_docstring', tr('Show docstring when cursor moving on a node of class browser tree'), None),
        ('Python', 108, 'choice', 'python_classbrowser_show_side', tr('Show class browser in side:'), [('Left', 'LEFT'), ('Right', 'RIGHT')]),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def add_mainframe_menu(menulist):
    menulist.extend([('IDM_PYTHON', #parent menu id
            [
                (100, 'IDM_PYTHON_CLASSBROWSER', tr('Class Browser')+'\tE=Alt+V', wx.ITEM_CHECK, 'OnPythonClassBrowser', tr('Show python class browser window.')),
                (110, 'IDM_PYTHON_CLASSBROWSER_REFRESH', tr('Refresh Class Browser'), wx.ITEM_NORMAL, 'OnPythonClassBrowserRefresh', tr('Refresh python class browser window.')),
            ]),
    ])
Mixin.setPlugin('pythonfiletype', 'add_menu', add_mainframe_menu)

def editor_init(win):
    win.class_browser = False
    win.init_class_browser = False #if the class view has shown
Mixin.setPlugin('editor', 'init', editor_init)

def OnPythonClassBrowser(win, event):
    win.document.class_browser = not win.document.class_browser
    win.document.panel.showWindow(win.pref.python_classbrowser_show_side, win.document.class_browser)
    if win.document.panel.visible(win.pref.python_classbrowser_show_side):
        if win.document.init_class_browser == False:
            win.document.init_class_browser = True
            win.document.outlinebrowser.show()
Mixin.setMixin('mainframe', 'OnPythonClassBrowser', OnPythonClassBrowser)

def aftersavefile(win, filename):
    if (win.edittype == 'edit'
        and win.languagename == 'python'
        and win.pref.python_classbrowser_refresh_as_save
        and win.init_class_browser):
        wx.CallAfter(win.outlinebrowser.show)
Mixin.setPlugin('editor', 'aftersavefile', aftersavefile)

def OnPythonClassBrowserRefresh(win, event):
    win.document.outlinebrowser.show()
Mixin.setMixin('mainframe', 'OnPythonClassBrowserRefresh', OnPythonClassBrowserRefresh)

def OnPythonUpdateUI(win, event):
    eid = event.GetId()
    if eid == win.IDM_PYTHON_CLASSBROWSER and hasattr(win, 'document') and win.document and not win.document.multiview:
        event.Check(win.document.panel.visible(win.pref.python_classbrowser_show_side) and getattr(win.document, 'init_class_browser', False))
Mixin.setMixin('mainframe', 'OnPythonUpdateUI', OnPythonUpdateUI)

def on_enter(mainframe, document):
    wx.EVT_UPDATE_UI(mainframe, mainframe.IDM_PYTHON_CLASSBROWSER, mainframe.OnPythonUpdateUI)
Mixin.setPlugin('pythonfiletype', 'on_enter', on_enter)

def on_document_enter(mainframe, document):
    if document.languagename != 'python':
        return
    if mainframe.pref.python_classbrowser_show and document.init_class_browser == False:
        document.class_browser = not document.class_browser
        document.panel.showWindow(mainframe.pref.python_classbrowser_show_side, document.class_browser)
        if document.panel.visible(mainframe.pref.python_classbrowser_show_side):
            if document.init_class_browser == False:
                document.init_class_browser = True
                document.outlinebrowser.show()
Mixin.setPlugin('editctrl', 'on_document_enter', on_document_enter)

def on_leave(mainframe, filename, languagename):
    mainframe.Disconnect(mainframe.IDM_PYTHON_CLASSBROWSER, -1, wx.wxEVT_UPDATE_UI)
Mixin.setPlugin('pythonfiletype', 'on_leave', on_leave)

def add_images(images):
    s = [
        ('MODULE', 'images/module.gif'),
        ('VARIABLE', 'images/vars.gif'),
        ('METHOD', 'images/method.gif'),
        ('FUNCTION', 'images/function.gif'),
        ('CLASS_OPEN', 'images/minus.gif'),
        ('CLASS_CLOSE', 'images/plus.gif'),
        ]
    images.extend(s)
Mixin.setPlugin('outlinebrowser', 'add_images', add_images)

c = lambda x,y:cmp(x[0].upper(), y[0].upper())

def parsetext(win, editor):
    pref = Globals.pref
    if editor.edittype == 'edit' and editor.languagename == 'python':
        if not hasattr(editor, 'syntax_info') or not editor.syntax_info:
            from modules import PyParse
            nodes = PyParse.parseString(editor.GetText())
        else:
            nodes = editor.syntax_info
    else:
        return

    #add doc_nodes to editor
    editor.doc_nodes = {}

    imports = nodes.get_imports(1)
    if imports:
        for i, v in enumerate(imports):
            importline, lineno = v
            win.replacenode(None, i, importline, win.get_image_id('MODULE'), None,
                {'data':lineno}, win.get_image_id('MODULE'),
                sorttype=pref.python_classbrowser_sort)
    functions = nodes.find('function')
    #process locals
    addlocals(win, nodes, nodes, None)
    if functions:
        funcs = [(x.name, x.info, x.lineno, x.docstring) for x in functions.values]
        if pref.python_classbrowser_sort:
            funcs.sort(c)
        for i, v in enumerate(funcs):
            name, info, lineno, docstring = v
            _id, obj = win.replacenode(None, i, info, win.get_image_id('FUNCTION'),
                None,  {'data':lineno}, win.get_image_id('FUNCTION'),
                sorttype=pref.python_classbrowser_sort)
            editor.doc_nodes[_id] = docstring
    classes = nodes.find('class')
    if classes:
        clses = [(x.name, x.info, x.lineno, x) for x in classes.values]
        if pref.python_classbrowser_sort:
            clses.sort(c)
        for i, v in enumerate(clses):
            name, info, lineno, obj = v
            #process classes and functions
            _id, node = win.replacenode(None, i, name, win.get_image_id('CLASS_CLOSE'),
                win.get_image_id('CLASS_OPEN'), {'data':lineno},
                win.get_image_id('CLASS_CLOSE'), sorttype=pref.python_classbrowser_sort)
            editor.doc_nodes[_id] = obj.docstring
            #process locals
            addlocals(win, nodes, obj, node)
            objs = [(x.name, x.type, x.info, x.lineno, x) for x in obj.values]
            if pref.python_classbrowser_sort:
                objs.sort(c)
            for i, v in enumerate(objs):
                oname, otype, oinfo, olineno, oo = v
                imagetype = None
                if otype == 'class' or otype == 'function':
                    _id, obj = win.replacenode(node, i, oinfo, win.get_image_id('METHOD'),
                        None,  {'data':olineno}, win.get_image_id('METHOD'),
                        sorttype=pref.python_classbrowser_sort)
                    editor.doc_nodes[_id] = oo.docstring


Mixin.setPlugin('outlinebrowser', 'parsetext', parsetext)

def addlocals(win, root, node, treenode):
    pref = Globals.pref

    s = []
    names = []
    for i in range(len(node.locals)):
        name = node.locals[i]
        t, v, lineno = node.local_types[i]
        if t not in ('class', 'function', 'import'):
            info = name + ' : ' + 'unknow'
            if t == 'reference':
                if v:
                    if node.type == 'class':
                        result = root.guess_type(lineno, 'self.' + name)
                    else:
                        result = root.guess_type(lineno, name)
                    if result:

                        if result[0] not in ('reference', 'class', 'function', 'import'):
                            info = name + ' : ' + result[0]
                        else:
                            if result[1]:
                                if result[0] in ('class', 'function'):
                                    info = name + ' : ' + result[1].info
                                else:
                                    info = name + ' : ' + result[1]
                            else:
                                info = name + ' : ' + result[0]
                    else:
                        info = name + ' : ' + v
            else:
                info = name + ' : ' + t
            s.append((info, lineno))

    if pref.python_classbrowser_sort:
        s.sort(c)
    for i, v in enumerate(s):
        info, lineno = v
        win.replacenode(treenode, i, info , win.get_image_id('VARIABLE'), None,
            {'data':lineno}, win.get_image_id('VARIABLE'),
            sorttype=pref.python_classbrowser_sort)

def new_window(win, document, panel):
    from OutlineBrowser import OutlineBrowser
    parent = panel.getSide(Globals.pref.python_classbrowser_show_side)
    document.outlinebrowser = OutlineBrowser(parent, document, autoexpand=False)
    document.outlinebrowser.set_tooltip_func(on_get_tool_tip)
Mixin.setPlugin('textpanel', 'new_window', new_window)

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (2000, 'classbrowser'),
        (2050, '|'),
    ])

    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'classbrowser':(wx.ITEM_CHECK, 'IDM_PYTHON_CLASSBROWSER', 'images/classbrowser.gif', tr('Class Browser'), tr('Class browser'), 'OnPythonClassBrowser'),
    })
Mixin.setPlugin('pythonfiletype', 'add_tool_list', add_tool_list)

def afterclosewindow(win):
    if hasattr(win.document, 'panel') and hasattr(win.document.panel, 'showWindow'):
        win.document.panel.showWindow(win.pref.python_classbrowser_show_side, False)
Mixin.setPlugin('mainframe', 'afterclosewindow', afterclosewindow)

def on_jump_definition(editor, word):
    if editor.edittype == 'edit' and editor.languagename == 'python':
        if not hasattr(editor, 'syntax_info') or not editor.syntax_info:
            from modules import PyParse
            nodes = PyParse.parseString(editor.GetText())
        else:
            nodes = editor.syntax_info
        lineno = editor.GetCurrentLine() + 1 #syntax line is based on 1, but editor line is base on 0
        result = nodes.search_name(lineno, word)
        if result:
            t, v, line = result
            editor.goto(line)
Mixin.setPlugin('editor', 'on_jump_definition', on_jump_definition)

def on_get_tool_tip(win, event):
    if hasattr(win.editor, 'doc_nodes') and Globals.pref.python_classbrowser_show_docstring:
        nodes = win.editor.doc_nodes
        item = event.GetItem()
        if item.IsOk():
            _id = win.tree.GetPyData(item)
            tip = nodes.get(_id, '')
            if tip:
                try:
                    tip = remove_leading_spaces(win.editor, eval(tip).rstrip())
                    event.SetToolTip(tip)
                except:
                    import traceback
                    traceback.print_exc()
                    error.traceback()

import re
re_spaces = re.compile(r'^(\s*)')
re_eol = re.compile(r'\r\n|\r|\n')
def remove_leading_spaces(win, text):
    minspaces = []
    contentlines = re_eol.sub(win.getEOLChar(), text).splitlines()
    flag = False
    index = 0
    for i, line in enumerate(contentlines):
        #skip blank line
        if not line.strip():
            if not flag:
                index = i + 1
            continue
        flag = True
        b = re_spaces.search(line)
        if b:
            minspaces.append(b.span()[1])

    minspace = min(minspaces)
    lines = [x[minspace:] for x in contentlines[index:]]

    return '\n'.join(lines)

def savepreferencevalues(old_values):
    pref = Globals.pref
    side = old_values['python_classbrowser_show_side']
    if side.lower() != pref.python_classbrowser_show_side.lower():
        for document in Globals.mainframe.editctrl.getDocuments():
            if document.panel.visible(side):
                document.outlinebrowser.Destroy()
                document.panel.showWindow(side, False)
                new_window(document.panel.parent, document, document.panel)
                document.panel.showWindow(pref.python_classbrowser_show_side, True)
                document.outlinebrowser.show()
Mixin.setPlugin('prefdialog', 'savepreferencevalues', savepreferencevalues)



#-----------------------  mRun.py ------------------


import wx
import types
from modules import Mixin
from modules import common
from modules import Globals

def message_init(win):

    wx.EVT_IDLE(win, win.OnIdle)
    wx.EVT_END_PROCESS(win.mainframe, -1, win.mainframe.OnProcessEnded)
    wx.EVT_KEY_DOWN(win, win.OnKeyDown)
    wx.EVT_KEY_UP(win, win.OnKeyUp)
    wx.EVT_UPDATE_UI(win, win.GetId(),  win.RunCheck)

    win.MAX_PROMPT_COMMANDS = 25

    win.process = None
    win.pid = -1

    win.CommandArray = []
    win.CommandArrayPos = -1

    win.editpoint = 0
    win.writeposition = 0
    win.callback = None
Mixin.setPlugin('messagewindow', 'init', message_init)

def RunCommand(win, command, redirect=True, hide=False, input_decorator=None,
        callback=None):
    """replace $file = current document filename"""
    global input_appendtext

    #test if there is already a running process
    if hasattr(win, 'messagewindow') and win.messagewindow and win.messagewindow.process:
        common.showmessage(win, tr("The last process didn't stop yet. Please stop it and try again."))
        return
    if input_decorator:
        input_appendtext = input_decorator(appendtext)
    else:
        input_appendtext = appendtext
    if redirect:
        win.createMessageWindow()
        win.panel.showPage(tr('Messages'))
        win.callplugin('start_run', win, win.messagewindow)
        win.messagewindow.SetReadOnly(0)
        win.messagewindow.callback = callback
        appendtext(win.messagewindow, '> ' + command + '\n')

        win.messagewindow.editpoint = win.messagewindow.GetLength()
        win.messagewindow.writeposition = win.messagewindow.GetLength()
        win.SetStatusText(tr("Running "), 0)
        try:
            win.messagewindow.process = wx.Process(win)
            win.messagewindow.process.Redirect()
            if wx.Platform == '__WXMSW__':
                if hide == False:
                    win.messagewindow.pid = wx.Execute(command, wx.EXEC_ASYNC|wx.EXEC_NOHIDE, win.messagewindow.process)
                else:
                    win.messagewindow.pid = wx.Execute(command, wx.EXEC_ASYNC, win.messagewindow.process)
            else:
                win.messagewindow.pid = wx.Execute(command, wx.EXEC_ASYNC|wx.EXEC_MAKE_GROUP_LEADER, win.messagewindow.process)
            if hasattr(win.messagewindow, 'inputstream') and win.messagewindow.inputstream:
                win.messagewindow.inputstream.close()
            win.messagewindow.inputstream = win.messagewindow.process.GetInputStream()
            win.messagewindow.outputstream = win.messagewindow.process.GetOutputStream()
            win.messagewindow.errorstream = win.messagewindow.process.GetErrorStream()
        except:
            win.messagewindow.process = None
            dlg = wx.MessageDialog(win, tr("There are some issues with running the program.\nPlease run it in the shell.") ,
                "Error", wx.OK | wx.ICON_EXCLAMATION)
            dlg.ShowModal()
    else:
        wx.Execute(command, wx.EXEC_ASYNC)
Mixin.setMixin('mainframe', 'RunCommand', RunCommand)

def StopCommand(win):
    if win.messagewindow.process:
        wx.Process_Kill(win.messagewindow.pid, wx.SIGKILL)
        win.messagewindow.SetReadOnly(1)
        win.messagewindow.pid = -1
        win.messagewindow.process = None
    if Globals.pref.message_setfocus_back:
        wx.CallAfter(win.document.SetFocus)
Mixin.setMixin('mainframe', 'StopCommand', StopCommand)


def OnIdle(win, event):
    if win.process is not None:
        if win.inputstream:
            if win.inputstream.CanRead():
                text = win.inputstream.read()
                input_appendtext(win, text)
                win.writeposition = win.GetLength()
                win.editpoint = win.GetLength()
        if win.errorstream:
            if win.errorstream.CanRead():
                text = win.errorstream.read()
                input_appendtext(win, text)
                win.writeposition = win.GetLength()
                win.editpoint = win.GetLength()
Mixin.setMixin('messagewindow', 'OnIdle', OnIdle)

def OnKeyDown(win, event):
    keycode = event.GetKeyCode()
    pos = win.GetCurrentPos()
    if win.pid > -1:
        if (pos >= win.editpoint) and (keycode == wx.WXK_RETURN):
            text = win.GetTextRange(win.writeposition, win.GetLength())
            l = len(win.CommandArray)
            if (l < win.MAX_PROMPT_COMMANDS):
                win.CommandArray.insert(0, text)
                win.CommandArrayPos = -1
            else:
                win.CommandArray.pop()
                win.CommandArray.insert(0, text)
                win.CommandArrayPos = -1

            if isinstance(text, types.UnicodeType):
                text = common.encode_string(text)
            win.outputstream.write(text + '\n')
            win.GotoPos(win.GetLength())
            win.CmdKeyExecute(wx.stc.STC_CMD_NEWLINE)
            win.writeposition = win.GetLength()
            return
        if keycode == wx.WXK_UP:
            if (len(win.CommandArray) > 0):
                if (win.CommandArrayPos + 1) < l:
                    win.GotoPos(win.editpoint)
                    win.SetTargetStart(win.editpoint)
                    win.SetTargetEnd(win.GetLength())
                    win.CommandArrayPos = win.CommandArrayPos + 1
                    win.ReplaceTarget(win.CommandArray[win.CommandArrayPos])
            else:
                event.Skip()

        elif keycode == wx.WXK_DOWN:
            if len(win.CommandArray) > 0:
                win.GotoPos(win.editpoint)
                win.SetTargetStart(win.editpoint)
                win.SetTargetEnd(win.GetLength())
                if (win.CommandArrayPos - 1) > -1:
                    win.CommandArrayPos = win.CommandArrayPos - 1
                    win.ReplaceTarget(win.CommandArray[win.CommandArrayPos])
                else:
                    if (win.CommandArrayPos - 1) > -2:
                        win.CommandArrayPos = win.CommandArrayPos - 1
                    win.ReplaceTarget("")
            else:
                event.Skip()
    event.Skip()
Mixin.setMixin('messagewindow', 'OnKeyDown', OnKeyDown)

def OnKeyUp(win, event):
    keycode = event.GetKeyCode()
    #franz: pos was not used
    if keycode == wx.WXK_HOME:
        if (win.GetCurrentPos() < win.editpoint):
            win.GotoPos(win.editpoint)
        return
    elif keycode == wx.WXK_PRIOR:
        if (win.GetCurrentPos() < win.editpoint):
            win.GotoPos(win.editpoint)
        return
    event.Skip()
Mixin.setMixin('messagewindow', 'OnKeyUp', OnKeyUp)

def OnProcessEnded(win, event):
    if win.messagewindow.inputstream.CanRead():
        text = win.messagewindow.inputstream.read()
        input_appendtext(win.messagewindow, text)
    if win.messagewindow.errorstream.CanRead():
        text = win.messagewindow.errorstream.read()
        input_appendtext(win.messagewindow, text)

    if win.messagewindow.process:
        win.messagewindow.process.Destroy()
        win.messagewindow.process = None
        win.messagewindow.inputstream.close()
        win.messagewindow.inputstream = None
        win.messagewindow.outputstream = None
        win.messagewindow.errorstream = None
        win.messagewindow.pid = -1
        win.SetStatusText(tr("Finished! "), 0)
        if win.messagewindow.callback:
            wx.CallAfter(win.messagewindow.callback)
        if Globals.pref.message_setfocus_back:
            wx.CallAfter(win.document.SetFocus)
Mixin.setMixin('mainframe', 'OnProcessEnded', OnProcessEnded)

def appendtext(win, text):
    if not isinstance(text, unicode):
        try:
            text = unicode(text, common.defaultencoding)
        except UnicodeDecodeError:
            def f(x):
                if ord(x) > 127:
                    return '\\x%x' % ord(x)
                else:
                    return x
            text = ''.join(map(f, text))
    win.SetReadOnly(0)
    if Globals.pref.msgwin_max_lines>0:
        lines = (win.GetText().splitlines() + text.splitlines())[-1*Globals.pref.msgwin_max_lines:]
        eol = ['\n', '\r\n', '\r']
        win.SetText('')
        text = eol[win.GetEOLMode()].join(lines)
    flag = win.GetCurrentLine() == win.GetLineCount() - 1
    win.AppendText(text)
    if flag:
        win.GotoPos(win.GetLength())
    win.EmptyUndoBuffer()
input_appendtext = appendtext

def RunCheck(win, event):
    if (win.GetCurrentPos() < win.editpoint) or (win.pid == -1):
        win.SetReadOnly(1)
    else:
        win.SetReadOnly(0)
Mixin.setMixin('messagewindow', 'RunCheck', RunCheck)

def pref_init(pref):
    pref.msgwin_max_lines = 0
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('General'), 190, 'num', 'msgwin_max_lines', tr('Maxmize message window lines(0 no limited)'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)



#-----------------------  mScript.py ------------------

import wx
import sys
from modules import Mixin
from modules import makemenu

def pref_init(pref):
    pref.scripts = []
    pref.last_script_dir = ''
Mixin.setPlugin('preference', 'init', pref_init)

def add_mainframe_menu(menulist):
    menulist.extend([('IDM_TOOL',
        [
            (50, 'IDM_SCRIPT', tr('Scripts'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDM_SCRIPT', #parent menu id
        [
            (100, 'IDM_SCRIPT_MANAGE', tr('Scripts Manager...'), wx.ITEM_NORMAL, 'OnScriptManage', tr('Script manager.')),
            (110, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (120, 'IDM_SCRIPT_ITEMS', tr('(Empty)'), wx.ITEM_NORMAL, 'OnScriptItems', tr('Executes an script.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def OnScriptManage(win, event):
    from ScriptDialog import ScriptDialog

    dlg = ScriptDialog(win, win.pref)
    answer = dlg.ShowModal()
    if answer == wx.ID_OK:
        makescriptmenu(win, win.pref)
Mixin.setMixin('mainframe', 'OnScriptManage', OnScriptManage)

def beforeinit(win):
    win.old_script_accel = {}
    win.scriptmenu_ids=[win.IDM_SCRIPT_ITEMS]
    makescriptmenu(win, win.pref)
Mixin.setPlugin('mainframe', 'beforeinit', beforeinit)

def makescriptmenu(win, pref):
    menu = makemenu.findmenu(win.menuitems, 'IDM_SCRIPT')

    for id in win.scriptmenu_ids:
        menu.Delete(id)

    win.scriptmenu_ids = []
    if len(win.pref.scripts) == 0:
        id = win.IDM_SCRIPT_ITEMS
        menu.Append(id, tr('(Empty)'))
        menu.Enable(id, False)
        win.scriptmenu_ids=[id]
    else:
        accel = {}
        for description, filename in win.pref.scripts:
            id = wx.NewId()
            win.scriptmenu_ids.append(id)
            menu.Append(id, description)
            pos = description.find('\t')
            if pos > -1:
                key = description[pos+1:]
                accel[id] = (key, '')
            wx.EVT_MENU(win, id, win.OnScriptItems)
        if win.old_script_accel:
            win.removeAccel(win.old_script_accel)
        win.old_script_accel = accel
        if accel:
            win.insertAccel(accel)

def OnScriptItems(win, event):
    import wx.lib.dialogs
    import traceback
    from modules import common

    eid = event.GetId()
    index = win.scriptmenu_ids.index(eid)
    filename = win.pref.scripts[index][1]

    try:
        scripttext = open(common.encode_path(filename), 'rU').read()
    except:
        common.showerror(win, tr("Can't open the file %s.") % filename)
        return

    try:
        code = compile((scripttext + '\n'), common.encode_path(filename), 'exec')
    except:
        d = wx.lib.dialogs.ScrolledMessageDialog(win, (tr("Error compiling script.\n\nTraceback:\n\n") +
            ''.join(traceback.format_exception(*sys.exc_info()))), tr("Error"), wx.DefaultPosition, wx.Size(400,300))
        d.ShowModal()
        d.Destroy()
        return

    try:
        namespace = locals()
        exec code in namespace
    except:
        d = wx.lib.dialogs.ScrolledMessageDialog(win, (tr("Error running script.\n\nTraceback:\n\n") +
            ''.join(traceback.format_exception(*sys.exc_info()))), tr("Error"), wx.DefaultPosition, wx.Size(400,300))
        d.ShowModal()
        d.Destroy()
        return
Mixin.setMixin('mainframe', 'OnScriptItems', OnScriptItems)



#-----------------------  mLanguage.py ------------------

import wx
from modules import Mixin
from modules import makemenu
from modules import common

def add_mainframe_menu(menulist):
    menulist.extend([('IDM_TOOL',
        [
            (135, 'IDM_OPTION_LANGUAGE', tr('Language'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDM_OPTION_LANGUAGE',
        [
            (100, 'IDM_OPTION_LANGUAGE_ENGLISH', 'English', wx.ITEM_CHECK, 'OnOptionLanguageChange', 'Change langauage.'),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def beforeinit(win):
    langinifile = common.uni_work_file('lang/language.ini')
    win.language_ids = [win.IDM_OPTION_LANGUAGE_ENGLISH]
    win.language_country = ['']
    create_language_menu(win, langinifile)
Mixin.setPlugin('mainframe', 'beforeinit', beforeinit)

def create_language_menu(win, filename):
    menu = makemenu.findmenu(win.menuitems, 'IDM_OPTION_LANGUAGE')

    langs = open(filename).readlines()
    for lang in langs:
        lang = lang.strip()
        if lang == '':
            continue
        if lang[0] == '#':
            continue
        country, language = lang.strip().split(' ', 1)
        id = wx.NewId()
        win.language_ids.append(id)
        win.language_country.append(country)
        menu.Append(id, language, 'Change language', wx.ITEM_CHECK)
        wx.EVT_MENU(win, id, win.OnOptionLanguageChange)

    index = win.language_country.index(win.app.i18n.lang)
    menu.Check(win.language_ids[index], True)

def OnOptionLanguageChange(win, event):
    eid = event.GetId()
    index = win.language_ids.index(eid)
    country = win.language_country[index]
    wx.MessageDialog(win, tr("Because you changed the language, \nit will be enabled at next startup."), tr("Change language"), wx.OK).ShowModal()
    ini = common.get_config_file_obj()
    ini.language.default = country
    ini.save()

    # change menu check status
    menu = makemenu.findmenu(win.menuitems, 'IDM_OPTION_LANGUAGE')
    for id in win.language_ids:
        if id == eid:
            menu.Check(id, True)
        else:
            menu.Check(id, False)
Mixin.setMixin('mainframe', 'OnOptionLanguageChange', OnOptionLanguageChange)



#-----------------------  mLexer.py ------------------

__doc__ = 'C syntax highlitght process'

import wx
from modules import Mixin
import LexerClass
import LexerClass1
import LexerRst

def add_lexer(lexer):
    lexer.extend([
        (LexerClass.TextLexer.metaname, 'Plain Text|*.txt;*.bak;*.log;*.lst;*.diz;*.nfo',
            wx.stc.STC_LEX_NULL, 'text.stx', LexerClass.TextLexer),
        (LexerClass.CLexer.metaname, 'C/C++|*.c;*.cc;*.cpp;*.cxx;*.cs;*.h;*.hh;*.hpp;*.hxx',
            wx.stc.STC_LEX_CPP, 'c.stx', LexerClass.CLexer),
        (LexerClass.HtmlLexer.metaname, 'HTML|*.htm;*.html;*.shtml',
            wx.stc.STC_LEX_HTML, 'html.stx', LexerClass.HtmlLexer),
        (LexerClass.XMLLexer.metaname, 'XML|*.xml;*.xslt',
            wx.stc.STC_LEX_CONTAINER, 'xml.stx', LexerClass.XMLLexer),
        (LexerClass.PythonLexer.metaname, 'Python|*.py;*.pyw',
            wx.stc.STC_LEX_PYTHON, 'python.stx', LexerClass.PythonLexer),
        (LexerClass1.JavaLexer.metaname, 'Java|*.java',
            wx.stc.STC_LEX_CPP, 'java.stx', LexerClass1.JavaLexer),
        (LexerClass1.RubyLexer.metaname, 'Ruby|*.rb',
            wx.stc.STC_LEX_RUBY, 'ruby.stx', LexerClass1.RubyLexer),
        (LexerClass1.PerlLexer.metaname, 'Perl|*.pl',
            wx.stc.STC_LEX_PERL, 'perl.stx', LexerClass1.PerlLexer),
        (LexerClass1.CSSLexer.metaname, 'CSS|*.css',
            wx.stc.STC_LEX_CSS, 'css.stx', LexerClass1.CSSLexer),
        (LexerClass1.JSLexer.metaname, 'JavaScript|*.js',
            wx.stc.STC_LEX_CPP, 'js.stx', LexerClass1.JSLexer),
        (LexerClass1.PHPLexer.metaname, 'PHP|*.php3;*.phtml;*.php',
            wx.stc.STC_LEX_HTML, 'php.stx', LexerClass1.PHPLexer),
        (LexerClass1.ASPLexer.metaname, 'ASP|*.asp',
            wx.stc.STC_LEX_HTML, 'asp.stx', LexerClass1.ASPLexer),
        (LexerRst.RstLexer.metaname, 'reStructuredText|*.rst',
            wx.stc.STC_LEX_CONTAINER, 'rst.stx', LexerRst.RstLexer),
        (LexerClass1.LuaLexer.metaname, 'Lua|*.lua;*.wlua',
            wx.stc.STC_LEX_LUA, 'lua.stx', LexerClass1.LuaLexer),
        (LexerClass1.SliceLexer.metaname, 'Slice|*.ice',
            wx.stc.STC_LEX_CPP, 'slice.stx', LexerClass1.SliceLexer),
        (LexerClass1.BashLexer.metaname, 'Bash|*.sh',
             wx.stc.STC_LEX_BASH, 'bash.stx', LexerClass1.BashLexer)
    ])
Mixin.setPlugin('lexerfactory', 'add_lexer', add_lexer)

def add_new_files(new_files):
    new_files.extend([
        ('Plain Text', LexerClass.TextLexer.metaname),
        ('C/C++', LexerClass.CLexer.metaname),
        ('HTML', LexerClass.HtmlLexer.metaname),
        ('XML', LexerClass.XMLLexer.metaname),
        ('Python', LexerClass.PythonLexer.metaname),
        ('Java', LexerClass1.JavaLexer.metaname),
        ('Ruby', LexerClass1.RubyLexer.metaname),
        ('Perl', LexerClass1.PerlLexer.metaname),
        ('CSS', LexerClass1.CSSLexer.metaname),
        ('JavaScript', LexerClass1.JSLexer.metaname),
        ('PHP', LexerClass1.PHPLexer.metaname),
        ('ASP', LexerClass1.ASPLexer.metaname),
        ('reStructuredText', LexerRst.RstLexer.metaname),
        ('Lua', LexerClass1.LuaLexer.metaname),
        ('Slice', LexerClass1.SliceLexer.metaname),
        ('Bash', LexerClass1.BashLexer.metaname)
    ])
Mixin.setPlugin('mainframe', 'add_new_files', add_new_files)



#-----------------------  mSearchInFiles.py ------------------

import wx
import os.path
import sys
from modules import Mixin

def add_mainframe_menu(menulist):
    menulist.extend([
        ('IDM_SEARCH', #parent menu id
        [
            (145, 'IDM_SEARCH_FIND_IN_FILES', tr('Find In Files...')+'\tCtrl+Shift+F4', wx.ITEM_NORMAL, 'OnSearchFindInFiles', tr('Find text in files.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def createFindInFilesWindow(win):
    findinfiles_pagename = tr('Find in Files')
    if not win.panel.getPage(findinfiles_pagename):
        from FindInFiles import FindInFiles

        page = FindInFiles(win.panel.createNotebook('bottom'), win)
        win.panel.addPage('bottom', page, findinfiles_pagename)
    return findinfiles_pagename
Mixin.setMixin('mainframe', 'createFindInFilesWindow', createFindInFilesWindow)

def OnSearchFindInFiles(win, event):
    p = win.createFindInFilesWindow()
    win.panel.showPage(p)
Mixin.setMixin('mainframe', 'OnSearchFindInFiles', OnSearchFindInFiles)

def pref_init(pref):
    pref.searchinfile_searchlist = []
    pref.searchinfile_dirlist = []
    pref.searchinfile_extlist = []
    pref.searchinfile_case = False
    pref.searchinfile_subdir = True
    pref.searchinfile_regular = False
    pref.searchinfile_onlyfilename = False
    pref.searchinfile_defaultpath = os.path.dirname(sys.argv[0])
Mixin.setPlugin('preference', 'init', pref_init)



#-----------------------  mAutoBak.py ------------------

__doc__ = 'auto make bak file as open a file'

from modules import Mixin
from modules import common

def add_pref(preflist):
    preflist.extend([
        (tr('Document')+'/'+tr('Back-End'), 100, 'check', 'auto_make_bak', tr('Make file backup at opening a file'), None)
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def pref_init(pref):
    pref.auto_make_bak  = False
Mixin.setPlugin('preference', 'init', pref_init)

def openfile(win, filename):
    import shutil

    if filename and win.pref.auto_make_bak:
        bakfile = filename + '.bak'
        try:
            shutil.copyfile(filename, bakfile)
        except Exception, mesg:
            common.showerror(win, mesg)
Mixin.setPlugin('editor', 'openfile', openfile, Mixin.HIGH, 0)



#-----------------------  mAutoCheck.py ------------------

__doc__ = 'Auto check if the file is modified'

import wx
import os
from modules import Mixin
from modules import Globals

def add_pref(preflist):
    preflist.extend([
        (tr('Document')+'/'+tr('Back-End'), 110, 'check', 'auto_check', tr('Autocheck if opened documents were modified by others'), None),
        (tr('Document')+'/'+tr('Back-End'), 120, 'check', 'auto_check_confirm', tr('Confirm file reload'), None)
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def pref_init(pref):
    pref.auto_check  = True
    pref.auto_check_confirm = True
Mixin.setPlugin('preference', 'init', pref_init)

def on_set_focus(win, event):
    _check(Globals.mainframe)
Mixin.setPlugin('editor', 'on_set_focus', on_set_focus)

def _check(win):
    if win.pref.auto_check:
        for document in win.editctrl.getDocuments():
            if win.closeflag: return
            if document.filename and document.edittype == 'edit' and document.opened and hasattr(document, 'saving'):
                if os.path.exists(document.filename) and not checkFilename(win, document) and win.editctrl.filetimes.has_key(document.filename):
                    if not document.saving and getModifyTime(document.filename) > win.editctrl.filetimes[document.filename]:
                        def fn():
                            answer = wx.ID_NO
                            if win.pref.auto_check_confirm:
                                dlg = wx.MessageDialog(win, tr("Another application has modified [%s].\nDo you want to reopen it?") % document.filename, tr("Check"), wx.YES_NO | wx.ICON_QUESTION)
                                answer = dlg.ShowModal()
                            if answer == wx.ID_YES or not win.pref.auto_check_confirm:
                                state = document.save_state()
                                document.openfile(document.filename)
                                document.editctrl.switch(document)
                                document.restore_state(state)
                        wx.CallAfter(fn)
                        win.editctrl.filetimes[document.filename] = getModifyTime(document.filename)
                        return

def editctrl_init(win):
    win.filetimes = {}
Mixin.setPlugin('editctrl', 'init', editctrl_init)

def afteropenfile(win, filename):
    if filename and win.edittype == 'edit':
        win.editctrl.filetimes[filename] = getModifyTime(filename)
Mixin.setPlugin('editor', 'afteropenfile', afteropenfile)

def aftersavefile(win, filename):
    if win.edittype == 'edit':
        win.editctrl.filetimes[filename] = getModifyTime(filename)
Mixin.setPlugin('editor', 'aftersavefile', aftersavefile)

def closefile(win, document, filename):
    if filename and document.edittype == 'edit':
        if win.editctrl.filetimes.has_key(filename):
            del win.editctrl.filetimes[filename]
Mixin.setPlugin('mainframe', 'closefile', closefile)

def getModifyTime(filename):
    try:
        ftime = os.path.getmtime(filename)
    except:
        ftime = 0
    return ftime

def checkFilename(win, document):
    if not document.needcheck():
        return True
    if not os.path.exists(document.filename) and win.editctrl.filetimes[document.filename] != 'NO':
        dlg = wx.MessageDialog(win, tr("The file %s has been removed by others.\nDo you want to save it?") % document.filename, tr("Check"), wx.YES_NO | wx.ICON_QUESTION)
        answer = dlg.ShowModal()
        if answer == wx.ID_YES:
            document.savefile(document.filename, document.locale)
            document.editctrl.switch(document)
            win.editctrl.filetimes[document.filename] = getModifyTime(document.filename)
        else:
            win.editctrl.filetimes[document.filename] = 'NO'
        return True
    else:
        return False



#-----------------------  mTool.py ------------------

import wx
from modules import Mixin

__doc__ = 'Tool menu'

def add_menu(menulist):
    menulist.extend([(None,
        [
            (550, 'IDM_TOOL', tr('Tools'), wx.ITEM_NORMAL, None, ''),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_menu)



#-----------------------  mPyRun.py ------------------

import wx
import os
import sys
from modules import common
from modules import Mixin
from modules import Globals

def check_python():
    interpreters = []
    if wx.Platform == '__WXMSW__':
        from modules import winreg
        for v in ('2.3', '2.4', '2.5', '2.6', '2.7', '3.0', '3.1'):
            try:
                key = winreg.Key(winreg.HKLM, r'SOFTWARE\Python\Pythoncore\%s\InstallPath' % v)
                interpreters.append((v+' console', os.path.join(key.value, 'python.exe')))
                interpreters.append((v+' window', os.path.join(key.value, 'pythonw.exe')))
            except:
                pass
    else:
        version = '.'.join(map(str, sys.version_info[:2]))
        interpreters.append((version, sys.executable))
    return interpreters

def pref_init(pref):
    s = check_python()
    pref.python_interpreter = s
    if len(s) == 1:
        pref.default_interpreter = s[0][0]
    else:
        pref.default_interpreter = 'noexist'
    pref.python_show_args = False
    pref.python_save_before_run = False
    pref.python_default_paramters = {}
    for i in s:
        pref.python_default_paramters[i[0]] = '-u'
Mixin.setPlugin('preference', 'init', pref_init)

def OnSetPythonInterpreter(win, event):
    from InterpreterDialog import InterpreterDialog
    dlg = InterpreterDialog(win, win.pref)
    dlg.ShowModal()
Mixin.setMixin('prefdialog', 'OnSetPythonInterpreter', OnSetPythonInterpreter)

def add_pref(preflist):
    preflist.extend([
        ('Python', 150, 'button', 'python_interpreter', tr('Setup Python interpreter...'), 'OnSetPythonInterpreter'),
        ('Python', 155, 'check', 'python_show_args', tr('Show the Select Arguments dialog at Python program run'), None),
        ('Python', 156, 'check', 'python_save_before_run', tr('Save the modified document at Python program run'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def add_pyftype_menu(menulist):
    menulist.extend([('IDM_PYTHON', #parent menu id
        [
            (120, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (130, 'IDM_PYTHON_RUN', tr('Run')+u'\tE=F5', wx.ITEM_NORMAL, 'OnPythonRun', tr('Runs the Python program.')),
            (140, 'IDM_PYTHON_SETARGS', tr('Set Arguments...'), wx.ITEM_NORMAL, 'OnPythonSetArgs', tr('Sets the command-line arguments for a Python program.')),
            (150, 'IDM_PYTHON_END', tr('Stop Program'), wx.ITEM_NORMAL, 'OnPythonEnd', tr('Stops the current Python program.')),
            (155, 'IDM_PYTHON_DOCTEST', tr('Run Doctest'), wx.ITEM_NORMAL, 'OnPythonDoctests', tr('Runs doctest in the current document.')),
        ]),
    ])
Mixin.setPlugin('pythonfiletype', 'add_menu', add_pyftype_menu)

def editor_init(win):
    win.args = ''
    win.redirect = True
Mixin.setPlugin('editor', 'init', editor_init)

def _get_python_exe(win):
    s = win.pref.python_interpreter
    interpreters = dict(s)
    interpreter = interpreters.get(win.pref.default_interpreter, '')

    #check python execute
    e = check_python()
    for x, v in e:
        flag = False
        for i, t in enumerate(s):
            name, exe = t
            if exe == v:
                flag = True
                if name != x:
                    s[i] = (x, v)
        if not flag:
            s.append((x, v))
    win.pref.save()

    if not interpreter:
        value = ''
        if s:
            if len(s) > 1:
                dlg = SelectInterpreter(win, s[0][0], [x for x, v in s])
                if dlg.ShowModal() == wx.ID_OK:
                    value = dlg.GetValue()
                dlg.Destroy()
            else:
                value = s[0][0]

        if not value:
            common.showerror(win, tr("You didn't set the Python interpreter.\nPlease set it up first in the preferences."))

        interpreter = dict(s).get(value, '')
        win.pref.default_interpreter = value
        win.pref.save()

    return interpreter

def OnPythonRun(win, event):
    interpreter = _get_python_exe(win)
    if not interpreter: return

    doc = win.editctrl.getCurDoc()
    if doc.isModified() or doc.filename == '':
        if win.pref.python_save_before_run:
            win.OnFileSave(event)
        else:
            d = wx.MessageDialog(win, tr("The script can't run because the document hasn't been saved.\nWould you like to save it?"), tr("Run"), wx.YES_NO | wx.ICON_QUESTION)
            answer = d.ShowModal()
            d.Destroy()
            if answer == wx.ID_YES:
                win.OnFileSave(event)
            else:
                return

    if win.pref.python_show_args:
        if not get_python_args(win):
            return

    args = doc.args.replace('$path', os.path.dirname(doc.filename))
    args = args.replace('$file', doc.filename)
    ext = os.path.splitext(doc.filename)[1].lower()
    parameter = Globals.pref.python_default_paramters.get(Globals.pref.default_interpreter, '')
    interpreter = dict(Globals.pref.python_interpreter).get(Globals.pref.default_interpreter, '')
    command = u'"%s" %s "%s" %s' % (interpreter, parameter, doc.filename, args)
    #chanage current path to filename's dirname
    path = os.path.dirname(doc.filename)
    os.chdir(common.encode_string(path))

    win.RunCommand(command, redirect=win.document.redirect)
Mixin.setMixin('mainframe', 'OnPythonRun', OnPythonRun)

def get_python_args(win):
    if not Globals.pref.python_interpreter:
        common.showerror(win, tr("You didn't set the Python interpreter.\nPlease set it up first in the preferences."))
        return False

    from InterpreterDialog import PythonArgsDialog

    dlg = PythonArgsDialog(win, tr('Python Arguments Manager'),
        win.document.args, win.document.redirect)
    answer = dlg.ShowModal()
    value = dlg.GetValue()
    dlg.Destroy()
    if answer == wx.ID_OK:
        win.document.args = value['command_line']
        win.document.redirect = value['redirect']
        return True
    else:
        return False

def OnPythonSetArgs(win, event=None):
    get_python_args(win)
Mixin.setMixin('mainframe', 'OnPythonSetArgs', OnPythonSetArgs)

def OnPythonEnd(win, event):
    win.StopCommand()
    win.SetStatusText(tr("Stopped!"), 0)
Mixin.setMixin('mainframe', 'OnPythonEnd', OnPythonEnd)

def OnPythonDoctests(win, event):
    from modules import Globals
    from modules.Debug import error

    def appendtext(win, text):
        win.SetReadOnly(0)
        win.SetText('')
        win.GotoPos(win.GetLength())
        if not isinstance(text, unicode):
            try:
                text = unicode(text, common.defaultencoding)
            except UnicodeDecodeError:
                def f(x):
                    if ord(x) > 127:
                        return '\\x%x' % ord(x)
                    else:
                        return x
                text = ''.join(map(f, text))
        win.AddText(text)
        win.GotoPos(win.GetLength())
        win.EmptyUndoBuffer()
        win.SetReadOnly(1)

    def pipe_command(cmd, callback):
        from modules import Casing

        def _run(cmd):
            try:
                sin, sout, serr = os.popen3(cmd)
                if callback:
                    wx.CallAfter(callback, sout.read()+serr.read())
            except:
                error.traceback()

        d = Casing.Casing(_run, cmd)
        d.start_thread()

    def f(text):
        try:
            win.createMessageWindow()
            win.panel.showPage(tr('Messages'))
            if not text:
                text = 'Doctest for %s is successful!' % doc.filename
            appendtext(win.messagewindow, text)
        except:
            error.traceback()

    doc = win.editctrl.getCurDoc()
    if doc.isModified() or doc.filename == '':
        d = wx.MessageDialog(win, tr("The script can't run because the document hasn't been saved.\nWould you like to save it?"), tr("Run"), wx.YES_NO | wx.ICON_QUESTION)
        answer = d.ShowModal()
        d.Destroy()
        if answer == wx.ID_YES:
            win.OnFileSave(event)
        else:
            return

    path = os.path.normpath(os.path.join(Globals.workpath, 'packages/cmd_doctest.py'))
    filename = Globals.mainframe.editctrl.getCurDoc().filename
    interpreter = _get_python_exe(win)
    cmd = u'%s "%s" "%s"' % (interpreter, path, filename)
    pipe_command(cmd, f)
Mixin.setMixin('mainframe', 'OnPythonDoctests', OnPythonDoctests)

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (2100, 'run'),
        (2110, 'setargs'),
        (2120, 'stop'),
        (2130, 'doctest'),
        (2150, '|'),
    ])

    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'run':(wx.ITEM_NORMAL, 'IDM_PYTHON_RUN', 'images/run.gif', tr('Run'), tr('Runs the Python program.'), 'OnPythonRun'),
        'setargs':(wx.ITEM_NORMAL, 'IDM_PYTHON_SETARGS', 'images/setargs.gif', tr('Set Arguments'), tr('Sets the command-line arguments for a Python program.'), 'OnPythonSetArgs'),
        'stop':(wx.ITEM_NORMAL, 'IDM_PYTHON_END', 'images/stop.gif', tr('Stop Program'), tr('Stops the current Python program.'), 'OnPythonEnd'),
        'doctest':(wx.ITEM_NORMAL, 'IDM_PYTHON_DOCTEST', 'images/doctest.png', tr('Run Doctest'), tr('Runs dotest in the current document.'), 'OnPythonDoctests'),
    })
Mixin.setPlugin('pythonfiletype', 'add_tool_list', add_tool_list)

def OnPythonRunUpdateUI(win, event):
    eid = event.GetId()
    if eid in [ win.IDM_PYTHON_RUN, win.IDM_PYTHON_SETARGS ]:
        if not hasattr(win, 'messagewindow') or not win.messagewindow or not (win.messagewindow.pid > 0):
            event.Enable(True)
        else:
            event.Enable(False)
    elif eid == win.IDM_PYTHON_END:
        if hasattr(win, 'messagewindow') and win.messagewindow and (win.messagewindow.pid > 0):
            event.Enable(True)
        else:
            event.Enable(False)
Mixin.setMixin('mainframe', 'OnPythonRunUpdateUI', OnPythonRunUpdateUI)

def on_enter(mainframe, document):
    wx.EVT_UPDATE_UI(mainframe, mainframe.IDM_PYTHON_RUN, mainframe.OnPythonRunUpdateUI)
    wx.EVT_UPDATE_UI(mainframe, mainframe.IDM_PYTHON_SETARGS, mainframe.OnPythonRunUpdateUI)
    wx.EVT_UPDATE_UI(mainframe, mainframe.IDM_PYTHON_END, mainframe.OnPythonRunUpdateUI)
Mixin.setPlugin('pythonfiletype', 'on_enter', on_enter)

def on_leave(mainframe, filename, languagename):
    ret = mainframe.Disconnect(mainframe.IDM_PYTHON_RUN, -1, wx.wxEVT_UPDATE_UI)
    ret = mainframe.Disconnect(mainframe.IDM_PYTHON_SETARGS, -1, wx.wxEVT_UPDATE_UI)
    ret = mainframe.Disconnect(mainframe.IDM_PYTHON_END, -1, wx.wxEVT_UPDATE_UI)
Mixin.setPlugin('pythonfiletype', 'on_leave', on_leave)

def goto_error_line(msgwin, line, lineno):
    import re
    r = re.compile('File\s+"(.*?)",\s+line\s+(\d+)')
    b = r.search(common.encode_string(line, common.defaultfilesystemencoding))
    if b:
        return True, b.groups()
Mixin.setPlugin('messagewindow', 'goto_error_line', goto_error_line)

from modules import meide as ui

class SelectInterpreter(ui.SimpleDialog):
    def __init__(self, parent, value, interpreters):
        box = ui.VBox(namebinding='element')
        box.add(ui.Label(tr('Which Python interpreter do you want to use?')))
        box.add(ui.ComboBox(value, choices=interpreters, style=wx.CB_READONLY), name='interpreter')
        super(SelectInterpreter, self).__init__(parent, box, title=tr('Python Interpreters List'), fit=2)

        self.layout.SetFocus()

    def GetValue(self):
        return self.interpreter.GetValue()



#-----------------------  mShellRun.py ------------------

__doc__ = 'run external tools'

import os
import wx
from modules import Mixin
from modules import makemenu

def pref_init(pref):
    pref.shells = []
Mixin.setPlugin('preference', 'init', pref_init)

def add_mainframe_menu(menulist):
    menulist.extend([('IDM_TOOL',
        [
            (100, 'IDM_SHELL', tr('External Tools'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDM_SHELL', #parent menu id
        [
            (100, 'IDM_SHELL_MANAGE', tr('External Tools Manager...'), wx.ITEM_NORMAL, 'OnShellManage', tr('Shell command manager.')),
            (110, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (120, 'IDM_SHELL_ITEMS', tr('(Empty)'), wx.ITEM_NORMAL, 'OnShellItems', tr('Execute an shell command.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def OnShellManage(win, event):
    from ShellDialog import ShellDialog

    dlg = ShellDialog(win, win.pref)
    answer = dlg.ShowModal()
    if answer == wx.ID_OK:
        makeshellmenu(win, win.pref)
Mixin.setMixin('mainframe', 'OnShellManage', OnShellManage)

def beforeinit(win):
    win.shellmenu_ids=[win.IDM_SHELL_ITEMS]
    makeshellmenu(win, win.pref)
Mixin.setPlugin('mainframe', 'beforeinit', beforeinit)

def makeshellmenu(win, pref):
    menu = makemenu.findmenu(win.menuitems, 'IDM_SHELL')

    for id in win.shellmenu_ids:
        menu.Delete(id)

    win.shellmenu_ids = []
    if len(win.pref.shells) == 0:
        id = win.IDM_SHELL_ITEMS
        menu.Append(id, tr('(Empty)'))
        menu.Enable(id, False)
        win.shellmenu_ids=[id]
    else:
        for description, filename in win.pref.shells:
            id = wx.NewId()
            win.shellmenu_ids.append(id)
            menu.Append(id, description)
            wx.EVT_MENU(win, id, win.OnShellItems)

def OnShellItems(win, event):
    win.createMessageWindow()

    eid = event.GetId()
    index = win.shellmenu_ids.index(eid)
    command = win.pref.shells[index][1]
    command = command.replace('$path', os.path.dirname(win.document.filename))
    command = command.replace('$file', win.document.filename)
    wx.Execute(command)
Mixin.setMixin('mainframe', 'OnShellItems', OnShellItems)



#-----------------------  mEncoding.py ------------------

import wx
from modules import Mixin
from modules import common

def pref_init(pref):
    pref.select_encoding = False
    pref.default_encoding = common.defaultencoding
    pref.custom_encoding = ''
Mixin.setPlugin('preference', 'init', pref_init)

encodings = [common.defaultencoding]
if 'UTF-8' not in encodings and 'UTF8' not in encodings:
    encodings.append('UTF-8')

def add_pref(preflist):
    preflist.extend([
        (tr('General'), 120, 'check', 'select_encoding', tr('Show encoding dialog at file opening and at file saving'), None),
        (tr('Document'), 190, 'choice', 'default_encoding', tr('Default document encoding:'), encodings),
        (tr('Document'), 191, 'text', 'custom_encoding', tr("Set custom encoding to be default:"), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def _getencoding():
    ret = None
    from EncodingDialog import EncodingDialog
    dlg = EncodingDialog()
    answer = dlg.ShowModal()
    if answer == wx.ID_OK:
        ret = dlg.GetValue()
    dlg.Destroy()
    return ret

def getencoding(win, mainframe):
    ret = None
    if win.pref.select_encoding:
        ret = _getencoding()
    return ret
Mixin.setPlugin('mainframe', 'getencoding', getencoding)

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_DOCUMENT',
        [
            (125, 'IDM_DOCUMENT_CHANGE_ENCODING', tr('Change Encoding...'), wx.ITEM_NORMAL, 'OnDocumentChangeEncoding', tr("Changes the current encoding of the document.")),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_editor_menu(popmenulist):
    popmenulist.extend([ (None, #parent menu id
        [
            (250, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (260, 'IDPM_CHANGE_ENCODING', tr('Change Encoding...'), wx.ITEM_NORMAL, 'OnEditorDocumentChangeEncoding', tr("Changes the current encoding of the document.")),
        ]),
    ])
Mixin.setPlugin('editor', 'add_menu', add_editor_menu)

def OnDocumentChangeEncoding(win, event):
    ret = _getencoding()
    if ret:
        win.document.locale = ret
        common.set_encoding(win.document.locale)
        win.document.modified = True
        wx.CallAfter(win.editctrl.showTitle, win.document)
        wx.CallAfter(win.editctrl.showPageTitle, win.document)
Mixin.setMixin('mainframe', 'OnDocumentChangeEncoding', OnDocumentChangeEncoding)

def OnEditorDocumentChangeEncoding(win, event):
    win.mainframe.OnDocumentChangeEncoding(None)
Mixin.setMixin('editor', 'OnEditorDocumentChangeEncoding', OnEditorDocumentChangeEncoding)



#-----------------------  mShowLocale.py ------------------

__doc__ = 'show document locale in statusbar'

from modules import Mixin
from modules import common

def on_document_enter(win, document):
    if document.edittype == 'edit':
        common.set_encoding(win.document.locale)
Mixin.setPlugin('editctrl', 'on_document_enter', on_document_enter)

def fileopentext(win, stext):
    common.set_encoding(win.locale)
Mixin.setPlugin('editor', 'openfiletext', fileopentext)

def savefiletext(win, stext):
    common.set_encoding(win.locale)
Mixin.setPlugin('editor', 'savefiletext', savefiletext)

def afteropenfile(win, filename):
    common.set_encoding(win.locale)
Mixin.setPlugin('editor', 'afteropenfile', afteropenfile)



#-----------------------  mDDESupport.py ------------------

__doc__ = 'simulate DDE support'

import sys
from modules import DDE
from modules import Mixin
from modules import common

def app_init(app, filenames):
    if app.ddeflag:
        x = common.get_config_file_obj()
        port = x.server.get('port', 50009)
        if DDE.senddata('\r\n'.join(filenames), port=port):
            print """Found previous instance of UliPad and the files will be
opened in it, current instance will be quit. If you have not
seen the UliPad started, please change the DDE support port at
config.ini with :

    [server]
    port=50001 #or other port number

If it's alreay exit, contact ulipad author to get help."""
            sys.exit(0)
        else:
            DDE.run(port=port)
Mixin.setPlugin('app', 'dde', app_init, Mixin.HIGH, 0)

def afterclosewindow(win):
    if win.app.ddeflag:
        DDE.stop()
Mixin.setPlugin('mainframe', 'afterclosewindow', afterclosewindow)

def openfiles(win, files):
    if files:
        doc = None
        firstdoc = None
        for filename in files:
            doc = win.editctrl.new(filename, delay=True)
            if not firstdoc:
                firstdoc = doc
        win.Show()
        win.Raise()
        if firstdoc:
            win.editctrl.switch(firstdoc)
Mixin.setMixin('mainframe', 'openfiles', openfiles)



#-----------------------  mLexerFactory.py ------------------

__doc__ = 'Lexer control'

import wx
import os
from modules import Mixin
from modules import common
from modules import dict4ini
from modules import Globals
from LexerFactory import LexerFactory

def call_lexer(win, oldfilename, filename, language):

    lexer_obj = None
    flag = False
    for lexer in win.mainframe.lexers.lexobjs:
        prjfile = common.getProjectFile(filename)
        ini = dict4ini.DictIni(prjfile)
        ext = os.path.splitext(filename)[1]
        lexname = ini.highlight[ext]

        if lexname and lexname == lexer.name:   #find acp option
            if not hasattr(win, 'lexer') or lexname != win.lexer.name:
                lexer_obj = lexer
                flag = True
                break

        if not lexname and (language and language == lexer.name or lexer.matchfile(filename)):
            if not hasattr(win, 'lexer') or lexer.name != win.lexer.name:
                lexer_obj = lexer
                flag = True
                break

    else:
        if not hasattr(win, 'lexer'):
            lexer_obj = Globals.mainframe.lexers.getDefaultLexer()
            flag = True
    if flag:
        lexer_obj.colourize(win)
        wx.CallAfter(Globals.mainframe.editctrl.switch, win)
Mixin.setPlugin('editor', 'call_lexer', call_lexer)
Mixin.setPlugin('dirbrowser', 'call_lexer', call_lexer)


def beforeinit(win):
    win.lexers = LexerFactory(win)
Mixin.setPlugin('mainframe', 'beforeinit', beforeinit)

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_DOCUMENT',
        [
            (130, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (140, 'IDM_DOCUMENT_SYNTAX_HIGHLIGHT', tr('Syntax Highlight...'), wx.ITEM_NORMAL, 'OnDocumentSyntaxHighlight', tr('Specifies the syntax highlight to current document.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def OnDocumentSyntaxHighlight(win, event):
    items = win.lexers.getLexerNames()
    dlg = wx.SingleChoiceDialog(win, tr('Select a syntax highlight:'), tr('Syntax Highlight'), items, wx.CHOICEDLG_STYLE)
    if dlg.ShowModal() == wx.ID_OK:
        lexer = win.lexers.lexobjs[dlg.GetSelection()]
        lexer.colourize(win.document)
        win.editctrl.switch(win.document)
    dlg.Destroy()
Mixin.setMixin('mainframe', 'OnDocumentSyntaxHighlight', OnDocumentSyntaxHighlight)

def add_pref(preflist):
    preflist.extend([
        (tr('General'), 130, 'choice', 'default_lexer', tr('Default syntax highlight:'), LexerFactory.lexnames),
        (tr('Document'), 120, 'check', 'caret_line_visible', tr('Show caret line'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def pref_init(pref):
    pref.default_lexer = 'text'
    pref.caret_line_visible = True
Mixin.setPlugin('preference', 'init', pref_init)

def savepreference(mainframe, pref):
    mainframe.document.SetCaretLineVisible(pref.caret_line_visible)
Mixin.setPlugin('prefdialog', 'savepreference', savepreference)



#-----------------------  mChangeFileType.py ------------------

__doc__ = 'Process changing file type event'

from modules import Mixin

def on_document_lang_enter(win, document):
    win.mainframe.changefiletype.enter(win.mainframe, document)
Mixin.setPlugin('editctrl', 'on_document_lang_enter', on_document_lang_enter)

def on_document_lang_leave(win, filename, languagename):
    win.mainframe.changefiletype.leave(win.mainframe, filename, languagename)
Mixin.setPlugin('editctrl', 'on_document_lang_leave', on_document_lang_leave)

def afterinit(win):
    import ChangeFileType

    win.changefiletype = ChangeFileType.ChangeFileType()
Mixin.setPlugin('mainframe', 'afterinit', afterinit)



#-----------------------  mSyntaxPref.py ------------------

__doc__ = 'syntax preference'

import wx
from modules import common
from modules import Mixin

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_DOCUMENT',
        [
            (150, 'IDM_DOCUMENT_SYNTAX_PREFERENCE', tr('Syntax Preference...'), wx.ITEM_NORMAL, 'OnDocumentSyntaxPreference', tr('Syntax highlight preference setup.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def OnSyntax(win, event):
    from modules import Globals
    Globals.mainframe.OnDocumentSyntaxPreference(None)
Mixin.setMixin('prefdialog', 'OnSyntax', OnSyntax)

def add_pref(preflist):
    preflist.extend([
        (tr('Document'), 160, 'button', 'document_syntax', tr('Setup document syntax highlight'), 'OnSyntax'),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)


def OnDocumentSyntaxPreference(win, event):
    from modules import i18n
    from modules import Resource
    import SyntaxDialog

    syntax_resfile = common.uni_work_file('resources/syntaxdialog.xrc')
    filename = i18n.makefilename(syntax_resfile, win.app.i18n.lang)
    if hasattr(win.document, 'languagename'):
        name = win.document.languagename
    else:
        name = ''
    Resource.loadfromresfile(filename, win, SyntaxDialog.SyntaxDialog, 'SyntaxDialog', win, win.lexers, name).ShowModal()
Mixin.setMixin('mainframe', 'OnDocumentSyntaxPreference', OnDocumentSyntaxPreference)



#-----------------------  mPrint.py ------------------

__doc__ = 'print'

import wx
from modules import Mixin

def add_mainframe_menu(menulist):
    menulist.extend([('IDM_FILE',
        [
            (200, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (210, 'IDM_FILE_PRINT_MENU', tr('Print'), wx.ITEM_NORMAL, '', None),
        ]),
        ('IDM_FILE_PRINT_MENU',
        [
            (100, 'wx.ID_PRINT_SETUP', tr('Page Setup...'), wx.ITEM_NORMAL, 'OnFilePageSetup', tr('Selects a printer and printer connection.')),
            (105, 'IDM_FILE_PRINT_LINENUMBER', tr('Print Line Numbers'), wx.ITEM_CHECK, 'OnFilePrintLineNumber', tr('Prints the line numbers.')),
            (120, 'wx.ID_PREVIEW', tr('Print Preview...'), wx.ITEM_NORMAL, 'OnFilePrintPreview', tr('Displays the document on the screen as it would appear printed.')),
            (130, 'wx.ID_PRINT', tr('Print'), wx.ITEM_NORMAL, 'OnFilePrint', tr('Prints a document.')),
            (140, 'IDM_FILE_HTML', tr('HTML Document'), wx.ITEM_NORMAL, '', None),
        ]),
        ('IDM_FILE_HTML',
        [
            (100, 'IDM_FILE_HTML_PRINT_PREVIEW', tr('HTML Document Preview...'), wx.ITEM_NORMAL, 'OnFileHtmlPreview', tr('Displays the HTML document on the screen as it would appear printed.')),
            (110, 'IDM_FILE_HTML_PRINT', tr('Print HTML Document'), wx.ITEM_NORMAL, 'OnFileHtmlPrint', tr('Prints the current HTML document.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (125, 'print'),
    ])

    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'print':(wx.ITEM_NORMAL, 'wx.ID_PRINT', 'images/printer.gif', tr('Print'), tr('Prints a document.'), 'OnFilePrint'),
    })
Mixin.setPlugin('mainframe', 'add_tool_list', add_tool_list)

def pref_init(pref):
    pref.print_line_number = True
Mixin.setPlugin('preference', 'init', pref_init)

def mainframe_init(win):
    win.printer = None
Mixin.setPlugin('mainframe', 'init', mainframe_init)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_FILE_PRINT_LINENUMBER, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if hasattr(win, 'document') and win.document:
        if eid == win.IDM_FILE_PRINT_LINENUMBER:
            event.Check(win.pref.print_line_number)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

last_printer_type = None
def get_printer(win, t=None):
    global last_printer_type
    if win.printer:
        if t != last_printer_type:
            win.printer.Destroy()
        else:
            return win.printer
    if not t:
        from Print import SimpleDocPrinter
        win.printer = SimpleDocPrinter(win)
    elif t == 'html':
        from Print import MyPrinter
        win.printer = MyPrinter(win)
    last_printer_type = t

    return win.printer

def OnFilePrintLineNumber(win, event):
    win.pref.print_line_number = not win.pref.print_line_number
    win.pref.save()
Mixin.setMixin('mainframe', 'OnFilePrintLineNumber', OnFilePrintLineNumber)

def OnFilePageSetup(win, event):
    if get_printer(win):
        win.printer.PageSetup()
Mixin.setMixin('mainframe', 'OnFilePageSetup', OnFilePageSetup)

def OnFilePrint(win, event):
    if get_printer(win):
        win.printer.Print(win.document.GetText(), win.document.filename)
Mixin.setMixin('mainframe', 'OnFilePrint', OnFilePrint)

def OnFilePrintPreview(win, event):
    if get_printer(win):
        win.printer.PrintPreview(win.document.GetText(), win.document.filename)
Mixin.setMixin('mainframe', 'OnFilePrintPreview', OnFilePrintPreview)


def OnFileHtmlPreview(win, event):
    if get_printer(win, 'html'):
        win.printer.PreviewText(win.document.GetText(), win.document.filename)
Mixin.setMixin('mainframe', 'OnFileHtmlPreview', OnFileHtmlPreview)

def OnFileHtmlPrint(win, event):
    if get_printer(win, 'html'):
        win.printer.Print(win.document.GetText(), win.document.filename)
Mixin.setMixin('mainframe', 'OnFileHtmlPrint', OnFileHtmlPrint)



#-----------------------  mPlugins.py ------------------

__doc__ = 'Plugins manage'

import wx
from modules import Mixin
from modules import common

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_TOOL',
        [
            (130, 'IDM_TOOL_PLUGINS_MANAGE', tr('Plugins Manager...'), wx.ITEM_NORMAL, 'OnDocumentPluginsManage', 'Manages plugins.'),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def OnDocumentPluginsManage(win, event):
    from PluginDialog import PluginDialog

    dlg = PluginDialog(win)
    answer = dlg.ShowModal()
    dlg.Destroy()
Mixin.setMixin('mainframe', 'OnDocumentPluginsManage', OnDocumentPluginsManage)

def afterinit(win):
    win.plugin_imagelist = {
        'uncheck':  'images/uncheck.gif',
        'check':    'images/check.gif',
    }
    win.plugin_initfile = common.get_app_filename(win, 'plugins/__init__.py')
Mixin.setPlugin('mainframe', 'afterinit', afterinit)



#-----------------------  mPythonContextIndent.py ------------------

__doc__ = 'Context indent'

from modules import Mixin
from modules import Globals
import wx
import re

def OnKeyDown(win, event):
    if event.GetKeyCode() == wx.WXK_RETURN:
        if win.GetSelectedText():
            return False
        if win.pref.autoindent and win.pref.python_context_indent and win.languagename == 'python':
            pythonContextIndent(win)
            return True
Mixin.setPlugin('editor', 'on_key_down', OnKeyDown, Mixin.HIGH)

def add_pref(preflist):
    preflist.extend([
        ('Python', 110, 'check', 'python_context_indent', tr('Use context sensitive indent'), None)
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def pref_init(pref):
    pref.python_context_indent = True
Mixin.setPlugin('preference', 'init', pref_init)

def pythonContextIndent(win):
    pos = win.GetCurrentPos()
    if win.languagename == 'python':
        linenumber = win.GetCurrentLine()
        numtabs = win.GetLineIndentation(linenumber) / win.GetTabWidth()
        text = win.GetTextRange(win.PositionFromLine(linenumber), win.GetCurrentPos())
        if text.strip() == '':
            win.AddText(win.getEOLChar()+text)
            win.EnsureCaretVisible()
            return
        if win.pref.python_context_indent:
            linetext = win.GetLine(linenumber).rstrip()
            if linetext:
                if linetext[-1] == ':':
                    numtabs = numtabs + 1
                else:
                    #Remove Comment:
                    comment = linetext.find('#')
                    if comment > -1:
                        linetext = linetext[:comment]
                    #Keyword Search.
                    keyword = re.compile(r"(\sreturn\b)|(\sbreak\b)|(\spass\b)|(\scontinue\b)|(\sraise\b)", re.MULTILINE)
                    slash = re.compile(r"\\\Z")

                    if slash.search(linetext.rstrip()) is None:
                        if keyword.search(linetext) is not None:
                            numtabs = numtabs - 1
        #Go to current line to add tabs
        win.AddText(win.getEOLChar() + win.getIndentChar()*numtabs)
        win.EnsureCaretVisible()

def pref_init(pref):
    pref.paste_auto_indent = True
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('Document')+'/'+tr('Edit'), 150, 'check', 'paste_auto_indent', tr('Autoindent when pasting text block'), None)
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

re_spaces = re.compile(r'^(\s*)')
re_eol = re.compile(r'\r\n|\r|\n')
re_eol_end = re.compile(r'\r\n$|\r$|\n$', re.MULTILINE)

def Indent_paste(mainframe, win, content):
    if win.pref.paste_auto_indent and not win.selection_column_mode:
        b = re_eol.search(content)
        if not b:
            return False
        win.BeginUndoAction()
        try:
            if win.GetSelectedText():
                win.ReplaceSelection('')
            col = win.GetColumn(win.GetCurrentPos())
            line = win.getLineText(win.GetCurrentLine())
            indent = 0
            if line[:col].strip() == '':
                b = re_spaces.search(line)
                if b:
                    indent = len(b.group().expandtabs(win.GetTabWidth()))
                else:
                    indent = 0

                col = 0
                win.GotoPos(win.PositionFromLine(win.GetCurrentLine()))

            tabs, spaces = divmod(indent, win.GetTabWidth())
            if win.usetab:
                indentchars = '\t'*tabs + ' '*spaces
            else:
                indentchars = ' ' * indent

            hasendeol = False
            b = re_eol_end.search(content)
            if b:
                hasendeol = True
            minspaces = []
            contentlines = re_eol.sub(win.getEOLChar(), content).splitlines()
            for line in contentlines:
                #skip blank line
                if not line.strip():
                    continue
                b = re_spaces.search(line)
                if b:
                    minspaces.append(b.span()[1])

            minspace = min(minspaces)
            if col == 0:
                lines = [indentchars + x[minspace:] for x in contentlines[:1]]
            else:
                lines = [x[minspace:] for x in contentlines[:1]]
            lines.extend([indentchars + x[minspace:] for x in contentlines[1:]])
            if win.GetSelectedText():
                win.ReplaceSelection('')
            if hasendeol:
                win.AddText(win.getEOLChar().join(lines + ['']))
            else:
                win.AddText(win.getEOLChar().join(lines))
            win.EnsureCaretVisible()
        finally:
            win.EndUndoAction()
        return True
    elif win.selection_column_mode:
        col = win.GetColumn(win.GetCurrentPos())
        line = win.GetCurrentLine()
        lines = content.splitlines()
        win.BeginUndoAction()
        endline = min(len(lines) + line, win.GetLineCount())
        i = 0
        while line+i < endline:
            pos = min(win.PositionFromLine(line+i) + col, win.GetLineEndPosition(line+i))
            win.GotoPos(pos)
            win.AddText(lines[i])
            i += 1
        win.EnsureCaretVisible()
        win.EndUndoAction()
        return True
    else:
        return False
Mixin.setMixin('mainframe', 'Indent_paste', Indent_paste)

def on_paste(win, content):
    return Globals.mainframe.Indent_paste(win, content)
Mixin.setPlugin('editor', 'on_paste', on_paste)



#-----------------------  mFtp.py ------------------

__doc__ = 'ftp manage'

import wx
from modules import Mixin
from modules.Debug import error
from modules import common

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_WINDOW',
        [
            (160, 'IDM_WINDOW_FTP', tr('FTP Window'), wx.ITEM_CHECK, 'OnWindowFtp', tr('Shows the FTP pane.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def afterinit(win):
    win.ftp_imagelist = {
    'close':            'images/folderclose.gif',
    'document':         'images/file.gif',
    'parentfold':       'images/parentfold.gif',
}
    win.ftp_resfile = common.uni_work_file('resources/ftpmanagedialog.xrc')
    win.ftp = None
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDM_WINDOW_FTP:
        event.Check(bool(win.panel.getPage('FTP')) and win.panel.BottomIsVisible)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_WINDOW_FTP, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def on_notebook_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDPM_FTPWINDOW:
        event.Check(bool(win.panel.getPage('FTP')) and win.panel.BottomIsVisible)
Mixin.setPlugin('notebook', 'on_update_ui', on_notebook_updateui)

def init(win):
    wx.EVT_UPDATE_UI(win, win.IDPM_FTPWINDOW, win.OnUpdateUI)
Mixin.setPlugin('notebook', 'init', init)

def add_editor_menu(popmenulist):
    popmenulist.extend([ (None,
        [
            (150, 'IDPM_FTPWINDOW', tr('FTP Window'), wx.ITEM_CHECK, 'OnFtpWindow', tr('Shows the FTP pane.')),
        ]),
    ])
Mixin.setPlugin('notebook', 'add_menu', add_editor_menu)

def createFtpWindow(win, side='bottom'):
    page = win.panel.getPage('FTP')
    if not page:
        from FtpClass import Ftp

        page = Ftp(win.panel.createNotebook(side), win)
        win.panel.addPage(side, page, 'FTP')
    win.ftp = page
Mixin.setMixin('mainframe', 'createFtpWindow', createFtpWindow)

def OnWindowFtp(win, event):
    if not win.panel.getPage('FTP'):
        win.createFtpWindow()
        win.panel.showPage('FTP')
    else:
        win.panel.closePage('FTP')
Mixin.setMixin('mainframe', 'OnWindowFtp', OnWindowFtp)

def OnFtpWindow(win, event):
    if not win.panel.getPage('FTP'):
        win.mainframe.createFtpWindow('bottom')
        win.panel.showPage('FTP')
    else:
        win.panel.closePage('FTP')
Mixin.setMixin('notebook', 'OnFtpWindow', OnFtpWindow)

def pref_init(pref):
    pref.ftp_sites = []
    pref.sites_info = {}
    pref.last_ftp_site = 0
    pref.remote_paths = []
Mixin.setPlugin('preference', 'init', pref_init)

def afterclosewindow(win):
    if win.ftp and win.ftp.alive:
        try:
            win.ftp.ftp.quit()
        except:
            error.traceback()
Mixin.setPlugin('mainframe', 'afterclosewindow', afterclosewindow)

def add_ftp_menu(popmenulist):
    popmenulist.extend([ (None, #parent menu id
        [
            (100, 'IDPM_OPEN', tr('Open'), wx.ITEM_NORMAL, 'OnOpen', tr('Opens a file or a directory.')),
            (110, 'IDPM_NEWFILE', tr('New File'), wx.ITEM_NORMAL, 'OnNewFile', tr('Creates a new file.')),
            (120, 'IDPM_NEWDIR', tr('New Directory'), wx.ITEM_NORMAL, 'OnNewDir', tr('Creates a new directory.')),
            (130, 'IDPM_DELETE', tr('Delete'), wx.ITEM_NORMAL, 'OnDelete', tr('Deletes the selected file or a directory.')),
            (140, 'IDPM_RENAME', tr('Rename'), wx.ITEM_NORMAL, 'OnRename', tr('Renames the selected file or a directory.')),
            (150, '-', '', wx.ITEM_SEPARATOR, '', ''),
            (160, 'IDPM_REFRESH', tr('Refresh'), wx.ITEM_NORMAL, 'OnRefresh', tr('Refreshes the current directory.')),
            (170, '-', '', wx.ITEM_SEPARATOR, '', ''),
            (180, 'IDPM_UPLOAD', tr('Upload'), wx.ITEM_NORMAL, 'OnUpload', tr('Uploads a file.')),
            (190, 'IDPM_DOWNLOAD', tr('Download'), wx.ITEM_NORMAL, 'OnDownload', tr('Downloads a file.')),
        ]),
    ])
Mixin.setPlugin('ftpclass', 'add_menu', add_ftp_menu)

def OnOpen(win, event):
    win.OnEnter(event)
Mixin.setMixin('ftpclass', 'OnOpen', OnOpen)

def OnNewFile(win, event):
    win.newfile()
Mixin.setMixin('ftpclass', 'OnNewFile', OnNewFile)

def OnNewDir(win, event):
    win.newdir()
Mixin.setMixin('ftpclass', 'OnNewDir', OnNewDir)

def OnDelete(win, event):
    win.delete()
Mixin.setMixin('ftpclass', 'OnDelete', OnDelete)

def OnRename(win, event):
    win.rename()
Mixin.setMixin('ftpclass', 'OnRename', OnRename)

def OnUpload(win, event):
    win.upload()
Mixin.setMixin('ftpclass', 'OnUpload', OnUpload)

def OnDownload(win, event):
    win.download()
Mixin.setMixin('ftpclass', 'OnDownload', OnDownload)

def readfiletext(win, filename, stext):
    import re

    re_ftp = re.compile('^ftp\((\d+)\):')
    b = re_ftp.search(filename)
    if b:
        siteno = int(b.group(1))
        filename = filename.split(':', 1)[1]
        from FtpClass import readfile
        text = readfile(win.mainframe, filename, siteno)
        if text:
            win.needcheckfile = False
            if text is not None:
                stext.append(text)
            else:
                stext.append(None)
            return True, True
        else:
            return True, False
Mixin.setPlugin('editor', 'readfiletext', readfiletext)

def writefiletext(win, filename, text):
    import re

    re_ftp = re.compile('^ftp\((\d+)\):')
    b = re_ftp.search(filename)
    if b:
        siteno = int(b.group(1))
        filename = filename.split(':', 1)[1]
        from FtpClass import writefile
        flag = writefile(win.mainframe, filename, siteno, text)
        return True, True, flag
Mixin.setPlugin('editor', 'writefiletext', writefiletext)

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (127, 'ftp'),
    ])

    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'ftp':(wx.ITEM_CHECK, 'IDM_WINDOW_FTP', 'images/ftp.gif', tr('FTP'), tr('Shows the FTP pane.'), 'OnWindowFtp'),
    })
Mixin.setPlugin('mainframe', 'add_tool_list', add_tool_list)

def getShortFilename(win):
    import re
    import os.path

    if win.title:
        return win.title

    re_ftp = re.compile('^ftp\((\d+)\):')
    b = re_ftp.search(win.filename)
    if b:
        return os.path.basename(win.filename.split(':', 1)[1])
    else:
        return os.path.basename(win.getFilename())
Mixin.setMixin('editor', 'getShortFilename', getShortFilename)



#-----------------------  mWindow.py ------------------

import wx
from modules import Mixin
from modules import Globals

def add_mainframe_menu(menulist):
    menulist.extend([(None,
        [
            (890, 'IDM_WINDOW', tr('Windows'), wx.ITEM_NORMAL, '', ''),
        ]),
        ('IDM_WINDOW',
        [
            (100, 'IDM_WINDOW_LEFT', tr('Left Window')+'\tAlt+Z', wx.ITEM_CHECK, 'OnWindowLeft', tr('Shows the left pane.')),
            (110, 'IDM_WINDOW_BOTTOM', tr('Bottom Window')+'\tAlt+X', wx.ITEM_CHECK, 'OnWindowBottom', tr('Shows the bottom pane.')),
            (120, '-', '', wx.ITEM_SEPARATOR, '', ''),
            (130, 'IDM_WINDOW_SHELL', tr('Shell Window'), wx.ITEM_CHECK, 'OnWindowShell', tr('Shows the Shell pane.')),
            (140, 'IDM_WINDOW_MESSAGE', tr('Messages Window'), wx.ITEM_CHECK, 'OnWindowMessage', tr('Shows the Messages pane.')),
        ]),
        ('IDM_EDIT',
        [
            (280, '-', '', wx.ITEM_SEPARATOR, '', ''),
            (290, 'IDM_EDIT_CLEARSHELL', tr('Clear Shell Contents') + '\tCtrl+Alt+R', wx.ITEM_NORMAL, 'OnEditClearShell', tr('Clears the contents of the shell.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)


def OnWindowLeft(win, event):
    flag = not win.panel.LeftIsVisible

    win.panel.showWindow('left', flag)
Mixin.setMixin('mainframe', 'OnWindowLeft', OnWindowLeft)

def OnWindowBottom(win, event):
    flag = not win.panel.BottomIsVisible

    win.panel.showWindow('bottom', flag)
    if flag:
        if not win.panel.bottombook or win.panel.bottombook.GetPageCount() == 0:
            win.panel.showPage(_shell_page_name)
Mixin.setMixin('mainframe', 'OnWindowBottom', OnWindowBottom)

_shell_page_name = tr('Shell')
_message_page_name = tr('Messages')
def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDM_WINDOW_LEFT:
        event.Check(win.panel.LeftIsVisible)
    elif eid == win.IDM_WINDOW_BOTTOM:
        event.Check(win.panel.BottomIsVisible)
    elif eid == win.IDM_WINDOW_SHELL:
        event.Check(bool(win.panel.getPage(_shell_page_name)))
    elif eid == win.IDM_WINDOW_MESSAGE:
        event.Check(bool(win.panel.getPage(_message_page_name)))
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_WINDOW_LEFT, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_WINDOW_BOTTOM, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_WINDOW_SHELL, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_WINDOW_MESSAGE, win.OnUpdateUI)
    win.messagewindow = None
    win.shellwindow = None
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def on_notebook_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDPM_SHELLWINDOW:
        event.Check(bool(Globals.mainframe.panel.getPage(_shell_page_name)) and win.panel.BottomIsVisible)
    if eid == win.IDPM_MESSAGEWINDOW:
        event.Check(bool(Globals.mainframe.panel.getPage(_message_page_name)) and win.panel.BottomIsVisible)
Mixin.setPlugin('notebook', 'on_update_ui', on_notebook_updateui)

def init(win):
    wx.EVT_UPDATE_UI(win, win.IDPM_SHELLWINDOW, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDPM_MESSAGEWINDOW, win.OnUpdateUI)
Mixin.setPlugin('notebook', 'init', init)

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (450, 'left'),
        (500, 'bottom'),
        (510, 'shell'),
    ])

    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'left':(wx.ITEM_CHECK, 'IDM_WINDOW_LEFT', 'images/left.gif', tr('Toggle Left Pane'), tr('Shows or hides the left pane.'), 'OnWindowLeft'),
        'bottom':(wx.ITEM_CHECK, 'IDM_WINDOW_BOTTOM', 'images/bottom.gif', tr('Toggle Bottom Pane'), tr('Shows or hides the bottom pane.'), 'OnWindowBottom'),
        'shell':(wx.ITEM_CHECK, 'IDM_WINDOW_SHELL', 'images/shell.gif', tr('Toggle Shell Pane'), tr('Shows or hides the Shell pane.'), 'OnWindowShell'),
    })
Mixin.setPlugin('mainframe', 'add_tool_list', add_tool_list)

def createShellWindow(win):
    side = Globals.pref.shell_window_side
    if not win.panel.getPage(_shell_page_name):
        from ShellWindow import ShellWindow

        page = ShellWindow(win.panel.createNotebook(side), win)
        win.panel.addPage(side, page, _shell_page_name)
    win.shellwindow = win.panel.getPage(_shell_page_name)
Mixin.setMixin('mainframe', 'createShellWindow', createShellWindow)

def createMessageWindow(win):
    if not win.panel.getPage(_message_page_name):
        from MessageWindow import MessageWindow

        page = MessageWindow(win.panel.createNotebook('bottom'), win)
        win.panel.addPage('bottom', page, _message_page_name)
    win.messagewindow = win.panel.getPage(_message_page_name)
Mixin.setMixin('mainframe', 'createMessageWindow', createMessageWindow)

def OnWindowShell(win, event):
    if not win.panel.getPage(_shell_page_name):
        win.createShellWindow()
        win.panel.showPage(_shell_page_name)
    else:
        win.panel.closePage(_shell_page_name)
Mixin.setMixin('mainframe', 'OnWindowShell', OnWindowShell)

def OnWindowMessage(win, event):
    if not win.panel.getPage(_message_page_name):
        win.createMessageWindow()
        win.panel.showPage(_message_page_name)
    else:
        win.panel.closePage(_message_page_name)
Mixin.setMixin('mainframe', 'OnWindowMessage', OnWindowMessage)

def add_editor_menu(popmenulist):
    popmenulist.extend([ (None,
        [
            (120, 'IDPM_SHELLWINDOW', tr('Shell Pane'), wx.ITEM_CHECK, 'OnShellWindow', tr('Shows the Shell pane.')),
            (130, 'IDPM_MESSAGEWINDOW', tr('Messages Pane'), wx.ITEM_CHECK, 'OnMessageWindow', tr('Shows the Messages pane.')),
        ]),
    ])
Mixin.setPlugin('notebook', 'add_menu', add_editor_menu)

def OnShellWindow(win, event):
    if not win.panel.getPage(_shell_page_name):
        win.mainframe.createShellWindow()
        win.panel.showPage(_shell_page_name)
    else:
        win.panel.closePage(_shell_page_name)
Mixin.setMixin('notebook', 'OnShellWindow', OnShellWindow)

def OnMessageWindow(win, event):
    if not win.panel.getPage(_message_page_name):
        win.mainframe.createMessageWindow()
        win.panel.showPage(_message_page_name)
    else:
        win.panel.closePage(_message_page_name)
Mixin.setMixin('notebook', 'OnMessageWindow', OnMessageWindow)

def OnEditClearShell(win, event):
    shellwin = win.panel.getPage(_shell_page_name)
    if shellwin:
        shellwin.clear()
        shellwin.prompt()
Mixin.setMixin('mainframe', 'OnEditClearShell', OnEditClearShell)

def add_pref(preflist):
    preflist.extend([
        (tr('Python'), 180, 'choice', 'shell_window_side', tr('Placement of the Shell pane is:'),
            [('Left', 'left'), ('Bottom', 'bottom')])
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def pref_init(pref):
    pref.shell_window_side = 'bottom'
Mixin.setPlugin('preference', 'init', pref_init)



#-----------------------  mRegister.py ------------------

import wx
import os
import sys
from modules import Mixin
from modules.Debug import error
from modules import common


if wx.Platform == '__WXMSW__':
    import _winreg

    def add_mainframe_menu(menulist):
        menulist.extend([ ('IDM_TOOL',
            [
                (890, '-', '', wx.ITEM_SEPARATOR, '', ''),
                (900, 'IDM_TOOL_REGISTER', tr('Register To Windows Explorer'), wx.ITEM_NORMAL, 'OnToolRegister', tr('Registers UliPad to the context menu of Windows Explorer.')),
                (910, 'IDM_TOOL_UNREGISTER', tr('Unregister From Windows Explorer'), wx.ITEM_NORMAL, 'OnToolUnRegister', tr('Unregisters UliPad from the context menu of Windows Explorer.')),
            ]),
        ])
    Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

    def OnToolRegister(win, event):
        try:
            key = _winreg.OpenKey(_winreg.HKEY_CLASSES_ROOT, '*', _winreg.KEY_ALL_ACCESS)
            filename = os.path.basename(sys.argv[0])
            f, ext = os.path.splitext(filename)
            if ext == '.exe':
                command = '"%s" "%%L"' % os.path.normpath(common.uni_work_file(filename))
            else:
                path = os.path.normpath(common.uni_work_file('%s.pyw' % f))
                execute = sys.executable.replace('python.exe', 'pythonw.exe')
                command = '"%s" "%s" "%%L"' % (execute, path)
            _winreg.SetValue(key, 'shell\\UliPad\\command', _winreg.REG_SZ, common.encode_string(command, common.defaultfilesystemencoding))
            common.note(tr('Done'))
        except:
            error.traceback()
            wx.MessageDialog(win, tr('Registering UliPad to the context menu of Windows Explorer failed.'), tr("Error"), wx.OK | wx.ICON_EXCLAMATION).ShowModal()
    Mixin.setMixin('mainframe', 'OnToolRegister', OnToolRegister)

    def OnToolUnRegister(win, event):
        try:
            key = _winreg.OpenKey(_winreg.HKEY_CLASSES_ROOT, '*\\shell', _winreg.KEY_ALL_ACCESS)
            _winreg.DeleteKey(key, 'UliPad\\command')
            _winreg.DeleteKey(key, 'UliPad')
            common.note(tr('Successful!'))
        except:
            error.traceback()
            wx.MessageDialog(win, tr('Unregistering UliPad from the context menu of Windows Explorer failed.'), tr("Error"), wx.OK | wx.ICON_EXCLAMATION).ShowModal()
    Mixin.setMixin('mainframe', 'OnToolUnRegister', OnToolUnRegister)



#-----------------------  mConvert.py ------------------

import wx
from modules import Mixin
from modules.Debug import error
from modules import common

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_EDIT',
        [
            (270, 'IDM_EDIT_CONVERT', tr('Convert'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDM_EDIT_CONVERT',
        [
            (100, 'IDM_EDIT_CONVERT_OUTPUTHTMLWINDOW', tr('Output To HTML Window'), wx.ITEM_RADIO, 'OnConvertOutput', tr('Outputs converted text in HTML window.')),
            (110, 'IDM_EDIT_CONVERT_OUTPUTMESSAGEWINDOW', tr('Output To Message Window'), wx.ITEM_RADIO, 'OnConvertOutput', tr('Outputs converted text in message window.')),
            (120, 'IDM_EDIT_CONVERT_REPLACEHERE', tr('Replace Selected Text'), wx.ITEM_RADIO, 'OnConvertOutput', tr('Replaces selected text with converted text.')),
            (130, '', '-', wx.ITEM_SEPARATOR, '', ''),
            (140, 'IDM_EDIT_CONVERT_DIRECT', tr('Output Directly To HTML Window'), wx.ITEM_NORMAL, 'OnConvertOutputDirectly', tr('Outputs directly the text in HTML window.')),
            (150, 'IDM_EDIT_CONVERT_REST2HTML', tr('reSt To HTML'), wx.ITEM_NORMAL, 'OnConvertRest2Html', tr('Converts reStructuredText source to HTML.')),
            (160, 'IDM_EDIT_CONVERT_PY2HTML', tr('Py To HTML'), wx.ITEM_NORMAL, 'OnConvertPy2Html', tr('Converts python source to HTML.')),
            (170, 'IDM_EDIT_CONVERT_TEXTILE2HTML', tr('Textile To HTML'), wx.ITEM_NORMAL, 'OnConvertTextile2Html', tr('Converts textile source to HTML.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_editor_menu(popmenulist):
    popmenulist.extend([ (None,
        [
            (240, 'IDPM_EDIT_CONVERT', tr('Convert'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDPM_EDIT_CONVERT',
        [
            (100, 'IDPM_EDIT_CONVERT_OUTPUTHTMLWINDOW', tr('Output To HTML Window'), wx.ITEM_RADIO, 'OnConvertOutput', tr('Outputs converted text in HTML window.')),
            (110, 'IDPM_EDIT_CONVERT_OUTPUTMESSAGEWINDOW', tr('Output To Message Window'), wx.ITEM_RADIO, 'OnConvertOutput', tr('Outputs converted text in message window.')),
            (120, 'IDPM_EDIT_CONVERT_REPLACEHERE', tr('Replace Selected Text'), wx.ITEM_RADIO, 'OnConvertOutput', tr('Replaces selected text with converted text.')),
            (130, '', '-', wx.ITEM_SEPARATOR, '', ''),
            (140, 'IDPM_EDIT_CONVERT_DIRECT', tr('Output Directly To HTML Window'), wx.ITEM_NORMAL, 'OnOutputDirectly', tr('Outputs directly the text in HTML window.')),
            (150, 'IDPM_EDIT_CONVERT_REST2HTML', tr('reSt To HTML'), wx.ITEM_NORMAL, 'OnRest2Html', tr('Converts reStructuredText source to HTML.')),
            (160, 'IDPM_EDIT_CONVERT_PY2HTML', tr('Py To HTML'), wx.ITEM_NORMAL, 'OnPy2Html', tr('Converts python source to HTML.')),
            (170, 'IDPM_EDIT_CONVERT_TEXTILE2HTML', tr('Textile To HTML'), wx.ITEM_NORMAL, 'OnTextile2Html', tr('Converts textile source to HTML.')),
        ]),
    ])
Mixin.setPlugin('editor', 'add_menu', add_editor_menu)


def OnConvertOutputDirectly(win, event):
    text = win.document.GetSelectedText()
    output_text(win, text, mode=0)
Mixin.setMixin('mainframe', 'OnConvertOutputDirectly', OnConvertOutputDirectly)

def OnOutputDirectly(win, event):
    win.mainframe.OnConvertOutputDirectly(event)
Mixin.setMixin('editor', 'OnOutputDirectly', OnOutputDirectly)

def OnConvertRest2Html(win, event):
    try:
        def html_fragment(input_string, source_path=None, destination_path=None,
                       input_encoding='unicode', doctitle=1, initial_header_level=1):
            from docutils import core

            overrides = {'input_encoding': input_encoding,
                         'doctitle_xform': doctitle,
                         'initial_header_level': initial_header_level}
            parts = core.publish_parts(
                source=input_string, source_path=source_path,
                destination_path=destination_path,
                writer_name='html', settings_overrides=overrides)
            fragment = parts['fragment']
            return fragment

        text = win.document.GetSelectedText()
        otext = html_fragment(text)
        output_text(win, otext)
    except Exception, msg:
        error.traceback()
        common.showerror(win, msg)
Mixin.setMixin('mainframe', 'OnConvertRest2Html', OnConvertRest2Html)

def OnRest2Html(win, event):
    win.mainframe.OnConvertRest2Html(event)
Mixin.setMixin('editor', 'OnRest2Html', OnRest2Html)

def OnConvertTextile2Html(win, event):
    try:
        import textile
    except:
        error.traceback()
        common.showmessage(win, tr("You should install textile module first!"))

    class MyTextiler(textile.Textiler):
        def process(self, head_offset=textile.HEAD_OFFSET):
            self.head_offset = head_offset

            # Process each block.
            self.blocks = self.split_text()

            text = []
            for [function, captures] in self.blocks:
                text.append(function(**captures))

            text = '\n\n'.join(text)

            # Add titles to footnotes.
            text = self.footnotes(text)


            return text
    try:
        text = win.document.GetSelectedText()
        t = MyTextiler(text)
        otext = t.process()

        output_text(win, otext)
    except Exception, msg:
        error.traceback()
        common.showerror(win, msg)
Mixin.setMixin('mainframe', 'OnConvertTextile2Html', OnConvertTextile2Html)

def OnTextile2Html(win, event):
    win.mainframe.OnConvertTextile2Html(event)
Mixin.setMixin('editor', 'OnTextile2Html', OnTextile2Html)

def OnConvertPy2Html(win, event):
    from modules import colourize

    text = win.document.GetSelectedText()
    otext = colourize.Parser(text).format()

    output_text(win, otext)
Mixin.setMixin('mainframe', 'OnConvertPy2Html', OnConvertPy2Html)

def OnPy2Html(win, event):
    win.mainframe.OnConvertPy2Html(event)
Mixin.setMixin('editor', 'OnPy2Html', OnPy2Html)

def OnConvertOutput(win, event):
    eid = event.GetId()
    if eid == win.IDM_EDIT_CONVERT_OUTPUTHTMLWINDOW:
        win.pref.converted_output = 0
    elif eid == win.IDM_EDIT_CONVERT_OUTPUTMESSAGEWINDOW:
        win.pref.converted_output = 1
    elif eid == win.IDM_EDIT_CONVERT_REPLACEHERE:
        win.pref.converted_output = 2
    win.pref.save()
Mixin.setMixin('mainframe', 'OnConvertOutput', OnConvertOutput)

def OnConvertOutput(win, event):
    eid = event.GetId()
    if eid == win.IDPM_EDIT_CONVERT_OUTPUTHTMLWINDOW:
        win.pref.converted_output = 0
    elif eid == win.IDPM_EDIT_CONVERT_OUTPUTMESSAGEWINDOW:
        win.pref.converted_output = 1
    elif eid == win.IDPM_EDIT_CONVERT_REPLACEHERE:
        win.pref.converted_output = 2
    win.pref.save()
Mixin.setMixin('editor', 'OnConvertOutput', OnConvertOutput)

def mainframe_init(win):
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_CONVERT_REST2HTML, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_CONVERT_PY2HTML, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_CONVERT_TEXTILE2HTML, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_CONVERT_OUTPUTHTMLWINDOW, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_CONVERT_DIRECT, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_CONVERT_OUTPUTMESSAGEWINDOW, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_CONVERT_REPLACEHERE, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'init', mainframe_init)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if hasattr(win, 'document') and win.document:
        if eid in [win.IDM_EDIT_CONVERT_DIRECT, win.IDM_EDIT_CONVERT_REST2HTML,
            win.IDM_EDIT_CONVERT_PY2HTML, win.IDM_EDIT_CONVERT_TEXTILE2HTML]:
            event.Enable(win.document.GetSelectedText and len(win.document.GetSelectedText()) > 0)
        elif eid == win.IDM_EDIT_CONVERT_OUTPUTHTMLWINDOW:
            event.Check(win.pref.converted_output == 0)
        elif eid == win.IDM_EDIT_CONVERT_OUTPUTMESSAGEWINDOW:
            event.Check(win.pref.converted_output == 1)
        elif eid == win.IDM_EDIT_CONVERT_REPLACEHERE:
            event.Check(win.pref.converted_output == 2)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def editor_init(win):
    wx.EVT_UPDATE_UI(win, win.IDPM_EDIT_CONVERT_REST2HTML, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDPM_EDIT_CONVERT_PY2HTML, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDPM_EDIT_CONVERT_TEXTILE2HTML, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDPM_EDIT_CONVERT_DIRECT, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDPM_EDIT_CONVERT_OUTPUTHTMLWINDOW, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDPM_EDIT_CONVERT_OUTPUTMESSAGEWINDOW, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDPM_EDIT_CONVERT_REPLACEHERE, win.OnUpdateUI)
Mixin.setPlugin('editor', 'init', editor_init)

def on_editor_updateui(win, event):
    eid = event.GetId()
    if eid in [win.IDPM_EDIT_CONVERT_DIRECT, win.IDPM_EDIT_CONVERT_REST2HTML,
        win.IDPM_EDIT_CONVERT_PY2HTML, win.IDPM_EDIT_CONVERT_TEXTILE2HTML]:
        event.Enable(len(win.GetSelectedText()) > 0)
    elif eid == win.IDPM_EDIT_CONVERT_OUTPUTHTMLWINDOW:
        event.Check(win.pref.converted_output == 0)
    elif eid == win.IDPM_EDIT_CONVERT_OUTPUTMESSAGEWINDOW:
        event.Check(win.pref.converted_output == 1)
    elif eid == win.IDPM_EDIT_CONVERT_REPLACEHERE:
        event.Check(win.pref.converted_output == 2)
Mixin.setPlugin('editor', 'on_update_ui', on_editor_updateui)

def pref_init(pref):
    pref.converted_output = 0
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('Document'), 150, 'choice', 'converted_output', tr('Choose where converted text is to be outputted:'), [tr('To HTML window'), tr('To message window'), tr('Replace selected text')]),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def output_text(mainframe, text, mode=-1):
    win = mainframe

    if mode == -1:
        mode = win.pref.converted_output

    if mode == 0:
        from HtmlPage import HtmlDialog

        ot = """<html>
<head>
   <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
</head>
<body>
%s
</body>
</html>
""" % text.encode('utf-8')

        HtmlDialog(win, tr('Html Convertion'), ot).ShowModal()
    elif mode == 1:
        win.createMessageWindow()
        win.panel.showPage(tr('Messages'))
        win.messagewindow.SetText(text)
    elif mode == 2:
        win.document.ReplaceSelection(text)



#-----------------------  mHtmlFileType.py ------------------

__doc__ = 'Html syntax highlitght process'

import wx
from modules import Mixin
import FiletypeBase
from modules import Globals

class HtmlFiletype(FiletypeBase.FiletypeBase):

    __mixinname__ = 'htmlfiletype'
    menulist = [ (None,
        [
            (890, 'IDM_HTML', 'HTML', wx.ITEM_NORMAL, None, ''),
        ]),
    ]
    toollist = []               #your should not use supperclass's var
    toolbaritems= {}

def add_filetypes(filetypes):
    filetypes.extend([('html', HtmlFiletype)])
Mixin.setPlugin('changefiletype', 'add_filetypes', add_filetypes)

def add_html_menu(menulist):
    menulist.extend([('IDM_HTML', #parent menu id
            [
                (100, 'IDM_HTML_BROWSER_LEFT', tr('View HTML Content In Left Pane'), wx.ITEM_NORMAL, 'OnHtmlBrowserInLeft', tr('Views html content in left pane.')),
                (110, 'IDM_HTML_BROWSER_BOTTOM', tr('View HTML Content In Bottom Pane'), wx.ITEM_NORMAL, 'OnHtmlBrowserInBottom', tr('Views html content in bottom pane.')),
            ]),
    ])
Mixin.setPlugin('htmlfiletype', 'add_menu', add_html_menu)

def OnHtmlBrowserInLeft(win, event):
    dispname = win.createHtmlViewWindow('left', Globals.mainframe.editctrl.getCurDoc())
    if dispname:
        win.panel.showPage(dispname)
Mixin.setMixin('mainframe', 'OnHtmlBrowserInLeft', OnHtmlBrowserInLeft)

def OnHtmlBrowserInBottom(win, event):
    dispname = win.createHtmlViewWindow('bottom', Globals.mainframe.editctrl.getCurDoc())
    if dispname:
        win.panel.showPage(dispname)
Mixin.setMixin('mainframe', 'OnHtmlBrowserInBottom', OnHtmlBrowserInBottom)

def createHtmlViewWindow(win, side, document):
    dispname = document.getShortFilename()
    obj = None
    for pagename, panelname, notebook, page in win.panel.getPages():
        if is_htmlview(page, document):
            obj = page
            break

    if not obj:
        if win.document.documenttype == 'texteditor':
            from mixins import HtmlPage
            page = HtmlPage.HtmlImpactView(win.panel.createNotebook(side), document.getRawText())
            page.document = win.document    #save document object
            page.htmlview = True
            win.panel.addPage(side, page, dispname)
            win.panel.setImageIndex(page, 'html')
            return page
    else:
        obj.load(document.getRawText())
        return obj
Mixin.setMixin('mainframe', 'createHtmlViewWindow', createHtmlViewWindow)

def other_popup_menu(editctrl, document, menus):
    if document.documenttype == 'texteditor' and document.languagename == 'html':
        menus.extend([ (None,
            [
                (920, 'IDPM_HTML_VIEW_LEFT', tr('View Html Content in Left Pane'), wx.ITEM_NORMAL, 'OnHtmlHtmlViewLeft', tr('Views html content in left pane.')),
                (930, 'IDPM_HTML_VIEW_BOTTOM', tr('View Html Content in Bottom Pane'), wx.ITEM_NORMAL, 'OnHtmlHtmlViewBottom', tr('Views html content in bottom pane.')),
            ]),
        ])
Mixin.setPlugin('editctrl', 'other_popup_menu', other_popup_menu)

def OnHtmlHtmlViewLeft(win, event=None):
    win.mainframe.OnHtmlBrowserInLeft(None)
Mixin.setMixin('editctrl', 'OnHtmlHtmlViewLeft', OnHtmlHtmlViewLeft)

def OnHtmlHtmlViewBottom(win, event=None):
    win.mainframe.OnHtmlBrowserInBottom(None)
Mixin.setMixin('editctrl', 'OnHtmlHtmlViewBottom', OnHtmlHtmlViewBottom)

def setfilename(document, filename):
    for pagename, panelname, notebook, page in Globals.mainframe.panel.getPages():
        if is_htmlview(page, document):
            title = document.getShortFilename()
            Globals.mainframe.panel.setName(page, title)
Mixin.setPlugin('editor', 'setfilename', setfilename)

def closefile(win, document, filename):
    for pagename, panelname, notebook, page in Globals.mainframe.panel.getPages():
        if is_htmlview(page, document):
            Globals.mainframe.panel.closePage(page)
Mixin.setPlugin('mainframe', 'closefile', closefile)

def is_htmlview(page, document):
    if hasattr(page, 'htmlview') and page.htmlview and page.document is document:
        return True
    else:
        return False



#-----------------------  mHotKey.py ------------------

from modules import Mixin
from modules import common
from modules.Debug import error

def init_accelerator(win, accellist, editoraccellist):
    ini = common.get_config_file_obj(onelevel=True)

    keylist = {}
    for mid, v in accellist.items():
        keys, func = v
        if not keys:
            continue
        if not keys in keylist:
            keylist[keys] = (mid, 'main')
        else:
            error.error('There is already %s defined! Please check.' % keys)

    for mid, v in editoraccellist.items():
        keys, func = v
        if not keys in keylist:
            keylist[keys] = (mid, 'editor')
        else:
            error.error('There is already %s defined! Please check.' % keys)

    #mid can be a mainframe menu ID or a mainframe function name
    #which should only has one parameter
    for mid, hotkey in ini.main_hotkey.items():
        _id, _t = keylist.get(hotkey, ('', ''))
        if _id:
            if _t == 'main':
                keys, func = accellist[_id]
                accellist[_id] = ('', func)
            else:
                keys, func = editoraccellist[_id]
                editoraccellist[_id] = ('', func)

        if mid in editoraccellist:
            keys, func = editoraccellist[mid]
            del editoraccellist[mid]
            accellist[mid] = (hotkey, func)
        elif mid in accellist:
            keys, func = accellist[mid]
            accellist[mid] = (hotkey, func)

    #mid can be a editor menu ID or a editor function name
    #which should only has one parameter
    for mid, hotkey in ini.editor_hotkey.items():
        _id, _t = keylist.get(hotkey, ('', ''))
        if _id:
            if _t == 'main':
                keys, func = accellist[_id]
                accellist[_id] = ('', func)
            else:
                keys, func = editoraccellist[_id]
                editoraccellist[_id] = ('', func)

        if accellist.has_key(mid):
            keys, func = accellist[mid]
            del accellist[mid]
            editoraccellist[mid] = (hotkey, func)
        elif editoraccellist.has_key(mid):
            keys, func = editoraccellist[mid]
            editoraccellist[mid] = (hotkey, func)
Mixin.setPlugin('mainframe', 'init_accelerator', init_accelerator)



#-----------------------  mPythonFileType.py ------------------

import wx
import FiletypeBase
from modules import Mixin

class PythonFiletype(FiletypeBase.FiletypeBase):

    __mixinname__ = 'pythonfiletype'
    menulist = [ (None,
        [
            (890, 'IDM_PYTHON', 'Python', wx.ITEM_NORMAL, None, ''),
        ]),
    ]
    toollist = []               #your should not use supperclass's var
    toolbaritems= {}

def add_filetypes(filetypes):
    filetypes.extend([('python', PythonFiletype)])
Mixin.setPlugin('changefiletype', 'add_filetypes', add_filetypes)



#-----------------------  mModuleFile.py ------------------

from modules import Mixin
import wx
import wx.stc
import os.path

def add_py_menu(menulist):
    menulist.extend([
        ('IDM_PYTHON', #parent menu id
        [
            (115, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (116, 'IDM_VIEW_OPEN_MODULE', tr('Open Module File') + '\tF6', wx.ITEM_NORMAL, 'OnViewOpenModuleFile', tr('Open current word as Python module file.')),
        ]),
    ])
Mixin.setPlugin('pythonfiletype', 'add_menu', add_py_menu)

def other_popup_menu(editor, projectname, menus):
    if editor.languagename == 'python' :
        menus.extend([(None, #parent menu id
            [
                (10, 'IDPM_OPEN_MODULE', tr('Open Module File') + '\tF6', wx.ITEM_NORMAL, 'OnOpenModuleFile', tr('Open current word as Python module file.')),
                (20, '', '-', wx.ITEM_SEPARATOR, None, ''),
            ]),
        ])
Mixin.setPlugin('editor', 'other_popup_menu', other_popup_menu)

def OnViewOpenModuleFile(win, event):
    openmodulefile(win, getword(win))
Mixin.setMixin('mainframe', 'OnViewOpenModuleFile', OnViewOpenModuleFile)

def OnOpenModuleFile(win, event):
    openmodulefile(win.mainframe, getword(win.mainframe))
Mixin.setMixin('editor', 'OnOpenModuleFile', OnOpenModuleFile)

def openmodulefile(mainframe, module):
    try:
        mod = my_import(module)
        f, ext = os.path.splitext(mod.__file__)
        filename = f + '.py'
        if os.path.exists(filename):
            mainframe.editctrl.new(filename)
    except:
        pass

def my_import(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def getword(mainframe):
    doc = mainframe.document
    if doc.GetSelectedText():
        return doc.GetSelectedText()
    pos = doc.GetCurrentPos()
    start = doc.WordStartPosition(pos, True)
    end = doc.WordEndPosition(pos, True)
    if end > start:
        i = start - 1
        while i >= 0:
            if doc.getChar(i) in mainframe.getWordChars() + '.':
                start -= 1
                i -= 1
            else:
                break
        i = end
        length = doc.GetLength()
        while i < length:
            if doc.getChar(i) in mainframe.getWordChars()+ '.':
                end += 1
                i += 1
            else:
                break
    return doc.GetTextRange(start, end)



#-----------------------  mSplashWin.py ------------------

import wx
from modules import common
from modules import Mixin

def add_pref(preflist):
    preflist.extend([
        (tr('General'), 140, 'check', 'splash_on_startup', tr('Show splash screen at startup'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def beforegui(app):
    splashimg = common.uni_work_file('images/splash.jpg')
    app.splashwin = None
    if app.pref.splash_on_startup:
        app.splashwin = wx.SplashScreen(wx.Image(splashimg).ConvertToBitmap(),
            wx.SPLASH_CENTRE_ON_SCREEN|wx.SPLASH_NO_TIMEOUT, 0, None, -1)
Mixin.setPlugin('app', 'beforegui', beforegui)

def init(pref):
    pref.splash_on_startup = True
Mixin.setPlugin('preference', 'init', init)

def show(mainframe):
    if mainframe.app.splashwin:
        wx.FutureCall(1000, mainframe.app.splashwin.Destroy)
Mixin.setPlugin('mainframe', 'show', show)



#-----------------------  mModuleInfo.py ------------------

import wx
from modules import Mixin

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_HELP', #parent menu id
        [
            (102, 'IDM_HELP_MODULES', tr('Extended Modules Info'), wx.ITEM_NORMAL, 'OnHelpModules', tr('Extended modules infomation.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def OnHelpModules(win, event):
    from ModulesInfo import show_modules_info
    show_modules_info(win)
Mixin.setMixin('mainframe', 'OnHelpModules', OnHelpModules)



#-----------------------  mDirBrowser.py ------------------

import wx
import os
from modules import Mixin
from modules import Globals

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (115, 'dir'),
    ])

    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'dir':(wx.ITEM_CHECK, 'IDM_WINDOW_DIRBROWSER', 'images/dir.gif', tr('Directory Browser'), tr('Shows the Directory Browser pane.'), 'OnWindowDirBrowser'),
    })
Mixin.setPlugin('mainframe', 'add_tool_list', add_tool_list)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_WINDOW_DIRBROWSER, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

_dirbrowser_pagename = tr('Directory Browser')

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDM_WINDOW_DIRBROWSER:
        page = win.panel.getPage(_dirbrowser_pagename)
        event.Check(bool(page) and win.panel.LeftIsVisible)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def add_mainframe_menu(menulist):
    menulist.extend([('IDM_FILE',
        [
            (138, 'IDM_WINDOW_DIRBROWSER', tr('Directory Browser')+'\tF2', wx.ITEM_CHECK, 'OnWindowDirBrowser', tr('Shows the Directory Browser pane.'))
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_notebook_menu(popmenulist):
    popmenulist.extend([(None,
        [
            (170, 'IDPM_DIRBROWSERWINDOW', tr('Directory Browser'), wx.ITEM_NORMAL, 'OnDirBrowserWindow', tr('Shows the Directory Browser pane.')),
        ]),
    ])
Mixin.setPlugin('notebook', 'add_menu', add_notebook_menu)

def on_notebook_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDPM_DIRBROWSERWINDOW:
        event.Check(bool(Globals.mainframe.panel.getPage(tr('Directory Browser'))) and win.panel.LeftIsVisible)
Mixin.setPlugin('notebook', 'on_update_ui', on_notebook_updateui)

def init(win):
    wx.EVT_UPDATE_UI(win, win.IDPM_DIRBROWSERWINDOW, win.OnUpdateUI)
Mixin.setPlugin('notebook', 'init', init)

def afterinit(win):
    win.dirbrowser_imagelist = {
        'close':'images/folderclose.gif',
        'open':'images/folderopen.gif',
        'item':'images/file.gif',
    }
    if win.pref.open_last_dir_as_startup and win.pref.last_dir_paths:
        wx.CallAfter(win.createDirBrowserWindow, win.pref.last_dir_paths)
        wx.CallAfter(win.panel.showPage, _dirbrowser_pagename)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def createDirBrowserWindow(win, dirs=None):
    page = None
    if not win.panel.getPage(_dirbrowser_pagename):
        from DirBrowser import DirBrowser

        if not dirs:
            dirs = win.pref.last_dir_paths
        page = DirBrowser(win.panel.createNotebook('left'), win, dirs)
        win.panel.addPage('left', page, _dirbrowser_pagename)
    return page
Mixin.setMixin('mainframe', 'createDirBrowserWindow', createDirBrowserWindow)

def toggleDirBrowserWindow(win):
    page = win.panel.getPage(_dirbrowser_pagename)
    if page:
        win.panel.closePage(_dirbrowser_pagename)
    else:
        if win.createDirBrowserWindow():
            win.panel.showPage(_dirbrowser_pagename)
Mixin.setMixin('mainframe', 'toggleDirBrowserWindow', toggleDirBrowserWindow)

def OnWindowDirBrowser(win, event):
    win.toggleDirBrowserWindow()
Mixin.setMixin('mainframe', 'OnWindowDirBrowser', OnWindowDirBrowser)

def OnDirBrowserWindow(win, event):
    win.mainframe.toggleDirBrowserWindow()
Mixin.setMixin('notebook', 'OnDirBrowserWindow', OnDirBrowserWindow)

def pref_init(pref):
    pref.recent_dir_paths = []
    pref.recent_dir_paths_num = 20
    pref.last_dir_paths = []
    pref.open_last_dir_as_startup = True
    pref.dirbrowser_last_addpath = os.getcwd()
    if wx.Platform == '__WXMSW__':
        cmdline = os.environ['ComSpec']
        pref.command_line = cmdline
    else:
        pref.command_line = 'gnome-terminal --working-directory={path}'
    pref.open_project_setting_dlg = True
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('General'), 150, 'check', 'open_last_dir_as_startup', tr('Open the last directory at startup'), None),
        (tr('General'), 151, 'check', 'open_project_setting_dlg', tr('Open the Project Settings dialog if a directory is added to the Directory Browser'), None),
        (tr('General'), 160, 'openfile', 'command_line', tr('Command line of Open Command Window Here:'), {'span':True}),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def after_addpath(dirbrowser, node):
    Globals.mainframe.pref.last_dir_paths = dirbrowser.getTopDirs()
    Globals.mainframe.pref.save()
Mixin.setPlugin('dirbrowser', 'after_addpath', after_addpath)

def after_closepath(dirbrowser, path):
    Globals.mainframe.pref.last_dir_paths = dirbrowser.getTopDirs()
    Globals.mainframe.pref.save()
Mixin.setPlugin('dirbrowser', 'after_closepath', after_closepath)

def afterclosewindow(win):
    win.panel.showWindow('LEFT', False)
    win.panel.showWindow('bottom', False)
Mixin.setPlugin('mainframe', 'afterclosewindow', afterclosewindow)



#-----------------------  mInputAssistant.py ------------------

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
        else:
            event.Skip()
            return True
    elif key == wx.WXK_ESCAPE:
        # clear nested calltip state if something is wrong.
        win.calltip_stack.clear()
        del win.function_parameter[:]
        win.calltip.cancel()

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



#-----------------------  mFileNew.py ------------------

import wx
import os
from modules import Id
from modules import Mixin
from modules import common
from modules import makemenu
from modules import Globals
from modules.wxctrl import FlatButtons

def pref_init(pref):
    pref.last_new_type = ''
Mixin.setPlugin('preference', 'init', pref_init)

def add_tool_list(toollist, toolbaritems):
    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'new':(10, create_new),
    })
Mixin.setPlugin('mainframe', 'add_tool_list', add_tool_list, Mixin.LOW)

def create_new(win, toolbar):
    _id = Id.makeid(win, 'IDM_FILE_NEW')
    btnNew = FlatButtons.FlatBitmapMenuButton(toolbar, _id, common.getpngimage('images/new.gif'))
    btnNew.SetRightClickFunc(win.OnFileNews)
    btnNew.SetToolTip(wx.ToolTip(tr('New File')))
    wx.EVT_BUTTON(btnNew, _id, win.OnFileNew)

    return btnNew

def OnFileNew(win, event):
    new_file(win)
Mixin.setMixin('mainframe', 'OnFileNew', OnFileNew)

def OnFileNews(win, event):
    eid = event.GetId()
    size = win.toolbar.GetToolSize()
    pos = win.toolbar.GetToolPos(eid)
    menu = wx.Menu()
    create_menu(win, menu)
    win.PopupMenu(menu, (size[0]*pos, size[1]))
    menu.Destroy()
Mixin.setMixin('mainframe', 'OnFileNews', OnFileNews)

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_FILE_NEWMORE',
        [
           (100, 'IDM_FILE_NEWMORE_NULL', tr('(Empty)'), wx.ITEM_NORMAL, '', ''),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def init(win):
    menu = makemenu.findmenu(win.menuitems, 'IDM_FILE_NEWMORE')
    menu.Delete(win.IDM_FILE_NEWMORE_NULL)
    create_menu(win, menu)
Mixin.setPlugin('mainframe', 'init', init)

def new_file(win, lexname=None):
    if not lexname:
        lexname = win.pref.last_new_type
    if lexname:
        lexer = win.lexers.getNamedLexer(lexname)
        text = ''
        if lexer:
            templatefile = common.getConfigPathFile('template.%s' % lexer.name)
            if os.path.exists(templatefile):
                text = file(templatefile).read()
                text = common.decode_string(text)
                import re
                eolstring = {0:'\n', 1:'\r\n', 2:'\r'}
                eol = eolstring[Globals.pref.default_eol_mode]
                text = re.sub(r'\r\n|\r|\n', eol, text)
            else:
                text = ''
        document = win.editctrl.new(defaulttext=text, language=lexer.name)
        if document:
            document.goto(document.GetTextLength())
    else:
        win.editctrl.new()

def create_menu(win, menu):
    ids = {}
    def _OnFileNew(event, win=win, ids=ids):
        lexname = ids.get(event.GetId(), '')
        new_file(win, lexname)
        win.pref.last_new_type = lexname
        win.pref.save()

    for name, lexname in win.filenewtypes:
        _id = wx.NewId()
        menu.AppendCheckItem(_id, "%s" % name)
        ids[_id] = lexname
        if lexname == win.pref.last_new_type:
            menu.Check(_id, True)
        wx.EVT_MENU(win, _id, _OnFileNew)




#-----------------------  mProxy.py ------------------

from modules import Mixin

def pref_init(pref):
    pref.use_proxy = False
    pref.proxy = ''
    pref.proxy_port = 8000
    pref.proxy_user = ''
    pref.proxy_password = ''
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):

    def _get(name):
        def _f(name=name):
            from modules import Globals
            return getattr(Globals.pref, name)
        return _f

    from modules import meide as ui
    box = ui.VGroup(tr('Network'))
    grid = ui.SimpleGrid()
    grid.add('', ui.Check(_get('use_proxy'), tr('Use a proxy')), name='use_proxy', span=True)
    grid.add(tr('IP address:'), ui.Text(_get('proxy')), name='proxy')
    grid.add(tr('Port number:'), ui.Int(_get('proxy_port')), name='proxy_port')
    grid.add(tr('Username:'), ui.Text(_get('proxy_user')), name='proxy_user')
    grid.add(tr('Password:'), ui.Password(_get('proxy_password')), name='proxy_password')
    box.add(grid)
    preflist.extend([
        (tr('Network'), 100, box, '', '', {'span':True}),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)



#-----------------------  mPad.py ------------------

import wx
import os
from modules import common, Mixin

def mainframe_init(win):
    win.memo_win = None
Mixin.setPlugin('mainframe', 'init', mainframe_init)

def pref_init(pref):
    pref.easy_memo_lastpos = 0
Mixin.setPlugin('preference', 'init', pref_init)

def add_mainframe_menu(menulist):
    menulist.extend([('IDM_TOOL', #parent menu id
        [
            (140, '-', '', wx.ITEM_SEPARATOR, '', ''),
            (150, 'IDM_TOOL_MEMO', tr('Easy Memo') + u'\tF12', wx.ITEM_CHECK, 'OnToolMemo', tr('Shows the window Easy Memo for writing notes.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def OnToolMemo(win, event):
    if win.memo_win:
        win.memo_win.Close()
        win.memo_win = None
    else:
        import Pad
        from modules import Globals
        pad = Pad.PAD(win, os.path.join(Globals.userpath, common.get_config_file_obj().default.get('memo', 'memo.txt')), tr('Easy Memo'))
        pad.Show()
        win.memo_win = pad
Mixin.setMixin('mainframe', 'OnToolMemo', OnToolMemo)

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (600, 'memo'),
    ])

    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'memo':(wx.ITEM_CHECK, 'IDM_TOOL_MEMO', 'images/memo.gif', tr('Open Easy Memo Window'), tr('Show Easy Memo windows, and you can write down everything what you want.'), 'OnToolMemo'),
    })
Mixin.setPlugin('mainframe', 'add_tool_list', add_tool_list)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_TOOL_MEMO, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDM_TOOL_MEMO:
        if win.memo_win:
            event.Check(True)
        else:
            event.Check(False)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)



#-----------------------  mPythonProject.py ------------------

import sys
from modules import Mixin
from modules.Debug import error
from modules import common
import wx
import os
from modules import Globals

def add_project(project_names):
    project_names.extend(['python'])
Mixin.setPlugin('dirbrowser', 'add_project', add_project)

def project_begin(dirwin, project_names, path):
    if 'python' in project_names and path not in sys.path:
        sys.path.insert(0, path)
Mixin.setPlugin('dirbrowser', 'project_begin', project_begin)

def project_end(dirwin, project_names, path):
    if 'python' in project_names:
        try:
            if path in sys.path:
                sys.path.remove(path)
        except:
            error.traceback()
Mixin.setPlugin('dirbrowser', 'project_end', project_end)

def other_popup_menu(dirwin, projectname, menus):
    item = dirwin.tree.GetSelection()
    if not item.IsOk(): return
    if 'python' in projectname:
        menus.extend([ (None,
            [
                (145, 'IDPM_PYTHON_CREATE_PACKAGE', tr('Create Python Package'), wx.ITEM_NORMAL, 'OnCreatePythonPackage', ''),
            ]),
        ])
Mixin.setPlugin('dirbrowser', 'other_popup_menu', other_popup_menu)

def OnCreatePythonPackage(dirwin, event):
    item = dirwin.tree.GetSelection()
    if not item.IsOk(): return
    dir = common.getCurrentDir(dirwin.get_node_filename(item))

    from modules import Entry
    dlg = Entry.MyTextEntry(Globals.mainframe, tr('Input Directory Name'),
        tr('Input Directory Name'))
    path = ''
    if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetValue()
    dlg.Destroy()

    path = os.path.join(dir, path)
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except Exception, e:
            common.showerror(str(e))
    init_file = os.path.join(path, '__init__.py')
    if not os.path.exists(init_file):
        f = file(init_file, 'wb')
        f.close()
    dirwin.OnRefresh()
Mixin.setMixin('dirbrowser', 'OnCreatePythonPackage', OnCreatePythonPackage)



#-----------------------  mTodoWindow.py ------------------

import wx
from modules import Mixin

def add_mainframe_menu(menulist):
    menulist.extend([('IDM_WINDOW', #parent menu id
        [
            (210, 'IDM_WINDOW_TODO', tr('TODO Window')+u'\tCtrl+T', wx.ITEM_CHECK, 'OnWindowTODO', tr('Opens the TODO window.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_notebook_menu(popmenulist):
    popmenulist.extend([ (None,
        [
            (190, 'IDPM_TODOWINDOW', tr('TODO Window'), wx.ITEM_CHECK, 'OnNTodoWindow', tr('Opens the TODO window.')),
        ]),
    ])
Mixin.setPlugin('notebook', 'add_menu', add_notebook_menu)

def pref_init(pref):
    pref.auto_todo = True
    pref.todo_column1 = 80
    pref.todo_column2 = 50
    pref.todo_column3 = 90
    pref.todo_column4 = 300
    pref.todo_column5 = 200
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('Document'), 180, 'check', 'auto_todo', tr('Autoshow TODO window when a file with a TODO tag is opened'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

_todo_pagename = tr('TODO')

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDM_WINDOW_TODO:
        event.Check(bool(win.panel.getPage(_todo_pagename)) and win.panel.BottomIsVisible)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_WINDOW_TODO, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def on_notebook_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDPM_TODOWINDOW:
        event.Check(bool(win.panel.getPage(_todo_pagename)) and win.panel.BottomIsVisible)
Mixin.setPlugin('notebook', 'on_update_ui', on_notebook_updateui)

def init(win):
    wx.EVT_UPDATE_UI(win, win.IDPM_TODOWINDOW, win.OnUpdateUI)
Mixin.setPlugin('notebook', 'init', init)

def createtodowindow(win):
    if not win.panel.getPage(_todo_pagename):
        from TodoWindow import TodoWindow

        page = TodoWindow(win.panel.createNotebook('bottom'), win)
        win.panel.addPage('bottom', page, _todo_pagename)
    win.todowindow = win.panel.getPage(_todo_pagename)
Mixin.setMixin('mainframe', 'createtodowindow', createtodowindow)

def OnWindowTODO(win, event):
    if not win.panel.getPage(_todo_pagename):
        win.createtodowindow()
        win.panel.showPage(_todo_pagename)
        win.todowindow.show(win.document)
    else:
        win.panel.closePage(_todo_pagename)
Mixin.setMixin('mainframe', 'OnWindowTODO', OnWindowTODO)

def OnNTodoWindow(win, event):
    if not win.panel.getPage(_todo_pagename):
        win.mainframe.createtodowindow()
        win.panel.showPage(_todo_pagename)
        win.mainframe.todowindow.show(win.mainframe.document)
    else:
        win.panel.closePage(_todo_pagename)
Mixin.setMixin('notebook', 'OnNTodoWindow', OnNTodoWindow)

def aftersavefile(win, filename):
    def f():
        todo = win.mainframe.panel.getPage(_todo_pagename)
        if todo:
            data = read_todos(win)
            if data:
                win.mainframe.todowindow.show(win, data)
                return
        else:
            if win.pref.auto_todo and win.todo_show_status:
                data = read_todos(win)
                if data:
                    win.mainframe.createtodowindow()
                    win.mainframe.panel.showPage(_todo_pagename)
                    win.mainframe.todowindow.show(win, data)
                    return
        win.mainframe.panel.closePage(_todo_pagename, savestatus=False)
    wx.CallAfter(f)
Mixin.setPlugin('editor', 'aftersavefile', aftersavefile)

def on_document_enter(win, editor):
    if win.pref.auto_todo:
        if editor.todo_show_status:
            data = read_todos(win.document)
            if data:
                win.mainframe.createtodowindow()
                win.mainframe.panel.showPage(_todo_pagename)
                win.mainframe.todowindow.show(win.document, data)
                return
    else:
        todo = win.mainframe.panel.getPage(_todo_pagename)
        if todo:
            data = read_todos(win.document)
            if data:
                win.mainframe.todowindow.show(win.document, data)
                return
    win.mainframe.panel.closePage(_todo_pagename, savestatus=False)
Mixin.setPlugin('editctrl', 'on_document_enter', on_document_enter)

def editor_init(editor):
    editor.todo_show_status = True
Mixin.setPlugin('editor', 'init', editor_init)

def on_show(todowin):
    todowin.editor.todo_show_status = True
Mixin.setPlugin('todowindow', 'show', on_show)

def on_close(todowin, savestatus=True):
    if savestatus:
        todowin.editor.todo_show_status = False
Mixin.setPlugin('todowindow', 'close', on_close)

def read_todos(editor):
    from mixins.TodoWindow import read_todos as read

    return read(editor)



#-----------------------  mMessageWindow.py ------------------

import wx
from modules import Mixin
from modules import Globals

def other_popup_menu(win, menus):
    menus.extend([(None, #parent menu id
        [
            (190, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (200, 'IDPM_GOTO', tr('Goto error line'), wx.ITEM_NORMAL, 'OnGoto', tr('Goto the line that occurs the error.')),
        ]),
    ])
Mixin.setPlugin('messagewindow', 'other_popup_menu', other_popup_menu)

def OnGoto(win, event):
    line = win.GetCurLine()
    ret = win.execplugin('goto_error_line', win, *line)
    if ret:
        filename, lineno = ret
        Globals.mainframe.editctrl.new(filename)
        wx.CallAfter(Globals.mainframe.document.goto, int(lineno))
Mixin.setMixin('messagewindow', 'OnGoto', OnGoto)

def messagewindow_init(win):
    wx.EVT_LEFT_DCLICK(win, win.OnGoto)
Mixin.setPlugin('messagewindow', 'init', messagewindow_init)

def pref_init(pref):
    pref.clear_message = True
    pref.message_wrap = False
    pref.message_setfocus_back = False
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('General'), 170, 'check', 'clear_message', tr('Autoclear messages window content at program run'), None),
        (tr('General'), 180, 'check', 'message_setfocus_back', tr('Set focus back to document window after program run'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def add_mainframe_menu(menulist):
    menulist.extend([
        ('IDM_EDIT',
        [
            (291, 'IDM_EDIT_CLEARMESSAGE', tr('Clear Messages Window') + '\tShift+F5', wx.ITEM_NORMAL, 'OnEditClearMessage', tr('Clears content of messages window.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def OnEditClearMessage(win, event):
    if hasattr(win, 'messagewindow') and win.messagewindow:
        win.messagewindow.OnClear(None)
Mixin.setMixin('mainframe', 'OnEditClearMessage', OnEditClearMessage)

def start_run(win, messagewindow):
    if win.pref.clear_message:
        messagewindow.SetText('')
Mixin.setPlugin('mainframe', 'start_run', start_run)




#-----------------------  mColumnMode.py ------------------
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
    win.SetSelection(-1, pos)

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
    if win.column_mode and not (key in (wx.WXK_DOWN, wx.WXK_UP) and shift):
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



#-----------------------  mCommands.py ------------------

import wx
from modules import Mixin
from modules import Globals
import Commands

_impact_mode = False
buf = []

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_TOOL', #parent menu id
        [
            (137, 'IDM_TOOL_SEARCHCMDS', tr('Commands'), wx.ITEM_NORMAL, '', ''),
        ]),
        ('IDM_TOOL_SEARCHCMDS',
        [
            (100, 'IDM_TOOL_SEARCHCMDS_SEARCH', tr('Searching...') +'\tCtrl+K', wx.ITEM_NORMAL, 'OnToolSearchCMDS', tr('Searches commands.')),
            (110, 'IDM_TOOL_SEARCHCMDS_IMPACT_MODE', tr('Switch Impact Mode') +'\tCtrl+Shift+K', wx.ITEM_CHECK, 'OnToolSearchCMDSImpactMode', tr('Switches commands searching impact mode.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def mainframe_init(win):
    win.command_mode = False
Mixin.setPlugin('mainframe', 'init', mainframe_init)


def on_kill_focus(win, event):
    return Globals.mainframe.command_mode is True
Mixin.setPlugin('editor', 'on_kill_focus', on_kill_focus)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_TOOL_SEARCHCMDS_IMPACT_MODE, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if hasattr(win, 'document') and win.document:
        if eid == win.IDM_TOOL_SEARCHCMDS_IMPACT_MODE:
            event.Check(win.pref.commands_impact)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def showinfo(text):
    win = Globals.mainframe.statusbar
    win.show_panel('Command: '+text, color='#AAFFAA', font=wx.Font(10, wx.TELETYPE, wx.NORMAL, wx.BOLD, True))

def OnToolSearchCMDS(win, event):
    global _impact_mode
    if not win.pref.commands_impact:
        from mixins import SearchWin
        s = SearchWin.SearchWin(win, tr("Search Commands"))
        s.Show()
    else:
        _impact_mode = True
        showinfo('')
Mixin.setMixin('mainframe', 'OnToolSearchCMDS', OnToolSearchCMDS)

def OnToolSearchCMDSImpactMode(win, event):
    win.pref.commands_impact = not win.pref.commands_impact
    win.pref.save()
Mixin.setMixin('mainframe', 'OnToolSearchCMDSImpactMode', OnToolSearchCMDSImpactMode)

def pref_init(pref):
    pref.commands_impact = False
    pref.commands_autoclose = True
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('Commands'), 100, 'check', 'commands_impact', tr('Enable commands search impact mode'), None),
        (tr('Commands'), 110, 'check', 'commands_autoclose', tr('Close commands search window after command executed'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def on_first_char(win, event):
    global _impact_mode, buf
    if _impact_mode:
        key = event.GetKeyCode()
        if key < 127:
            buf.append(chr(key))
            showinfo(' '.join(buf))
            Mixin.reload_obj(Commands)
            commandar = Commands.getinstance()
            s = commandar.impact_search(''.join(buf))
            if len(s) == 1:     #find a cmd
                showinfo(' '.join(buf + ['('+s[0][0]+')']))
                cmd_id = s[0][-1]
                commandar.run(cmd_id)
                buf = []
            elif len(s) == 0:
                buf = []
        return True
Mixin.setPlugin('editor', 'on_first_char', on_first_char)

def on_first_keydown(win, event):
    global _impact_mode
    if _impact_mode:
        key = event.GetKeyCode()
        if key in (wx.WXK_ESCAPE, wx.WXK_RETURN):
            _impact_mode = False
            Globals.mainframe.statusbar.hide_panel()
            return True
        else:
            return False
Mixin.setPlugin('editor', 'on_first_keydown', on_first_keydown)



#-----------------------  mMultiView.py ------------------

import wx
from modules import Mixin
from modules import Globals

def add_editor_menu(popmenulist):
    popmenulist.extend([ (None,
        [
            (200, 'IDPM_MULTIVIEWWINDOW', tr('Open Multiview Window'), wx.ITEM_NORMAL, 'OnMultiViewWindow', tr('Opens the multiview window.')),
        ]),
    ])
Mixin.setPlugin('notebook', 'add_menu', add_editor_menu)

def createMultiViewWindow(win, side, document):
    dispname = document.getShortFilename()
    filename = document.filename

    obj = None
    for pagename, panelname, notebook, page in win.panel.getPages():
        if is_multiview(page, document):
            obj = page
            break
    if not obj:
        if hasattr(document, 'GetDocPointer'):
            from mixins import Editor

            page = Editor.TextEditor(win.panel.createNotebook(side), None, filename, document.documenttype, multiview=True)
            page.SetDocPointer(document.GetDocPointer())
            page.document = document    #save document object
            document.lexer.colourize(page, True)
            win.panel.addPage(side, page, dispname)
            win.panel.setImageIndex(page, 'document')
            return page
    else:
        return obj
Mixin.setMixin('mainframe', 'createMultiViewWindow', createMultiViewWindow)

def OnMultiViewWindow(win, event):
    side = win.getSide()
    dispname = win.mainframe.createMultiViewWindow(side, Globals.mainframe.editctrl.getCurDoc())
    if dispname:
        win.panel.showPage(dispname)
Mixin.setMixin('notebook', 'OnMultiViewWindow', OnMultiViewWindow)

def closefile(win, document, filename):
    for pagename, panelname, notebook, page in Globals.mainframe.panel.getPages():
        if is_multiview(page, document):
            Globals.mainframe.panel.closePage(page)
Mixin.setPlugin('mainframe', 'closefile', closefile)

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_WINDOW',
        [
            (220, 'IDM_WINDOW_MULTIVIEWWINDOW', tr('Open Multiview Window'), wx.ITEM_NORMAL, 'OnWindowMultiView', tr('Opens the multiview window.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def OnWindowMultiView(win, event):
    dispname = win.createMultiViewWindow('bottom', Globals.mainframe.document)
    if dispname:
        win.panel.showPage(dispname)
Mixin.setMixin('mainframe', 'OnWindowMultiView', OnWindowMultiView)

def setfilename(document, filename):
    for pagename, panelname, notebook, page in Globals.mainframe.panel.getPages():
        if is_multiview(page, document):
            title = document.getShortFilename()
            Globals.mainframe.panel.setName(page, title)
Mixin.setPlugin('editor', 'setfilename', setfilename)

def other_popup_menu(editctrl, document, menus):
    if document.documenttype == 'texteditor':
        menus.extend([ (None,
            [
                (600, '', '-', wx.ITEM_SEPARATOR, None, ''),
                (700, 'IDPM_MULTIVIEW_LEFT', tr('Open MultiView In Left Pane'), wx.ITEM_NORMAL, 'OnOpenViewLeft', tr('Opens the multiview of current document in left pane.')),
                (800, 'IDPM_MULTIVIEW_BOTTOM', tr('Open MultiView In Bottom Pane'), wx.ITEM_NORMAL, 'OnOpenViewBottom', tr('Opens the multiview of current document in bottom pane.')),
            ]),
        ])
Mixin.setPlugin('editctrl', 'other_popup_menu', other_popup_menu)

def OnOpenViewLeft(win, event):
    dispname = win.mainframe.createMultiViewWindow('left', Globals.mainframe.editctrl.getCurDoc())
    if dispname:
        win.mainframe.panel.showPage(dispname)
Mixin.setMixin('editctrl', 'OnOpenViewLeft', OnOpenViewLeft)

def OnOpenViewBottom(win, event):
    dispname = win.mainframe.createMultiViewWindow('bottom', Globals.mainframe.editctrl.getCurDoc())
    if dispname:
        win.mainframe.panel.showPage(dispname)
Mixin.setMixin('editctrl', 'OnOpenViewBottom', OnOpenViewBottom)

def is_multiview(page, document):
    if (hasattr(page, 'multiview') and page.multiview and
            hasattr(page, 'document') and page.document is document):
        return True
    else:
        return False



#-----------------------  mCustomLexer.py ------------------

import wx.stc
from modules import Mixin

def editor_init(win):
    wx.stc.EVT_STC_STYLENEEDED(win, win.GetId(), win.OnStyleNeeded)
Mixin.setPlugin('editor', 'init', editor_init)

def OnStyleNeeded(win, event):
    lexer = getattr(win, 'lexer', None)
    if lexer:
        if lexer.syntaxtype == wx.stc.STC_LEX_CONTAINER:
            lexer.styleneeded(win, event.GetPosition())
Mixin.setMixin('editor', 'OnStyleNeeded', OnStyleNeeded)



#-----------------------  mRestFileType.py ------------------

import wx
from modules import Mixin
import FiletypeBase
from modules import Globals
from modules.Debug import error

class RestFiletype(FiletypeBase.FiletypeBase):

    __mixinname__ = 'restfiletype'
    menulist = [ (None,
        [
            (890, 'IDM_REST', 'ReST', wx.ITEM_NORMAL, None, ''),
        ]),
    ]
    toollist = []               #your should not use supperclass's var
    toolbaritems= {}

def add_filetypes(filetypes):
    filetypes.extend([('rst', RestFiletype)])
Mixin.setPlugin('changefiletype', 'add_filetypes', add_filetypes)

def add_rest_menu(menulist):
    menulist.extend([('IDM_REST', #parent menu id
            [
                (100, 'IDM_REST_VIEW_IN_LEFT', tr('View HTML Result In Left Pane'), wx.ITEM_NORMAL, 'OnRestViewHtmlInLeft', tr('Views HTML result in left pane.')),
                (110, 'IDM_REST_VIEW_IN_BOTTOM', tr('View HTML Result In Bottom Pane'), wx.ITEM_NORMAL, 'OnRestViewHtmlInBottom', tr('Views HTML result in bottom pane.')),
            ]),
    ])
Mixin.setPlugin('restfiletype', 'add_menu', add_rest_menu)

def OnRestViewHtmlInLeft(win, event):
    dispname = win.createRestHtmlViewWindow('left', Globals.mainframe.editctrl.getCurDoc())
    if dispname:
        win.panel.showPage(dispname)
Mixin.setMixin('mainframe', 'OnRestViewHtmlInLeft', OnRestViewHtmlInLeft)

def OnRestViewHtmlInBottom(win, event):
    dispname = win.createRestHtmlViewWindow('bottom', Globals.mainframe.editctrl.getCurDoc())
    if dispname:
        win.panel.showPage(dispname)
Mixin.setMixin('mainframe', 'OnRestViewHtmlInBottom', OnRestViewHtmlInBottom)

def closefile(win, document, filename):
    for pagename, panelname, notebook, page in Globals.mainframe.panel.getPages():
        if is_resthtmlview(page, document):
            Globals.mainframe.panel.closePage(page)
Mixin.setPlugin('mainframe', 'closefile', closefile)

def setfilename(document, filename):
    for pagename, panelname, notebook, page in Globals.mainframe.panel.getPages():
        if is_resthtmlview(page, document):
            title = document.getShortFilename()
Mixin.setPlugin('editor', 'setfilename', setfilename)

def createRestHtmlViewWindow(win, side, document):
    dispname = document.getShortFilename()
    obj = None
    for pagename, panelname, notebook, page in win.panel.getPages():
        if is_resthtmlview(page, document):
            obj = page
            break

    if not obj:
        if win.document.documenttype == 'texteditor':
            text = html_fragment(document.GetText().encode('utf-8'), win.document.filename)
            if text:
                page = RestHtmlView(win.panel.createNotebook(side), text, document)
                win.panel.addPage(side, page, dispname)
                win.panel.setImageIndex(page, 'html')
                return page
    return obj
Mixin.setMixin('mainframe', 'createRestHtmlViewWindow', createRestHtmlViewWindow)

def other_popup_menu(editctrl, document, menus):
    if document.documenttype == 'texteditor' and document.languagename == 'rst':
        menus.extend([ (None,
            [
                (900, 'IDPM_REST_HTML_LEFT', tr('View Html Result in Left Pane'), wx.ITEM_NORMAL, 'OnRestHtmlViewLeft', tr('Views html result in left pane.')),
                (910, 'IDPM_REST_HTML_BOTTOM', tr('View Html Result in Bottom Pane'), wx.ITEM_NORMAL, 'OnRestHtmlViewBottom', tr('Views html result in bottom pane.')),
            ]),
        ])
Mixin.setPlugin('editctrl', 'other_popup_menu', other_popup_menu)

def OnRestHtmlViewLeft(win, event=None):
    win.mainframe.OnRestViewHtmlInLeft(None)
Mixin.setMixin('editctrl', 'OnRestHtmlViewLeft', OnRestHtmlViewLeft)

def OnRestHtmlViewBottom(win, event=None):
    win.mainframe.OnRestViewHtmlInBottom(None)
Mixin.setMixin('editctrl', 'OnRestHtmlViewBottom', OnRestHtmlViewBottom)

def html_fragment(content, path=''):
    from docutils.core import publish_string

    try:
        return publish_string(content, writer_name = 'html', source_path=path)
    except:
        error.traceback()
        return None

from mixins import HtmlPage
import tempfile
import os
_tmp_rst_files_ = []

class RestHtmlView(wx.Panel):
    def __init__(self, parent, content, document):
        wx.Panel.__init__(self, parent, -1)

        mainframe = Globals.mainframe
        self.document = document
        self.resthtmlview = True
        self.rendering = False
        box = wx.BoxSizer(wx.VERTICAL)
        self.chkAuto = wx.CheckBox(self, -1, tr("Stop auto updated"))
        box.Add(self.chkAuto, 0, wx.ALL, 2)
        if wx.Platform == '__WXMSW__':
            import wx.lib.iewin as iewin

            self.html = HtmlPage.IEHtmlWindow(self)
            if wx.VERSION < (2, 8, 8, 0):
                self.html.ie.Bind(iewin.EVT_DocumentComplete, self.OnDocumentComplete, self.html.ie)
                self.html.ie.Bind(iewin.EVT_ProgressChange, self.OnDocumentComplete, self.html.ie)
            else:
                self.html.ie.AddEventSink(self)
        else:
            self.html = HtmlPage.DefaultHtmlWindow(self)
            self.html.SetRelatedFrame(mainframe, mainframe.app.appname + " - Browser [%s]")
            self.html.SetRelatedStatusBar(0)

        self.tmpfilename = None
        self.load(content)
        if wx.Platform == '__WXMSW__':
            box.Add(self.html.ie, 1, wx.EXPAND|wx.ALL, 1)
        else:
            box.Add(self.html, 1, wx.EXPAND|wx.ALL, 1)

        self.SetSizer(box)

    def create_tempfile(self, content):
        if not self.tmpfilename:
            path = os.path.dirname(self.document.filename)
            if not path:
                path = None
            fd, self.tmpfilename = tempfile.mkstemp('.html', dir=path)
            os.write(fd, content)
            os.close(fd)
            _tmp_rst_files_.append(self.tmpfilename)
        else:
            file(self.tmpfilename, 'w').write(content)

    def load(self, content):
        self.create_tempfile(content)
        self.html.Load(self.tmpfilename)

    def refresh(self, content):
        self.create_tempfile(content)
        wx.CallAfter(self.html.DoRefresh)

    def canClose(self):
        return True

    def isStop(self):
        return self.chkAuto.GetValue()

    def OnClose(self, win):
        if self.tmpfilename:
            try:
                _tmp_rst_files_.remove(self.tmpfilename)
                os.unlink(self.tmpfilename)
            except:
                pass

    #for version lower than 2.8.8.0
    def OnDocumentComplete(self, evt):
        if self.FindFocus() is not self.document:
            self.document.SetFocus()

    #for version higher or equal 2.8.8.0
    def DocumentComplete(self, this, pDisp, URL):
        if self.FindFocus() is not self.document:
            self.document.SetFocus()

def is_resthtmlview(page, document):
    if hasattr(page, 'resthtmlview') and page.resthtmlview and page.document is document:
        return True
    else:
        return False

def on_modified(win):
    for pagename, panelname, notebook, page in Globals.mainframe.panel.getPages():
        if is_resthtmlview(page, win) and not page.isStop() and not page.rendering:
            page.rendering = True
            from modules import Casing

            def f():
                try:
                    text = html_fragment(win.GetText().encode('utf-8'), win.filename)
                    page.refresh(text)
                finally:
                    page.rendering = False
            d = Casing.Casing(f)
            d.start_thread()
            break
Mixin.setPlugin('editor', 'on_modified', on_modified)

def on_close(win, event):
    for i in _tmp_rst_files_:
        if os.path.exists(i):
            try:
                os.unlink(i)
            except:
                pass
Mixin.setPlugin('mainframe','on_close', on_close)



#-----------------------  mCTags.py ------------------

import os
import wx.stc
from modules import Mixin
from modules import common
from modules import dict4ini
from modules.Debug import error

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_SEARCH',
        [
            (175, 'IDM_SEARCH_GOTO_DEF', tr('Jump To The Definition')+'\tE=Ctrl+I', wx.ITEM_NORMAL, 'OnSearchJumpDef', tr('Jumps to head of line containing variable or function definition.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_editor_menu(popmenulist):
    popmenulist.extend([ (None, #parent menu id
        [
            (10, 'IDPM_GOTO_DEF', tr('Jump To The Definition')+'\tCtrl+I', wx.ITEM_NORMAL, 'OnJumpDef', tr('Jumps to definition.')),
        ]),
    ])
Mixin.setPlugin('editor', 'add_menu', add_editor_menu)

_mlist = {}
def OnSearchJumpDef(win, event):
    global _mlist

    word = getword(win)
    from modules import ctags

    flag = False
    prjfile = common.getProjectFile(win.document.getFilename())
    if prjfile:
        path = os.path.dirname(prjfile)
        ini = dict4ini.DictIni(prjfile)
        s = []
        for c in ini.ctags.values():
            c = os.path.join(path, c)
            p = os.path.dirname(c)
            try:
                s.extend(ctags.get_def(c, word, p))
            except:
                error.traceback()
        if len(s) == 1:
            d, f, m = s[0]
            win.editctrl.new(f)
            flag = jump_to_file(win, d, f, m)
        elif len(s) > 1:
            text = []
            _mlist = {}
            for i, v in enumerate(s):
                d, f, m = v
                key = str(i+1)+'|'+d+'|'+os.path.basename(f)
                text.append(key)
                _mlist[key] = (d, f, m)
            win.document.UserListShow(2, " ".join(text))
            flag = True
    if not flag:
        win.document.callplugin('on_jump_definition', win.document, word)
Mixin.setMixin('mainframe', 'OnSearchJumpDef', OnSearchJumpDef)

def on_user_list_selction(win, list_type, text):
    t = list_type
    if t == 2:  #1 is used by input assistant
        if _mlist:
            v = _mlist.get(text, None)
            if v:
                d, f, m = v
                jump_to_file(win, d, f, m)
Mixin.setPlugin('editor', 'on_user_list_selction', on_user_list_selction)

def OnJumpDef(win, event):
    win.mainframe.OnSearchJumpDef(event)
Mixin.setMixin('editor', 'OnJumpDef', OnJumpDef)

def getword(mainframe):
    doc = mainframe.document
    if doc.GetSelectedText():
        return doc.GetSelectedText()
    pos = doc.GetCurrentPos()
    start = doc.WordStartPosition(pos, True)
    end = doc.WordEndPosition(pos, True)
    if end > start:
        i = start - 1
        while i >= 0:
            if doc.getChar(i) in mainframe.getWordChars() + '.':
                start -= 1
                i -= 1
            else:
                break
        i = end
        length = doc.GetLength()
        while i < length:
            if doc.getChar(i) in mainframe.getWordChars()+ '.':
                end += 1
                i += 1
            else:
                break
    return doc.GetTextRange(start, end)

def jump_to_file(win, d, f, m):
    doc = win.editctrl.new(f)
    if doc:
        count = doc.GetLineCount()
        if m.startswith('/^') and m.endswith('$/'):
            m = m[2:-2]

            for i in range(count):
                line = doc.GetLine(i)
                if line.startswith(m):
                    wx.CallAfter(doc.SetFocus)
                    wx.CallAfter(doc.goto, i-1)
                    return True
        elif m.isdigit():
            wx.CallAfter(doc.SetFocus)
            wx.CallAfter(doc.GotoLine, int(m)-1)
            return True
    return False





#-----------------------  mSyntaxCheck.py ------------------

import wx
from modules import Mixin

menulist = [('IDM_PYTHON', #parent menu id
        [
            (170, 'IDM_PYTHON_CHECK', tr('Check Syntax'), wx.ITEM_NORMAL,
                'OnPythonCheck', tr('Check python source code syntax.')),
        ]),
]
Mixin.setMixin('pythonfiletype', 'menulist', menulist)

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (2140, 'check'),
    ])

    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'check':(wx.ITEM_NORMAL, 'IDM_PYTHON_CHECK', 'images/spellcheck.gif', tr('Check Syntax'), tr('Check python source code syntax.'), 'OnPythonCheck'),
    })
Mixin.setPlugin('mainframe', 'add_tool_list', add_tool_list)

def OnPythonCheck(win, event):
    import SyntaxCheck
    SyntaxCheck.Check(win, win.document)
Mixin.setMixin('mainframe', 'OnPythonCheck', OnPythonCheck)

def init(pref):
    pref.auto_py_check = True
    pref.auto_py_pep8_check = True
    pref.py_check_skip_long_line = True
    pref.py_check_skip_blank_lines = True
    pref.py_check_skip_tailing_whitespace = True
Mixin.setPlugin('preference', 'init', init)

preflist = [
        (tr('Python'), 160, 'check', 'auto_py_check', tr('Check for syntax errors at file saving'), None),
        (tr('Python'), 170, 'check', 'auto_py_pep8_check', tr('Check syntax for PEP8-style at python program run'), None),
]
Mixin.setMixin('preference', 'preflist', preflist)

def aftersavefile(win, filename):
    if win.edittype == 'edit' and win.languagename == 'python' and win.pref.auto_py_check:
        import SyntaxCheck
        wx.CallAfter(SyntaxCheck.Check, win.mainframe, win)
Mixin.setPlugin('editor', 'aftersavefile', aftersavefile, Mixin.LOW)

def createSyntaxCheckWindow(win):
    if not win.panel.getPage(tr('Check Syntax')):
        from SyntaxCheck import SyntaxCheckWindow

        page = SyntaxCheckWindow(win.panel.createNotebook('bottom'), win)
        win.panel.addPage('bottom', page, tr('Check Syntax'))
    win.syntaxcheckwindow = win.panel.getPage(tr('Check Syntax'))
Mixin.setMixin('mainframe', 'createSyntaxCheckWindow', createSyntaxCheckWindow)



#-----------------------  mRstProject.py ------------------

from modules import Mixin
from modules import common

project_names = ['ReST']
Mixin.setMixin('dirbrowser', 'project_names', project_names)

def set_project(ini, projectnames):
    if 'ReST' in projectnames:
        common.set_acp_highlight(ini, '.txt', 'rst.acp', 'rst')
Mixin.setPlugin('dirbrowser', 'set_project', set_project)

def remove_project(ini, projectnames):
    if 'ReST' in projectnames:
        common.remove_acp_highlight(ini, '.txt', 'rst.acp', 'rst')
Mixin.setPlugin('dirbrowser', 'remove_project', remove_project)



#-----------------------  mEPyDoc.py ------------------

import re
import wx
from modules import Mixin

def other_popup_menu(editor, projectname, menus):
    if editor.languagename == 'python':
        menus.extend([(None, #parent menu id
            [
                (9, 'IDPM_PYTHON_EPYDOC', tr('Create Comment for Function'), wx.ITEM_NORMAL, 'OnPythonEPyDoc', 'Creates comment for a function.'),
            ]),
        ])
Mixin.setPlugin('editor', 'other_popup_menu', other_popup_menu)

re_func = re.compile('^(\s*)def\s+[\w\d_]+\((.*?)\):')
comment_template = """

@author: %(username)s

%(parameters)s
@return:
@rtype:
"""
def OnPythonEPyDoc(win, event=None):
    def output(win, indent, parameters, pos):
        t = (indent / win.GetTabWidth() + 1) * win.getIndentChar()
        startpos = win.PositionFromLine(win.LineFromPosition(pos)+1)
        win.GotoPos(startpos)
        text = '"""' + comment_template % {'parameters':parameters, 'username':win.pref.personal_username} + '"""' + win.getEOLChar()
        s = ''.join([t + x for x in text.splitlines(True)])
        win.AddText(s)
        win.EnsureCaretVisible()

    line = win.GetCurrentLine()
    text = win.getLineText(line)
    pos = win.GetCurrentPos()
    if not text.strip():
        for i in range(line-1, -1, -1):
            text = win.getLineText(i)
            if text.strip():
                break

    b = None
    if text:
        b = re_func.match(text)
    if b:
        indent, parameters = b.groups()
        paras = [x.strip() for x in parameters.split(',')]
        s = []
        for x in paras:
            if x.startswith('**'):
                x = x[2:]
            if x.startswith('*'):
                x = x[1:]
            if '=' in x:
                x = x.split('=')[0]
            x = x.strip()
            s.append('@param %s:' % x)
            s.append('@type %s:' % x)
        s = win.getEOLChar().join(s)
        output(win, len(indent), s, pos)
        return
Mixin.setMixin('editor', 'OnPythonEPyDoc', OnPythonEPyDoc)



#-----------------------  mPersonalInfo.py ------------------

from modules import Mixin

def pref_init(pref):
    pref.personal_username = ''
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('Personal'), 100, 'text', 'personal_username', tr('Username:'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)



#-----------------------  mRegex.py ------------------

import wx
from modules import Mixin

regex_pagename = tr("Regex")
def createRegexWindow(win):
    if not win.panel.getPage(regex_pagename):
        from mixins import RegexWindow

        page = RegexWindow.RegexWindow(win.panel.createNotebook('bottom'))
        win.panel.addPage('bottom', page, regex_pagename)
    return regex_pagename
Mixin.setMixin('mainframe', 'createRegexWindow', createRegexWindow)

def add_mainframe_menu(menulist):
    menulist.extend([('IDM_TOOL', #parent menu id
        [
            (170, 'IDM_TOOL_REGEX', tr('Live Regular Expression'), wx.ITEM_NORMAL, 'OnToolRegex', tr('Live regular expression searching.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def OnToolRegex(win, event):
    p = win.createRegexWindow()
    win.panel.showPage(p)
Mixin.setMixin('mainframe', 'OnToolRegex', OnToolRegex)



#-----------------------  mSmartNav.py ------------------

import wx
import os
from modules import Mixin
from modules.wxctrl import FlatButtons
from modules import common
from modules import Id
from modules import Globals

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_SEARCH',
        [
            (176, 'IDM_SEARCH_SMART_NAV', tr('Smart Navigation'), wx.ITEM_NORMAL, '', ''),
        ]),
        ('IDM_SEARCH_SMART_NAV',
            [
                (100, 'IDM_SEARCH_NAV_PREV', tr('Go To Previous File'), wx.ITEM_NORMAL, 'OnSmartNavPrev', tr('Goes to previous file.')),
                (110, 'IDM_SEARCH_NAV_NEXT', tr('Go To Next File'), wx.ITEM_NORMAL, 'OnSmartNavNext', tr('Goes to next file.')),
                (120, 'IDM_SEARCH_NAV_CLEAR', tr('Clear Filenames'), wx.ITEM_NORMAL, 'OnSmartNavClear', tr('Clears buffered filenames.')),
            ]),

    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (235, 'smartprev'),
        (236, 'smartnext'),
    ])

    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'smartprev':(10, create_prev),
        'smartnext':(10, create_next),
    })
Mixin.setPlugin('mainframe', 'add_tool_list', add_tool_list)

def create_prev(win, toolbar):
    ID_PREV = Id.makeid(win, 'IDM_SEARCH_NAV_PREV')
    btnPrev = FlatButtons.FlatBitmapMenuButton(toolbar, ID_PREV, common.getpngimage('images/nav_left.gif'))
    btnPrev.SetRightClickFunc(win.OnSmartNavPrevFiles)
    btnPrev.SetToolTip(wx.ToolTip(tr('Previous File')))
    wx.EVT_BUTTON(btnPrev, ID_PREV, win.OnSmartNavPrev)
    wx.EVT_UPDATE_UI(win, win.IDM_SEARCH_NAV_PREV, win.OnUpdateUI)

    return btnPrev

def create_next(win, toolbar):
    ID_NEXT = Id.makeid(win, 'IDM_SEARCH_NAV_NEXT')
    btnNext = FlatButtons.FlatBitmapMenuButton(toolbar, ID_NEXT, common.getpngimage('images/nav_right.gif'))
    btnNext.SetRightClickFunc(win.OnSmartNavNextFiles)
    btnNext.SetToolTip(wx.ToolTip(tr('Next File')))
    wx.EVT_BUTTON(btnNext, ID_NEXT, win.OnSmartNavNext)
    wx.EVT_UPDATE_UI(win, win.IDM_SEARCH_NAV_NEXT, win.OnUpdateUI)

    return btnNext


def GotoSmartNavIndex(index):
    pref = Globals.mainframe.pref
    pref.smart_nav_cur = index
    pref.save()
    if pref.smart_nav_cur < 0 or not pref.smart_nav_files:
        return
    state = pref.smart_nav_files[pref.smart_nav_cur]
    doc = Globals.mainframe.editctrl.new_with_state(state)
    if not doc:
        del pref.smart_nav_files[pref.smart_nav_cur]

def OnSmartNavPrev(win, event=None):
    pref = Globals.mainframe.pref
    pref.smart_nav_cur -= 1
    GotoSmartNavIndex(pref.smart_nav_cur)
Mixin.setMixin('mainframe', 'OnSmartNavPrev', OnSmartNavPrev)

def OnSmartNavNext(win, event=None):
    pref = Globals.mainframe.pref
    pref.smart_nav_cur += 1
    GotoSmartNavIndex(pref.smart_nav_cur)
Mixin.setMixin('mainframe', 'OnSmartNavNext', OnSmartNavNext)

def OnSmartNavClear(win, event=None):
    pref = Globals.mainframe.pref
    pref.smart_nav_cur = -1
    pref.smart_nav_files = []
    pref.save()
Mixin.setMixin('mainframe', 'OnSmartNavClear', OnSmartNavClear)

def OnSmartNavPrevFiles(win, btn):
    menu = wx.Menu()
    pref = win.pref
    for i in range(pref.smart_nav_cur-1, -1, -1)[:10]:
        v = pref.smart_nav_files[i]
        filename, state, bookmarks = v
        def OnFunc(event, index=i):
            GotoSmartNavIndex(index)

        _id = wx.NewId()
        item = wx.MenuItem(menu, _id, os.path.basename(filename), filename)
        wx.EVT_MENU(win, _id, OnFunc)
        menu.AppendItem(item)
    btn.PopupMenu(menu)
Mixin.setMixin('mainframe', 'OnSmartNavPrevFiles', OnSmartNavPrevFiles)

def OnSmartNavNextFiles(win, btn):
    menu = wx.Menu()
    pref = win.pref
    for i in range(pref.smart_nav_cur+1, len(pref.smart_nav_files))[:10]:
        v = pref.smart_nav_files[i]
        filename, state, bookmarks = v
        def OnFunc(event, index=i):
            GotoSmartNavIndex(index)

        _id = wx.NewId()
        item = wx.MenuItem(menu, _id, os.path.basename(filename), filename)
        wx.EVT_MENU(win, _id, OnFunc)
        menu.AppendItem(item)
    btn.PopupMenu(menu)
Mixin.setMixin('mainframe', 'OnSmartNavNextFiles', OnSmartNavNextFiles)

def on_update_ui(win, event):
    pref = win.pref
    eid = event.GetId()
    if eid == win.IDM_SEARCH_NAV_PREV:
        event.Enable(len(pref.smart_nav_files) > 0 and pref.smart_nav_cur > 0)
    elif eid == win.IDM_SEARCH_NAV_NEXT:
        event.Enable(len(pref.smart_nav_files) > 0 and pref.smart_nav_cur < len(pref.smart_nav_files) - 1)
Mixin.setPlugin('mainframe', 'on_update_ui', on_update_ui)

def pref_init(pref):
    pref.smart_nav_files  = []
    pref.smart_nav_cur = -1
Mixin.setPlugin('preference', 'init', pref_init)

def get_state(editor):
    pref = editor.pref
    filename, state, bookmarks = v = editor.get_full_state()
    if not filename: return #so the filename should not be empty

    if not pref.smart_nav_files or pref.smart_nav_files[pref.smart_nav_cur][0] != filename:   #add new file
        pref.smart_nav_files = pref.smart_nav_files[:pref.smart_nav_cur+1]    #remove the next files
        pref.smart_nav_files.append(v)
        del pref.smart_nav_files[:-20]
        pref.smart_nav_cur = len(pref.smart_nav_files) - 1
        pref.save()
    else:   #equal current nav file, so just update the value
        pref.smart_nav_files[pref.smart_nav_cur] = v
        pref.save()

def on_key_up(win, event):
    get_state(win)
Mixin.setPlugin('editor', 'on_key_up', on_key_up)

def on_mouse_up(win, event):
    get_state(win)
Mixin.setPlugin('editor', 'on_mouse_up', on_mouse_up)

def on_document_enter(win, document):
    if document.documenttype == 'texteditor' and not Globals.starting:
        get_state(document)
Mixin.setPlugin('editctrl', 'on_document_enter', on_document_enter)



#-----------------------  mReloadMixins.py ------------------
import wx
from modules import Mixin
import ReloadMixins


def add_mainframe_menu(menulist):
    menulist.extend([('IDM_TOOL', #parent menu id
        [
            (138, 'IDM_TOOL_AUTO_LOAD_MIXINS', tr('Autoreload Mixins'), wx.ITEM_NORMAL, '', ''),
        ]),
        ('IDM_TOOL_AUTO_LOAD_MIXINS',
        [
            (110, 'IDM_TOOL_MIXINS_NAME', tr('Select Mixins Name To Reload') +'\tCtrl+M', wx.ITEM_NORMAL, 'OnToolReloadName', tr('Selects Mixin names to reload.')),
            (120, 'IDM_TOOL_ENABLE_RELOAD_MIXINS', tr('Enable Reload Mixins') +'\tCtrl+Shift+M', wx.ITEM_CHECK, 'OnToolreload_mixins', tr('Switches to Mixins reload mode.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)


def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_TOOL_ENABLE_RELOAD_MIXINS, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_TOOL_MIXINS_NAME, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)


def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDM_TOOL_ENABLE_RELOAD_MIXINS:
        event.Check(win.pref.mixin_reload_mixins_mode)
    if  eid == win.IDM_TOOL_MIXINS_NAME:
        if  win.pref.mixin_reload_mixins_mode:
            event.Enable(True)
        else:
            event.Enable(False)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)


def OnToolReloadName(win, event):
    reload(ReloadMixins)
    from ReloadMixins import MixinDialog

    dlg = MixinDialog(win)
    answer = dlg.ShowModal()
    dlg.Destroy()


Mixin.setMixin('mainframe', 'OnToolReloadName', OnToolReloadName)


def OnToolreload_mixins(win, event):
    if  win.pref.mixin_reload_mixins_mode:
        mode = "normal mode"
    else:
        mode = "auto reload Mixin plugins mode"
    dlg = wx.MessageDialog(win, 'Are you want to switch to %s?\n this operation will'
            ' take effect after restarting this program!\n'
            'so doing this will close this program!\n'
            'the patch was made by ygao,you can contact me at ygao2004@gmail.com' % mode,
            "reload Mixins", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
    try: res = dlg.ShowModal()
    finally: dlg.Destroy()
    if res == wx.ID_YES:
        pass
    elif res == wx.ID_CANCEL:
        return
    win.pref.mixin_reload_mixins_mode = not win.pref.mixin_reload_mixins_mode
    win.pref.save()
    reload(ReloadMixins)
    if  win.pref.mixin_reload_mixins_mode:
        from ReloadMixins import MixinDialog
        dlg = MixinDialog(win)
        answer = dlg.ShowModal()
        dlg.Destroy()
        #ReloadMixins.create_import_py(win,flag=True)
    else:
        ReloadMixins.create_import_py(win)
Mixin.setMixin('mainframe', 'OnToolreload_mixins', OnToolreload_mixins)


def pref_init(pref):
    pref.mixin_reload_mixins_mode = False
    pref.mixin_reload_name = []
Mixin.setPlugin('preference', 'init', pref_init)






#-----------------------  mDebug.py ------------------

from modules import Mixin
import wx
import os
from modules import common

menulist = [('IDM_PYTHON', #parent menu id
                [
                        (160, 'IDM_PYTHON_DEBUG', tr('Debug In WinPdb'), wx.ITEM_NORMAL, 'OnPythonDebug', tr('Debug the current program in WinPdb.')),
                ]),
]
Mixin.setMixin('pythonfiletype', 'menulist', menulist)

toollist = [
        (2130, 'debug'),
]
Mixin.setMixin('pythonfiletype', 'toollist', toollist)

toolbaritems = {
        'debug':(wx.ITEM_NORMAL, 'IDM_PYTHON_DEBUG', 'images/debug.png', tr('Debug'), tr('Debug the current program in WinPdb.'), 'OnPythonDebug'),
}
Mixin.setMixin('pythonfiletype', 'toolbaritems', toolbaritems)

def OnPythonDebug(win, event):
    interpreters = dict(win.pref.python_interpreter)
    interpreter = interpreters.get(win.pref.default_interpreter, '')
    if not interpreter:
        common.showerror(win, tr("You didn't setup python interpreter, \nplease setup it first in Preference dialog"))
        return
    try:
        import wx
    except:
        common.showerror(win, tr("You should install wxPython package to run the Debugger."))
        return

    cmd = os.path.normpath('"%s" "%s/packages/winpdb/winpdb.py" -t -c "%s" "%s"' % (interpreter, win.app.workpath, win.document.filename, win.document.args))
    wx.Execute(cmd)
Mixin.setMixin('mainframe', 'OnPythonDebug', OnPythonDebug)



#-----------------------  mVersionControl.py ------------------

import wx
from modules import Mixin

def pref_init(pref):
    pref.version_control_export_path = ''
    pref.version_control_checkout_path = ''
Mixin.setPlugin('preference', 'init', pref_init)



#-----------------------  mShell.py ------------------

import wx
from modules import Mixin

def add_editor_menu(popmenulist):
    popmenulist.extend([ (None, #parent menu id
        [
            (5, 'IDPM_COPY_RUN', tr('Run In Shell') + '\tCtrl+F5', wx.ITEM_NORMAL, 'OnEditorCopyRun', ''),
        ]),
    ])
Mixin.setPlugin('editor', 'add_menu', add_editor_menu)

def editor_init(win):
    wx.EVT_UPDATE_UI(win, win.IDPM_COPY_RUN, win.OnUpdateUI)
Mixin.setPlugin('editor', 'init', editor_init)

def editor_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDPM_COPY_RUN:
        event.Enable(bool(win.hasSelection()))
Mixin.setPlugin('editor', 'on_update_ui', editor_updateui)

def OnEditorCopyRun(win, event):
    _copy_and_run(win)
Mixin.setMixin('editor', 'OnEditorCopyRun', OnEditorCopyRun)

import re
re_space = re.compile(r'^\s+')
def lstrip_multitext(text):
    lines = text.splitlines()
    m = 999999
    for line in lines:
        b = re_space.search(line)
        if b:
            m = min(len(b.group()), m)
        else:
            m = 0
            break
    return '\n'.join([x[m:] for x in lines])

def _copy_and_run(doc):
    from modules import Globals

    win = Globals.mainframe
    text = doc.GetSelectedText()
    if text:
        win.createShellWindow()
        win.panel.showPage(tr('Shell'))
        shellwin = win.panel.getPage(tr('Shell'))
        shellwin.Execute(lstrip_multitext(text))

def OnEditCopyRun(win, event):
    _copy_and_run(win.editctrl.getCurDoc())
Mixin.setMixin('mainframe', 'OnEditCopyRun', OnEditCopyRun)

def add_mainframe_menu(menulist):
    menulist.extend([
        ('IDM_EDIT',
        [
            (285, 'IDM_EDIT_COPY_RUN', tr('Run In Shell') + '\tCtrl+F5', wx.ITEM_NORMAL, 'OnEditCopyRun', tr('Copy code to shell window and run it.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDM_EDIT_COPY_RUN:
        doc = win.editctrl.getCurDoc()
        event.Enable(bool(doc.hasSelection()))
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_COPY_RUN, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)




#-----------------------  mConfig.py ------------------

from modules import Mixin

def add_pref(preflist):
    preflist.extend([
        ('Config.ini', 100, 'check', '_config_default_debug', tr('Enable debug mode'), None)
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)



#-----------------------  mDocumentArea.py ------------------

import wx
from modules import Mixin
from modules import meide as ui

def create_document_area(win):
    win.mainframe.documentarea = DocumentArea(win.top)
Mixin.setPlugin('mainsubframe', 'init', create_document_area)

class DocumentArea(wx.Panel, Mixin.Mixin):

    __mixinname__ = 'documentarea'

    def __init__(self, parent):
        self.initmixin()

        wx.Panel.__init__(self, parent, -1)

        self.sizer = ui.VBox(0).create(self).auto_layout()
        obj = self.execplugin('init', self)
        self.sizer.add(obj, proportion=1, flag=wx.EXPAND)




#-----------------------  mCodeSnippet.py ------------------

import wx
from modules import Mixin
from modules import Globals
from modules import common

def add_mainframe_menu(menulist):
    menulist.extend([
        ('IDM_WINDOW',
        [
            (151, 'IDM_WINDOW_CODESNIPPET', tr('Code Snippets Window'), wx.ITEM_CHECK, 'OnWindowCodeSnippet', tr('Opens code snippets window.'))
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_notebook_menu(popmenulist):
    popmenulist.extend([(None,
        [
            (135, 'IDPM_CODESNIPPETWINDOW', tr('Code Snippets Window'), wx.ITEM_CHECK, 'OnCodeSnippetWindow', tr('Opens code snippet window.')),
        ]),
    ])
Mixin.setPlugin('notebook', 'add_menu', add_notebook_menu)

def add_images(images):
    images.update({
        'close': 'images/folderclose.gif',
        'open': 'images/folderopen.gif',
        'item': 'images/file.gif',
        })
Mixin.setPlugin('codesnippet', 'add_images', add_images)

def add_image(imagelist, imageids, name, image):
    if name not in ('close', 'open'):
        return

    m = [
        ('modified', common.getpngimage('images/TortoiseModified.gif')),
    ]

    for f, imgfile in m:
        bmp = common.merge_bitmaps(image, imgfile)
        index = imagelist.Add(bmp)
        imageids[name+f] = index
Mixin.setPlugin('codesnippet', 'add_image', add_image)

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (650, 'snippet'),
    ])

    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'snippet':(wx.ITEM_CHECK, 'IDM_WINDOW_CODESNIPPET', 'images/snippet.png', tr('Open Code Snippets Window'), tr('Open code snippet window.'), 'OnToolbarWindowCodeSnippet'),
    })
Mixin.setPlugin('mainframe', 'add_tool_list', add_tool_list)

_codesnippet_page_name = tr('Code Snippets')

def createCodeSnippetWindow(win):
    try:
        import xml.etree.ElementTree
    except:
        import elementtree.ElementTree

    page = win.panel.getPage(_codesnippet_page_name)
    if not page:
        from CodeSnippet import CodeSnippetWindow

        page = CodeSnippetWindow(win.panel.createNotebook('left'), win)
        win.panel.addPage('left', page, _codesnippet_page_name)
    return page
Mixin.setMixin('mainframe', 'createCodeSnippetWindow', createCodeSnippetWindow)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_WINDOW_CODESNIPPET, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDM_WINDOW_CODESNIPPET:
        page = win.panel.getPage(_codesnippet_page_name)
        event.Check(bool(page) and win.panel.LeftIsVisible)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def on_notebook_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDPM_CODESNIPPETWINDOW:
        event.Check(bool(win.panel.getPage(_codesnippet_page_name)) and win.panel.LeftIsVisible)
Mixin.setPlugin('notebook', 'on_update_ui', on_notebook_updateui)

def init(win):
    wx.EVT_UPDATE_UI(win, win.IDPM_CODESNIPPETWINDOW, win.OnUpdateUI)
Mixin.setPlugin('notebook', 'init', init)

def OnToolbarWindowCodeSnippet(win, event):
    page = win.panel.getPage(_codesnippet_page_name)
    if page:
        win.panel.closePage(_codesnippet_page_name)
    else:
        if win.createCodeSnippetWindow():
            win.panel.showPage(_codesnippet_page_name)
Mixin.setMixin('mainframe', 'OnToolbarWindowCodeSnippet', OnToolbarWindowCodeSnippet)

def OnWindowCodeSnippet(win, event):
    page = win.panel.getPage(_codesnippet_page_name)
    if page:
        win.panel.closePage(_codesnippet_page_name)
    else:
        if win.createCodeSnippetWindow():
            win.panel.showPage(_codesnippet_page_name)
Mixin.setMixin('mainframe', 'OnWindowCodeSnippet', OnWindowCodeSnippet)

def OnCodeSnippetWindow(win, event):
    page = win.mainframe.panel.getPage(_codesnippet_page_name)
    if page:
        win.mainframe.panel.closePage(_codesnippet_page_name)
    else:
        if win.mainframe.createCodeSnippetWindow():
            win.mainframe.panel.showPage(_codesnippet_page_name)
Mixin.setMixin('notebook', 'OnCodeSnippetWindow', OnCodeSnippetWindow)

def close_page(page, name):
    if name == tr('Code Snippet'):
        win = Globals.mainframe
        for pagename, panelname, notebook, page in win.panel.getPages():
            if hasattr(page, 'code_snippet') and page.code_snippet:
                ret = win.panel.closePage(page, savestatus=False)
                break
Mixin.setPlugin('notebook', 'close_page', close_page)

def on_close(win, event):
    if event.CanVeto():
        win = Globals.mainframe
        snippet = win.panel.getPage(_codesnippet_page_name)
        if snippet:
            return not snippet.canClose()
Mixin.setPlugin('mainframe', 'on_close', on_close)

def pref_init(pref):
    pref.snippet_recents = []
    pref.snippet_lastdir = ''
    pref.snippet_files = []
Mixin.setPlugin('preference', 'init', pref_init)

def createCodeSnippetEditWindow(win):
    snippet = None
    for pagename, panelname, notebook, page in win.panel.getPages():
        if hasattr(page, 'code_snippet') and page.code_snippet:
            snippet = page
            break
    if not snippet:
        from mixins.Editor import TextEditor
        snippet = TextEditor(win.panel.createNotebook('bottom'), None, 'Snippet', 'texteditor', True)
        #.document is important
        snippet.document = snippet
        snippet.cansavefileflag = False
        snippet.needcheckfile = False
        snippet.savesession = False
        snippet.code_snippet = True
        win.panel.addPage('bottom', snippet, tr('Snippet'))
    if snippet:
        win.panel.showPage(snippet)
        return snippet
Mixin.setMixin('mainframe', 'createCodeSnippetEditWindow', createCodeSnippetEditWindow)

def on_modified(win):
    if hasattr(win, 'code_snippet') and win.code_snippet:
        if not win.snippet_obj.changing:
            win.snippet_obj.update_node(win.snippet_obj.tree.GetSelection(), newcontent=win.GetText())
Mixin.setPlugin('editor', 'on_modified', on_modified)

def on_selected(win, text):
    doc = Globals.mainframe.editctrl.getCurDoc()
    doc.AddText(text)
    wx.CallAfter(doc.SetFocus)
Mixin.setPlugin('codesnippet', 'on_selected', on_selected)



#-----------------------  mIndentMove.py ------------------

import wx
from modules import Mixin
from modules import Globals

def pref_init(pref):
    pref.document_move_next_indent_selection = True
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('Document')+'/'+tr('Edit'), 170, 'check', 'document_move_next_indent_selection', tr('Always select from start of line when moving down to next matching indent'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def on_key_down(editor, event):
    ctrl = event.ControlDown()
    shift = event.ShiftDown()
    alt = event.AltDown()

    if not shift and not ctrl and alt:
        if event.GetKeyCode() == wx.WXK_LEFT:
            editor.move_parent_indent()
            return True
        elif event.GetKeyCode() == wx.WXK_UP:
            editor.move_prev_indent()
            return True
        elif event.GetKeyCode() == wx.WXK_DOWN:
            editor.move_next_indent()
            return True
        elif event.GetKeyCode() == wx.WXK_RIGHT:
            editor.move_child_indent()
            return True
Mixin.setPlugin('editor', 'on_key_down', on_key_down)

def move_parent_indent(editor):
    line = editor.GetCurrentLine()
    indent = editor.GetLineIndentation(line)
    line -= 1
    comment_chars = editor.get_document_comment_chars()
    while line > -1:
        line_text = editor.GetLine(line)
        text = line_text.strip()
        if text and not line_text.startswith(comment_chars):
            i = editor.GetLineIndentation(line)
            editor.GotoLine(line)
            if i < indent:
                editor.GotoLine(line)
                break

        line -= 1
Mixin.setMixin('editor', 'move_parent_indent', move_parent_indent)

def move_prev_indent(editor):
    line = editor.GetCurrentLine()
    indent = editor.GetLineIndentation(line)
    line -= 1
    comment_chars = editor.get_document_comment_chars()
    while line > -1:
        line_text = editor.GetLine(line)
        text = line_text.strip()
        if text and not line_text.startswith(comment_chars):
            i = editor.GetLineIndentation(line)
            if i <= indent:
                editor.GotoLine(line)
                break

        line -= 1
Mixin.setMixin('editor', 'move_prev_indent', move_prev_indent)

def move_next_indent(editor):
    line = editor.GetCurrentLine()
    if editor.GetSelectionStart() < editor.GetCurrentPos():
        startpos = editor.GetSelectionStart()
    else:
        startpos = editor.FindColumn(line, 0)
    indent = editor.GetLineIndentation(line)
    line += 1
    comment_chars = editor.get_document_comment_chars()
    while line < editor.GetLineCount():
        line_text = editor.GetLine(line)
        text = line_text.strip()
        if text and not line_text.startswith(comment_chars):
            i = editor.GetLineIndentation(line)
            if i <= indent:
                editor.GotoLine(line)
                if Globals.pref.document_move_next_indent_selection:
                    editor.SetSelectionStart(startpos)
                    editor.SetSelectionEnd(editor.GetCurrentPos())
                return

        line += 1

    if editor.GetCurrentLine() < editor.GetLineCount() - 1:
        editor.goto(line-1)
        if Globals.pref.document_move_next_indent_selection:
            editor.SetSelectionStart(startpos)
            editor.SetSelectionEnd(editor.GetCurrentPos())
    else:
        editor.GotoPos(editor.GetTextLength())
        if Globals.pref.document_move_next_indent_selection:
            editor.SetSelectionStart(startpos)
            editor.SetSelectionEnd(editor.GetTextLength())
Mixin.setMixin('editor', 'move_next_indent', move_next_indent)

def move_child_indent(editor):
    line = editor.GetCurrentLine()
    indent = editor.GetLineIndentation(line)
    line += 1
    comment_chars = editor.get_document_comment_chars()
    while line < editor.GetLineCount():
        line_text = editor.GetLine(line)
        text = line_text.strip()
        if text and not line_text.startswith(comment_chars):
            i = editor.GetLineIndentation(line)
            if i > indent:
                editor.GotoLine(line)
                break
            else:
                break

        line += 1
Mixin.setMixin('editor', 'move_child_indent', move_child_indent)



#-----------------------  mCheckUpdate.py ------------------

import wx
from modules import Mixin
from modules import Version
from modules import common
from modules.HyperLinksCtrl import HyperLinkCtrl, EVT_HYPERLINK_LEFT
from modules import Globals
from modules import meide as ui

def pref_init(pref):
    pref.check_update = True
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('Update'), 100, 'check', 'check_update', tr('Check for updates at startup'), None),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

class UpdateDialog(wx.Dialog):
    homepage = 'http://code.google.com/p/ulipad/downloads/list'

    def __init__(self, parent, version):
        wx.Dialog.__init__(self, parent, -1, size = (400, 340), style = wx.DEFAULT_DIALOG_STYLE, title = tr('Check Update'))

        box = ui.VBox(padding=6, namebinding='widget').create(self).auto_layout()
        h = box.add(ui.HBox)
        h.add(ui.Label(tr('There is new version %s of UliPad.') % version))

        self.ID_HOMEPAGE = wx.NewId()
        self.homepage = HyperLinkCtrl(self, self.ID_HOMEPAGE, tr("Goto Download page"), URL=self.homepage)
        h.add(self.homepage).bind(EVT_HYPERLINK_LEFT, self.OnDownload)

        box.add(ui.Check(Globals.pref.check_update, tr("Check for updates at startup")), name='chkCheck').bind('check', self.OnCheck)

        box.add(ui.Button(tr("OK"), id=wx.ID_OK), name='btnOk', flag=wx.ALIGN_CENTER|wx.ALL, border=10)
        self.btnOk.SetDefault()

        box.auto_fit(2)

    def OnDownload(self, event):
        common.webopen(self.homepage)

    def OnCheck(self, event):
        Globals.pref.check_update = self.chkCheck.GetValue()

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_HELP', #parent menu id
        [
            (800, 'IDM_HELP_UPDATE', tr('Check For Updates'), wx.ITEM_NORMAL, 'OnHelpCheckUpdate', tr('Check if where is new version of UliPad.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def check_update(force=False):
    from modules import Casing
    import urllib2

    def f():
        from xmlrpclib import ServerProxy, Transport, loads

        class UrllibTransport(Transport):
            def __init__(self, proxy, verbose=0):
                self.proxy = proxy
                self.verbose = verbose
                self.opener = opener = urllib2.OpenerDirector()
                if proxy:
                    opener.add_handler(urllib2.ProxyHandler({'http':self.proxy}))
                else:
                    opener.add_handler(urllib2.ProxyHandler())
                opener.add_handler(urllib2.UnknownHandler())
                opener.add_handler(urllib2.HTTPHandler())
                opener.add_handler(urllib2.HTTPDefaultErrorHandler())
                opener.add_handler(urllib2.HTTPSHandler())
                opener.add_handler(urllib2.HTTPErrorProcessor())

            def request(self, host, handler, request_body, verbose=1):
                f = self.opener.open('http://'+host+handler, request_body)
                u, f = loads(f.read())
                return u

        pref = Globals.pref
        if pref.use_proxy:
            if pref.proxy_user and pref.proxy_password:
                auth = pref.proxy_user + ':' + pref.proxy_password + '@'
            else:
                auth = ''
            proxy = auth + pref.proxy + ':' + str(pref.proxy_port)
        else:
            proxy = None
        try:
            server = ServerProxy("http://ulipad.appspot.com/XMLRPC", transport=UrllibTransport(proxy))
            version = server.version()
            def _f():
                if version > Version.version:
                    dlg = UpdateDialog(Globals.mainframe, version)
                    dlg.ShowModal()
                    dlg.Destroy()
                else:
                    if force:
                        common.showmessage(tr("There is no newer version."))
            wx.CallAfter(_f)
        except Exception, e:
            if force:
                wx.CallAfter(common.showerror, e)

    if not force:
        d = Casing.Casing(f)
        d.start_thread()
    else:
        f()
def OnHelpCheckUpdate(win, event):
    check_update(True)
Mixin.setMixin('mainframe', 'OnHelpCheckUpdate', OnHelpCheckUpdate)

def on_show(win):
    if not Globals.pref.check_update:
        return
    wx.FutureCall(1000, check_update)
Mixin.setPlugin('mainframe', 'show', on_show)



#-----------------------  mWrapText.py ------------------

import wx
from modules import Globals
from modules import meide as ui
from modules import Mixin

class WrapTextDialog(wx.Dialog):
    def __init__(self, title=tr('Wrap Text'), values=None):
        wx.Dialog.__init__(self, Globals.mainframe, -1, style = wx.DEFAULT_DIALOG_STYLE, title = title, size=(600, 300))

        self.sizer = box = ui.VBox(namebinding='widget').create(self).auto_layout()
        grid = box.add(ui.SimpleGrid)
        grid.add(tr('Width'), ui.Int(75), name='width')
        grid.add(tr('Indent'), ui.Text(''), name='indent')
        grid.add(tr('First Line Indent'), ui.Text(''), name='firstindent')
        grid.add(tr('Skip Beginning Characters'), ui.Text(''), name='skipchar')
        grid.add(tr('Remove Tailing Characters'), ui.Text(''), name='remove_tailingchar')
        grid.add(tr('Add Tailing Characters'), ui.Text(''), name='add_tailingchar')
        box.add(ui.simple_buttons(), flag=wx.ALIGN_CENTER|wx.BOTTOM)

        box.auto_fit(2)

        if values:
            box.SetValue(values)

    def GetValue(self):
        return self.sizer.GetValue()

def add_mainframe_menu(menulist):
    menulist.extend([
        ('IDM_EDIT_FORMAT',
        [
            (126, 'IDM_EDIT_FORMAT_WRAP', tr('Wrap Text...')+'\tCtrl+Shift+T', wx.ITEM_NORMAL, 'OnEditFormatWrap', tr('Wraps selected text.')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_editor_menu(popmenulist):
    popmenulist.extend([
        ('IDPM_FORMAT',
        [
            (126, 'IDPM_FORMAT_WRAP', tr('Wrap Text...')+'\tE=Ctrl+Shift+T', wx.ITEM_NORMAL, 'OnFormatWrap', tr('Wraps selected text.')),
        ]),
    ])
Mixin.setPlugin('editor', 'add_menu', add_editor_menu)

def OnEditFormatWrap(win, event):
    OnFormatWrap(win.document, event)
Mixin.setMixin('mainframe', 'OnEditFormatWrap', OnEditFormatWrap)

def pref_init(pref):
    pref.wrap_width = 75
    pref.wrap_indent = ''
    pref.wrap_firstindent = ''
    pref.wrap_skipchar = ''
    pref.wrap_remove_tailingchar = ''
    pref.wrap_add_tailingchar = ''
Mixin.setPlugin('preference', 'init', pref_init)

def OnFormatWrap(win, event):
    pref = Globals.pref
    v = {'width':pref.wrap_width, 'indent':pref.wrap_indent,
        'firstindent':pref.wrap_firstindent, 'skipchar':pref.wrap_skipchar,
        'remove_tailingchar':pref.wrap_remove_tailingchar,
        'add_tailingchar':pref.wrap_add_tailingchar}
    dlg = WrapTextDialog(values=v)
    value = None
    if dlg.ShowModal() == wx.ID_OK:
        value = dlg.GetValue()
        pref.wrap_width = value['width']
        pref.wrap_indent = value['indent']
        pref.wrap_firstindent = value['firstindent']
        pref.wrap_skipchar = value['skipchar']
        pref.wrap_remove_tailingchar = value['remove_tailingchar']
        pref.wrap_add_tailingchar = value['add_tailingchar']
        pref.save()
    dlg.Destroy()
    if value:
        text = win.GetSelectedText()
        from modules.wraptext import wraptext
        text = wraptext(text, value['width'], cr=win.getEOLChar(),
            indent=value['indent'], firstindent=value['firstindent'],
            skipchar=value['skipchar'], remove_tailingchar=value['remove_tailingchar'],
            add_tailingchar=value['add_tailingchar'])
        start, end = win.GetSelection()
        win.SetTargetStart(start)
        win.SetTargetEnd(end)
        win.ReplaceTarget(text)
Mixin.setMixin('editor', 'OnFormatWrap', OnFormatWrap)

def mainframe_init(win):
    wx.EVT_UPDATE_UI(win, win.IDM_EDIT_FORMAT_WRAP, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'init', mainframe_init)

def editor_init(win):
    wx.EVT_UPDATE_UI(win, win.IDPM_FORMAT_WRAP, win.OnUpdateUI)
Mixin.setPlugin('editor', 'init', editor_init)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDM_EDIT_FORMAT_WRAP:
        event.Enable(win.document and win.document.GetSelectedText and len(win.document.GetSelectedText()) > 0)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def on_editor_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDPM_FORMAT_WRAP:
        event.Enable(len(win.GetSelectedText()) > 0)
Mixin.setPlugin('editor', 'on_update_ui', on_editor_updateui)



#-----------------------  mLexerBase.py ------------------

from modules import Mixin
import LexerBase
from modules import Globals

def add_pref(preflist):
    names = LexerBase.color_theme.keys()
    names.sort()
    preflist.extend([
        (tr('General'), 131, 'choice', 'default_color_theme', tr('Default color theme:'), names),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def pref_init(pref):
    pref.default_color_theme = 'Blue'
Mixin.setPlugin('preference', 'init', pref_init)

def set_default_style(lexer):
    lexer.set_color_theme(Globals.pref.default_color_theme)
Mixin.setPlugin('lexerbase', 'set_default_style', set_default_style)

def savepreferencevalues(values):
    mainframe = Globals.mainframe
    pref = Globals.pref
    if values['default_color_theme'] != pref.default_color_theme:
        mainframe.lexers.reset()
        for document in mainframe.editctrl.getDocuments():
            for lexer in mainframe.lexers.items():
                if document.languagename == lexer.name:
                    lexer.colourize(document, force=True)
                    break
Mixin.setPlugin('prefdialog', 'savepreferencevalues', savepreferencevalues)



#-----------------------  mGuessLang.py ------------------

import re
from modules import Mixin

r_lang = re.compile('^#!\s*/usr/bin/env\s+(\w+)')
def guess_language(win, language):
    l = win.GetLine(0).lower()
    lang = language
    if not lang and l[:2]=="#!":
        b = r_lang.search(l)
        if b:
            lang = b.groups()[0]

    return lang
Mixin.setPlugin('editor', 'guess_lang', guess_language)




