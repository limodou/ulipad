#   Programmer: limodou
#   E-mail:     limodou@gmail.com
#
#   Copyleft 2008 limodou
#
#   Distributed under the terms of the BSD license.

import os, sys
from optparse import OptionParser
import copy

def env(app, dir='', nomodel=False):
    import gluon.html as html
    import gluon.validators as validators
    from gluon.http import HTTP, redirect
    from gluon.languages import translator
    from gluon.cache import Cache
    from gluon.globals import Request, Response, Session
    from gluon.sqlhtml import SQLFORM, SQLTABLE
    from gluon.dal import BaseAdapter, SQLDB, SQLField, DAL, Field
    from gluon.compileapp import local_import_aux, LoadFactory
    
    request=Request()
    response=Response()
    session=Session()
    
    if not dir:
        request.folder = os.path.join('applications', app)
    else:
        request.folder = dir
        
    environment={}
#    for key in html.__all__: environment[key]=eval('html.%s' % key)
#    for key in validators.__all__: environment[key]=eval('validators.%s' % key)
    for key in html.__all__:
        environment[key] = getattr(html, key)
    for key in validators.__all__:
        environment[key] = getattr(validators, key)
    global __builtins__
    environment['__builtins__'] = __builtins__
    environment['T']=translator(request)
#    environment['HTTP']=HTTP
#    environment['redirect']=redirect
#    environment['request']=request
#    environment['response']=response
#    environment['session']=session
#    environment['cache']=Cache(request)
#    environment['SQLDB']=SQLDB
#    SQLDB._set_thread_folder(os.path.join(request.folder,'databases'))
#    environment['SQLField']=SQLField
#    environment['SQLFORM']=SQLFORM
#    environment['SQLTABLE']=SQLTABLE
#    
#    if not nomodel:
#        model_path = os.path.join(request.folder,'models', '*.py')
#        from glob import glob
#        for f in glob(model_path):
#            fname, ext = os.path.splitext(f)
#            execfile(f, environment)
##            print 'Imported "%s" model file' % fname

    environment['HTTP'] = HTTP
    environment['redirect'] = redirect
    environment['request'] = request
    environment['response'] = response
    environment['session'] = session
    environment['DAL'] = DAL
    environment['Field'] = Field
    environment['SQLDB'] = SQLDB        # for backward compatibility
    environment['SQLField'] = SQLField  # for backward compatibility
    environment['SQLFORM'] = SQLFORM
    environment['SQLTABLE'] = SQLTABLE
    environment['LOAD'] = LoadFactory(environment)
    environment['local_import'] = \
        lambda name, reload=False, app=request.application:\
        local_import_aux(name,reload,app)
    BaseAdapter.set_folder(os.path.join(request.folder, 'databases'))
    response._view_environment = copy.copy(environment)
    
    return environment

def run(app, options):
    _env = env(app, options.nomodel)

    if not options.plain:
        try:
            import IPython
            shell = IPython.Shell.IPShell(argv=[], user_ns=_env)
            shell.mainloop()
            return
        except:
            print 'error: Import IPython error, please check you installed IPython'\
                    ' correctly, and use default python shell.'
            
    import code
    try:
        import readline
    except ImportError:
        pass
    else:
        import rlcompleter
        readline.set_completer(rlcompleter.Completer(_env).complete)
        readline.parse_and_bind("tab:complete")

    pythonrc = os.environ.get("PYTHONSTARTUP")
    if pythonrc and os.path.isfile(pythonrc):
        try:
            execfile(pythonrc)
        except NameError:
            pass
    code.interact(local=_env)

def get_usage():
    usage = """
  %prog app
"""
    return usage

def execute_from_command_line(argv=None):
    if argv is None:
        argv = sys.argv

    parser = OptionParser(usage=get_usage())
    parser.add_option('-p', '--plain', action='store_true', help='Default python shell, not to use IPython.')
    parser.add_option('-M', '--nomodel', action='store_true', help='Not auto load model files.')
    options, args = parser.parse_args(argv[1:])

    if len(args) != 1:
        parser.print_help()
        sys.exit(0)

    from gluon.fileutils import untar

    appname=args[0]
    path=os.path.join('applications',appname)
    if not os.access(path,os.F_OK):
        if raw_input('application %s does not exit, create (y/n)?' % appname).lower() in ['y','yes']:
            os.mkdir(path)
            untar('welcome.tar',path)    
        else: return
    run(appname, options)

if __name__ == '__main__':
    execute_from_command_line()