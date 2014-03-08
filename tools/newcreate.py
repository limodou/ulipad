import re
import sys
import os
import pickle

def main():
    text = file('../mixins/__init__.py').read()
    re_import = re.compile('^#import (.*)$', re.M)
    result = re_import.findall(text)
    if result:
        fp = file('../mixins/Import.py', 'wb')
        fp.write("""\
#   Programmer: limodou
#   E-mail:     limodou@gmail.com
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

import os
import pickle
from modules import Globals
from modules import Mixin

pfile = os.path.join(Globals.workpath, 'mixins.pickls')
Mixin.__mixinset__ = pickle.load(file(pfile, 'rb'))
Mixin.ENABLE = False
""")

        def _(s):
            return s

        sys.path.insert(0, os.path.abspath('../mixins'))
        sys.path.insert(0, os.path.abspath('..'))
        import __builtin__
        __builtin__.__dict__['tr'] = _

        for f in result:
#            print 'dealing ... ', f
            mod = __import__(f)

        from modules import Mixin
        Mixin.MUST_FUNC = True
        from modules import Debug
        Debug.debug = Debug.Debug('../debug.txt')

        processMixin(Mixin.__mixinset__)
        pfile = '../mixins.pickls'
        pickle.dump(Mixin.__mixinset__, file(pfile, 'wb'))
        Mixin.printMixin()
        print "Successful!"

def processMixin(mixins):
    for name, value in mixins.items():
        mixins, plugins = value
        keys = mixins.keys()
        keys.sort()
#        print 'mixins'
        for k in keys:
            t, f = mixins[k]
            import sys
            print sys.__stdout__,t,'\n',f
            if callable(f):
                mixins[k] = t, 'mixins.%s.%s' % (f.__module__, f.__name__)
            else:
                print k, mixins[k]
                #raise Exception, 'Mixin should be callable'
#            print '\t', k, mixins[k]
        keys = plugins.keys()
        keys.sort()
#        print 'plugins'
        for k in keys:
#            print '\t', k
            alist = plugins[k]
            alist.sort()
            for i in range(len(alist)):
                nice, f = alist[i]
                alist[i] = nice, 'mixins.%s.%s' % (f.__module__, f.__name__)
#                print '\t\t', nice, alist[i][1]

if __name__ == '__main__':
    main()
