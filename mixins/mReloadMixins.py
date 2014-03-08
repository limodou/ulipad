#   Programmer:     ygao
#   E-mail:         ygao2004@gmail.com
#
#   Copyleft 2007 ygao
#
#   Distributed under the terms of the GPL (GNU Public License)
#   this patch was maded by ygao for Ulipad.
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
#    Globals.mainframe.Close()
Mixin.setMixin('mainframe', 'OnToolreload_mixins', OnToolreload_mixins)


def pref_init(pref):
    pref.mixin_reload_mixins_mode = False
    pref.mixin_reload_name = []
Mixin.setPlugin('preference', 'init', pref_init)



