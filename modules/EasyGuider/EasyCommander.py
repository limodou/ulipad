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
#   Update 2005/11/17
#      * Add checkbox before every element to Eanble/Disable the control
#      * Disable logging
#

import wx
import sys
import os.path
import EasyUtils
import getopt
import os.path
import traceback

__appname__ = 'EasyGuider'
__author__ = 'limodou'
__version__ = '0.1'

class wxApp(wx.App):
    def OnInit(self):
        return True

class EasyCommander:
    def __init__(self, parent=None, easyfile=None, cmdoption=None, inline=True, values=None, outputencoding=None):
        self.inline = inline #indicate that EasyCommnader is in other apps
        self.easyfile = easyfile
        self.cmdoption = cmdoption
        self.parent = parent
        self.values = values
        self.outputencoding = outputencoding

        self.initlog()
        self.processCommandLineArguments()
        if not wx.GetApp():
            self.wxApp = wxApp(0)
        self.mod = self.getPageModule()

    def run(self):
        mod = self.mod

        #read config information from imported template module
        if hasattr(mod, 'scriptfile') and mod.scriptfile:
            self.scriptfile = mod.scriptfile
        elif hasattr(mod, 'templatefile') and mod.templatefile:
            self.templatefile = mod.templatefile
        elif hasattr(mod, 'inipickle') and mod.inipickle:
            self.inipickle = mod.inipickle
        elif hasattr(mod, 'picklefile') and mod.picklefile:
            self.picklefile = mod.picklefile
        elif hasattr(mod, 'outputfile') and mod.outputfile:
            self.outputfile = mod.outputfile
        elif hasattr(mod, 'yamlfile') and mod.yamlfile:
            self.yamlfile = mod.yamlfile
            try:
                import yaml
            except:
                self.yamlfile = ''

        if self.picklefile:
            try:
                f = file(self.picklefile)
                import pickle
                self.values = pickle.load(f)
                f.close()
            except:
                self.log.traceback()
        elif self.inipickle:
            try:
                import obj2ini
                self.values = obj2ini.load(self.inipickle)
            except:
                self.log.traceback()
        elif self.yamlfile:
            try:
                import yaml
                self.values = yaml.loadFile(self.yamlfile).next()
            except:
                self.log.traceback()
        self.easy = easy = self.create_easy(mod, self.values)
        if easy.ShowModal() == wx.ID_OK:
            self.values = easy.GetValue()
            if self.picklefile:
                try:
                    import pickle
                    f = file(self.picklefile, 'wb')
                    pickle.dump(self.values, f)
                    f.close()
                except:
                    self.log.traceback()
            elif self.inipickle:
                try:
                    import obj2ini
                    obj2ini.dump(self.values, self.inipickle)
                except:
                    self.log.traceback()
            elif self.yamlfile:
                try:
                    import yaml
                    yaml.dumpToFile(file(self.yamlfile, 'wb'), self.values)
                except:
                    self.log.traceback()

            if self.scriptfile:
                #cal scriptpath
                SCRIPTPATH = ''
                if hasattr(mod, '__file__'):
                    SCRIPTPATH = os.path.dirname(os.path.abspath(os.path.join(os.path.dirname(mod.__file__), self.scriptfile)))
                #add scriptpath
                #self.values['SCRIPTPATH'] = SCRIPTPATH
                oldworkpath = os.getcwd()
                try:
#                    os.chdir(SCRIPTPATH)
#                    from meteor import TemplateScript, Template
#                    from StringIO import StringIO
#                    buf = StringIO()
#                    template = Template()
#                    template.load(os.path.basename(self.scriptfile), 'text')
#                    buf.write(template.value('text', EasyUtils.str_object(self.values, self.outputencoding)))
#                    buf.seek(0)
#                    ts = TemplateScript()
#                    ts.run(buf, self.values, True)
                    if SCRIPTPATH:
                        os.chdir(SCRIPTPATH)
                    from meteor import TemplateScript
                    ts = TemplateScript()
                    ts.run(self.scriptfile, self.values, True)
                finally:
                    os.chdir(oldworkpath)
#                    if self.verbose:
#                        print buf.getvalue()
            elif self.templatefile:
                from meteor import Template
                template = Template()
                template.load(self.templatefile)
                if isinstance(self.outputfile, (str, unicode)):
                    f = file(self.outputfile, 'wb')
                elif not self.outputfile:
                    f = sys.stdout
                else:
                    f = self.outputfile
                f.write(template.value(values=EasyUtils.str_object(self.values, self.outputencoding)))
            return True
        else:
            return False

    def Destroy(self):
        if self.easy:
            self.easy.Destroy()

    def create_easy(self, mod, values):
        if hasattr(mod, 'wizard'):
            import EasyWizard
            return EasyWizard.EasyWizard(self.parent, bitmap=getattr(mod, 'bitmap', wx.NullBitmap), pagesinfo=mod.wizard, values=values)
        elif hasattr(mod, 'dialog'):
            import EasyDialog
            return EasyDialog.EasyDialog(self.parent, title=getattr(mod, 'title', 'EasyDialog'), elements=mod.dialog, values=values)
        elif hasattr(mod, 'notebook'):
            import EasyNotebook
            return EasyNotebook.EasyNotebook(self.parent, title=getattr(mod, 'title', 'EasyDialog'), pagesinfo=mod.notebook, values=values)

    def initlog(self):
#        import logging
#        self.log = log = logging.getLogger('EasyGuider')
#        hdlr = logging.FileHandler('EasyAdmin.log')
#        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
#        hdlr.setFormatter(formatter)
#        log.addHandler(hdlr)
#        log.setLevel(logging.WARNING)
        self.log = log = EasyUtils.EMPTY_CLASS()

        def trace():
#            message = traceback.format_exception(*sys.exc_info())
#            log.error(''.join(message))
            raise

        log.traceback = trace

    def processCommandLineArguments(self):
        #process command line

        self.templatefile = ''
        self.scriptfile = ''
        self.picklefile = ''
        self.inipickle = ''
        self.yamlfile = ''
        self.verbose = False
        self.outputfile = ''

        if self.inline:
            cmdstring = "t:s:p:i:o:e:y:"
        else:
            cmdstring = "Vvut:s:p:i:o:y:"
        if self.cmdoption is not None:
            cmdstring = self.cmdoption

        if self.inline:
            return

        try:
            opts, args = getopt.getopt(sys.argv[1:], cmdstring, [])
        except getopt.GetoptError:
            traceback.print_exc()
            self.Usage()
            sys.exit(1)

        for o, a in opts:
            if o == '-V':       #version
                self.Version()
                sys.exit()
            elif o == '-v':
                self.verbose = True
            elif o == '-u':     #usage
                self.Usage()
                sys.exit()
            elif o == '-t':     #template
                self.templatefile = a
            elif o == '-s':     #template script
                self.scriptfile = a
            elif o == '-p':     #pickle
                self.picklefile = a
            elif o == '-e':
                self.easyfile = a
            elif o == '-i':
                self.inipickle = a
            elif o == '-o':
                self.outputfile = a
            elif o == '-y':
                self.yamlfile = a

        if not self.inline:
            try:
                self.easyfile = args[0]
            except:
                self.Usage()
                sys.exit(1)

    def getPageModule(self):
        if isinstance(self.easyfile, (str, unicode)):
            dirname = os.path.dirname(os.path.abspath(self.easyfile))
            filename, ext = os.path.splitext(os.path.basename(self.easyfile))
            if ext.lower() != '.py':
                return []
            if sys.modules.has_key(filename):
                del sys.modules[filename]
            if dirname:
                sys.path.insert(0, dirname)
            mod = __import__(filename)
            if dirname:
                del sys.path[0]
            return mod
        else:
            return self.easyfile

    def GetValue(self):
        return self.values

    def Usage(self):
        print """Usage %s [options] EasyFilename

    -V      Show version
    -v      Verbose output
    -u      Show usage
    -t file Template file
    -s file Template script file
    -e file Easy Files (EasyWizard, EasyDialog, EasyNotebook)
    -p file Pickle file used to save input data
    -i file ini format Pickle file used to save input data
    -y file Yaml format Pickle file used to save input data
    -o file Output template file to file

    If you want to use template function you should install Meteor package which can
    be found at http://wiki.woodpecker.org.cn/moin.cgi/Meteor. The Meteor version must
    be above 0.1.3 .
    """ % sys.argv[0]

    def Version(self):
        print """%s Copyleft GPL
Author: %s
Version: %s""" % (__appname__, __author__, __version__)


if __name__ == '__main__':
    easy = EasyCommander(False)
    easy.run()
