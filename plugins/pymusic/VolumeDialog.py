import  wx

class VolumeDialog(wx.Dialog):
    def __init__(
            self, parent, ID, title, music,pos=wx.DefaultPosition,
            size=wx.DefaultSize,style=wx.DEFAULT_DIALOG_STYLE
            ):
        wx.Dialog.__init__(self, parent, ID)
        self.music=music
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.label=wx.StaticText(self,-1,tr('Volume'))
        sizer.Add(self.label, 0 , wx.ALIGN_CENTRE|wx.ALL,5)
        self.slider = wx.Slider(self, 3001, 1, 1, 255, (0, 0),(50,120), wx.SL_VERTICAL|wx.SL_LEFT)
        sizer.Add(self.slider, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        #wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS
        self.slider.SetTickFreq(5, 1)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.Bind(wx.EVT_SCROLL,self.OnScroll)
    def OnCloseWindow(self, event):
        self.Destroy()
    def OnScroll(self,event):
        self.music.MasterVolume=256-self.slider.GetValue()
