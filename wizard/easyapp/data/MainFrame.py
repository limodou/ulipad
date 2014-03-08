#coding=<#encoding#>

import wx
import resource
from EasyGuider import EasyActions
from EasyGuider import EasyMenu

class MainFrame(wx.Frame):

    def __init__(self, title=''):
        wx.Frame.__init__(self, None, -1, title)

        alist = EasyActions.makeactions(resource.actions)
        EasyMenu.makemenubar(self, alist, resource.menubar)
        EasyMenu.maketoolbar(self, alist, resource.toolbar)

        self.init()

        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def init(self):
        """add your initialization code"""
        pass

    def OnClose(self, event):
        event.Skip()

    def OnExit(self, event):
        self.Close()

    #add other event handler function
