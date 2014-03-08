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
#   $Id$

#from modules.ZestyParser import *
from NCustomLexer import *
import re
    
class RstLexer(CustomLexer):

    metaname = 'rst'

    keywords = ['footer', 'figure', 'danger', 'sectnum', 'image', 
            'admonition', 'replace', 'topic', 'raw', 'warning', 
            'caution', 'rubric', 'unicode', 'table', 'sidebar', 
            'contents', 'csv-table', 'container', 'hint', 'highlights', 
            'target-notes', 'tip', 'note', 'list-table', 
            'restructuredtext-test-directive', 'role', 
            'section-numbering', 'include', 'header', 'attention', 
            'important', 'pull-quote', 'compound', 'date', 
            'default-role', 'class', 'parsed-literal', 'title', 
            'line-block', 'meta', 'error', 'epigraph', 'alt'] + ['status', 
            'copyright', 'author', 'abstract', 'address', 'contact', 
            'dedication', 'version', 'authors', 'date', 'organization', 
            'revision']

    preview_code = """==========================================
 Docutils_ Project Documentation Overview
==========================================

:Author: David Goodger
:Contact: goodger@python.org
:Date: $Date: 2005-12-14 18:37:07 +0100 (Wed, 14 Dec 2005) $
:Revision: $Revision: 4215 $
:Copyright: This document has been placed in the public domain.

The latest working documents may be accessed individually below, or
from the ``docs`` directory of the `Docutils distribution`_.

.. _Docutils: http://docutils.sourceforge.net/%AD/
.. _Docutils distribution: http://docutils.sourceforge.net/#download

.. contents::
"""

#    def pre_colourize(self, win):
        #FOLDING
#        win.enablefolder = True
#        win.SetProperty("fold", "1")
#        win.SetProperty("tab.timmy.whinge.level", "1")

    def initSyntaxItems(self):
        self.addSyntaxItem('r_default',         'Default',              STYLE_DEFAULT,           self.STC_STYLE_TEXT)
        self.addSyntaxItem('keyword',           'Keyword',              STYLE_KEYWORD,           self.STC_STYLE_KEYWORD1)
        self.addSyntaxItem('inlineliteral',     'Inline Literal',       3,           self.STC_STYLE_STRING)
        self.addSyntaxItem('directurl',         'DirectUrl',            4,           self.STC_STYLE_LINK)
        self.addSyntaxItem('interpretedtext',   'Interpreted Text',     5,           self.STC_STYLE_TAG)
        self.addSyntaxItem('bold',              'Bold',                 6,           self.STC_STYLE_KEYWORD2)
        self.addSyntaxItem('emphasis',          'Emphasis',             7,           self.STC_STYLE_COMMENT)
    
    def loadToken(self):
        return TokenList([
            (re.compile(r'^\.\. (.+?)::', re.M), self.is_keyword(1)),
            (re.compile(r'^\s*:(.+?):', re.M), self.is_keyword(1)),
            (re.compile(r'``.*?``'), 3),
            (re.compile(r'\b_`.*?`|`.*?`_\b|\b\w+_\b|\b_\w+\b'), 5),
            (re.compile(r'\*\*.*?\*\*'), 6),
            (re.compile(r'\*.*?\*'), 7),
            (PATTERN_EMAIL, 4),
            (PATTERN_URL, 4),
        ])

