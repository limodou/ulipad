#! /usr/bin/env python
#coding=utf-8
#
# Author: limodou@gmail.com
# This program is based on pyPEG
#
# license: BSD
#
from pyPEG import *
import re
import types

__author__ = 'limodou'
__author_email__ = 'limodou@gmail.com'
__url__ = 'https://github.com/limodou/par'
__license__ = 'BSD'
__version__ = '0.9.7'

_ = re.compile

class SimpleVisitor(object):
    def __init__(self, grammar=None):
        self.grammar = grammar

    def visit(self, nodes, root=False):
        buf = []
        if not isinstance(nodes, (list, tuple)):
            nodes = [nodes]
        if root:
            method = getattr(self, '__begin__', None)
            if method:
                buf.append(method())
        for node in nodes:
            if isinstance(node, (str, unicode)):
                buf.append(node)
            else:
                if hasattr(self, 'before_visit'):
                    buf.append(self.before_visit(node))
                method = getattr(self, 'visit_' + node.__name__ + '_begin', None)
                if method:
                    buf.append(method(node))
                method = getattr(self, 'visit_' + node.__name__, None)
                if method:
                    buf.append(method(node))
                else:
                    if isinstance(node.what, (str, unicode)):
                        buf.append(node.what)
                    else:
                        buf.append(self.visit(node.what))
                method = getattr(self, 'visit_' + node.__name__ + '_end', None)
                if method:
                    buf.append(method(node))
                if hasattr(self, 'after_visit'):
                    buf.append(self.after_visit(node))
        
        if root:
            method = getattr(self, '__end__', None)
            if method:
                buf.append(method())
        return ''.join(buf)
