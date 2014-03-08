import re
import sys
text = file('../mixins/__init__.py').read()
re_import = re.compile('^#import (.*)$', re.M)
result = re_import.findall(text)
if result:
    fp = file('../mixins/Import.py', 'wb')
    fp.write("""#   Programmer:     limodou
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


""")
#       importlist = []
    textlist = []
    if sys.argv[1] == 'use_reload':
        for f in result:
            f = f.strip()
            fp.write('import' + '    '+ f + '\n')
        print "enable aouto reload plugins"        
    else:
        for f in result:
            f = f.strip()
            lines = file('../mixins/' + f + '.py').readlines()
            fp.write("#-----------------------  %s.py ------------------\n" % f)
            for line in lines:
                t = line.rstrip()
                if t and t[0] == '#': continue
                fp.write(t+'\n')
            fp.write("\n\n\n")
    fp.close()

    print "Successful!"
