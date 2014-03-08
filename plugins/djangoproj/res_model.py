page1 = [
('string', 'f_model_name', '', tr('Model Name:'), None),
]
page2 = [
('richlist', 'fields', [], u'', {
    'elements':[
        ('string', 'f_name', '', tr('Field Name:'), None),
        ('single', 'f_type', 'CharField', tr('File Type:'),
            ['AutoField', 'BooleanField', 'CharField', 'CommaSeparatedIntegerField', 'DateField',
            'DateTimeField', 'EmailField', 'FileField', 'FilePathField', 'FloatField', 'ImageField',
            'IntegerField', 'IPAddressField', 'NullBooleanField', 'PhoneNumberField', 'PositiveIntegerField',
            'PositiveSmallIntegerField', 'SlugField', 'SmallIntegerField', 'TextField', 'TimeField',
            'URLField', 'USStateField', 'XMLField']
        ),
        ('string', 'f_verbose', '', tr('Field Verbose:'), None),
        ('multi', 'f_bools', [], tr('Boolean parameter'),
            ['null', 'blank', 'db_index', 'editable', 'primary_key',
            'radio_admin', 'unique',
            ], (-1, 100)),
        (False, 'string', 'f_choices', '<choices tuple name>', tr('Para choices:'), None),
        (False, 'string', 'f_db_column', '', tr('Para db_column:'), None),
        (False, 'string', 'f_default', '', tr('Para default:'), None),
        (False, 'string', 'f_help_text', '', tr('Para help_text:'), None),
        (False, 'string', 'f_unique_for_date', '<date_field>', tr('Para unique_for_date:'), None),
        (False, 'string', 'f_unique_for_month', '<date_field>', tr('Para unique_for_month:'), None),
        (False, 'string', 'f_unique_for_year', '<date_field>', tr('Para unique_for_year:'), None),
        (False, 'string', 'f_validator_list', '<validator list>', tr('Para validator_list:'), None),
        (False, 'int', 'f_maxlength', 30, tr('(CharField)Para maxlength:'), None),
        (False, 'bool', 'f_auto_now', True, tr('(Date*Field)Para auto_now:'), None),
        (False, 'bool', 'f_auto_now_add', True, tr('(Date*Field)Para auto_now_add:'), None),
        (False, 'string', 'f_upload_to', '', tr('(File/ImageField)Para upload_to:'), None),
    ],
    'key':'f_name',
}),
]
wizard = [
{'title':tr('Model Information'), 'description':'', 'elements':page1, 'theme':'classic'},
{'title':tr('Fields Information'), 'description':'', 'elements':page2, 'theme':'classic'},
]
