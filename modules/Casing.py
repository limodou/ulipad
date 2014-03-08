#   Programmer:     limodou
#   E-mail:         limodou@gmail.com
#   
#   Copyleft 2006 limodou
#   
#   Distributed under the terms of the GPL (GNU Public License)
#   
#   Casing is free software; you can redistribute it and/or modify
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
#   Version = 0.2
#   Update:
#

import threading
import time
import Queue

FINISH = 1
EXCEPTION = 2
ABORT = 3
logging = None
quiet = True

def setlog(log):
    global logging
    logging = log

def setquiet(flag):
    global quiet
    quiet = flag

class AbortException(Exception):pass

class SyncVar(object):
    def __init__(self):
        self.flag = False
        self.lock = threading.Lock()

    def set(self, flag=True):
        self.lock.acquire()
        self.flag = flag
        self.lock.release()

    def isset(self):
        return self.flag

    def get(self):
        return self.flag

    def clear(self):
        self.lock.acquire()
        self.flag = False
        self.lock.release()

    def __ne__(self, other):
        return self.flag != other

    def __eq__(self, other):
        return self.flag == other

    def __nonzero__(self):
        return bool(self.flag)

class FuncThread(threading.Thread):
    def __init__(self, casing, syncvar, sync=False, kws={}):
        threading.Thread.__init__(self, name='casing_func_thread')
        self.casing = casing
        self.syncvar = syncvar
        self.sync = sync
        self.kws = kws

    def run(self):
        try:
            if self.sync:
                self.casing.sync_start(self.syncvar, kws=self.kws)
            else:
                self.casing.start(**self.kws)
            self.syncvar.clear()
        except:
            if logging:
                hasattr(logging, 'traceback')
                logging.traceback()
            else:
                if not quiet:
                    raise

class ProcessThread(threading.Thread):
    def __init__(self, casing, syncvar, sync=False):
        threading.Thread.__init__(self, name='casing_process_thread')
        self.casing = casing
        self.syncvar = syncvar
        self.sync = sync

    def run(self):
        try:
            func, args, kwargs = self.casing.on_process
            if kwargs.has_key('timestep'):
                timestep = kwargs['timestep']
                del kwargs['timestep']
            else:
                timestep = 0.5
            while 1:
                if self.syncvar:
                    if self.sync:
                        kwargs['syncvar'] = self.syncvar
                    func(*args, **kwargs)
                    time.sleep(timestep)
                else:
                    break
        except:
            if logging:
                hasattr(logging, 'traceback')
                logging.traceback()
            else:
                if not quiet:
                    raise

class MultiCasing(object):
    def __init__(self, size=10, need_manual_stop=False, timestep=1):
        self.on_finish = None
        self.on_process = None
        self.on_abort = None
        self.size = size
        self.need_manual_stop = need_manual_stop
        self.queue = Queue.Queue()
        self.active = []
        self.event = threading.Event()
        self.event.set()
        self._exit_flag = False
        self.thread_d = None
        self.timestep = timestep

    def start_thread(self):
        self.thread_d = d = Casing(self._start)
        if self.on_process:
            d.onprocess(self.on_process[0], *self.on_process[1], **self.on_process[2])
        d.start_thread()

    def start_sync_thread(self):
        self.thread_d = d = Casing(self._start, sync=True)
        if self.on_process:
            d.onprocess(self.on_process[0], *self.on_process[1], **self.on_process[2])
        d.start_sync_thread()

    def append(self, casing_obj):
        self.queue.put(casing_obj, block=True, timeout=1)

    def stop_thread(self):
        for obj in self.active:
            obj.stop_thread()
        self._exit_flag = True

    def _start(self, syncvar=None, sync=False):
        self._exit_flag = False
        self.running = True
        while not self._exit_flag:
            self.event.wait(self.timestep)
            if not self.queue.empty() and len(self.active) < self.size:
                casing = self.queue.get()
                self.active.append(casing)
                casing.onsync(self._on_sync, obj=casing)
                if not sync:
                    casing.start_thread()
                else:
                    casing.start_sync_thread()
            elif self.queue.empty() and not self.active: #not more thread obj need to run
                if not self.need_manual_stop:
                    break
            elif len(self.active) == self.size:
                self.event.clear()
            time.sleep(0.1)
        self.running = False
        if not self.active and self.queue.empty() and self.on_finish:
            self._run(self.on_finish)
        elif self.on_abort:
            self._run(self.on_abort)

    def _on_sync(self, flag, obj):
        self.active.remove(obj)
        self.event.set()

    def onfinish(self, func, *args, **kwargs):
        self.on_finish = func, args, kwargs

    def onprocess(self, func, *args, **kwargs):
        self.on_process = func, args, kwargs

    def onabort(self, func, *args, **kwargs):
        self.on_abort = func, args, kwargs

    def _run(self, func):
        f, args, kwargs = func
        return f(*args, **kwargs)

    def isactive(self):
        if not self.thread_d:
            return False
        else:
            return self.thread_d.isactive()

    def running_count(self):
        return len(self.active)

    def remaining_count(self):
        return self.queue.qsize()

class Casing(object):
    def __init__(self, func=None, *args, **kwargs):
        self.funcs = []
        if func:
            self.funcs.append((func, args, kwargs))
        self.on_success = None
        self.on_exception = None
        self.on_abort = None
        self.on_process = None
        self.on_sync = None     #used internal

        self.syncvar = None
        self.t_func = None
        self.p_func = None
        self.running = False

    def __add__(self, obj):
        assert isinstance(obj, Casing)
        self.funcs.extend(obj.funcs)
        return self

    def __radd__(self, obj):
        assert isinstance(obj, Casing)
        self.funcs.extend(obj.funcs)
        return self

    def copy(self):
        obj = Casing()
        for name, value in vars(self).items():
            setattr(obj, name, self._deepcopy(value))
        return obj

    def _deepcopy(self, obj):
        if isinstance(obj, tuple):
            s = []
            for i in range(len(obj)):
                s.append(self._deepcopy(obj[i]))
            return tuple(s)
        elif isinstance(obj, list):
            s = []
            for i in range(len(obj)):
                s.append(self._deepcopy(obj[i]))
            return s
        elif isinstance(obj, dict):
            s = {}
            for k, v in obj.items():
                s[k] = self._deepcopy(v)
            return s
        else:
            return obj

    def _update(self, src, kdict):
        for k, v in src.items():
            if kdict.has_key(k):
                src[k] = kdict[k]

    def append(self, func, *args, **kwargs):
        self.funcs.append((func, args, kwargs))

    def onsuccess(self, func, *args, **kwargs):
        self.on_success = func, args, kwargs

    def onexception(self, func, *args, **kwargs):
        self.on_exception = func, args, kwargs

    def onabort(self, func, *args, **kwargs):
        self.on_abort = func, args, kwargs

    def onprocess(self, func, *args, **kwargs):
        self.on_process = func, args, kwargs

    def onsync(self, func, *args, **kwargs):
        self.on_sync = func, args, kwargs

    def start(self, **kws):
        self.running = True
        try:
            try:
                for func, args, kwargs in self.funcs:
                    self._update(kwargs, kws)
                    ret = self._run((func, args, kwargs))
                if self.on_success:
                    self._run(self.on_success)
                if self.on_sync:
                    self._run(self.on_sync)
            except AbortException:
                if self.on_abort:
                    self._run(self.on_abort)
                else:
                    print 'Abort'
                return
            except SystemExit:
                return
            except:
                if self.on_exception:
                    self._run(self.on_exception)
                else:
                    if logging:
                        hasattr(logging, 'traceback')
                        logging.traceback()
                    else:
                        if not quiet:
                            raise
        finally:
            self.running = False

    def start_thread(self, **kws):
        self.syncvar = syncvar = SyncVar()
        self.syncvar.set()
        self.t_func = t = FuncThread(self, syncvar, kws=kws)
        self.p_func = None
        t.setDaemon(True)
        t.start()
        if self.on_process:
            self.p_func = t1 = ProcessThread(self, syncvar)
            t1.setDaemon(True)
            t1.start()

    def sync_start(self, syncvar, kws={}):
        self.running = True
        try:
            try:
                for func, args, kwargs in self.funcs:
                    self._update(kwargs, kws)
                    kwargs['syncvar'] = syncvar
                    if not syncvar:
                        return
                    self._run((func, args, kwargs))
                syncvar.clear()
                self._run(self.on_success)
                self._run_sync(FINISH)
            except AbortException:
                syncvar.clear()
                self._run_sync(ABORT)
                if self.on_abort:
                    self._run(self.on_abort)
                else:
                    print 'Abort'
                return
            except SystemExit:
                self._run_sync(ABORT)
                return
            except:
                syncvar.clear()
                self._run_sync(EXCEPTION)
                if self.on_exception:
                    self._run(self.on_exception)
                else:
                    if logging:
                        hasattr(logging, 'traceback')
                        logging.traceback()
                    else:
                        if not quiet:
                            raise
        finally:
            self.running = False

    def start_sync_thread(self, **kws):
        self.syncvar = syncvar = SyncVar()
        self.syncvar.set()
        self.t_func = t = FuncThread(self, syncvar, sync=True, kws=kws)
        self.p_func = None
        t.setDaemon(True)
        t.start()
        if self.on_process:
            self.p_func = t1 = ProcessThread(self, syncvar, sync=True)
            t1.setDaemon(True)
            t1.start()

    def stop_thread(self):
        if self.syncvar:
            self.syncvar.clear()

    def _run(self, func):
        if func:
            f, args, kwargs = func
            return f(*args, **kwargs)

    def _run_sync(self, flag):
        if self.on_sync:
            f, args, kwargs = self.on_sync
            kwargs['flag'] = flag
            return f(*args, **kwargs)

    def isactive(self):
#        if not self.t_func:
#            return False
#        else:
#            return self.t_func.isAlive()
        return self.running

def new_obj():
    return threading.local()

if __name__ == '__main__':
    def test(n, syncvar):
        for i in range(1, n):
            if syncvar:
                syncvar.set(i)
                print "=",i
                time.sleep(1)
            else:
                break

    def process(syncvar):
        print 'process...', syncvar.get()

    d = Casing(test, 10) + Casing(test, 20)
    d.onprocess(process, timestep=2)
    d.start_sync_thread()
    time.sleep(10)
    print 'stop'
    d.stop_thread()
