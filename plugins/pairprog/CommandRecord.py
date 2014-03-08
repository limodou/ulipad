#   Programmer: limodou
#   E-mail:     limodou@gmail.com
#
#   Copyleft 2006 limodou
#
#   Distributed under the terms of the GPL (GNU Public License)
#
#   NewEdit is free software; you can redistribute it and/or modify
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

import wx
import time
from modules import common
from modules import Globals

class CommandRecord(object):
    def __init__(self, commands=None, filename=None):
#        self.commands = []
#        self.setcommands(commands, filename)
#        self.curstep = -1
#        self.playing = False
        self.documents = []
        self.doing = False
            
#    def append(self, command):
#        """
#        command should be a tuple, the first is command name, the second is parameter
#        commands format is:
#            ('openfile', (filename, text)),
#            ('setlex', lexname)
#            ('settext', text),
#            ('gotopos', pos),
#            ('gotoline', line),
#            ('addtext', text),
#            ('deltext', textlength)
#        """
#        self.commands.append(command)
#        
#    def play(self, auto=False, timestep=0.1):
#        self.curstep = -1
#        self.playing = True
#        if auto:
#            while self.next():
#                if timestep:
#                    time.sleep(timestep)
#        
#    def next(self):
#        wx.SafeYield()
#        if not self.playing:
#            common.showerror(Globals.mainframe, tr("You shuld execute play method first"))
#            return
#        self.curstep += 1
#        if self.curstep < len(self.commands):
#            self.do_command()
#            return True
#        else:
#            self.playing = False
#            return
#    
#    def stop(self):
#        self.playing = False
#        
#    def do_next(self):
#        cmd, v = self.commands[self.curstep]
#        self.do_command(cmd, v)
#        
    def do_command(self, cmd, v):
        self.doing = True
        try:
            mainframe = Globals.mainframe
            editctrl = mainframe.editctrl
            serial_id = v[0]
            v = list(v)[1:]
            doc = editctrl.getCurDoc()
            
            if cmd == 'openfile':
                filename, text = v
                document = editctrl.new()
                if isinstance(text, str):
                    text = unicode(text, 'utf-8')
                document.SetText(text)
                document.setTitle(filename)
                self.add_document(serial_id, document)
            elif cmd == 'forgivefile':
                self.remove_document(serial_id)
            elif cmd == 'setlex':
                doc = self.check_document(serial_id)
                if doc:
                    for lexer in mainframe.lexers.lexobjs:
                        if lexer.name == v[0]:
                            lexer.colourize(doc)
            elif cmd == 'settext':
                doc = self.check_document(serial_id)
                if doc:
                    doc.SetText(v[0])
            elif cmd == 'gotopos':
                doc = self.check_document(serial_id)
                if doc:
                    doc.GotoPos(v[0])
            elif cmd == 'gotoline':
                doc = self.check_document(serial_id)
                if doc:
                    doc.GotoLine(v[0])
            elif cmd == 'addtext':
                doc = self.check_document(serial_id)
                if doc:
                    pos, text = v
                    doc.GotoPos(pos)
                    doc.AddText(text)
            elif cmd == 'deltext':
                doc = self.check_document(serial_id)
                if doc:
                    pos, length = v
                    doc.SetTargetStart(pos)
                    doc.SetTargetEnd(pos + length)
                    doc.ReplaceTarget('')
            if doc:
                doc.EnsureCaretVisible()
        finally:
            self.doing = False
        
    def check_document(self, _id):
        mainframe = Globals.mainframe
        editctrl = mainframe.editctrl
        doc = editctrl.getCurDoc()
        for s_id, fname, document in self.documents:
            if s_id == _id:
                if doc is not document:
                    editctrl.switch(document)
                return document
        else:
            return None
        
    def find_document(self, document):
        for s_id, fname, doc in self.documents:
            if doc is document:
                return s_id, fname, doc
        else:
            return None

#    def save(self, filename):
#        from modules.EasyGuider import obj2ini
#        try:
#            obj2ini.dump(self.commands, filename)
#        except:
#            common.warn("Saving commands to %(file)s failed" % {'file':filename})
#            
    def clear(self):
        self.commands = []
        self.documents =[]
        
#    def setcommands(self, commands=None, filename=None):
#        if filename:
#            from modules.EasyGuider import obj2ini
#            try:
#                self.commands = obj2ini.load(filename)
#            except:
#                self.commands = None
#                common.warn(tr("Can't open the file %(file)s" % {'file':filename}))
#        elif commands:
#            self.commands = commands
#            
    def add_document(self, _id, document):
        if not self.check_document(_id):
            self.documents.append((_id, document.getShortFilename(), document))
            
    def remove_document(self, _id):
        for i, (s_id, filename, doc) in enumerate(self.documents):
            if s_id == _id:
                del self.documents[i]
                return
    
    def enable(self):
        return not self.doing