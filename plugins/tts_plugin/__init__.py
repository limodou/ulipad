#   Programmer: limodou
#   E-mail:     limodou@gmail.com
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
#   $Id: PythonDoc.py 42 2005-09-28 05:19:21Z limodou $

from modules import Mixin
import wx
from modules import common
from modules.Debug import error

menulist = [ ('IDM_DOCUMENT', #parent menu id
    [
        (160, '', '-', wx.ITEM_SEPARATOR, '', ''),
        (170, 'IDM_DOCUMENT_STARTREAD', tr('Start Read Document'), wx.ITEM_NORMAL, 'OnDocumentStartRead', tr('Start read current document.')),
        (180, 'IDM_DOCUMENT_STOPREAD', tr('Stop Read Document'), wx.ITEM_NORMAL, 'OnDocumentStopRead', tr('Stop read current document.')),
        (180, 'IDM_DOCUMENT_VOICECONFIG', tr('Text To Speech Setting'), wx.ITEM_NORMAL, 'OnDocumentVoiceConfig', tr('Text to Speech setting.')),
    ]),
]
Mixin.setMixin('mainframe', 'menulist', menulist)

def init(pref):
    pref.tts_rate = -1
    pref.voice_name = ''
Mixin.setPlugin('preference', 'init', init)

def init(win):
    win.reading = False
    win.pytts = None
    win.pytts_flag = None
Mixin.setPlugin('mainframe', 'init', init)

def afterinit(win):
    wx.EVT_UPDATE_UI(win, win.IDM_DOCUMENT_STARTREAD, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_DOCUMENT_STOPREAD, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def OnUpdateUI(win, event):
    eid = event.GetId()
    if eid == win.IDM_DOCUMENT_STARTREAD:
        event.Enable(not win.reading)
    elif eid == win.IDM_DOCUMENT_STOPREAD:
        event.Enable(win.reading)
Mixin.setPlugin('mainframe', 'on_update_ui', OnUpdateUI)

def OnDocumentStartRead(win, event):
    if not win.pytts:
        try:
            import pyTTS
            win.pytts = pyTTS.Create()
            win.pytts_flag = pyTTS.tts_is_xml, pyTTS.tts_async
            win.pytts.OnEndStream = win.OnTTSEndStream
        except:
            error.traceback()
            common.showerror(win, tr("Can't import pyTTS module, please install it first."))
            return
    if win.document.hasSelection():
        text = win.document.GetSelectedText()
    else:
        text = win.document.GetText()
    win.reading = True
    import tts
    win.pytts.Rate = win.pref.tts_rate
    if win.pref.voice_name:
        win.pytts.SetVoiceByName(win.pref.voice_name)
    win.pytts.Speak(tts.maketext(text), *win.pytts_flag)
Mixin.setMixin('mainframe', 'OnDocumentStartRead', OnDocumentStartRead)

def OnDocumentStopRead(win, event):
    if win.reading:
        win.pytts.Stop()
        win.reading = False
Mixin.setMixin('mainframe', 'OnDocumentStopRead', OnDocumentStopRead)

def OnTTSEndStream(win, event):
    win.reading = False
Mixin.setMixin('mainframe', 'OnTTSEndStream', OnTTSEndStream)

def OnDocumentVoiceConfig(win, event):
    if not win.pytts:
        try:
            import pyTTS
            win.pytts = pyTTS.Create()
            win.pytts_flag = pyTTS.tts_is_xml, pyTTS.tts_async
            win.pytts.OnEndStream = win.OnTTSEndStream
        except:
            error.traceback()
            common.showerror(win, tr("Can't import pyTTS module, please install it first."))
            return
    voices = win.pytts.GetVoiceNames()
    if not voices:
        common.showerror(win, tr("There is no available voices installed"))
        return
    if not win.pref.voice_name:
        win.pref.voice_name = voices[0]
    dialog = [
            ('single', 'voice_name', win.pref.voice_name, tr('Voice names:'), zip(voices, voices)),
            ('int', 'tts_rate', win.pref.tts_rate, tr('TTS speak rate:'), None)
        ]
    from modules.EasyGuider import EasyDialog
    dlg = EasyDialog.EasyDialog(win, title=tr("Text to Speech setting"), elements=dialog)
    values = None
    if dlg.ShowModal() == wx.ID_OK:
        values = dlg.GetValue()
    dlg.Destroy()
    win.pref.tts_rate = values['tts_rate']
    win.pref.voice_name = values['voice_name']
    win.pref.save()
Mixin.setMixin('mainframe', 'OnDocumentVoiceConfig', OnDocumentVoiceConfig)