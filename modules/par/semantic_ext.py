def semantic_alert(visitor, block):
    """
    Format:
        
        {% alert class=error %}
        message
        {% endalert %}
    """
    txt = []
    cls = block['kwargs'].get('class', '')
    txt.append('<div class="ui %s message">' % cls)
    text = visitor.parse_text(block['body'], 'article')
    txt.append(text)
    txt.append('</div>')
    return '\n'.join(txt)

__section__ = 0
__seq__ = 0

def semantic_tabs(visitor, block):
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
    
    __section__ += 1
    
    r_name = re.compile(r'(^-- [^-]+ --$)', re.M)
    def get_id():
        global __seq__
        
        __seq__ += 1
        
        return 'tab_item_%d_%d' % (__section__, __seq__)
    
    txt = []
    txt.append('<div class="ui tabular filter menu">')
    
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
            txt.append('<a class="%sitem" data-tab="%s">%s</a>' % (cls, _id, items[i][3:-3]))
            in_tab = True
        
        i += 1
    txt.append('</div>')
    
    txt.append('<div class="tab-content">')
    for i, x in enumerate(entries):
        if i == 0:
            cls = ' active'
        else:
            cls = ''
        txt.append('<div class="ui divided inbox selection list%s tab" data-tab="%s">' % (cls, ids[i]))
        txt.append(visitor.parse_text(x, 'article'))
        txt.append('</div>')
        
    txt.append('</div>')
    txt.append('</div>')
    
    return '\n'.join(txt)
    
blocks = {'tabs':semantic_tabs, 'alert':semantic_alert, 'message':semantic_alert}