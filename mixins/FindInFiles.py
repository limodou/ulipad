#   Programmer:     limodou
#   E-mail:         limodou@gmail.com
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
#   $Id: FindInFiles.py 1837 2007-01-19 10:24:10Z limodou $

import wx
import os, fnmatch
import re
from modules import common
from modules import meide as ui
from modules import Globals

class FindInFiles(wx.Panel):
    def __init__(self, parent, pref, dirs=''):
        self.parent = parent
        wx.Panel.__init__(self, parent, -1)

        self.pref = Globals.pref
        self.mainframe = Globals.mainframe
        self.running = 0
        self.stopping = 0
        self.starting = 0

        self.box = box = ui.VBox()
        box.add(ui.Label(tr("Multiple directories or extensions should be separated by semicolons ';'")))
        h = ui.HBox()
        h.add(ui.Label(tr("Search for:")))
        h.add(ui.ComboBox(Globals.mainframe.document.GetSelectedText(), choices=self.pref.searchinfile_searchlist), name='search')\
            .bind('enter', self.OnKeyDown)
        h.add(ui.Label(tr("Directories:")))
        h.add(ui.ComboBox(dirs, choices=self.pref.searchinfile_dirlist), name='sdirs')\
            .bind('enter', self.OnKeyDown)
        h.add(ui.Button('...', size=(22,-1)), name='btnBrow').bind('click', self.OnDirButtonClick)
        box.add(h, flag=wx.EXPAND)
        h = ui.HBox()
        h.add(ui.Label(tr("Extensions:")))
        if not self.pref.searchinfile_extlist:
            v = '*.*'
        else:
            v = self.pref.searchinfile_extlist[0]
        h.add(ui.ComboBox(v, choices=self.pref.searchinfile_extlist), name='extns')\
            .bind('enter', self.OnKeyDown)
        h.add(ui.Check(self.pref.searchinfile_case, tr("Case sensitive")), name='cs')
        h.add(ui.Check(self.pref.searchinfile_subdir, tr("Search subdirectories")), name='ss')
        h.add(ui.Check(self.pref.searchinfile_regular, tr("Regular expression")), name='re')
        h.add(ui.Check(self.pref.searchinfile_onlyfilename, tr("Only show filename")), name='onlyfilename')
        box.add(h, flag=wx.EXPAND)
        box.add(ui.ListBox, name='results').bind(wx.EVT_LISTBOX_DCLICK, self.OpenFound)
        h = ui.HBox()
        h.add(ui.Label(tr('Status:')))
        h.add(ui.Text(tr("Ready.")), name='status')
        h.add(ui.Button(tr("Start Search")), name='btnRun').bind('click', self.OnFindButtonClick)
        h.add(ui.Button(tr("CopyClipboard"))).bind('click', self.OnCopyButtonClick)
        box.add(h, flag=wx.EXPAND)
        
        ui.create(self, box, namebinding='widget')
        
        self.status.Enable(False)
        
    def reset(self, dir):
        self.sdirs.SetValue(dir)
        self.search.SetValue(self.mainframe.document.GetSelectedText())
        self.results.Clear()

    def OpenFound(self, e):
        selected = self.results.GetSelection()
        if selected < 0:
            return
        cur = selected
        while (cur > 0) and (self.results.GetString(cur)[0] == ' '):
            cur -= 1
        fn = self.results.GetString(cur)
        line = 1
        a = self.results.GetString(selected)
        if a[0] == ' ':
            line = int(a.split(':', 1)[0])

        self.mainframe.editctrl.new(fn)
        self.mainframe.document.goto(line)

    def OnDirButtonClick(self, e):
        dlg = wx.DirDialog(self, tr("Choose a directory"), defaultPath = self.pref.searchinfile_defaultpath, style=wx.DD_DEFAULT_STYLE)
        a = dlg.ShowModal()
        if a == wx.ID_OK:
            a = self.sdirs.GetValue()
            if a:
                self.sdirs.SetValue(a+';'+dlg.GetPath())
            else:
                self.sdirs.SetValue(dlg.GetPath())
            self.pref.searchinfile_defaultpath = dlg.GetPath()
            self.pref.save()
        dlg.Destroy()

    def OnKeyDown(self, event):
        self.OnFindButtonClick(None)
    
    def OnFindButtonClick(self, e):
        if self.stopping:
            #already stopping
            return

        elif self.running:
            #running, we want to try to stop
            self.stopping = 1
            self.status.SetValue(tr("Stopping...please wait."))
            self.btnRun.SetLabel(tr("Start Search"))
            return

        if self.starting:
            #previously was waiting to start due to an
            #external yield, abort waiting and cancel
            #search
            self.starting = 0
            self.status.SetValue(tr("Search cancelled."))
            self.btnRun.SetLabel(tr("Start Search"))
            return

        #try to start
        self.starting = 1
        self.btnRun.SetLabel(tr("Stop Search"))

        #am currently the topmost call, so will continue.
        self.starting = 0
        self.running = 1

        def getlist(c):
            cc = c.GetCount()
            e = [c.GetString(i) for i in xrange(cc)]
            a = c.GetValue()
            if a:
                if a in e:
                    e.remove(a)
                e = [a] + e
                e = e[:10]
                if len(e) > cc:
                    c.Append(e[-1])
                for i in xrange(len(e)):
                    c.SetString(i, e[i])
            c.SetSelection(0)
            return e

        self.pref.searchinfile_searchlist = getlist(self.search)
        self.pref.searchinfile_dirlist = getlist(self.sdirs)
        self.pref.searchinfile_extlist = getlist(self.extns)
        self.pref.searchinfile_case = self.cs.IsChecked()
        self.pref.searchinfile_subdir = self.ss.IsChecked()
        self.pref.searchinfile_regular = self.re.IsChecked()
        self.pref.searchinfile_onlyfilename = self.onlyfilename.IsChecked()
        self.pref.save()

        search = self.search.GetValue()
        paths = self.sdirs.GetValue().split(';')
        extns = self.extns.GetValue().split(';') or ['*.*']
        case = self.cs.IsChecked()
        subd = self.ss.IsChecked()

        sfunct = self.searchST
        if self.re.IsChecked():
            sfunct = self.searchRE
            if case:
                search = re.compile(search)
            else:
                search = re.compile(search, re.IGNORECASE)

        results = self.results
        results.Clear()

        def _find():
            def file_iterator(path, subdirs, extns):
                try:    lst = os.listdir(path)
                except: return
                d = []
                for file in lst:
                    a = common.uni_join_path(path, file)
                    if os.path.isfile(a):
                        for extn in extns:
                            if fnmatch.fnmatch(file, str(extn)):
                                yield a
                                break
                    elif subdirs and os.path.isdir(a):
                        d.append(a)
                if not subdirs:
                    return
                for p in d:
                    for f in file_iterator(p, subdirs, extns):
                        yield f
            
            filecount = 0
            filefcount = 0
            foundcount = 0
            ss = tr("Found %i instances in %i files out of %i files checked.")
            
            for path in paths:
                if not self.running:
                    break
                for filename in file_iterator(path, subd, extns):
                    filecount += 1
                    if not self.stopping:
                        r = sfunct(filename, search, case)
                        if r:
                            try:
                                for a in r:
                                    wx.CallAfter(results.Append, a)
                                    if self.onlyfilename.IsChecked():
                                        break
                            except:
                                #for platforms with limited sized
                                #wx.ListBox controls
                                pass
                            filefcount += 1
                            foundcount += len(r)-1
                        wx.CallAfter(self.status.SetValue, (ss % (foundcount, filefcount, filecount)) + tr('...searching...'))
                    else:
                        break
            if self.stopping:
                self.stopping = 0
                ex = tr('...cancelled.')
                #was stopped by a button press
            else:
                self.running = 0
                ex = tr('...done.')
            wx.CallAfter(self.btnRun.SetLabel, tr("Start Search"))
            wx.CallAfter(self.status.SetValue, (ss%(foundcount, filefcount, filecount)) + ex)
            self.stopping = 0
            self.running = 0
            self.starting = 0
            
        if self.running:
            from modules import Casing
            d = Casing.Casing(_find)
            d.start_thread()
        
    def searchST(self, filename, pattern, casesensitive):
        try:
            lines = auto_uni_open_file(filename)
        except:
            import traceback
            traceback.print_exc()
            lines = []

        found = []
        if not casesensitive:
            pattern = pattern.lower()
        spt = self.pref.tabwidth*' '
        for i in range(len(lines)):
            try:
                if not casesensitive:
                    line = lines[i].lower()
                else:
                    line = lines[i]
                pos = line.find(pattern)
                if pos > -1:
                    if not found:
                        found.append(filename)
                    line = lines[i]
                    text = line[max(0, pos-20):pos+len(pattern)+20]
                    found.append('      '+str(i+1) + ': '+text.rstrip().replace('\t', spt))
            except:
                import traceback
                traceback.print_exc()
        return found

    def searchRE(self, filename, pattern, toss):
        try:
            lines = auto_uni_open_file(filename)
        except:
            lines = []
        found = []
        spt = self.pref.tabwidth*' '
        for i in range(len(lines)):
            try:
                line = lines[i]
                b = pattern.search(line)
                if b:
                    if not found:
                        found.append(filename)
                    text = line[max(0, b.start()-20):b.end()+20]
                    found.append('      '+str(i+1) + ': '+text.rstrip().replace('\t', spt))
            except: pass
        return found
    
    def OnCopyButtonClick(self, event):
        text = '\n'.join(self.results.GetStrings())
        do = wx.TextDataObject()
        do.SetText(text)
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(do)
            wx.TheClipboard.Close()
        else:
            wx.MessageBox(tr("Unable to open the clipboard"), tr("Error"))

def auto_uni_open_file(filename):
    text = open(filename, 'rU').read()
    from modules import unicodetext
    
    text, encoding = unicodetext.unicodetext(text)
    return text.splitlines()
