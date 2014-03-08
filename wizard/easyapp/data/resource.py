#coding=<#encoding#>

actions = [
    ('ID_FILE', '&File', None, '', 'File', None, None),
    ('ID_FILE_OPEN', '&Open\tCtrl+O', None, 'open', 'Open a file', 'images/blog.gif', None),
    ('ID_FILE_EXIT', 'E&xit\tAlt+F4', None, 'exit', 'Exit the program', None, 'OnExit'),
    ('ID_EDIT', '&Eile', None, '', 'Eile', None, None),
    ('ID_EDIT_UNDO', '&Undo', None, 'undo', 'Undo last command', 'images/undo.gif', None),
    ('ID_EDIT_REDO', '&Redo', None, 'redo', 'Redo last command', 'images/redo.gif', None),
]

menubar = [
    (None,
        [(100, 'ID_FILE'),
         (110, 'ID_EDIT')]),
    ('ID_FILE',
        [(100, 'ID_FILE_OPEN'),
         (110, '-'),
         (120, 'ID_FILE_EXIT')]),
    ('ID_EDIT',
        [(100, 'ID_EDIT_UNDO'),
         (110, 'ID_EDIT_REDO')]),
]

toolbar = [
    (100, 'ID_FILE_OPEN'),
    (110, '-'),
    (120, 'ID_EDIT_UNDO'),
    (130, 'ID_EDIT_REDO')
]
