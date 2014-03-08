import wx
import pySonic
import time
import threading
import VolumeDialog
import images
from modules import Mixin
from modules import common

def afterinit(win):
    win.m3u=None
    win.isloop=True
    win.src=None
    win.selectedid=-1
    win.musiclist=None
    win.music=pySonic.World()
    win.flag_pause = False
    win.playing = None
    win.playingid=None

    wx.EVT_UPDATE_UI(win, win.IDM_MUSIC_PLAY, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_MUSIC_STOP, win.OnUpdateUI)
    wx.EVT_UPDATE_UI(win, win.IDM_MUSIC_PAUSE, win.OnUpdateUI)
Mixin.setPlugin('mainframe', 'afterinit', afterinit)

def afterclosewindow(win):
    if win.src:
        try:
            if win.src.IsPlaying():
                win.isloop=False
                win.src.Stop()
                time.sleep(0.5)
        except:
            pass
Mixin.setPlugin('mainframe', 'afterclosewindow', afterclosewindow)

menulist = [(None,
        [
            (850, 'IDM_MUSIC', tr('Music'), wx.ITEM_NORMAL, None, ''),
        ]),
        ('IDM_MUSIC',
        [
            (210, 'IDM_MUSIC_PLAY', tr('Music Play'),wx.ITEM_NORMAL, 'OnMusicPlay', tr('Music Open Window.')),
            (211, 'IDM_MUSIC_STOP', tr('Music Stop'),wx.ITEM_NORMAL, 'OnMusicStop', tr('Music Stop.')),
            (212, 'IDM_MUSIC_PAUSE', tr('Music Pause'),wx.ITEM_NORMAL, 'OnMusicPause', tr('Music Pause.')),
            (212, 'IDM_MUSIC_VOLUME', tr('Music Volume'),wx.ITEM_NORMAL, 'OnMusicVolume', tr('Music Volume.')),
        ]),
    ]
Mixin.setMixin('mainframe', 'menulist', menulist)

toollist = [
    (2201, 'musicplay'),
    (2202, 'musicstop'),
    (2203, 'musicpause'),
    (2204, 'musicvolume'),
    (2300,'|'),
]
Mixin.setMixin('mainframe', 'toollist', toollist)

toolbaritems = {
    'musicplay':(wx.ITEM_NORMAL, 'IDM_MUSIC_PLAY', images.getMusicplayBitmap(),
                 tr('Music Play'), tr('Music Open Window.'), 'OnMusicPlay'),
    'musicstop':(wx.ITEM_NORMAL, 'IDM_MUSIC_STOP', images.getMusicstopBitmap(),
                 tr('Music Stop'), tr('Music Stop.'), 'OnMusicStop'),
    'musicpause':(wx.ITEM_NORMAL, 'IDM_MUSIC_PAUSE', images.getMusicpauseBitmap(),
                 tr('Music Pause'), tr('Music Pause.'), 'OnMusicPause'),
    'musicvolume':(wx.ITEM_NORMAL, 'IDM_MUSIC_VOLUME', images.getMusicvolumeBitmap(),
                 tr('Music Volume'), tr('Music Volume.'), 'OnMusicVolume'),
    }
Mixin.setMixin('mainframe', 'toolbaritems', toolbaritems)

def OnMusicVolume(win,event):
    win = VolumeDialog.VolumeDialog(win, -1, "MusicVolume", win.music,)
    win.Show(True)
Mixin.setMixin('mainframe', 'OnMusicVolume', OnMusicVolume)

def OnMusicPlay(win, event):
    if win.src:
        if win.src.IsPlaying():
            win.isloop=False
            win.src.Stop()
            time.sleep(0.2)
    if win.m3u:
        win.playing=win.m3u[win.selectedid]
    else:
        return
    win.isloop=True
    win.flag_pause=False
    threading.Thread(target=playmusic, args=(win,)).start()
Mixin.setMixin('mainframe', 'OnMusicPlay', OnMusicPlay)

def OnMusicStop(win,event):
    if win.src:
        if win.src.IsPlaying():
            win.isloop=False
            win.src.Stop()
            time.sleep(0.2)
Mixin.setMixin('mainframe', 'OnMusicStop', OnMusicStop)

def OnMusicPause(win,event):
    if win.src:
        if win.src.IsPaused():
            win.flag_pause=False
        else:
            win.flag_pause=True

Mixin.setMixin('mainframe', 'OnMusicPause', OnMusicPause)

def playmusic(win):
    win.isloop=True
    win.playingid=win.selectedid
    while win.isloop:
        if len(win.m3u.data)==0:
            return
        if win.playingid!=-1:
            if win.playingid>=len(win.m3u.data):
                win.playingid=0
        else:
            return
        try:
            win.playing=win.m3u.data[win.playingid]
        except:
            return
        try:
            win.musiclist.setplaying(win.playing['Author-Title'])
        except:
            pass
        try:
            win.src=pySonic.Source()
            filename=win.playing['Path']
            filename = common.encode_path(filename)
            win.src.Sound = pySonic.FileStream(filename, 0)
            win.src.Play()
        except:
            dlg = wx.MessageDialog(win, tr('Can\'t play!'),
                               tr('Error'),
                               wx.OK | wx.ICON_ERROR
                               )
            dlg.ShowModal()
            dlg.Destroy()
            return
        while win.src.IsPlaying():
            if win.src.IsPaused():
                if not win.flag_pause:
                    win.src.Play()
                    continue
            else:
                if win.flag_pause:
                    win.src.Pause()
                    continue
            time.sleep(0.4)
        if win.isloop:
            win.playingid=win.playingid+1
        time.sleep(0.2)

menulist = [('IDM_MUSIC',
    [
        (209, 'IDM_MUSIC_LIST_OPEN', tr('Open Music List Window'), wx.ITEM_NORMAL, 'OnOpenMusicList', tr('Open Music List Window.')),
    ]),
]
Mixin.setMixin('mainframe', 'menulist', menulist)

popmenulist = [(None,
    [
        (950, 'IDPM_MUSIC_WINDOW', tr('Open Music List Window'), wx.ITEM_NORMAL, 'OnOpenMusicWindow', tr('Open Music List Window.')),
    ]),
]
Mixin.setMixin('notebook', 'popmenulist', popmenulist)

def createMusicListWindow(win):
    page = win.panel.getPage(tr('MusicList'))
    if not page:
        from MusicListManage import MusicListManage
        page = MusicListManage(win.panel.createNotebook('bottom'), win)
        win.panel.addPage('bottom', page, tr('MusicList'))
    win.musiclist = page
Mixin.setMixin('mainframe', 'createMusicListWindow', createMusicListWindow)

def OnOpenMusicList(win, event):
    win.createMusicListWindow()
    win.panel.showPage(tr('MusicList'))
Mixin.setMixin('mainframe', 'OnOpenMusicList', OnOpenMusicList)

def OnOpenMusicWindow(win, event):
    win.mainframe.createMusicListWindow()
    win.panel.showPage(tr('MusicList'))
Mixin.setMixin('notebook', 'OnOpenMusicWindow', OnOpenMusicWindow)


def OnUpdateUI(win,event):
    eid=event.GetId()
    if eid in (win.IDM_MUSIC_STOP,win.IDM_MUSIC_PAUSE,win.IDM_MUSIC_PLAY):
        event.Enable((win.selectedid!=-1) and True or False)
Mixin.setPlugin('mainframe', 'on_update_ui', OnUpdateUI)
