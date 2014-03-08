#---------------------------------------------------
#                   UliPad script
# Author  :limodou
# Date    :2005/03/29
# Version :1.0
# Description:
#     Dict replace
#
#---------------------------------------------------
def run(win):
    import common

    delimeter = ';'
    dlg = wx.FileDialog(win, tr("Open Dict File"), "", "", "All files(*.*)|*.*", wx.OPEN|wx.HIDE_READONLY)
    if dlg.ShowModal() == wx.ID_OK:
        filename = dlg.GetPath().encode(common.defaultfilesystemencoding)
        d = {}
        lines = file(filename).readlines()
        for line in lines:
            if not line.strip(): continue
            a, b = line.split(delimeter)
            d[a] = b.strip()
        text = win.document.GetText()
        text = text.encode(win.document.locale)
        for a, b in d.items():
            text = text.replace(a, b)
        win.document.SetText(unicode(text, win.document.locale))

run(win)
