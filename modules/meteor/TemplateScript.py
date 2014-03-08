#   Programmer: limodou
#   E-mail:     limodou@gmail.com
#
#   Copyleft 2006 limodou
#
#   Distributed under the terms of the GPL (GNU Public License)
#
#   Meteor is free software; you can redistribute it and/or modify
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

import shutil
import glob
import os
import os.path
import Template
import csv

__all__ = ['TemplateScript']

class TemplateScript:
    def __init__(self):
        self.template = Template.Template()

    def run(self, script, vars=None, runtemplate=False):
        if not vars:
            vars = {}

        if isinstance(script, (str, unicode)):
            f = file(script)
        else:
            f = script

        self.oldworkpath = os.getcwd().replace('\\', '/')

        vars['_workpath'] = self.oldworkpath

        if runtemplate:
            from StringIO import StringIO
            buf = StringIO()
            template = Template.Template()
            template.load(f, 'text')
            buf.write(template.value(values=vars))
            buf.seek(0)
            f = buf

        try:
            lines = csv.reader(f, delimiter=' ')
            for v in lines:
                if v:
                    self._do(vars, *v)
        finally:
            os.chdir(self.oldworkpath)

    def _do(self, vars, *args):
        para = args
        cmd = para[0].lower()
        if cmd and cmd[0] == '#':
            return
        if cmd == 'cd':
            os.chdir(para[1])
        elif cmd == 'mkdir':
            if not os.path.exists(para[1]):
                os.makedirs(para[1])
        elif cmd == 'chmod':
            mode = int(para[2], 8)
            filelist = glob.glob(para[1])
            for f in filelist:
                os.chmod(para[1], mode)
        elif cmd == 'copy':
            filelist = glob.glob(para[1])
            for f in filelist:
                shutil.copy(f, para[2])
        elif cmd == 'copytree':
            my_copytree(para[1], para[2])
        elif cmd == 'run':
            self.template.load(para[1], para[2])
            file(para[4], 'wb').write(self.template.value(para[3], vars))
        elif cmd == 'shell':
            os.system(' '.join(args[1:]))

def my_copytree(src, dst, symlinks=False):
    """Recursively copy a directory tree using copy2().

    Modified from shutil.copytree

    """
    names = os.listdir(src)
    if not os.path.exists(dst):
        os.mkdir(dst)
    errors = []
    for name in names:
        if name and (name[0] == '.' or name == 'CVS'):
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                my_copytree(srcname, dstname, symlinks)
            else:
                shutil.copy2(srcname, dstname)
            # XXX What about devices, sockets etc.?
        except (IOError, os.error), why:
            errors.append((srcname, dstname, why))
    if errors:
        raise shutil.Error, errors

if __name__ == "__main__":
    vars = {
        'program':{
            'hello':[
                {'var'  :'var1'},
                {'var'  :'var2'},
                {'var'  :'var3'},
            ],
            'extern': "XXXXX",
        },
    }

    import StringIO

    buf = StringIO.StringIO("""mkdir src/doc
mkdir build
copy dict.xml src/doc
run ../tmp2.py python "program" build/s.py
""")

    ts = TemplateScript()
    ts.run(buf, vars)
