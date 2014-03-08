import os, sys
sys.path.insert(0, '..')
sys.path.insert(0, '../packages')

from modules import common
from xml.dom.minidom import parse
try:
    from xml.etree.ElementTree import ElementTree, Element, SubElement, dump
except:
    from elementtree.ElementTree import ElementTree, Element, SubElement, dump

class SnippetCatalog:
    def __init__(self, xmlfile):
        if not os.path.exists(xmlfile):
            return
        self.dom = parse(xmlfile)
        self.root = self.dom.documentElement  #or self.root = self.dom.firstChild

    def __iter__(self):
        self.iter = self.listnode(self.root)
        return self.iter

    def next(self):
        return self.iter.next()

    def listnode(self, node, level=0):
        for i in node.childNodes:
            if i.nodeType == i.ELEMENT_NODE:
                if i.nodeName == 'item':
                    caption = getTagText(i, 'caption')
                    id = i.getAttribute('id')
                    yield level, caption, int(id)
                    for v in self.listnode(i, level+1):
                        yield v

    def getmaxid(self):
        maxid = getTagText(self.root, 'maxid')
        return int(maxid)

class SnippetCode:
    def __init__(self, xmlfile):
        if not os.path.exists(xmlfile):
            return
        self.dom = parse(xmlfile)
        self.root = self.dom.documentElement

    def __iter__(self):
        return self.listnode()

    def listnode(self):
        for i in self.root.childNodes:
            if i.nodeType == i.ELEMENT_NODE:
                if i.nodeName == 'item':
                    abbr = getTagText(i, 'abbr')
                    author =getTagText(i, 'author')
                    description = getTagText(i, 'description')
                    date = getTagText(i, 'date')
                    version = getTagText(i, 'version')
                    code = getTagText(i, 'code')
                    yield abbr, description, author, version, date, code

def getTagText(root, tag):
    node = root.getElementsByTagName(tag)[0]
    rc = ""
    for node in node.childNodes:
        if node.nodeType in ( node.TEXT_NODE, node.CDATA_SECTION_NODE):
            rc = rc + node.data
    return rc

class NewSnippetFile(object):
    def __init__(self, filename):
        self.filename = filename
        self.root = Element('xml')
        e = SubElement(self.root, 'snippet')
        self.property = SubElement(e, 'properties')
        self.content = SubElement(e, 'content')
        self.tree = ElementTree(self.root)
        
    def add(self, parent, element):
        parent.append(element)
        return element
        
    def out(self):
        dump(self.root)
        
    def set_property(self, **kwargs):
        for k, v in kwargs.items():
            e = Element(k)
            e.text = v
            self.property.append(e)
        
    def save(self):
        self.tree.write(self.filename, 'utf-8')

def convert():
    xmlfile = common.unicode_abspath('../snippets/catalog.xml')
    outfile = common.unicode_abspath('../snippets/out.spt')
    if not os.path.exists(xmlfile):
        print 'File %s does not exist' % xmlfile
        return
    
    out = NewSnippetFile(outfile)
    out.set_property(title='Untitled')
    snippet = SnippetCatalog(xmlfile)
    lastlevel = -1
    stack = []
    lastnode = out.content
    for level, name, id in snippet:
        if level < lastlevel:
            stack = stack[:level+1]
        elif level > lastlevel:
            stack.append(lastnode)
        root = stack[level]
        lastnode = out.add(root, Element('folder', caption=name))
        lastlevel = level
        
        codes = SnippetCode(common.unicode_abspath('../snippets/snippet%s.xml' % id))
        for c in codes:
            n = out.add(lastnode, Element('node', caption=c[0]))
            n.text = c[-1]
    out.save()
    
if __name__ == '__main__':
    convert()