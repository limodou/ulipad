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
#   Version 0.1
#   This program is used to parse django's urlconf file. It can deal with standard
#   urls.py , e.g., it can parse prefix, pattern, method, and extra dictionary.
#   How to use it:
#
#   from DjangoUrlConf import URLConf
#   #URLConf can receive a usrconf filename, or leave it empty
#   u = URLConf([urlsfile])
#   #add common pattern
#   u.add(r'^test/$', 'newtest.test.main')
#   #add include pattern
#   u.add(r'^ajax/input/$', "include('newtest.test.ajax')")
#   #easyadd, it can automaticaly add '^' at the begin and '$' at the end
#   u.easyadd('tttt/input/', 'newtest.test.main')
#   #you can also pass it a dict variable
#   u.easyadd('tttt/input/', 'newtest.test.main', {'template': 'my_calendar/calendar'})
#   #you can find a pattern
#   u.find(r'^ajax/input/$')
#   #or easyfind a pattern
#   u.easyfind('ajax/input/')
#   #find mapping method
#   u.has_method('newtest.test.ajax')
#   #save to a file, if the filename is omit, then use the filename which passwd to URLConf class
#   u.save([filename])

import sys

class URLPatterns:
    def __init__(self):
        self.orders = []
        self.prefix = ''
        self.nodes = {}

    def render(self):
        s = ['urlpatterns = patterns(%s\n' % self.prefix]
        for key in self.orders:
            if not self.nodes.has_key(key) :
                s.append(key)
            else:
                s.append(self.render_item(key))
        s.append(")\n")
        return ''.join(s)

    def render_item(self, key):
        s = []
        p, d = self.nodes[key]
        if not p.startswith('include('):
            p = repr(p)
        s.append("    (r%r, %s" % (key, p))
        if d:
            if isinstance(d, dict):
                d = repr(d)
            s.append(", %s),\n" % d)
        else:
            s.append("),\n")
        return ''.join(s)

    def parse(self, text):
        text = text.replace('\r\n', '\n')
        text = text.replace('\r', '\n')

        i = 0
        last = 0
        flag = 0 #0 begin 1 comment 2 pattern
        while i<len(text):
            #skip blank
            while text[i] in (' ', '\t'):
                i += 1
            if text[i] == '#':  #if comment:
                while text[i] != '\n':
                    i += 1
                i += 1
                self.orders.append(text[last:i])
                last = i
            elif text[i] == '(':
                i += 1
                last = i
                level = 1
                while level != 0:
                    if text[i] == '(':
                        level += 1
                    elif text[i] == ')':
                        level -= 1
                    i += 1
                t = text[last:i-1]
                pos = t.find(',')
                if pos > -1:
                    key = eval(t[:pos])
                    pos += 1
                    begin = pos
                    pos = t.find(',', pos)
                    if pos > -1:
                        pattern = t[begin:pos].lstrip()
                        dict = t[pos+1:].rstrip()
                    else:
                        pattern = t[begin:].strip()
                        dict = None
                if key not in self.orders:
                    self.orders.append(key)
                self.nodes[key] = (pattern, dict)
                while text[i] != '\n':
                    i += 1
                i += 1
                last = i
            else:
                while i < len(text) and text[i] != '\n':
                    i += 1
                i += 1
                self.orders.append(text[last:i])
                last = i

        self.orders.pop(-1)


    def remove(self, key):
        if self.nodes.has_key(key):
            s = self.render_item(key)
            del self.nodes[key]
            pos = self.orders.index(key)
            self.orders[pos] = '#' + s

    def find(self, pattern):
        return self.nodes.get(pattern, None)

    def add(self, pattern, method, dict=None):
        if pattern not in self.orders:
            self.orders.append(pattern)
        self.nodes[pattern] = (method, dict)

    def has_method(self, method):
        for key, v in self.nodes():
            p, d = v
            if p == method:
                return key
        return None


class URLConf:
    def __init__(self, urlconf_filename=''):
        self.nodes = []
        self.urlconf = URLPatterns()
        self.filename = urlconf_filename
        self.read(self.filename)

    def out(self):
        self.save(sys.stdout)

    def save(self, filename=None):
        if not filename:
            filename = self.filename
        if isinstance(filename, (str, unicode)):
            f = file(filename, 'w')
        else:
            f = filename
        text = []
        for node in self.nodes:
            if isinstance(node, URLPatterns):
                text.append(node.render())
            else:
                if isinstance(node, (list, tuple)):
                    text.append(''.join(node))
                else:
                    text.append(node)
        s = ''.join(text)
        if s.find('from django.conf.urls.defaults import *') == -1:
            s = 'from django.conf.urls.defaults import *\n\n' + s

        f.write(s)


    def find(self, pattern):
        return self.urlconf.find(pattern, None)

    def easyfind(self, pattern):
        pattern = '^%s$' % pattern
        return self.find(pattern, None)

    def add(self, pattern, method, dict=None):
        self.urlconf.add(pattern, method, dict)

    def easyadd(self, pattern, method, dict=None):
        pattern = '^%s$' % pattern
        self.add(pattern, method, dict)

    def has_method(self, method):
        return self.urlconf.has_method(method)

    def read(self, filename):
        if not filename:
            self.nodes.append(self.urlconf)
            return

        f = file(filename)
        for line in f:
            if not line.startswith('urlpatterns'):
                self.nodes.append(line)
            else:
                begin = line.rfind('(')
                end = line.rfind(',')
                self.urlconf.prefix = line[begin+1:end]
                t = f.next()
                s = []
                while t.strip() != ')':
                    s.append(t)
                    t = f.next()
                self.urlconf.parse(''.join(s+[')']))
                self.nodes.append(self.urlconf)

if __name__ == '__main__':
#    u = URLConf('urls.py')
    u = URLConf()
#    print u.find('^ajax/input/$')
    u.add('^test/$', 'newtest.test.main')
    u.add('^ajax/input/$', "include('newtest.test.ajax')")
    u.easyadd('tttt/input/', 'newtest.test.main')
    u.easyadd('tttt/input/', 'newtest.test.main', {'template': 'my_calendar/calendar'})
    u.out()
