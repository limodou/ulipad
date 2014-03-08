def autodot(win, word, syncvar):
    if word.endswith('.'):
        word = word[:-1]

    if word == 'request':
        return ['env', 'cookies', 'get_vars', 'post_vars', 'vars', 'application',
            'function', 'args']
    elif word == 'response':
        return ['status', 'headers', 'body', 'session_id', 'cookies', 'keywords',
            'description', 'flash', 'menu']
       
    return []

