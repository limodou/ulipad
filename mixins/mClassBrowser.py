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
#   $Id: mClassBrowser.py 1897 2007-02-03 10:33:43Z limodou $

import wx
from modules import Mixin
from modules import Globals
from modules.Debug import error

def pref_init(pref):
    pref.python_classbrowser_show = False
    pref.python_classbrowser_refresh_as_save = True
    pref.python_classbrowser_show_docstring = False
    pref.python_classbrowser_sort = True
    pref.python_classbrowser_show_side = 'RIGHT'
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        ('Python', 100, 'check', 'python_classbrowser_show', tr('Show class browser window when opening python source file'), None),
        ('Python', 105, 'check', 'python_classbrowser_refresh_as_save', tr('Refresh class browser window when saving python source file'), None),
        ('Python', 106, 'check', 'python_classbrowser_show_docstring', tr('Show docstring when cursor moving on a node of class browser tree'), None),
#        ('Python', 107, 'check', 'python_classbrowser_sort', tr('Sort identifiers by alphabet in class browser'), None),
        ('Python', 108, 'choice', 'python_classbrowser_show_side', tr('Show class browser in side:'), [('Left', 'LEFT'), ('Right', 'RIGHT')]),
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def add_mainframe_menu(menulist):
    menulist.extend([('IDM_PYTHON', #parent menu id
            [
                (100, 'IDM_PYTHON_CLASSBROWSER', tr('Class Browser')+'\tE=Alt+V', wx.ITEM_CHECK, 'OnPythonClassBrowser', tr('Show python class browser window.')),
                (110, 'IDM_PYTHON_CLASSBROWSER_REFRESH', tr('Refresh Class Browser'), wx.ITEM_NORMAL, 'OnPythonClassBrowserRefresh', tr('Refresh python class browser window.')),
            ]),
    ])
Mixin.setPlugin('pythonfiletype', 'add_menu', add_mainframe_menu)

def editor_init(win):
    win.class_browser = False
    win.init_class_browser = False #if the class view has shown
Mixin.setPlugin('editor', 'init', editor_init)

def OnPythonClassBrowser(win, event):
    win.document.class_browser = not win.document.class_browser
    win.document.panel.showWindow(win.pref.python_classbrowser_show_side, win.document.class_browser)
    if win.document.panel.visible(win.pref.python_classbrowser_show_side):
        if win.document.init_class_browser == False:
            win.document.init_class_browser = True
            win.document.outlinebrowser.show()
Mixin.setMixin('mainframe', 'OnPythonClassBrowser', OnPythonClassBrowser)

def aftersavefile(win, filename):
    if (win.edittype == 'edit'
        and win.languagename == 'python'
        and win.pref.python_classbrowser_refresh_as_save
        and win.init_class_browser):
        wx.CallAfter(win.outlinebrowser.show)
Mixin.setPlugin('editor', 'aftersavefile', aftersavefile)

def OnPythonClassBrowserRefresh(win, event):
    win.document.outlinebrowser.show()
Mixin.setMixin('mainframe', 'OnPythonClassBrowserRefresh', OnPythonClassBrowserRefresh)

def OnPythonUpdateUI(win, event):
    eid = event.GetId()
    if eid == win.IDM_PYTHON_CLASSBROWSER and hasattr(win, 'document') and win.document and not win.document.multiview:
        event.Check(win.document.panel.visible(win.pref.python_classbrowser_show_side) and getattr(win.document, 'init_class_browser', False))
Mixin.setMixin('mainframe', 'OnPythonUpdateUI', OnPythonUpdateUI)

def on_enter(mainframe, document):
    wx.EVT_UPDATE_UI(mainframe, mainframe.IDM_PYTHON_CLASSBROWSER, mainframe.OnPythonUpdateUI)
Mixin.setPlugin('pythonfiletype', 'on_enter', on_enter)

def on_document_enter(mainframe, document):
    if document.languagename != 'python':
        return
    if mainframe.pref.python_classbrowser_show and document.init_class_browser == False:
        document.class_browser = not document.class_browser
        document.panel.showWindow(mainframe.pref.python_classbrowser_show_side, document.class_browser)
        if document.panel.visible(mainframe.pref.python_classbrowser_show_side):
            if document.init_class_browser == False:
                document.init_class_browser = True
                document.outlinebrowser.show()
Mixin.setPlugin('editctrl', 'on_document_enter', on_document_enter)

def on_leave(mainframe, filename, languagename):
    mainframe.Disconnect(mainframe.IDM_PYTHON_CLASSBROWSER, -1, wx.wxEVT_UPDATE_UI)
Mixin.setPlugin('pythonfiletype', 'on_leave', on_leave)

def add_images(images):
    s = [
        ('MODULE', 'images/module.gif'),
        ('VARIABLE', 'images/vars.gif'),
        ('METHOD', 'images/method.gif'),
        ('FUNCTION', 'images/function.gif'),
        ('CLASS_OPEN', 'images/minus.gif'),
        ('CLASS_CLOSE', 'images/plus.gif'),
        ]
    images.extend(s)
Mixin.setPlugin('outlinebrowser', 'add_images', add_images)

c = lambda x,y:cmp(x[0].upper(), y[0].upper())

def parsetext(win, editor):
    pref = Globals.pref
    if editor.edittype == 'edit' and editor.languagename == 'python':
        if not hasattr(editor, 'syntax_info') or not editor.syntax_info:
            from modules import PyParse
            nodes = PyParse.parseString(editor.GetText())
        else:
            nodes = editor.syntax_info
    else:
        return
    
    #add doc_nodes to editor
    editor.doc_nodes = {}
    
    imports = nodes.get_imports(1)
    if imports:
        for i, v in enumerate(imports):
            importline, lineno = v
            win.replacenode(None, i, importline, win.get_image_id('MODULE'), None, 
                {'data':lineno}, win.get_image_id('MODULE'), 
                sorttype=pref.python_classbrowser_sort)
    functions = nodes.find('function')
    #process locals
    addlocals(win, nodes, nodes, None)
    if functions:
        funcs = [(x.name, x.info, x.lineno, x.docstring) for x in functions.values]
        if pref.python_classbrowser_sort:
            funcs.sort(c)
        for i, v in enumerate(funcs):
            name, info, lineno, docstring = v
            _id, obj = win.replacenode(None, i, info, win.get_image_id('FUNCTION'), 
                None,  {'data':lineno}, win.get_image_id('FUNCTION'), 
                sorttype=pref.python_classbrowser_sort)
            editor.doc_nodes[_id] = docstring
    classes = nodes.find('class')
    if classes:
        clses = [(x.name, x.info, x.lineno, x) for x in classes.values]
        if pref.python_classbrowser_sort:
            clses.sort(c)
        for i, v in enumerate(clses):
            name, info, lineno, obj = v
            #process classes and functions
            _id, node = win.replacenode(None, i, name, win.get_image_id('CLASS_CLOSE'), 
                win.get_image_id('CLASS_OPEN'), {'data':lineno}, 
                win.get_image_id('CLASS_CLOSE'), sorttype=pref.python_classbrowser_sort)
            editor.doc_nodes[_id] = obj.docstring
            #process locals
            addlocals(win, nodes, obj, node)
            objs = [(x.name, x.type, x.info, x.lineno, x) for x in obj.values]
            if pref.python_classbrowser_sort:
                objs.sort(c)
            for i, v in enumerate(objs):
                oname, otype, oinfo, olineno, oo = v
                imagetype = None
                if otype == 'class' or otype == 'function':
                    _id, obj = win.replacenode(node, i, oinfo, win.get_image_id('METHOD'), 
                        None,  {'data':olineno}, win.get_image_id('METHOD'),
                        sorttype=pref.python_classbrowser_sort)
                    editor.doc_nodes[_id] = oo.docstring
#                win.tree.Expand(node)

    
Mixin.setPlugin('outlinebrowser', 'parsetext', parsetext)

def addlocals(win, root, node, treenode):
    pref = Globals.pref

    s = []
    names = []
    for i in range(len(node.locals)):
        name = node.locals[i]
        t, v, lineno = node.local_types[i]
        if t not in ('class', 'function', 'import'):
            info = name + ' : ' + 'unknow'
            if t == 'reference':
                if v:
                    if node.type == 'class':
                        result = root.guess_type(lineno, 'self.' + name)
                    else:
                        result = root.guess_type(lineno, name)
                    if result:
                        
                        if result[0] not in ('reference', 'class', 'function', 'import'):
                            info = name + ' : ' + result[0]
                        else:
                            if result[1]:
                                if result[0] in ('class', 'function'):
                                    info = name + ' : ' + result[1].info
                                else:
                                    info = name + ' : ' + result[1]
                            else:
                                info = name + ' : ' + result[0]
                    else:
                        info = name + ' : ' + v
            else:
                info = name + ' : ' + t
            s.append((info, lineno))
            
    if pref.python_classbrowser_sort:
        s.sort(c)
    for i, v in enumerate(s):
        info, lineno = v
        win.replacenode(treenode, i, info , win.get_image_id('VARIABLE'), None,  
            {'data':lineno}, win.get_image_id('VARIABLE'),
            sorttype=pref.python_classbrowser_sort)
    
def new_window(win, document, panel):
    from OutlineBrowser import OutlineBrowser
    parent = panel.getSide(Globals.pref.python_classbrowser_show_side)
    document.outlinebrowser = OutlineBrowser(parent, document, autoexpand=False)
    document.outlinebrowser.set_tooltip_func(on_get_tool_tip)
Mixin.setPlugin('textpanel', 'new_window', new_window)

def add_tool_list(toollist, toolbaritems):
    toollist.extend([
        (2000, 'classbrowser'),
#        (2010, 'classbrowserrefresh'),
        (2050, '|'),
    ])

    #order, IDname, imagefile, short text, long text, func
    toolbaritems.update({
        'classbrowser':(wx.ITEM_CHECK, 'IDM_PYTHON_CLASSBROWSER', 'images/classbrowser.gif', tr('Class Browser'), tr('Class browser'), 'OnPythonClassBrowser'),
#        'classbrowserrefresh':(wx.ITEM_NORMAL, 'IDM_PYTHON_CLASSBROWSER_REFRESH', 'images/classbrowserrefresh.gif', tr('class browser refresh'), tr('Class browser refresh'), 'OnPythonClassBrowserRefresh'),
    })
Mixin.setPlugin('pythonfiletype', 'add_tool_list', add_tool_list)

def afterclosewindow(win):
    if hasattr(win.document, 'panel') and hasattr(win.document.panel, 'showWindow'):
        win.document.panel.showWindow(win.pref.python_classbrowser_show_side, False)
Mixin.setPlugin('mainframe', 'afterclosewindow', afterclosewindow)

#add identifier jump
def on_jump_definition(editor, word):
    if editor.edittype == 'edit' and editor.languagename == 'python':
        if not hasattr(editor, 'syntax_info') or not editor.syntax_info:
            from modules import PyParse
            nodes = PyParse.parseString(editor.GetText())
        else:
            nodes = editor.syntax_info
        lineno = editor.GetCurrentLine() + 1 #syntax line is based on 1, but editor line is base on 0
        result = nodes.search_name(lineno, word)
        if result:
            t, v, line = result
            editor.goto(line)
Mixin.setPlugin('editor', 'on_jump_definition', on_jump_definition)

def on_get_tool_tip(win, event):
    if hasattr(win.editor, 'doc_nodes') and Globals.pref.python_classbrowser_show_docstring:
        nodes = win.editor.doc_nodes
        item = event.GetItem()
        if item.IsOk():
            _id = win.tree.GetPyData(item)
            tip = nodes.get(_id, '')
            if tip:
                try:
                    tip = remove_leading_spaces(win.editor, eval(tip).rstrip())
                    event.SetToolTip(tip)
                except:
                    import traceback
                    traceback.print_exc()
                    error.traceback()
                
import re
re_spaces = re.compile(r'^(\s*)')
re_eol = re.compile(r'\r\n|\r|\n')
def remove_leading_spaces(win, text):
    minspaces = []
    contentlines = re_eol.sub(win.getEOLChar(), text).splitlines()
    flag = False
    index = 0
    for i, line in enumerate(contentlines):
        #skip blank line
        if not line.strip():
            if not flag:
                index = i + 1
            continue
        flag = True
        b = re_spaces.search(line)
        if b:
            minspaces.append(b.span()[1])
            
    minspace = min(minspaces)
    lines = [x[minspace:] for x in contentlines[index:]]
        
    return '\n'.join(lines)
 
def savepreferencevalues(old_values):
    pref = Globals.pref
    side = old_values['python_classbrowser_show_side']
    if side.lower() != pref.python_classbrowser_show_side.lower():
        for document in Globals.mainframe.editctrl.getDocuments():
            if document.panel.visible(side):
                document.outlinebrowser.Destroy()
                document.panel.showWindow(side, False)
                new_window(document.panel.parent, document, document.panel)
                document.panel.showWindow(pref.python_classbrowser_show_side, True)
                document.outlinebrowser.show()
Mixin.setPlugin('prefdialog', 'savepreferencevalues', savepreferencevalues)
