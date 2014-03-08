from docutils.core import publish_file

import glob
import os.path
import sys

def deal(source_dir):
    print 'source dir %s' % source_dir

    for f in glob.glob('%s/*.txt' % source_dir):
        fi=open(f)
        filename, ext = os.path.splitext(f)
        filename = filename+'.htm'
        print '\tprocessing %s to %s' % (f, filename)
        fo=open(filename, "w")
#        publish_file(source=fi, destination=fo, writer_name='html', settings_overrides={'output_encoding': 'cp936'})
        publish_file(source=fi, destination=fo, writer_name='html')

deal('.')
for x in os.listdir('.'):
    if os.path.isdir(x) and x not in ['.svn']:
        deal(x)
