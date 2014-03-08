from meteor import *

info = T('''[info]
author = <#pin_author#>
date = <#pin_date#>
version = "<#pin_version#>"
description = "<#pin_description#>"
homepage = <#pin_homepage#>

''')

modules = T('''[modules]
<#modules_names#>
<#modules_info#>
''')

modules_names = T('''<#m_name#> = <#m_name#>
''')

modules_info = T('''[<#m_name#>]
name = <#m_name#>
homepage = <#m_homepage#>
download = <#m_download#>
description = "<#m_description#>"
version = "<#m_version#>"
''')

text = T('''<#info#><#modules#>''')
