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
#   version 0.1
#   This program is used for parsing settings.py. So it has many limits.
#   It has some features:
#    *  Remaining comments in settings, including comments in tuple. And if the
#       comments in tuple data type, they should be nearby the first '(' or the
#       last ')', other comments will be lost.
#    *  You can delete a key, but when you save the settings, the key will be
#       comment but not be really delete
#    *  You can also get a comment key, and if you set a new value to it,
#       the key will be uncomment. Or you can also remove the key object's delete flag
#       to uncomment the key, just like:
#
#       obj = ini.get_obj('KEY')
#       obj.delete = False
#    *  If the value is value, DjangoIni will read it as list, so you can deal with
#       the key as a list. But when it's saved, it'll be automaticaly converted to tuple,
#       just keeping the same type in settings.py
#    *  The instance of DjangoIni acts as a dict object, so you can do like:
#       from DjangoIni import DjangoIni
#       ini = DjangoIni('settings.py')
#       ini['KEY']              if a key has been delete, so it'll complain a KeyError Exception
#       ini.get('KEY', defaultvalue)    if a key has been delete, it'll also can be returned
#       ini.keys()              omit the key deleted
#       ini.has_key('KEY')      omit the key deleted
#       ini.get_obj('KEY')      can also get a delete obj
#       ini.save(filename or fileobj)   saving the result to file
#

import codecs
import copy
import re
import os
import sys

r_line = re.compile(r'(\w+)\s+=\s*([^#]+)')

class DeleteException(Exception):pass

class Node:
    def __init__(self, parent, key, old_value, lines, span=None, new=False, delete=False):
        self.parent = parent
        self.key = key
        self.value = copy.deepcopy(old_value)
        self.old_value = copy.deepcopy(old_value)
        self.lines = lines
        self.delete = delete
        self.new = new
        self.span = span

    def render(self):
        if self.lines[0] == -1:     #new
            if isinstance(self.value, (tuple, list)):
                line = []
                line.append('%s = (')
                for i in self.value:
                    line.append(' '*4 + repr(i) + ',')
                line.append(')')
            else:
                line = ['%s = %r' % (self.key, self.value)]
        else:
            if len(self.lines) == 1:
                line = self.parent.get_lines(self.lines[0])
                b, e = self.span
                line = ["%s = %r" % (self.key, self.value) + line[e:]]
            else:
                b, e = self.lines
                line = [self.parent.get_lines(b)]
                has_more = False
                for j in self.parent.get_lines(b+1, e-1):
                    if j.strip().startswith('#'):
                        line.append(j)
                    else:
                        has_more = True
                        break
                for i in self.value:
                    line.append(' '*4 + repr(i) + ',')
                line.append(')')

                if has_more:
                    lines = self.parent.get_lines(b+1, e-1)
                    lines.reverse()
                    for j in lines:
                        if j.strip().startswith('#'):
                            line.insert(len(line)-1, j)
                        else:
                            break

        if self.delete:
            if self.new:
                return None
            else:
                return ['#'+x for x in line]
        return line

class DjangoIni(object):
    def __init__(self, filename='', encoding='utf-8'):
        self._items = {}
        self._orders = {}
        self._id = 0
        self._max_id = 99999
        self._lines = []
        self.filename = filename
        self.read(self.filename)

    def _add_order(self, key):
        self._id += 1
        self._orders[key] = self._id

    def _add_max_order(self, key):
        self._max_id += 1
        self._orders[key] = self._max_id

    def read(self, filename, encoding='utf-8'):
        if not filename:
            return

        dir = os.path.dirname(filename)
        sys.path.insert(0, dir)
        modulename = os.path.splitext(os.path.basename(filename))[0]
        if sys.modules.has_key(modulename):
            del sys.modules[modulename]
        mod = __import__(modulename)
        #delete .pyc file
        try:
            os.remove(os.path.splitext(mod.__file__)[0] + '.pyc')
        except:
            pass
        sys.path.pop(0)
        f = codecs.open(filename, encoding=encoding)
        i = 0
        for line in f:
            line = line.rstrip()
            self._lines.append(line)    #saving all lines
            if line.startswith('#'):
                deleteflag = True
                line = line[1:]
            else:
                deleteflag = False
            b = r_line.search(line)
            if b:
                self._lines[-1] = line
                key, value = b.groups()
                lines = [i]
                x, y = b.span(2)
                if deleteflag:
                    x = x + 1
                value = value.strip()
                obj = Node(self, key, value, lines, span=(0, x+len(value)), delete=deleteflag)
                self._items[key] = obj
                self._add_order(key)
                if value == '(':
                    s = ['(']
                    while 1:
                        line = f.next().rstrip()
                        if line.startswith('#') and deleteflag:
                            line = line[1:]
                        self._lines.append(line)
                        i += 1
                        if line != ')':
                            t = line.lstrip()
                            if not t.startswith('#'):
                                s.append(line)
                        else:
                            obj.old_value = s
                            obj.value = [x.strip()[:-1] for x in s if not x.strip().startswith('#')]
                            lines.append(i+1)
                            s.append(')')
                            value = ''.join(s)
                            break
                else:
                    if value and value[0] in ("'", '"'):
                        ch = value[0]
                        pp = [ch]
                        line_iter = iter(line[x+1:])
                        for j in line_iter:
                            if j == '\\':
                                pp.append(j)
                                j = line_iter.next()
                                pp.append(j)
                            elif j == ch:
                                pp.append(j)
                                break
                            else:
                                pp.append(j)
                        value = ''.join(pp)
                        obj.span = (0, x + len(value))

                if hasattr(mod, key):
                    obj.value = getattr(mod, key)
                else:
                    obj.value = eval(value)
                if isinstance(obj.value, tuple):
                    obj.value = list(obj.value)
            i += 1

    def get_lines(self, start, end=-1):
        if end <= start:
            return self._lines[start]
        else:
            return self._lines[start:end]

    def out(self):
        a = [(value, key) for key, value in self._orders.items()]
        a.sort()
        for i, key in a:
            print key, self._items[key].value, self._items[key].lines

    def __setitem__(self, name, value):
        obj = self._items.get(name, None)
        if not obj:
            obj = Node(self, name, value, [-1], new=True)
            self._items[name] = obj
            self._add_max_order(name)
        else:
            if obj.delete:
                obj.delete = False
            obj.value = value

    def __getitem__(self, name):
        obj = self._items.get(name, None)
        if obj:
            if obj.delete:
                raise DeleteException, 'The value has been deleted!'
            else:
                return obj.value
        else:
            raise KeyError, name

    def __delitem__(self, name):
        """set an item's delete flag, so the result will be commented in .py file"""
        obj = self._items.get(name, None)
        if obj:
            obj.delete = True
        else:
            raise KeyError, name

    def get(self, name, defaultvalue):
        """Get an item, but also can get deleted item"""
        obj = self._items.get(name, None)
        if obj:
            return obj.value
        else:
            return defaultvalue

    def get_obj(self, name):
        """Get an item, but also can get deleted item"""
        obj = self._items.get(name, None)
        if obj:
            return obj
        else:
            raise KeyError, name

    def keys(self):
        return self._items.keys()

    def values(self):
        return [obj.value for obj in self.items.values()]

    def has_key(self, name):
        return self._items.has_key(name)

    def save(self, filename=None, encoding='utf-8'):
        if not filename:
            filename = self.filename
        a = [(value, key) for key, value in self._orders.items()]
        a.sort()

        k = 0
        s = []
        last = []
        for i, key in a:
            obj = self._items[key]
            b = obj.lines[0]
            while k < b:
                s.append(self.get_lines(k))
                k += 1
            if len(obj.lines) == 1:
                b = obj.lines[0]
                if b == -1:
                    last.extend(obj.render())
                else:
                    s.extend(obj.render())
                    k = b + 1
            else:
                b, e = obj.lines
                s.extend(obj.render())
                k = e
        s.extend(last)

        if isinstance(filename, (str, unicode)):
            f = codecs.open(filename, 'w', encoding)
            f.write('\n'.join(s))
            f.close()
        else:
            filename.write('\n'.join(s))

if __name__ == '__main__':
    ini = DjangoIni('settings.py')
    print ini.keys()
    print ini['LANGUAGE_CODE']
    ini['ADMINS'].append(('limodou', 'limodou@gmail.com'))
    ini['DATABASE_ENGINE'] = ''
    ini['DEBUG'] = False
    ini['NEW'] = 'This is test'
#    ini.save('t.py')
    print '-----------------------------------------------'
    ini.save(sys.stdout)
