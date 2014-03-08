import wx
import glob
import os
from modules import Globals

def _acp_fname(language_name):
    return os.path.join(Globals.confpath, '%s.acp' % language_name)


def add_mainframe_menu(menulist):
    menulist.extend([('IDM_TOOL', #parent menu id
        [
            (160, 'IDM_TOOL_CFG_AUTOACP', tr('Configure AutoACP...'),
            wx.ITEM_NORMAL, 'OnConfigureAutoACP',
            tr('Configure Auto ACP')),
        ]),
    ])


def pref_init(pref):
    '''Called to handle "preference initialization."

    pref is a magical object that pickles it's attributes.  So any attribute you
    set, will be saved when Ulipad is shutdown.  When Ulipad starts, it loads
    the pref object from the last saved instance.
    '''
    # auto_acpd is a dictionary mapping parent acps to a list of sub-acps.
    # Here, we provide a default empty dictionary which will be used the first
    # time this plugin is called.
    pref.auto_acpd = getattr(pref, 'auto_acpd', {})


def on_document_lang_enter(win, document):
    '''Install sub acp's when the lang_enter event occurs.

    This event is called when the document changes and the language type
    changes.

    win: a mixins.EditorFactory.EditorFactory instance.
    document: a mixins.Editor.TextEditor instance.
    '''
    acpd = Globals.pref.auto_acpd
    if document.languagename not in acpd:
        return

    ia = Globals.mainframe.input_assistant
    for acp in acpd.get(document.languagename, []):
        acp_fname = _acp_fname(acp)
        document.custom_assistant.append(ia.get_assistant(acp_fname))
    ia.install_acp(document, document.languagename, True)


def on_configure(win, event):
    '''Called when the TOOL -> Configure AutoACP... is selected from the menu.

    When the user selects Configure AutoACP, the ConfigAutoAcpDlg is displayed
    allowing the user to select the SUB ACP's for each available ACP.

    win: mixins.Mainframe.Mainframe instance.
    event: not sure.
    '''
    # This code was ripped from mInputAssistant.py
    ia = win.input_assistant
    win = win.editctrl.getCurDoc()

    # Get a list of acp's installed for the current language.
    installed_acps = [acp.filename for acp in ia.get_acp(win.languagename)]

    # Now the custom ACP's
    custom_acps = [obj.filename for obj in win.custom_assistant]

    # Grab *all* of the acp's.
    all_acps = (glob.glob(os.path.join(Globals.workpath, '*.acp')) +
                glob.glob(os.path.join(Globals.confpath, '*.acp')))

    # TODO: figure out how to reflect the current ACP's
    # Update the Globals.pref.auto_acpd to reflect the current ACP's.  This can
    # be changed by selecting Document -> Apply Autocompleted Files from the
    # menu.  (I'm not sure of a good way to do this.)

    from ConfigAutoAcpDlg import ConfigAutoAcpDlg
    dlg = ConfigAutoAcpDlg(win, all_acps = all_acps,
                           installed_acps = Globals.pref.auto_acpd)
    if dlg.ShowModal() == wx.CANCEL:
        return

    Globals.pref.auto_acpd = dlg.installed_acps