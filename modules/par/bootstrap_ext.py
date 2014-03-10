def bootstrap_tabs(visitor, items):
    def format_id(s):
        return s.replace('.', '-')
    
    txt = []
    txt.append('<div class="tabbable">')
    
    txt.append('<ul class="nav nav-tabs">')
    for i, x in enumerate(items):
        if 'title' not in x:
            x['kwargs']['title'] = x['kwargs']['id']
        if i == 0:
            cls = ' class="active"'
        else:
            cls = ''
        txt.append('<li%s><a href="#%s" data-toggle="tab">%s</a></li>' % (cls, format_id(x['kwargs']['id']), x['kwargs']['title']))
    txt.append('</ul>')
    
    txt.append('<div class="tab-content">')
    for i, x in enumerate(items):
        if i == 0:
            cls = ' active'
        else:
            cls = ''
        txt.append('<div class="tab-pane%s" id="%s">' % (cls, format_id(x['kwargs']['id'])))
        text = visitor.parse_text(x['body'], 'article')
        txt.append(text)
        txt.append('</div>')
    txt.append('</div>')
    
    txt.append('</div>')
    
    return '\n'.join(txt)

def bootstrap_alert(visitor, items):
    """
    Format:
        
        [[alert(class=error)]]:
            message
    """
    txt = []
    for x in items:
        cls = x['kwargs'].get('class', '')
        if cls:
            cls = 'alert-%s' % cls
        txt.append('<div class="alert %s">' % cls)
        if 'close' in x['kwargs']:
            txt.append('<button class="close" data-dismiss="alert">&times;</button>')
        text = visitor.parse_text(x['body'], 'article')
        txt.append(text)
        txt.append('</div>')
    return '\n'.join(txt)

def new_bootstrap_alert(visitor, block):
    """
    Format:
        
        {% alert class=error %}
        message
        {% endalert %}
    """
    if 'new' in block:
        txt = []
        cls = block['kwargs'].get('class', '')
        if cls:
            cls = 'alert-%s' % cls
        txt.append('<div class="alert %s">' % cls)
        if 'close' in block['kwargs']:
            txt.append('<button class="close" data-dismiss="alert">&times;</button>')
        text = visitor.parse_text(block['body'], 'article')
        txt.append(text)
        txt.append('</div>')
        return '\n'.join(txt)
    else:
        return bootstrap_alert(visitor, block)

__section__ = 0
__seq__ = 0

def new_bootstrap_tabs(visitor, block):
    """
    Render text as bootstrap tabs, for example:
        
        {% tabs %}
        -- name --
        ...
        ...
        -- name --
        ...
        ...
        {% endtabs %}
    """
    import re
    global __section__
    
    if 'new' in block:
        __section__ += 1
        
        r_name = re.compile(r'(^-- [^-]+ --$)', re.M)
        def get_id():
            global __seq__
            
            __seq__ += 1
            
            return 'tab_item_%d_%d' % (__section__, __seq__)
        
        txt = []
        txt.append('<div class="tabbable">')
        
        txt.append('<ul class="nav nav-tabs">')
        
        body = block['body']
        i = 0
        items = r_name.split(body)
        first = True
        entries = []
        in_tab = False #if tab processed
        ids = []
        while i<len(items):
            if in_tab:
                entries.append(items[i])
                in_tab = False
            if items[i].startswith('-- ') and items[i].endswith(' --'):
                if first:
                    cls = ' class="active"'
                    first = False
                else:
                    cls = ''
                _id = get_id()
                ids.append(_id)
                txt.append('<li%s><a href="#%s" data-toggle="tab">%s</a></li>' % (cls, _id, items[i][3:-3]))
                in_tab = True
            
            i += 1
        txt.append('</ul>')
        
        txt.append('<div class="tab-content">')
        for i, x in enumerate(entries):
            if i == 0:
                cls = ' active'
            else:
                cls = ''
            txt.append('<div class="tab-pane%s" id="%s">' % (cls, ids[i]))
            txt.append(visitor.parse_text(x, 'article'))
            txt.append('</div>')
            
        txt.append('</div>')
        txt.append('</div>')
        
        return '\n'.join(txt)
    else:
        return bootstrap_tabs(visitor, block)
    
blocks = {'tabs':new_bootstrap_tabs, 'alert':new_bootstrap_alert}