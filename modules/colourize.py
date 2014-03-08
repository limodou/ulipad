# -*- coding: iso-8859-1 -*-
"""
    MoinMoin - Python Source Parser

    @copyright: 2001 by Jürgen Hermann <jh@web.de>
    @license: GNU GPL, see COPYING for details.
"""

# Imports
import StringIO
import keyword, token, tokenize
import cgi
import types

#############################################################################
### Python Source Parser (does Hilighting)
#############################################################################

_KEYWORD = token.NT_OFFSET + 1
_TEXT    = token.NT_OFFSET + 2

_colors = {
    token.NUMBER:       '#0080C0',
    token.OP:           '#0000C0',
    token.STRING:       '#804000',
    tokenize.COMMENT:   '#008000',
    token.NAME:         '#000000',
    token.ERRORTOKEN:   '#FF8080',
    _KEYWORD:           '#0000FF',
    _TEXT:              '#000000',
}


class Parser:
    """ Send colored python source.
    """

    def __init__(self, raw):
        """ Store the source text.
        """
        self.raw = raw.expandtabs().rstrip()
        self.unicode = False
        self.result = []

    def format(self, linenumber=True):
        """ Parse and send the colored source.
        """
        # store line offsets in self.lines
        self.lines = [0, 0]
        pos = 0
        while 1:
            pos = self.raw.find('\n', pos) + 1
            if not pos: break
            self.lines.append(pos)
        self.lines.append(len(self.raw))

        # write line numbers
        if linenumber:
            self.result.append('<table border="0"><tr><td align="right" valign="top">')
            self.result.append('<td align="right" valign="top"><pre><font face="Lucida,Courier New" color="%s">' % _colors[_TEXT])
            for idx in range(1, len(self.lines)-1):
                self.result.append('%3d \n' % idx)
            self.result.append('</font></pre></td><td valign="top">')

        # parse the source and write it
        self.pos = 0
        text = StringIO.StringIO(self.raw)
        self.result.append('<pre><font face="Lucida,Courier New">')
        try:
            tokenize.tokenize(text.readline, self)
        except tokenize.TokenError, ex:
            msg = ex[0]
            line = ex[1][0]
            self.result.append("<h3>ERROR: %s</h3>%s\n" % (
                msg, self.raw[self.lines[line]:]))
        self.result.append('</font></pre>')

        # close table
        if linenumber:
            self.result.append('</td></tr></table>')

        text = ''.join(self.result)
        return text

    def __call__(self, toktype, toktext, (srow,scol), (erow,ecol), line):
        """ Token handler.
        """
        if 0: print "type", toktype, token.tok_name[toktype], "text", toktext, \
                    "start", srow,scol, "end", erow,ecol, "<br>"

        # calculate new positions
        oldpos = self.pos
        newpos = self.lines[srow] + scol
        self.pos = newpos + len(toktext)

        # handle newlines
        if toktype in [token.NEWLINE, tokenize.NL]:
            self.result.append('\n')
            return

        # send the original whitespace, if needed
        if newpos > oldpos:
            self.result.append(self.raw[oldpos:newpos])

        # skip indenting tokens
        if toktype in [token.INDENT, token.DEDENT]:
            self.pos = newpos
            return

        # map token type to a color group
        if token.LPAR <= toktype and toktype <= token.OP:
            toktype = token.OP
        elif toktype == token.NAME and keyword.iskeyword(toktext):
            toktype = _KEYWORD
        color = _colors.get(toktype, _colors[_TEXT])

        style = ''
        if toktype == token.ERRORTOKEN:
            style = ' style="border: solid 1.5pt #FF0000;"'

        # send text
        self.result.append('<font color="%s"%s>' % (color, style))
        if toktype == _KEYWORD:
            self.result.append('<b>')
        self.result.append(cgi.escape(toktext))
        if toktype == _KEYWORD:
            self.result.append('</b>')
        self.result.append('</font>')

if __name__ == "__main__":
    import os
    print "Formatting..."

    # open own source
    source = open('colourize.py').read()

    # write colorized version to "python.html"
    file('colourize.html', 'w').write(Parser(source).format(False))
