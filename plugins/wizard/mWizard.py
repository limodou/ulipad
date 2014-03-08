#   Programmer: limodou
#   E-mail:     limodou@gmail.coms
#
#   Copyleft 2006 limodou
#
#   Distributed under the terms of the GPL (GNU Public License)
#
#   NewEdit is free software; you can redistribute it and/or modify
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
#   $Id: mSnippets.py,v 1.8 2004/11/27 15:52:08 limodou Exp $

from modules import Mixin
import wx
import images

menulist = [
    ('IDM_WINDOW',
    [
        (190, 'IDM_WINDOW_WIZARD', tr('Wizard Window'), wx.ITEM_CHECK, 'OnWindowWizard', tr('Opens wizard window.'))
    ]),
]
Mixin.setMixin('mainframe', 'menulist', menulist)

popmenulist = [ (None,
    [
        (140, 'IDPM_WIZARDWINDOW', tr('Wizard Window'), wx.ITEM_CHECK, 'OnWizardWindow', tr('Opens wizard window.')),
    ]),
]
Mixin.setMixin('notebook', 'popmenulist', popmenulist)

toollist = [
        (550, 'wizard'),
]
Mixin.setMixin('mainframe', 'toollist', toollist)

_wizard_pagename = tr('Wizard')

#order, IDname, imagefile, short text, long text, func
toolbaritems = {
        'wizard':(wx.ITEM_CHECK, 'IDM_WINDOW_WIZARD', images.getWizardBitmap(), _wizard_pagename, tr('Opens wizard window.'), 'OnWindowWizard'),
}
Mixin.setMixin('mainframe', 'toolbaritems', toolbaritems)

def on_mainframe_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDM_WINDOW_WIZARD:
        event.Check(bool(win.panel.getPage(_wizard_pagename)) and win.panel.LeftIsVisible)
Mixin.setPlugin('mainframe', 'on_update_ui', on_mainframe_updateui)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_WINDOW_WIZARD, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def on_notebook_updateui(win, event):
    eid = event.GetId()
    if eid == win.IDPM_WIZARDWINDOW:
        event.Check(bool(win.panel.getPage(_wizard_pagename)) and win.panel.LeftIsVisible)
Mixin.setPlugin('notebook', 'on_update_ui', on_notebook_updateui)

def init(win):
    wx.EVT_UPDATE_UI(win, win.IDPM_WIZARDWINDOW, win.OnUpdateUI)
Mixin.setPlugin('notebook', 'init', init)

def createWizardWindow(win):
    if not win.panel.getPage(_wizard_pagename):
        from WizardPanel import WizardPanel

        page = WizardPanel(win.panel.createNotebook('left'), win)
        win.panel.addPage('left', page, _wizard_pagename)
Mixin.setMixin('mainframe', 'createWizardWindow', createWizardWindow)

def OnWindowWizard(win, event):
    if not win.panel.getPage(_wizard_pagename):
        win.createWizardWindow()
        win.panel.showPage(_wizard_pagename)
    else:
        win.panel.closePage(_wizard_pagename)
Mixin.setMixin('mainframe', 'OnWindowWizard', OnWindowWizard)

def OnWizardWindow(win, event):
    if not win.panel.getPage(_wizard_pagename):
        win.mainframe.createWizardWindow()
        win.panel.showPage(_wizard_pagename)
    else:
        win.panel.closePage(_wizard_pagename)
Mixin.setMixin('notebook', 'OnWizardWindow', OnWizardWindow)
