#   Programmer:     limodou
#   E-mail:         limodou@gmail.com
#   
#   Copyleft 2006 limodou
#   
#   Distributed under the terms of the GPL (GNU Public License)
#   
#   UliPad is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#   $Id: ModulesInfo.py 1457 2006-08-23 02:12:12Z limodou $

import glob
import os.path
from modules import dict4ini
from modules import common
from modules.Debug import error

def show_modules_info(win):
    files = glob.glob(os.path.join(win.workpath, 'plugins/*/*.pin'))
    plugins = []
    for f in files:
        key = os.path.basename(os.path.dirname(f))
        x = dict4ini.DictIni(f)
        tr_color = '#CCFFFF'
        platform = x.info.get('platform', '')
        platform = platform.upper()
        p = {'name':key, 'desc':x.info.get('description', ''), 'homepage':x.info.get('homepage', ''),
            'author':x.info.get('author', ''), 'date':x.info.get('date', ''), 'platform':platform,
            'version':x.info.get('version', ''), 'tr_color':tr_color}
        plugins.append(p)
        m = []
        for j, k in enumerate(x.modules.values()):
            i = x.get(k)
            if j % 2:
                t_color = '#FFFFFF'
            else:
                t_color = '#66FF00'
            m.append({'name':x[k].get('name', ''), 'homepage':x[k].get('homepage', ''), 'download':x[k].get('download', ''),
            'description':x[k].get('description', ''), 'version':x[k].get('version', ''), 't_color':t_color})
        p['modules'] = m

    from modules.meteor import Template

    template = Template()
    import T_modulesinfo
    template.load(T_modulesinfo, 'python')

    f = os.path.join(win.app.userpath, 'modulesinfo.html')
    try:
        fout = file(f, "w")
        fout.write(template.value('html', {'body':plugins}))
        fout.close()
        common.webopen(f)
    except:
        error.traceback()
        common.showerror(win, tr("Output modules information error!"))
