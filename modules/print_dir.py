#! /usr/bin/env python
#coding=utf-8
import os, sys
import fnmatch

space = 4
stack = {0:''}

def path_line(level, path, is_dir, is_last):
    s = []
    leading = stack[level-1]
    
    if is_dir:
        path = path+'/'
        
    if is_last:
        s.append(leading + '`-- ' + path)
        leading += '    '
    else:
        s.append(leading + '|-- ' + path)
        leading += '|   '
        
    stack[level] = leading
    
    return ''.join(s)

def walk(dir, level=1, skips=['.svn', '*.pyc']):
    r = []
    dirs = [x for x in os.listdir(dir) if not any([fnmatch.fnmatch(x, y) for y in skips])]
    num = len(dirs)
    for i, path in enumerate(sorted(dirs, cmp=lambda x,y: cmp(x.lower(), y.lower()))):
        p = os.path.join(dir, path)
        flag = os.path.isdir(p)
        r.append(path_line(level, path, flag, i==num-1))
        if flag:
            r.extend(walk(p, level+1, skips=skips))
            
    return r
    
if __name__ == '__main__':
    if len(sys.argv) == 1:
        path = '.'
    else:
        path = sys.argv[1]
    print path
    print '\n'.join(walk(path))