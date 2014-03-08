#!c:\python24\bin\python.exe
"""Django model to DOT (Graphviz) converter
by Antonio Cavedoni <antonio@cavedoni.org>

Make sure your DJANGO_SETTINGS_MODULE is set to your project and call 
the script like this:

  $ python modelviz.py <app_label> > <filename>.dot

Example:

  $ python modelviz.py camera > foo.dot
"""
__version__ = "0.5.1"
__svnid__ = "$Id: modelviz.py 4 2006-08-06 19:48:42Z verbosus $"
__license__ = "Python"
__author__ = "Antonio Cavedoni <http://cavedoni.com/>"
__contributors__ = [
   "Stefano J. Attardi <http://attardi.org/>",
   "limodou <http://www.donews.net/limodou/>"
   ]

from django.db import models
from django.db.models import get_models
from django.db.models.fields.related import \
    ForeignKey, OneToOneField, ManyToManyField
from django.db.models.fields.generic import GenericRelation

def generate_dot(app_label):
   app = models.get_app(app_label)

   graph = []
   graph.append("digraph %s {" % ('"' + app.__name__ + '"'))
   graph.append("""  fontname = "Helvetica"
  fontsize = 8
      
  node [
    fontname = "Helvetica"
    fontsize = 8
    shape = "record"
  ]
   edge [
    fontname = "Helvetica"
    fontsize = 8
  ]
""")
   for o in get_models(app):
      graph.append(""" subgraph cluster_%(model)s {
  shape = "record";
  label = "%(model)s";
  fontname = "Helvetica";
  fontsize = 10;
  labelfontcolor = "black";
  %(model)s [label = "{""" % {'model': o.__name__})

      # model attributes
      def add_attributes():
         graph.append("<%(model)s_%(field)s>%(field)s : %(related)s|" % \
                      {'model': o.__name__, 'field': field.name, 
                       'related': type(field).__name__})

      for field in o._meta.fields:
         add_attributes()
         
      if o._meta.many_to_many:
         for field in o._meta.many_to_many:
            add_attributes()

      graph.append(""" }"] [color="white" shape="record"];\n }\n""")

      # relations
      rel = []
      def add_relation(extras=""):
         _rel = """ %(model)s:%(model)s_%(field)s -> %(related)s 
         [label="%(relationship)s"] %(extras)s;\n""" % {
            'model': o.__name__, 'field': field.name, 
            'related': field.rel.to.__name__, 
            'relationship': type(field).__name__,
            'extras': extras}
         if _rel not in rel:
            rel.append(_rel)

      for field in o._meta.fields:
         if isinstance(field, ForeignKey):
            add_relation()
         elif isinstance(field, OneToOneField):
            add_relation("[arrowhead=none arrowtail=none]")

      if o._meta.many_to_many:
         for field in o._meta.many_to_many:
            if isinstance(field, ManyToManyField):
               add_relation("[arrowhead=normal arrowtail=normal]")
            elif isinstance(field, GenericRelation):
               add_relation(
                  '[style="dotted"] [arrowhead=normal arrowtail=normal]')
      graph.append("".join(rel))

   graph.append('}')
   return "".join(graph)

def createdotfile(app_label, filename):
    r = generate_dot(app_label)
    file(filename, 'w').write(r)
    
if __name__ == "__main__":
   import sys
   app_label = sys.argv[1]
   print generate_dot(app_label)