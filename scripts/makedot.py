
def run(win):
    import wx

    if win.document.isModified() or win.document.filename == '':
        d = wx.MessageDialog(win, tr("The file has not been saved, and it would not be run.\nWould you like to save the file?"), tr("Run"), wx.YES_NO | wx.ICON_QUESTION)
        answer = d.ShowModal()
        d.Destroy()
        if (answer == wx.ID_YES):
            win.OnFileSave(None)
        else:
            return

    class MOD:pass

    mod = MOD()

    mod.dialog = [
    ('savefile', 'imagefile', '', 'Saving image filename:', None),
    ('single', 'filetype', 'png', 'Image file type:', [('Gif', 'gif'), ('Png', 'png'), ('Jpeg', 'jpg')]),
    ('string', 'args', '', 'Other command line options:', None),
    ]
    mod.title = 'Input dot command line'

    from modules.EasyGuider import EasyCommander
    from modules.Debug import error
    from modules import common

    easy = EasyCommander.EasyCommander(win, mod, cmdoption='')
    if easy.run():
        values = easy.GetValue()
        import os
        try:
            cmd = 'dot -T%s -o%s %s %s' % (values['filetype'], common.encode_string(values['imagefile'], common.defaultfilesystemencoding), values['args'], win.document.filename)
            win.createMessageWindow()
            win.panel.showPage(tr('Message'))
            win.messagewindow.SetText(cmd)
            os.system(cmd)
        except:
            error.traceback()
            common.showerror(win, tr("Can't execute [%s]") % cmd)
            return
        if os.path.exists(values['imagefile']):
            from modules import ImageWin
            try:
                win = ImageWin.ImageWin(win, values['imagefile'])
                win.Show()
            except:
                common.showerror(win, tr("Can't open image file %s") % values['imagefile'])

run(win)
