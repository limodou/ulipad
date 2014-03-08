import doctest
import os, sys

path = os.path.dirname(sys.argv[1])
sys.path.insert(0, path)
execfile(sys.argv[1])
doctest.testmod(report=True, verbose=False)
