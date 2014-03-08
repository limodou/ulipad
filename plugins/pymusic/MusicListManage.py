__doc__ = 'Music List'

import wx
from modules.Debug import error
import os
import PyM3u
import threading
import time
from modules import common
from modules import CheckList
from modules import Globals

class MusicListManage(wx.Panel):
    def __init__(self, parent, mainframe):
        self.parent = parent
        self.mainframe = mainframe
        self.defm3u = os.path.join(Globals.userpath, 'default.m3u')
        if not os.path.isfile(self.defm3u):
            fout=open(self.defm3u,'w')
            fout.write('#EXTM3U\n')
            fout.close()
        self.m3u=PyM3u.M3u(self.defm3u)
        self.mainframe.m3u=self.m3u
        self.m3u.Load()
        self.mainframe.selectedid=-1
        wx.Panel.__init__(self, parent, -1)
        box = wx.BoxSizer(wx.VERTICAL)
        box1 = wx.BoxSizer(wx.HORIZONTAL)

        self.m3u_filename = wx.StaticText(self, -1, '')
        self.playingname = wx.StaticText(self,-1,'')
        box.Add(self.m3u_filename, 0, wx.ALL|wx.EXPAND, 3)
        box.Add(self.playingname, 0, wx.ALL|wx.EXPAND, 3)

        #add button
        self.ID_ADD = wx.NewId()
        self.btnAdd = wx.Button(self, self.ID_ADD, tr('Add'))
        box1.Add(self.btnAdd, 0, wx.RIGHT, 2)

        self.ID_ADDDIR =wx.NewId()
        self.btnAddDir = wx.Button(self, self.ID_ADDDIR, tr('AddDir'))
        box1.Add(self.btnAddDir, 0, wx.RIGHT, 2)

        self.ID_DEL = wx.NewId()
        self.btnDel = wx.Button(self, self.ID_DEL, tr('Delete'))
        box1.Add(self.btnDel, 0, wx.RIGHT, 2)

        self.ID_OPEN = wx.NewId()
        self.btnOpen = wx.Button(self, self.ID_OPEN, tr('OpenList'))
        box1.Add(self.btnOpen, 0, wx.RIGHT, 2)


        self.ID_SAVE = wx.NewId()
        self.btnSave = wx.Button(self, self.ID_SAVE, tr('SaveList'))
        box1.Add(self.btnSave, 0, wx.RIGHT, 2)

        box.Add(box1, 0, wx.ALL, 3)


        #create listctrl
        self.musiclist = CheckList.List(self, columns=[
                (tr("Id"), 30, 'left'),
                (tr("Author - Title"), 280, 'left'),
                (tr("Time"), 80, 'right'),
                (tr("Path"), 400, 'left'),
                ], style=wx.LC_REPORT | wx.SUNKEN_BORDER)

        box.Add(self.musiclist, 1, wx.EXPAND)

        wx.EVT_BUTTON(self.btnAdd, self.ID_ADD, self.OnAdd)
        wx.EVT_BUTTON(self.btnAddDir, self.ID_ADDDIR, self.OnAddDir)
        wx.EVT_BUTTON(self.btnDel, self.ID_DEL, self.OnDel)
        wx.EVT_BUTTON(self.btnOpen, self.ID_OPEN, self.OnOpen)
        wx.EVT_BUTTON(self.btnSave, self.ID_SAVE, self.OnSave)
        wx.EVT_LIST_ITEM_ACTIVATED(self.musiclist,self.musiclist.GetId(),self.OnActivated)
        wx.EVT_LIST_ITEM_SELECTED(self.musiclist,self.musiclist.GetId(),self.OnSelected)

        self.SetSizer(box)
        self.SetAutoLayout(True)
        self.OnUpdateData()

    def OnActivated(self,event):
        if self.mainframe.src:
            if self.mainframe.src.IsPlaying():
                self.mainframe.isloop=False
                self.mainframe.flag_pause=False
                self.mainframe.src.Stop()
                time.sleep(0.2)
        self.mainframe.selectedid=int(event.GetText()-1)
        from plugins.pymusic import playmusic
        self.mainframe.playing=self.m3u[self.mainframe.selectedid]
        threading.Thread(target=playmusic, args=(self.mainframe,)).start()
        self.setplaying(self.mainframe.playing['Author-Title'])

    def OnSelected(self,event):
        self.mainframe.selectedid=int(event.GetText())
        
    def OnAdd(self, event):
        dialog = wx.FileDialog(self.mainframe,
                               "Add Media File To Music List",
                               "",
                               "",
                               "Media files(*.mp3;*.wma;*.asf;*.mid;*.wav)|*.mp3;*.wma;*.asf;*.mid;*.wav",
                               wx.OPEN|wx.MULTIPLE  )
        filenames=[]
        filename = ''
        if dialog.ShowModal() == wx.ID_OK:
            filenames = dialog.GetPaths()
        dialog.Destroy()
        record={}
        for filename in filenames:
            if self.m3u.isExists(filename):
                continue
            if filename.lower().endswith(".mp3"):
                from PyMp3Info import MP3FileInfo
                fi=MP3FileInfo(filename)
                if fi.parse():
                    record['Author-Title']=(fi['author'] and fi['author']+' - ' or '')+fi['title']
                else:
                    record['Author-Title']=os.path.split(filename)[-1]
            else:
                record['Author-Title']=os.path.split(filename)[-1]
            try:
                from pySonic import FileStream
                f=FileStream(common.encode_string(filename, common.defaultfilesystemencoding),0)
                record['Time']=str(int(f.Duration))
                del f
            except:
                error.traceback()
                dlg = wx.MessageDialog(self, tr('Can\'t add file [%s] or this file isn\'t a media file!') % filename,
                               tr('Error'),
                               wx.OK | wx.ICON_ERROR
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
                dlg.ShowModal()
                dlg.Destroy()
                record={}
                continue
            record['Path']=filename
            self.m3u.Append(record)
            self.addrecord(record)
        self.m3u.SaveToFile(self.defm3u)
            
    def OnAddDir(self,event):
        dialog = wx.DirDialog(self.mainframe,
                               "Add Dir\All Media files to Music List",
                               ".",
                               0,
                               name="Add Dir"
                              )
        path=[]
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
        else:
            return
        for root, dirs, files in os.walk(path):
            for file in files:
                filename=os.path.join(root,file)
                if self.m3u.isExists(filename):
                    continue
                if filename[-4:].lower() in ['.mp3','.wav','.mid','.wma','.asf']:
                    file = common.decode_string(filename, common.defaultfilesystemencoding)
                    record={}
                    if filename.lower().endswith(".mp3"):
                        from PyMp3Info import MP3FileInfo
                        fi = MP3FileInfo(filename)
                        if fi.parse():
                            record['Author-Title']=(fi['author'] and fi['author']+' - ' or '')+fi['title']
                        else:
                            record['Author-Title']=os.path.split(filename)[-1]
                    else:
                        record['Author-Title']=os.path.split(filename)[-1]
                    try:
                        from pySonic import FileStream
                        f=FileStream(common.encode_string(filename, common.defaultfilesystemencoding), 0)
                        record['Time']=str(int(f.Duration))
                        del f
                    except:
                        dlg = wx.MessageDialog(self, tr('Can\'t add file [%s] or this file isn\'t a media file!') % filename,
                                       tr('Error'),
                                       wx.OK | wx.ICON_ERROR
                                       )
                        dlg.ShowModal()
                        dlg.Destroy()
                        continue
                    record['Path'] = filename
                    self.m3u.Append(record)
                    self.addrecord(record)
        self.m3u.SaveToFile(self.defm3u)

    def OnDel(self, event):
        item = self.musiclist.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        while item > -1:
            self.musiclist.delline(item)
            self.m3u.Delete(item)
            item = self.musiclist.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
        self.mainframe.selectedid = -1
        self.m3u.SaveToFile(self.defm3u)
        
        for i in range(self.musiclist.GetItemCount()):
            self.musiclist.SetStringItem(i,0,str(i).rjust(3))

    def OnSave(self, event):
        filepath=os.path.split(self.m3u.filepath)
        dialog = wx.FileDialog(self.mainframe, "Save M3u File", filepath[0], filepath[1], "M3u files(*.m3u)|*.m3u", wx.SAVE|wx.OVERWRITE_PROMPT )
        filename = ''
        if dialog.ShowModal() == wx.ID_OK:
            filename = dialog.GetPath()
        dialog.Destroy()
        if filename:
            self.m3u.SaveToFile(filename)

    def OnOpen(self, event):
        if self.m3u.IsModify():
            dialog=wx.MessageDialog(self.mainframe,"Save the m3u file to file ?",'Save m3u file!',wx.YES_NO|wx.YES_DEFAULT)
            if dialog.ShowModal()==wx.ID_YES:
                self.OnSave()
            dialog.Destroy()
        dialog = wx.FileDialog(self.mainframe, "Open M3u File", "", "", "M3u files(*.m3u)|*.m3u", wx.OPEN )
        filename = ''
        if dialog.ShowModal() == wx.ID_OK:
            filename = dialog.GetPath()
        dialog.Destroy()
        if filename:
            self.m3u.ClearAll()
            self.m3u.Load(filename)
            self.OnUpdateData()

    def addrecord(self,record):
        lastid=self.musiclist.GetItemCount()
        self.musiclist.addline([
            str(lastid+1),
            common.decode_string(record['Author-Title'], common.defaultfilesystemencoding),
            timeformat(record['Time']),
            common.decode_string(record['Path'], common.defaultfilesystemencoding)
            ])

    def setplaying(self,playing):
        self.playingname.SetLabel('Playing : %s'%playing)
        
    def OnUpdateData(self):
        self.m3u_filename.SetLabel('M3U File : '+self.m3u.GetFilePath())
        if self.mainframe.playing:
            self.setplaying(self.mainframe.playing['Author-Title'])
        else:
            self.setplaying('Playing : No Playing')
        self.musiclist.DeleteAllItems()
        for id in range(len(self.m3u.data)):
            self.musiclist.InsertStringItem(id,str(id+1))
            record=self.m3u.data[id]
            try:
                self.musiclist.SetStringItem(id,1,record['Author-Title'])
            except:
                self.musiclist.SetStringItem(id,1,os.path.split(record['Path'])[-1])
            self.musiclist.SetStringItem(id,2,timeformat(record['Time']))
            try:
                self.musiclist.SetStringItem(id,3,record['Path'])
            except:
                self.musiclist.SetStringItem(id,3,'?'*len(record['Path']))

def timeformat(s):
    t = int(s)
    h, t = divmod(t, 3600)
    s = ''
    if h:
        s += '%dh' % h
    m, t = divmod(t, 60)
    if m:
        s += "%d'" % m
    if t:
        s += '%d"' % t
    return s