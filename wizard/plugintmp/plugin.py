def run(mainframe, x):
    from modules.EasyGuider import EasyCommander, EasyUtils
    easy = EasyCommander.EasyCommander(parent=mainframe, easyfile='easyPlugin.py', inline=True, cmdoption='', outputencoding=x.options.encoding)
    if easy.run():
        values = easy.GetValue()
        var = {'text':{}}
        d = var['text']
        d.update({
            'pin_author':values['pin_author'],
            'pin_name':values['pin_name'],
            'pin_email':values['pin_email'],
            'pin_date':values['pin_date'],
            'pin_version':values['pin_version'],
            'pin_description':values['pin_description'],
            'pin_homepage':values['pin_homepage'],

        })
        d['neweditpath'] = mainframe.workpath
        if values['modules_info']:
            d['modules_names'] = values['modules_info']
            d['modules_info'] = values['modules_info']
        else:
            d['modules'] = []

        from meteor import TemplateScript, Template
        from StringIO import StringIO
        buf = StringIO()
        template = Template()
        template.load('plugin.script', 'text')
        buf.write(template.value('text', EasyUtils.str_object(var)))
        buf.seek(0)
        ts = TemplateScript()
        ts.run(buf, var)

        return True
