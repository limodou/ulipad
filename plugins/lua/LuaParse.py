#   Programmer: zhangchunlin
#   E-mail:     zhangchunlin@gmail.com
#
#   Copyleft 2010 zhangchunlin
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



def parseFile(filename):
    text = open(filename).read()
    return parseString(text)

def parseString(string):
    # Initialize the dict for this module's contents
    list = []

    lines = string.splitlines()

    line_no = 0

    for line in lines :
        line_no += 1
        ls = line.lstrip()

        if ls[:9] == 'function ':
            # it's a function
            list.append(('METHOD',ls,line_no))
        elif ls[:7]=='require':
            list.append(('MODULE',ls,line_no))

    return list

def main():
    # Main program for testing.
    import sys
    file = sys.argv[1]

    s = parseFile(file)
    print 'functions ......'
    functions = s['function'].values()
    for info, lineno in functions:
        print lineno, info

if __name__ == "__main__":
    main()
