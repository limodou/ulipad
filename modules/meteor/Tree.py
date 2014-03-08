#   Programmer: limodou
#   E-mail:     limodou@gmail.com
#
#   Copyleft 2005 limodou
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

"""
This module is used to save a tree. You can add a variable to a tree as tree["/root/node"],
and get it from the tree as tree["/root/node"]. The tree is save as a dict inside. And you
can save it or read it from xml type file.
"""

import types
import xml.dom.minidom

class UnsupportType(Exception): pass

class Tree:
    def __init__(self, dicts=None):
        if not dicts:
            self.dicts = {}
        else:
            self.dicts = dicts
        self.tab = ' ' * 4

    def __getitem__(self, key):
        path = self._path(key)

        dict = self.getNode(self.dicts, path)
        return dict.get(path[-1], None)

    def __setitem__(self, key, value):
        path = self._path(key)

        dict = self.getNode(self.dicts, path)
        dict[path[-1]] = value

    def append(self, key, value):
        path = self._path(key)
        key = path[-1]

        dict = self.getNode(self.dicts, path)
        print 'dict', dict

        if dict.has_key(key):
            if isinstance(dict[key], types.ListType):
                dict[key].append(value)
            elif isinstance(dict[key], types.TupleType):
                dict[key] = dict[key] + (value,)
            else:
                dict[key] = [dict[key], value]
        else:
            dict[key] = value

    def getNode(self, dicts, path):
        if len(path) > 1:
            node = path[0]
            if not dicts.has_key(node):
                dicts[node] = {}
            return self.getNode(dicts[node], path[1:])
        return dicts

    def _path(self, key):
        if key.startswith('/'):
            key = key[1:]
        return key.split('/')

    def write_to_xml(self):
        s = []
        s.append('<?xml version="1.0" encoding="utf-8"?>\n')
        s.append('<tree>\n')
        self._write_dict(s, self.dicts, level = 1)
        s.append('</tree>\n')
        return ''.join(s)

    def _write_dict(self, s, dicts, level):
        for key, value in dicts.items():
            if isinstance(value, types.DictType):
                s.append(self.tab * level + '<%s>\n' % key)
                self._write_dict(s, value, level + 1)
                s.append(self.tab * level + '</%s>\n' % key)
            elif isinstance(value, types.BooleanType):
                s.append(self.tab * level + '<%s type="boolean">%s</%s>\n' % (key, str(value), key))
            elif isinstance(value, types.StringType):
                s.append(self.tab * level + '<%s type="string">%s</%s>\n' % (key, self._quoteText(value), key))
            elif isinstance(value, types.UnicodeType):
                s.append(self.tab * level + '<%s type="unicode">%s</%s>\n' % (key, self._quoteText(value.encode('utf-8')), key))
            elif isinstance(value, types.IntType):
                s.append(self.tab * level + '<%s type="int">%d</%s>\n' % (key, value, key))
            elif isinstance(value, types.LongType):
                s.append(self.tab * level + '<%s type="long">%ld</%s>\n' % (key, value, key))
            elif isinstance(value, types.FloatType):
                s.append(self.tab * level + '<%s type="float">%f</%s>\n' % (key, value, key))
            elif isinstance(value, types.ListType) or isinstance(value, types.TupleType):
                for v in value:
                    dic = {key:v}
                    self._write_dict(s, dic, level)
            else:
                raise UnsupportType, 'Unsupport type'

    def read_from_xml(self, text):
        self.dicts = {}
        dom = xml.dom.minidom.parseString(text)
        root = dom.documentElement
        self._read_from_xml(self.dicts, root)

    def _read_from_xml(self, dicts, root):
        for node in root.childNodes:
            name = node.nodeName.encode('utf-8')
            if node.nodeType == node.ELEMENT_NODE:
                if node.hasAttribute('type'):
                    t = node.getAttribute('type')
                    content = self._getTagText(node)

                    if t == 'int':
                        value = int(content)
                    elif t == 'long':
                        value = long(content)
                    elif t == 'string':
                        value = content.encode('utf-8')
                    elif t == 'unicode':
                        value = content
                    elif t == 'boolean':
                        if content == 'True':
                            value = True
                        else:
                            value = False
                    elif t == 'float':
                        value = float(content)
                    else:
                        raise UnsupportType, 'Unsupport type'

                    if dicts.has_key(name):
                        v = dicts[name]
                        if isinstance(v, types.ListType):
                            v.append(value)
                        else:
                            dicts[name] = [dicts[name], value]
                    else:
                        dicts[name] = value
                else:
                    dic = {}
                    if dicts.has_key(name):
                        v = dicts[name]
                        if isinstance(v, types.ListType):
                            v.append(dic)
                        else:
                            dicts[name] = [dicts[name], dic]
                    else:
                        dicts[name] = dic

                    self._read_from_xml(dic, node)

    def _getTagText(self, tag):
        rc = ''
        for node in tag.childNodes:
            if node.nodeType in ( node.TEXT_NODE, node.CDATA_SECTION_NODE):
                rc = rc + node.data
        return rc

    def _quoteText(self, text):
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        return text

    def getDict(self):
        return self.dicts

if __name__ == '__main__':
    tree = Tree()

    name = 'china'
    tree['/root/command/test1'] =[{ 'var':'<&amp;>'}, {'var':'limodou'}]
    tree['/root/command/ttt'] =[unicode(name, 'utf-8'), 100, {'a':False}]
    tree['/root/command/ttt'] =[(1,2), ('aaa', 'bbb', 'cccc')]  #this form is not support
    text = tree.write_to_xml()
    file("dict.xml", 'w').write(text)
    text = file('dict.xml').read()
    tree.read_from_xml(text)
    print tree.dicts
