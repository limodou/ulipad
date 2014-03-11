import os

class Git(object):
    def __init__(self, path):
        self.path = self.find_repo(path)
        self._branch = None
        self._branches = None
        
    def find_repo(self, path):
        lastdir = ''
        while lastdir != path:
            if os.path.exists(os.path.join(path, '.git')):
                return path
            lastdir = path
            path = os.path.dirname(path)
              
    def _exec(self, cmd):
#        cmd = ('git --git-dir=%s ' % self.path) + str(cmd)
        cmd = 'git ' + str(cmd)
#        print cmd
        in_, out_, err_ = os.popen3(cmd, 't')
        return out_
    
    @property
    def branch(self):
        if self._branch:
            return self._branch
        
        for line in self._exec('branch'):
            if line[0] == '*':
                self._branch = line[2:].rstrip()
                return self._branch

    @property
    def branches(self):
        if self._branches:
            return self._branches

        s = []
        for line in self._exec('branch'):
            s.append(line[2:].rstrip())
        self._branches = s
        return s
        
    @property
    def head(self):
        return self._exec('rev-parse "%s"' % self.branch).read().strip()
    
    def status_files(self):
        for line in self._exec('status -s -unormal --porcelain --ignored'):
            flag, filename = line[:2], line[3:].rstrip()
            yield flag[0] if flag[0] != ' ' else flag[1], filename

