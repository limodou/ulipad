#   Programmer: limodou
#   E-mail:     limodou@gmail.com
#
#   Copyleft 2006 limodou
#
#   Distributed under the terms of the GPL (GNU Public License)
#
#   NewEdit is free software; you can redistribute it and/or modify
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


import tokenize # Python tokenizer
import token
import StringIO

# each Python class is represented by an instance of this class
class Class:
    '''Class to represent a Python class.'''
    def __init__(self, name, info, lineno):
        self.name = name
        self.methods = {}
        self.lineno = lineno
        self.info = info

    def addmethod(self, name, info, lineno):
        self.methods[name] = (info, lineno)

def parseFile(filename):
    text = open(filename).read()
    return parseString(text)

def parseString(string):
    # Initialize the dict for this module's contents
    dict = {'class':{}, 'function':{}, 'import':[]}

    stack = [] # stack of (class, indent) pairs

    lines = string.splitlines()

    line_no = 0

    for line in lines :
        line_no += 1
        ls = line.lstrip()

        if ls[:4] == 'def ':
            thisindent = len(line)-len(ls)
            while stack and stack[-1][1] >= thisindent:
                del stack[-1]

            if stack:
                cur_class = stack[-1][0]
                if isinstance(cur_class, Class):
                    # it's a method
                    cur_class.addmethod(ls, ls, line_no)
                # else it's a nested def
            else:
                # it's a function
                dict['function'][ls] = (ls, line_no)
            stack.append((None, thisindent)) # Mark

        elif ls[:6] == 'class ':

            thisindent = len(line)-len(ls)
            while stack and stack[-1][1] >= thisindent:
                del stack[-1]

            cur_class = Class(ls, ls, line_no)
            if not stack:
                dict['class'][ls] = cur_class
            stack.append((cur_class, thisindent))

    return dict

def main():
    # Main program for testing.
    import sys
    file = sys.argv[1]

    s = parseFile(file)
    print 'import ......'
    imports = s['import']
    for info, lineno in imports:
        print lineno, info
    print 'functions ......'
    functions = s['function'].values()
    for info, lineno in functions:
        print lineno, info
    print 'class ......'
    classes = s['class'].values()
    for c in classes:
        print c.info, c.lineno
        for info, lineno in c.methods.values():
            print '    ', lineno, info

if __name__ == "__main__":
    main()
