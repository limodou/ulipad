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
#   $Id$

from mixins.NCustomLexer import *
    
class FortranLexer(CustomLexer):

    metaname = 'fortran'
    casesensitive = False

    keywords = ('''
        admit allocatable allocate assign assignment at backspace block call case 
        character close common complex contains continue cycle data deallocate 
        default dimension do double else elseif elsewhere end enddo endfile endif 
        endwhile entry equivalence execute exit external forall format function
        go goto guess if implicit in inout inquire integer intent interface intrinsic
        kind logical loop map module namelist none nullify only open operator optional 
        otherwise out parameter pointer private procedure program public quit
        read real record recursive remote result return rewind save select sequence 
        stop structure subroutine target then to type union until use where while 
        write''').split()

    preview_code = """! Free Format
program main
write(*,*) "Hello" !This is also comment
write(*,*) &
"Hello"
wri&
&te(*,*) "Hello"
end
"""
    
    comment_begin = '!'
