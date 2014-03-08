# Released under the GNU Lesser General Public License, v2.1 or later
# Copyright (c) 2002 Juri Pakaste <juri@iki.fi>
# $Id: OPML.py,v 1.5 2002/10/17 21:14:49 juri Exp $
# Fixed some bugs by limodou 2005/12/22

from xml.sax import make_parser, handler
from xml.sax.handler import feature_namespaces
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesImpl
import sys

class OPML(dict):
    def __init__(self):
        self.outlines = []

    def output(self, stream = sys.stdout):
        xg = XMLGenerator(stream)
        def elemWithContent(name, content):
            xg.startElement(name, AttributesImpl({}))
            if content is not None:
                xg.characters(content)
            xg.endElement(name)
        xg.startElement("opml", AttributesImpl({'version': '1.1'}))
        xg.startElement("head", AttributesImpl({}))
        for key in ('title', 'dateCreated', 'dateModified', 'ownerName',
                    'ownerEmail', 'expansionState', 'vertScrollState',
                    'windowTop', 'windowBotton', 'windowRight', 'windowLeft'):
            if self.has_key(key) and self[key] != "":
                elemWithContent(key, self[key])
        xg.endElement("head")
        xg.startElement("body", AttributesImpl({}))
        for o in self.outlines:
            o.output(xg)
        xg.endElement("body")
        xg.endElement("opml")

class Outline(dict):
    __slots__ = ('_children')

    def __init__(self):
        self._children = []

    def add_child(self, outline):
        self._children.append(outline)

    def get_children_iter(self):
        return self.OIterator(self)

    children = property(get_children_iter, None, None, "")

    def output(self, xg):
        xg.startElement("outline", AttributesImpl(self))
        for c in self.children:
            c.output(xg)
        xg.endElement("outline")

    class OIterator:
        def __init__(self, o):
            self._o = o
            self._index = -1

        def __iter__(self):
            return self

        def next(self):
            self._index += 1
            if self._index < len(self._o._children):
                return self._o._children[self._index]
            else:
                raise StopIteration

class OutlineList:
    def __init__(self):
        self._roots = []
        self._stack = []

    def add_outline(self, outline):
        if len(self._stack):
            self._stack[-1].add_child(outline)
        else:
            self._roots.append(outline)
        self._stack.append(outline)

    def close_outline(self):
        if len(self._stack):
            del self._stack[-1]

    def roots(self):
        return self._roots

class OPMLHandler(handler.ContentHandler):
    def __init__(self):
        self._outlines = OutlineList()
        self._opml = None
        self._content = ""

    def startElement(self, name, attrs):
        if self._opml is None:
            if name != 'opml':
                raise ValueError, "This doesn't look like OPML"
            self._opml = OPML()
        if name == 'outline':
            o = Outline()
            o.update(attrs)
            self._outlines.add_outline(o)
        self._content = ""

    def endElement(self, name):
        if name == 'outline':
            self._outlines.close_outline()
            return
        if name == 'opml':
            self._opml.outlines = self._outlines.roots()
            return
        for key in ('title', 'dateCreated', 'dateModified', 'ownerName',
                    'ownerEmail', 'expansionState', 'vertScrollState',
                    'windowTop', 'windowBotton', 'windowRight', 'windowLeft'):
            if name == key:
                self._opml[key] = self._content
                return

    def characters(self, ch):
        self._content += ch

    def get_opml(self):
        return self._opml

def parse(stream):
    parser = make_parser()
    parser.setFeature(feature_namespaces, 0)
    handler = OPMLHandler()
    parser.setContentHandler(handler)

    parser.parse(stream)
    return handler.get_opml()
