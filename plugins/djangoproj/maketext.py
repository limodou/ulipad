import wx

def getmodel(win, values=None):
    if not values:
        values = []
    import res_model
    from modules.EasyGuider import EasyWizard
    easy = EasyWizard.EasyWizard(win, pagesinfo=res_model.wizard, values=values)
    v = None
    if easy.ShowModal() == wx.ID_OK:
        v = easy.GetValue()
    easy.Destroy()
    return v


ofields = {'f_choices':'choices',
    'f_db_column':'db_column', 'f_default':'default', 'f_help_text':'help_text',
    'f_unique_for_date':'unique_for_date', 'f_unique_for_month':'unique_for_month',
    'f_unique_for_year':'unique_for_year', 'f_validator_list':'validator_list',
    'f_maxlength':'maxlength', 'f_auto_now':'auto_now', 'f_auto_now_add':'auto_now_add',
    'f_upload_to':'upload_to',
    }

def maketext(values):
    if values:
        text = ["""
class %(f_model_name)s(models.Model):
""" % values]
        for d in values['fields']:
            text.append('    %(f_name)s = models.%(f_type)s(' % d)
            s = []
            if 'f_verbose' in d:
                s.append("'%s'" % d['f_verbose'])
            for key, value in d.items():
                if key in ofields:
                    s.append('%s=%s' % (ofields[key], repr(value)))
            if d.has_key('f_bools'):
                for k in d['f_bools']:
                    s.append('%s=True' % k)
            if s:
                text.append(', '.join(s))
            text.append(')\n')
        return ''.join(text)
    return ''
