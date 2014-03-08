#name:Remove Blank Line

def run(win):
    text = win.document.GetText()
    lines = text.splitlines()
    s = []
    for line in lines:
        if not line.strip(): continue
        s.append(line)
    win.document.SetText(win.document.getEOLChar().join(s))
run(win)
