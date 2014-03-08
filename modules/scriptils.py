#   Programmer:     Helio Perroni Filho
#   E-mail:         xperroni@gmail.com
#
#   Copyleft 2011 Helio Perroni Filho
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

__doc__ = 'Colection of utility functions to create UliPad scripts.'

from StringIO import StringIO


def emptytab(win):
    r'''Returns a reference to an empty tab, creating one if the current tab
        is not empty.
    '''
    return win.document if isemptytab(win) else newtab(win)


def isdirtytab(win):
    r'''Checks whether the current editor tab's buffer is dirty (i.e. has
        contents not yet commited to disk).
    '''
    doc = win.document
    title = win.GetTitle()
    return doc.filename == '' or title.endswith('*')



def isemptytab(win):
    r'''Checks whether the current editor tab is a new tab with no contents.
    '''
    doc = win.document
    title = win.GetTitle()
    return doc.filename == '' and not title.endswith('*')


def newtab(win):
    r'''Creates a new tab, returning a reference to the enclosed document
        object.
    '''
    win.editctrl.new()
    return win.document


def reader(win):
    r'''Returns a file-like object with access to the current tab's contents.
        If the current tab is dirty, the memory buffer is accessed; otherwise,
        the underlying file is accessed.
    '''
    doc = win.document
    if isdirtytab(win):
        text = doc.GetText()
        return StringIO(text)
    else:
        return open(doc.filename)
