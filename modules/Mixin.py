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
#   $Id: Mixin.py 2039 2007-04-09 05:06:27Z limodou $

import types
from Debug import debug
from Debug import error
import sys
import os.path
import inspect
__obj_time_set__ = {}
__mixins_funcs_time_set__ = {}

__mixinset__ = {}   #used to collect all mixins and plugins
HIGH = 1    #plugin high
MIDDLE = 2
LOW = 3
MUST_FUNC = False
ENABLE = True
RELOAD_MIXINS = False
RELOAD_NAME = ['Import']


log = None

class Mixin(object):
    __mixinname__ = ''  #mixin interface name, all subclass need define its own __mixinname__

    def __init__(self):
        self.initmixin()

    def initmixin(self):
        debug.info('[Mixin] Dealing class [%s]' % self.__class__.__name__)
        if self.__class__.__name__ == 'Mixin':  #don't dealing Mixin class itself
            return
        if hasattr(self.__class__, '__mixinflag__'):
            if self.__class__.__mixinflag__ >= 1:   #having executed mixin
                return
            else:
                self.__class__.__mixinflag__ = 1
        else:
            setattr(self.__class__, '__mixinflag__', 1)
        if not self.__mixinname__:
            debug.warn('[Mixin] The class [%s] has not a mixinname defined' % self.__class__.__name__)
            return
        if not __mixins_funcs_time_set__.has_key(self.__mixinname__):
            __mixins_funcs_time_set__[self.__mixinname__] = {}
        

        if __mixinset__.has_key(self.__mixinname__):
            debug.info('[Mixin] Mixinning class [%s]' % self.__class__.__name__)
            mixins, plugins = __mixinset__[self.__mixinname__]
            items = {}
            for name, value in mixins.items():
                if not value[0]:
                    setProperty(self.__class__, name, value[1], self)
                else:
                    items[name] = value[1]
            mixins_funcs_time = __mixins_funcs_time_set__[self.__mixinname__]
            setattr(self.__class__, '__mixins__', items)
            setattr(self.__class__, '__plugins__', plugins)
            setattr(self.__class__, '__mixins_funcs_time__', mixins_funcs_time)
        else:
            setattr(self.__class__, '__mixins__', {})
            setattr(self.__class__, '__plugins__', {})
            setattr(self.__class__, '__mixins_funcs_time__', {})
        setattr(self.__class__, '__one_plugins__', {})

    def callplugin_once(self, name, *args, **kwargs):
        if self.__one_plugins__.get(name, 0) < 1:
            self.__one_plugins__[name] = 1
            self.callplugin(name, *args, **kwargs)

    def callplugin(self, name, *args, **kwargs):
        if not self.__plugins__.has_key(name):
            #debug.error('[Mixin] The plugin [%s] has not been implemented yet!' % name)
            return

        items = self.__plugins__[name]
        items.sort()
        for i in range(len(items)):
            #debug.info("[Mixin] Call plugin [%s]" % name)
            nice, f = items[i]
            f = import_func(f)
            if  name not in ("on_update_ui", "on_idle"):
                if  RELOAD_MIXINS:
                    if  get_name(f) not in RELOAD_NAME:
                        mod = sys.modules[f.__module__]
                        sfile = get_source(mod)
                        if  self.__mixins_funcs_time__.get(f, None) is None:
                            self.set_func_time(f)
                            if  self.__mixins_funcs_time__.get(sfile, None) is None:
                                self.set_module_time(mod)
                        else:
                            if  self.need_reinstall_func(f, mod):
                                if os.path.exists(sfile) and os.path.getmtime(sfile) > self.__mixins_funcs_time__[sfile]:
                                    new_mod = reload(mod)
                                    self.set_module_time(new_mod)
                                    new_f = getattr(new_mod, f.__name__)
                                    self.set_func_time(new_f)
                                elif os.path.exists(sfile) and os.path.getmtime(sfile) == self.__mixins_funcs_time__[sfile]:
                                    new_mod = sys.modules[f.__module__]
                                    new_f = getattr(new_mod, f.__name__)
                                    self.set_func_time(new_f)
                                #new_f = getattr(__import__(f.__module__, '', '', ['']), f.__name__)
                                for mixins_item in items:
                                    if  mixins_item[1] == f:
                                        #items[i] = (nice, new_f)
                                        #items.remove(mixins_item)
                                        f = new_f
            if callable(f):
                items[i] = (nice, f)
            try:
                f(*args, **kwargs)
            except SystemExit:
                raise
            except:
                if log:
                    log.traceback()
                else:
                    raise

    def execplugin_once(self, name, *args, **kwargs):
        if self.__one_plugins__.get(name, 0) < 1:
            self.__one_plugins__[name] = 1
            return self.callplugin(name, *args, **kwargs)

    def execplugin(self, name, *args, **kwargs):
        """If some function return True, then all invokes return. So if you want the next function will
        process coninuely, you should return False or None"""
        if not self.__plugins__.has_key(name):
            #debug.error('[Mixin] The plugin [%s] has not been implemented yet!' % name)
            return None

        items = self.__plugins__[name]
        items.sort()
        for i in range(len(items)):
            nice, f = items[i]
            f = import_func(f)
            if  RELOAD_MIXINS:
                if  get_name(f) not in RELOAD_NAME:
                    mod = sys.modules[f.__module__]
                    sfile = get_source(mod)
                    if  self.__mixins_funcs_time__.get(f, None) is None:
                        self.set_func_time(f)
                        if  self.__mixins_funcs_time__.get(sfile, None) is None:
                            self.set_module_time(mod)
                    else:
                        if  self.need_reinstall_func(f, mod):
                            if  os.path.getmtime(sfile) > self.__mixins_funcs_time__[sfile] and sfile == self.__mixins_funcs_time__[f][1]:
                                new_mod = reload(mod)
                                self.set_module_time(new_mod)
                                del self.__mixins_funcs_time__[f]
                                new_f = getattr(new_mod, f.__name__)
                                self.set_func_time(new_f)
                            elif os.path.getmtime(sfile) >= self.__mixins_funcs_time__[sfile] and sfile == self.__mixins_funcs_time__[f][1]:
                                new_mod = sys.modules[f.__module__]
                                del self.__mixins_funcs_time__[f]
                                new_f = getattr(new_mod, f.__name__)
                                self.set_func_time(new_f)
                            #new_f = getattr(__import__(f.__module__, '', '', ['']), f.__name__)
                            for mixins_item in items:
                                if  mixins_item[1] == f:
                                    #items[i] = (nice, new_f)
                                    #items.remove(mixins_item)
                                    f = new_f
            if callable(f):
                items[i] = (nice, f)
            try:
#                if debug.is_debug() and name not in ['on_update_ui', 'on_idle']:
#                    debug.info('>>> %s (name=%s, args=%r, kwargs=%r)' % (self.__class__.__name__, name, args, kwargs))
#                    t = time.time()
                v = f(*args, **kwargs)
#                if debug.is_debug() and name not in ['on_update_ui', 'on_idle']:
#                    debug.info('--- end (time=%d)' % (time.time() - t))
            except SystemExit:
                raise
            except:
                if log:
                    log.traceback()
                    continue
                else:
                    raise
            if v:
                if type(v) == types.TupleType:
                    r = v[1:]
                    if len(r) == 1:
                        return r[0]
                    else:
                        return r
                else:
                    return v
        return None

    def __getattr__(self, name):
        if self.__mixins__.has_key(name):
            f = import_func(self.__mixins__[name])
            self.__mixins__[name] = f
            return setProperty(self.__class__, name, f, self)
            #return getattr(self, name)
        else:
            raise AttributeError, name

    def need_reinstall_func(self, f, mod):
        try:
            sfile = get_source(mod)
            if os.path.getmtime(sfile) > self.__mixins_funcs_time__.get(f)[0]:
                return True
            else:
                return False
        except:
            error.traceback()
            return False
        
    def set_module_time(self, mod):
        try:
            sfile = get_source(mod)
            if os.path.exists(sfile):
                self.__mixins_funcs_time__[sfile] = os.path.getmtime(sfile)
                #self.__mixins_funcs_time__[f] = os.path.getmtime(sfile)
        except:
            error.traceback()
            
    def set_func_time(self, f):
        try:
            mod = sys.modules[f.__module__]
            sfile = get_source(mod)
            if os.path.exists(sfile):
                self.__mixins_funcs_time__[f] = (os.path.getmtime(sfile),sfile)
        except:
            error.traceback()
        
#def searchpackage(packagename):
#   module=__import__(packagename)
#   if hasattr(module, '__all__'):
#       for i in module.__all__:
#           debug.info('[Mixin] Dealing module [%s]' % i)
#           __import__(packagename+'.'+i)

def setMixin(mixinname, name, value):
    if not ENABLE:
        return

    if MUST_FUNC and not callable(value):
        print "name=%s, value=%r" % (name, value)
        raise Exception, 'The value should be a callable object'

    if __mixinset__.has_key(mixinname):
        mixins = __mixinset__[mixinname][0]
    else:
        __mixinset__[mixinname] = ({}, {})
        mixins = __mixinset__[mixinname][0]

    if MUST_FUNC:
        mixins[name] = (1, value)
    else:
        if isinstance(value, (dict, tuple, list)):
            if mixins.has_key(name):
                if isinstance(value, dict):
                    mixins[name][1].update(value)
                    mixins[name] = (0, mixins[name][1])
                elif isinstance(value, list):
                    mixins[name][1].extend(value)
                    mixins[name] = (0, mixins[name][1])
                else:
                    mixins[name] = (0, mixins[name][1] + value)
            else:
                mixins[name] = (0, value)
        else:
            if  RELOAD_MIXINS:
                if  get_name(value) not in RELOAD_NAME:
                    setPlugin(mixinname, name, value, kind=MIDDLE, nice=-1)
            mixins[name] = (0, value)

def setPlugin(mixinname, name, value, kind=MIDDLE, nice=-1):
    if not ENABLE:
        return

    if MUST_FUNC and not callable(value):
        print "name=%s, value=%r" % (name, value)
        raise Exception, 'The value should be a callable object'

    if not __mixins_funcs_time_set__.has_key(mixinname):
        __mixins_funcs_time_set__[mixinname] = {}
    
    
    if __mixinset__.has_key(mixinname):
        plugins = __mixinset__[mixinname][1]
        mixins_funcs_time = __mixins_funcs_time_set__[mixinname]
    else:
        __mixinset__[mixinname] = ({}, {})
        plugins = __mixinset__[mixinname][1]
        __mixins_funcs_time_set__[mixinname] = {}
        mixins_funcs_time = __mixins_funcs_time_set__[mixinname]

    if nice == -1:
        if kind == MIDDLE:
            nice = 500
        elif kind == HIGH:
            nice = 100
        else:
            nice = 900
    if plugins.has_key(name):
        plugins[name].append((nice, value))
    else:
        plugins[name] = [(nice, value)]
    if  RELOAD_MIXINS:
        if  get_name(value) not in RELOAD_NAME:
            f = value
            mod = sys.modules[f.__module__]

            if  mixins_funcs_time.get(f, None) is None:

                try:
                    sfile = get_source(mod)
                    if os.path.exists(sfile):
                        mixins_funcs_time[f] = os.path.getmtime(sfile),sfile
                except:
                    error.traceback()
                
                if  mixins_funcs_time.get(sfile, None) is None:
                    try:
                        sfile = get_source(mod)
                        if os.path.exists(sfile):
                            mixins_funcs_time[sfile] = os.path.getmtime(sfile)
                    except:
                        error.traceback()


                    
def get_source(mod):
    "get source file from module"
    mfile = mod.__file__
    mainfile, ext = os.path.splitext(mfile)
    sfile = mainfile + '.py'
    return sfile


def get_name(f):
    "form function get source file main name"
    mod = sys.modules[f.__module__]
    sfile = get_source(mod)
    return os.path.splitext(os.path.basename(sfile))[0]
    
def reload_obj(obj):
    "if python obj source file is changed, reload it"
    source = None
    mod = None
    try:
        source = inspect.getsourcefile(obj)
    except:
        return False
    if  source:
        obj_time = __obj_time_set__.get(source, None)
        if  obj_time is None:
            __obj_time_set__[source] = os.path.getmtime(source)
            return False
        else:
            if  os.path.getmtime(source) > obj_time:
                mod = inspect.getmodule(obj)
                mod_name = mod.__name__
                name = mod.__name__.split('.')
                if  mod:
                    try:
                        del sys.modules[mod.__name__]
                    except:
                        pass
                # note: handle "from xxx import yyy"  by ygao 2007/04/06
                mod1 = __import__(mod_name, globals(), locals(),  list(name[-1]))
                reload(mod1)
                __obj_time_set__[source] = os.path.getmtime(source)
                return True
        
def setProperty(obj, name, value, self):
    if isinstance(value, (dict, tuple, list)):
        if hasattr(obj, name):
            oldvalue = getattr(obj, name)
            if isinstance(value, dict):
                oldvalue.update(value)
            elif isinstance(value, list):
                oldvalue.extend(value)
            else:
                setattr(obj, name, oldvalue + value)
        else:
            setattr(obj, name, value)
        return getattr(self, name)
    else:
        f = import_func(value)
#        #bug: if name is "getShortFilename",in case no file opened,program will crash.
#        if  name in ("OnPythonRunUpdateUI", 'OnPythonUpdateUI', "getShortFilename"):
#            setattr(obj, name, f)
#            return getattr(self, name)
#            
        if  RELOAD_MIXINS:
            if  get_name(f) not in RELOAD_NAME:
                def ff(*args, **kwargs):
                    return self.execplugin(name,*args, **kwargs)
                f = ff        
        setattr(obj, name, f)
        return getattr(self, name)


def import_func(info):
    if isinstance(info, str):
        mod, func = info.rsplit('.', 1)
        info = getattr(__import__(mod, '', '', ['']), func)
    return info

def printMixin():
    debug.info("[Mixin] Printing mixin set...")
    for name, value in __mixinset__.items():
        mixins, plugins = value
        debug.info("\tname=%s" % name)
        debug.info("\t   |----mixin")
        keys = mixins.keys()
        keys.sort()
        for k in keys:
            t, f = mixins[k]
            if callable(f):
                debug.info("\t          |%s\t%s.%s" % (k, f.__module__, f.__name__))
            else:
                debug.info("\t          |%s %s" % (k, f))
        debug.info("\t   |----plugin")
        keys = plugins.keys()
        keys.sort()
        for k in keys:
            debug.info("\t          |%s" % k)
            for nice, f in plugins[k]:
                if callable(f):
                    debug.info("\t\t          %d %s.%s" % (nice, f.__module__, f.__name__))
                else:
                    debug.info("\t\t          %d %s" % (nice, f))

def setlog(logobj):
    global log
    log = logobj
