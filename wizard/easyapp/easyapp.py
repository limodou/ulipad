#coding=gb2312
page1_elements = [
    ('dir', 'appdir', '.', u'应用输出目录：', None),
    ('string', 'encoding', 'gbk', u'程序文件编码：', None),
    ('string', 'appname', 'AppName', u'应用名称：', None),
    ('string', 'author', 'Author', u'作者：', None),
    ('string', 'version', '0.1', u'版本：', None),
    ('string', 'mainframetitle', u'主窗体', u'主窗体标题：', None),
    ]

wizard = [
{'title':u'应用基本信息', 'description':u'填入应用的基本信息', 'elements':page1_elements},
]

scriptfile = 'easyapp.script'
