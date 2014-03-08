import glob
import sys
import os.path

f = sys.argv[1]
flist = file('filelist.txt', 'w')

for i in file(f):
    if i.strip():
        flag, path = i.split()
        if flag.lower() == 'f':
            flist.write(path + '\n')
        else:
            files = glob.glob(os.path.normpath(os.path.join(path, '*.py')))
            flist.write('\n'.join(files) + '\n')
flist.close()
