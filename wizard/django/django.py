def run(mainframe, x):
    from modules.EasyGuider import EasyCommander
    easy = EasyCommander.EasyCommander(parent=mainframe, easyfile='easyDjango.py', inline=True, cmdoption='', outputencoding=x.options.encoding)
    if easy.run():
        values = easy.GetValue()
        values['secret_key'] = get_secret_key()
        if values['db_port'] == 0:
            values['db_port'] = ''

        from modules.meteor import TemplateScript
#        from StringIO import StringIO
#        buf = StringIO()
#        template = Template()
#        template.load('plugin.script', 'text')
#        buf.write(template.value('text', EasyUtils.str_object(values)))
#        buf.seek(0)
#        ts = TemplateScript()
        ts = TemplateScript()
        ts.run('django.script', vars=values, runtemplate=True)
        from modules.DjangoIni import DjangoIni
        import os
        ini = DjangoIni(os.path.join(values['proj_dir'], values['proj_name'], 'settings.py'))
        ini['ADMINS'].append((values['username'], values['email']))
        ini['DATABASE_ENGINE'] = values['database']
        ini['DATABASE_NAME'] = values['db_file']
        ini['DATABASE_PASSWORD'] = values['db_password']
        ini['DATABASE_HOST'] = values['db_host']
        ini['DATABASE_PORT'] = values['db_port']
        ini['TIME_ZONE'] = values['time_zone']
        ini['LANGUAGE_CODE'] = values['language']
        ini['MEDIA_ROOT'] = os.path.join(values['proj_dir'], values['proj_name'], 'media').replace('\\', '/')
        ini['SECRET_KEY'] = values['secret_key']
        ini['ROOT_URLCONF'] = values['proj_name'] + '.urls'
        ini.save()

        return True

def get_secret_key():
    from random import choice
    secret_key = ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
    return secret_key
