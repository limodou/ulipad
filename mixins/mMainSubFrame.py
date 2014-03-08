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
#   $Id: mMainSubFrame.py 1595 2006-10-12 03:01:34Z limodou $

from modules import Mixin
import MyPanel

class MainSubFrame(MyPanel.SashPanel, Mixin.Mixin):

    __mixinname__ = 'mainsubframe'

    def __init__(self, parent, mainframe):
        self.initmixin()
        self.parent = parent
        self.mainframe = mainframe
        self.mainframe.panel = self

        MyPanel.SashPanel.__init__(self, parent)
        
        self.callplugin('init', self)

def init(win):
    return MainSubFrame(win, win)
Mixin.setPlugin('mainframe', 'init', init)
