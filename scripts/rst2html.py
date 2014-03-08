#---------------------------------------------------
#                   UliPad script
# Author  :limodou
# Date    :2004/07/08
# Version :1.0
# Description:
#     Convert reStructuredText to Html
# Name: Convert reStructuredText to Html
#
#---------------------------------------------------
def run(win):
    from docutils.core import publish_file
    import os.path
    import StringIO

    filename = win.document.filename
    fi=StringIO.StringIO(win.document.GetText().encode(win.document.locale))
    f, ext = os.path.splitext(filename)
    htmlfile = f+'.htm'
    fo=open(htmlfile, "w")
    publish_file(source=fi, destination=fo, writer_name='html')
    fi.close()
    fo.close()
    win.SetStatusText('Success!')
#       win.editctrl.new(htmlfile)

run(win)
