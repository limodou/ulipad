import doctest
import os, sys

path = os.path.dirname(sys.argv[1])
sys.path.insert(0, path)
os.chdir(path)
execfile(sys.argv[1])
doctest.testmod(report=True, verbose=False)
