#   Programmer:     limodou
#   E-mail:         limodou@gmail.com
#   
#   Copyleft 2006 limodou
#   
#   Distributed under the terms of the GPL (GNU Public License)
#   
#   UliPad is free software; you can redistribute it and/or modify
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
#   $Id: DocumentBase.py 1540 2006-09-29 04:43:04Z limodou $

__doc__ = 'Document base class'

import os.path
import wx

class PanelBase:
    documenttype = 'default'

    def __init__(self, parent, filename, **kwargs):
        self.parent = parent
        self.filename = filename
        self.document = self.createDocument(**kwargs)

    def createDocument(self, **kwargs):
        return DocumentBase(self, self.filename, self.documenttype, **kwargs)

class NULL_CLASS:
    def __call__(self, *argv, **kwargs):
        return None

    def __nonzero__(self):
        return False

    def __str__(self):
        return ''

    def __eq__(self, other):
        if not other:
            return True
        else:
            return False

    def __ne__(self, other):
        if other:
            return True
        else:
            return False

    def __int__(self):
        return 0

class DocumentBase:
    def __init__(self, parent, filename, documenttype, **kwargs):
        self.parent = parent
        self.panel = parent
        self.edittype = 'edit'          #edit is the commonly usage, whick indicate this is a editor
        self.documenttype = documenttype
        self.filename = filename
        self.pageimagename = documenttype
        self.languagename = ''          #like c, html, python
        self.locale = ''
        self.cansavefileflag = False
        self.needcheckfile = False
        self.savesession = False
        self.title = ''
        self.canopenfileflag = False
        self.canedit = False
        self.opened = False

    def openfile(self, filename='', encoding='', delay=False, *args, **kwargs):
        self.filename = filename
        self.locale = encoding
        self.opened = False

    def savefile(self, filename, encoding):
        self.filename = filename
        self.locale = encoding

    def getShortFilename(self):
        if self.title:
            if len(self.title) > 10:
                return self.title[:10] + '...'
            return self.title
        return os.path.basename(self.getFilename())

    def getFilename(self):
        if self.title:
            return self.title
        return self.filename

    def isModified(self):
        return False

    def isMe(self, filename, documenttype='texteditor'):
        if wx.Platform == '__WXMSW__':
            if isinstance(filename, unicode):
                file1 = filename.encode('utf-8')
            else:
                file1 = filename
            file1 = file1.lower()
            if isinstance(self.filename, unicode):
                file2 = self.filename.encode('utf-8')
            else:
                file2 = self.filename
            file2 = file2.lower()
            flag = file1 == file2
        else:
            flag = filename == self.filename
        if filename and flag and self.documenttype == documenttype:
            return True
        else:
            return False

    def canopenfile(self, filename, documenttype='texteditor'):
        return self.canopenfileflag and not self.isModified() and self.documenttype == documenttype

    def isReadOnly(self):
        return False

    def cansavefile(self):
        return self.cansavefileflag

    def needcheck(self):
        return self.needcheckfile

    def __eq__(self, obj):
        return id(self) == id(obj)

    def __ne__(self, obj):
        return id(self) != id(obj)

    def __nonzero__(self):
        return True

    def __getattr__(self, name):
        return NULL_CLASS()

    def setFilename(self, filename):
        self.filename = filename
        self.callplugin('setfilename', self, filename)
