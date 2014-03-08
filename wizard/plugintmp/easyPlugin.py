import time

page1_elements = [
    ('string', 'pin_name', '', tr('Plugin Name:'), None),
    ('string', 'pin_author', '', tr('Author:'), None),
    ('string', 'pin_email', '', tr('Email:'), None),
    ('date', 'pin_date', time.strftime("%Y-%m-%d"), tr('Date:'), None),
    ('string', 'pin_version', '', tr('Version:'), None),
    ('lines', 'pin_description', '', tr('Description:'), None),
    ('string', 'pin_homepage', '', tr('Homepage:'), None),
    ]

page2_elements = [
    ('richlist', 'modules_info', [], tr('Modules Information'), {
        'elements':[
            ('string', 'm_name', '', tr('Module Name:'), None),
            ('string', 'm_homepage', '', tr('Homepage:'), None),
            ('string', 'm_download', '', tr('Download:'), None),
            ('string', 'm_version', '', tr('Version:'), None),
            ('lines', 'm_description', '', tr('Description:'), None),
        ]
    }),
    ]
notebook = [
{'title':u'Plugin Wizard', 'description':u'Basic plugin information', 'elements':page1_elements},
{'title':u'External Module Information', 'description':u'External modules information', 'elements':page2_elements},
]
