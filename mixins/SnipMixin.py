"""
This code comes from Kibleur C.
Site/Blog: http://kib2.webfactional.com/
"""

import re
import operator
import wx.stc
from modules import common

MARK_SNIPPET   = 4
MARK_SNIPPET_COLOR = '#508559'

F_START = "${"
F_END   = "}"
S_START = "$<"
S_END   = ">"
SPLIT = ":"

_start_len = len(F_START)
_end_len   = len(F_END)

class Snippet(object):
    """
    A Snippet is a part of text containing Fields.
    Fields can be :
    
    1. tabtrigger fields    : ${number:default value}
    2. mirror fields        : ${number}
    3. tranformed field     : $<number:transform>
    
    Field may have Scopes:
    (TODO)
    """
    def __init__(self, template, startPos=0, indentlevel=0, name='', scope=None):
        self.name = name
        self.scope = scope
        self.startPos = startPos
        self.template = template
        self.fields = self._getFields()
        self.stField = -1
        self.indentLevel = indentlevel
        #self.long = len( self._render( self.fields[0] ) )
        
    def parse(self, template, start_pos=0, startpattern= F_START, endpattern=F_END, splitpattern=SPLIT):
        """
        Parse a string and returns the fields list.
        Fields can be :
        1. Placeholders/tab stops: ${num:text} The key is equal to num
        2. Mirrors: ${num} (e.g. ${1}) . The key is num
        3. Transformations: ${num/pattern/replacement/options} (e.g. ${1/text/other $0/})
        4. Variables: $(variable) (e.g. $(FileNameExt))

        The '$', '/', '}', and '`' characters can be escaped with
        the '\' character.
        """
        fields = []
        fields_dic = {}
        fields_starts = []
        
        # if there's no endMarker Field in
        # the snippet, we put one after
        if template.find('${0}') == -1:
            #print 'adding an endMarker'
            template += '${0}'
            
        # to start at a given position
        template = template[start_pos:]

        for pos, _ in enumerate(template):
            if template[pos:pos + _start_len] == startpattern :
                if template[pos-1:pos] != '\\' :
                    fields_starts.append(pos)
                else:
                    print 'escaping this char...'
            elif template[pos:pos + _end_len] == endpattern:
                depth = len(fields_starts)
                if depth:
                    start = fields_starts.pop()
                    code = template[start:pos+_end_len]
                    try:
                        # key and content if the field is like ${num:value}
                        key, content = template[start + _start_len:pos].split(splitpattern, 1)
                    except:
                        # key=-1 and content if the field is like ${num}
                        key, content = -1, template[start + _start_len:pos]
                        #print 'slave with value ',template[start + _start_len:pos]

                    f = Field( None, start, content, code, id=int(key), depth=depth-1)
                    if f.id != -1 :
                        fields_dic[f.id] = f
                    fields.append(f)

        # Settings for masters/slaves
        for f in fields :
            # If field.id = -1, it's a slave
            if f.id == -1 :
                if f.value !="0" :
                    mast = fields_dic[int(f.value)]
                    mast.slaves.append(f)
                    f.master = mast
                    f.val = mast.value
                else:
                    # it's an endMarker
                    f.isEndMarker = True
                    f.value=''
        return fields
        
    def getReplaceFields(self, template, start_pos=0, id=0, startpattern= "$<", endpattern=">", splitpattern=":"):
        field = []
        fields_starts = []
        template = template[start_pos:]

        for pos, _ in enumerate(template):
            if template[pos:pos + _start_len + len(str(id))] == startpattern + str(id):
                if template[pos-1:pos] != '\\' :
                    fields_starts.append(pos)
                else:
                    # escape this string
                    pass
            elif template[pos:pos + _end_len] == endpattern:
                depth = len(fields_starts)
                if depth:
                    start = fields_starts.pop()
                    code = template[start:pos+1]
                    _,content = template[start + _start_len:pos].split(splitpattern, 1)               
                    field.append((code, content))
        return field
        
    def _render(self, thefield):
        tpl = self.template
        tpl = tpl.replace(thefield.code, thefield.value)
        for c in thefield.slaves :
            c.value = thefield.value
            tpl = tpl.replace(c.code, c.value)
        tpl = tpl.replace('${0}', '')
        #self.template = tpl
        return tpl
        
    def _getFields(self):
        fields = self.parse(self.template, 0)
        fields.sort(key=operator.attrgetter('id'))
        myfields = [f for f in fields if f.id>0]
        return myfields
        
    def _fieldIter(self):
        for f in self._getFields():
            yield f


class Field(object):
    def __init__(self, parent_snip, start, value='', code='',id=-1, depth=0):
        self.parent_snip = parent_snip
        self.start = start
        self.depth = depth
        self.slaves = []
        self.transf = []
        self.id = id
        self.value = value
        self.code = code
        self.isEndMarker = False
        self.master = None
        
    def __str__(self):
        out = "Field\n"
        out += "\tId=%d\n\tOffset=%d\n\tCont='%s'\n\tCode='%s'\n\tSlaves: %d"\
        %(self.id, self.start, self.value, self.code, len(self.slaves))
        return out
        
    def _setValue(self, newval):
        self.value = newval
        if len(self.slaves) > 0 :
            for s in self.slaves :
                s.setValue = newval
                
    def _getValue(self):
        return self.value
        
    val = property(_getValue, _setValue, doc="Propeties of Field value" )
    
    def slavesNumber(self):
        return len(self.slaves)

re_field = re.compile('%s.*?%s' % (re.escape(F_START), re.escape(F_END)), re.DOTALL)
class SnipMixin(object):
    def __init__(self, editor):
        self.editor = editor
        self.snippet_stack = []
        self.resetSnippet()
        
    def start(self, tpl, start, end):
#        self.editor.SetSelBackground(1, "#CA5515")
#        self.editor.SetSelForeground(1, "#42332A")

        # TODO: the snippet's scope
        the_scope = self.editor.GetStyleAt(self.editor.GetCurrentPos())

        # if another is running, 
        # push it in the stack
        if self.snippet != None:
            self.snippet_stack.append(self.snippet)
            
        b = re_field.search(tpl)
        if b:
            # create the snippet and retrieve the fields list from it
            self.snippet = Snippet(tpl, start, scope = the_scope)
            self.snippet.fieldsList = self.snippet._getFields()
            self.snippet.index = -1
            self.snippet.cursor = start
     
            # Add a new line and set a snippet marker in the margin
            line = self.editor.LineFromPosition(end)
            self.snippet.end_marker = self.editor.MarkerAdd(line, MARK_SNIPPET)
            self.editor.MarkerSetBackground(MARK_SNIPPET, MARK_SNIPPET_COLOR)

            # snippet mode : On
            self.snip_mode = True
            self.nextField(start)

    def nextField(self, pos):
        
        tpl_start, tpl_end, tpl_text = self.snippet_text()
        
        # if something went wrong and the snippet has been
        # 'messed up' (e.g. by undo/redo commands)
        if not tpl_text :
            # common.warn(tr('Something went wrong with this snippet'))
            self.cancel()
            # ygao noet: if something wrong, yeild to TAB event.
            event = wx.KeyEvent(wx.wxEVT_KEY_DOWN)
            event.m_keyCode = wx.WXK_TAB
            self.editor.ProcessEvent(event)
            return
    
        # 1. Update the mirrors and transforms Fields
        # of the current Field
        self.editor.BeginUndoAction()
        if self.snippet.index > -1 :
            self.editor.SetSelection(self.snippet.cursor, self.editor.GetCurrentPos())
            
            # the text that has been entered
            last_item = self.editor.GetSelectedText()
    
            # Transformations replacements
            # TODO : needs better security management
            replace_list = self.snippet.getReplaceFields(tpl_text, id = self.snippet.fieldsList[self.snippet.index-1].id)
            item = last_item
            for i,cod in enumerate(replace_list) :
                if replace_list[i][0] != '':
                    self.replace_snippet_text(self.snippet_text(), replace_list[i][0], eval(replace_list[i][1]))
            
            self.ind = self.snippet.fieldsList[self.snippet.index].id
            #print 'current index=', str(self.ind)
            mirror = '${' + str(self.ind) + '}'
            self.replace_snippet_text(self.snippet_text(), mirror, last_item)
            tpl_start, tpl_end, tpl_text = self.snippet_text()
        self.editor.EndUndoAction()
    
        # 2.FIND NEXT SNIPPET FIELD OR FINISH
        self.editor.BeginUndoAction()
        self.snippet.index += 1
        self.iter = 1
        try:
            
            try :
                try :
                    next_field = self.snippet.fieldsList[self.snippet.index]
                    self.ind = next_field.id
                except:
    #                error.traceback()
                    next_field = -1
        
                s = tpl_text.find('${' + str(next_field.id) + ':')
        
                if s != -1 and next_field != -1 :
                    tpl_start, tpl_end, tobefound = self.snippet_text()
                    s = tobefound.find(next_field.code) + self.snippet.startPos
                    if s !=-1:
                        e = s + len(next_field.code)
                        self.editor.SetSelection(s, e)
                        self.snippet.cursor = s
                        regex = '${' + str(self.ind) + '}'
                        self.editor.ReplaceSelection(next_field.value)
                        self.editor.SetSelection( s, s + len(next_field.value) )
                    else:
                        self.nextField(pos)
                else :
                    self.nextField(pos)
                    
            except : # FINISH
    #            error.traceback()
                tpl_start, tpl_end, tpl_text = self.snippet_text()
    #            print self.editor.GetTextRange(tpl_start, tpl_end), tpl_text
        
                if tpl_end :
                    # compensate for extra char in CR+LF line endings
    #                if self.editor.EOLMode == 0 :
    #                    tpl_end = tpl_end - 1
                    self.editor.SetSelection(tpl_end, tpl_end)
        
                s = self.editor.FindText(tpl_start, tpl_end, '${0}', wx.stc.STC_FIND_MATCHCASE)
    #            print s, tpl_start, tpl_end, self.editor.GetTextRange(tpl_start, tpl_end)
                if s != -1:
                    self.editor.SetSelection(s, s+len('${0}'))
                    self.editor.ReplaceSelection('')
                else :
                    self.editor.SetSelection(tpl_end, tpl_end) # at snippet end marker
        
                self.editor.MarkerDeleteHandle( self.snippet.end_marker )
                
                # restore previous running snippet (if any)
                if len(self.snippet_stack)>0 :
                    self.snippet = self.snippet_stack.pop()
                    self.snippet.index -= 1
                else :
                    self.resetSnippet()
        finally:
            self.editor.EndUndoAction()
        self.oldpos = pos
    
    def cancel(self):
        self.editor.MarkerDeleteHandle( self.snippet.end_marker )
        if len(self.snippet_stack)>0 :
            self.snippet = self.snippet_stack.pop()
            self.snippet.index -= 1
##        else :
##            self.resetSnippet()
        # todo: this can fix some error? 2008:02:22 by ygao
        self.resetSnippet()
        
    def resetSnippet(self):
        self.snip_mode = False
        self.snippet = None
    
    def snippet_text(self):
#        print 'SNIPPET=',self.snippet, self.snippet.startPos, self.snippet.index
        s = self.snippet.startPos
        line = self.editor.MarkerLineFromHandle(self.snippet.end_marker)
        e = self.editor.GetLineEndPosition(line)
        if e < s :
            return None, None, None
        else:
            return s, e, self.editor.GetTextRange(s, e)
        
    def getRawText(self, string):
        if wx.USE_UNICODE:
            s = string.encode('utf-8')
            return s
        else:
            return string
        
    def replace_snippet_text(self, text_info, src, des):
        start, end, text = text_info
        if not text: return
        length = len(self.getRawText(src))
        b = self.editor.FindText(start, end, src, wx.stc.STC_FIND_MATCHCASE)
        self.editor.BeginUndoAction()
        try:
            while b != -1:
                e = b + length
                self.editor.SetTargetStart(b)
                self.editor.SetTargetEnd(e)
                self.editor.ReplaceTarget(des)
                rt = self.getRawText(des)
                diff = len(rt) - (e-b)
                end += diff
                start = b + len(rt)
                b = self.editor.FindText(start, end, src, wx.stc.STC_FIND_MATCHCASE)
        finally:
            self.editor.EndUndoAction()
    
