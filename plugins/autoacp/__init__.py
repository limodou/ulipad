#
# autoacp allows multiple ACP input assistants to be installed when a specified
# language acp is installed.  This plugin was created just for this purpose.
#
# Necessity is the mother of invention -- I thought it would be beneficial to
# have jQuery autocompletion when editing mako files.  Once that was working, it
# seemed like a good idea to have javascript completion when editing mako files.
#
# This plugin allows users to define a custom set of ACP rules, so that when a
# file is opened, the user's "sub" ACP input assistants would be installed.
#

from config import add_mainframe_menu, on_configure, pref_init, \
     on_document_lang_enter
from modules import Mixin

Mixin.setPlugin('preference', 'init', pref_init)
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)
Mixin.setPlugin('editctrl', 'on_document_lang_enter', on_document_lang_enter)
Mixin.setMixin('mainframe', 'OnConfigureAutoACP', on_configure)
