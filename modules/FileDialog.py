#coding=gb2312
class _DUMYCLASS:pass

def openfiledlg(title, message, defaultdir='', filefilter='*.*'):
    obj = _DUMYCLASS()
    obj.title = title
    obj.dialog = [
        ('static', 'message', message, '', None),
        ('openfile', 'file', '', '', None),
    ]
    from EasyGuider import EasyCommander
    easy = EasyCommander.EasyCommander(easyfile=obj)
    try:
        if easy.run():
            f = easy.GetValue()['file']
            return f
        else:
            return None
    finally:
        easy.Destroy()

def savefiledlg(title, message, defaultdir='', filefilter='*.*'):
    obj = _DUMYCLASS()
    obj.title = title
    obj.dialog = [
        ('static', 'message', message, '', None),
        ('savefile', 'file', '', '', None),
    ]
    from EasyGuider import EasyCommander
    easy = EasyCommander.EasyCommander(easyfile=obj)
    try:
        if easy.run():
            f = easy.GetValue()['file']
            return f
        else:
            return None
    finally:
        easy.Destroy()
