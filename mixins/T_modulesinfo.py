from modules.meteor import *

header = T('''<HTML>
<HEAD>
<TITLE> UliPad Extended Modules Information </TITLE>
<style type="text/css">
<!--
body {  font-family: "Verdana", "Arial", "Helvetica", "sans-serif"; font-size: 11px; text-decoration: none}
tr {  font-family: "Verdana", "Arial", "Helvetica", "sans-serif"; font-size: 11px; text-decoration: none}
-->
</style>
</HEAD>

<BODY>

<h2 class="title" align="center">UliPad Extended Modules Information</h2>
<TABLE align="center" width="768">
''')

body = T('''<TR bgcolor="<#tr_color#>">
        <TD width="200">Name: <B><a href="<#homepage#>"><#name#></a></B> <#platform#></TD>
        <TD colspan="2">Description: <#desc#></TD>
</TR>
<TR>
        <TD>Author: <B><#author#></B></TD>
        <TD>Date: <B><#date#></B></TD>
        <TD>Version: <B><#version#></B></TD>
</TR>
<#modules#>
<tr>
    <td colspan="3">&nbsp;</tr>
</tr>
''')

modules = T('''<TR>
        <TD>Extended Modules</TD>
        <TD colspan="2">
        <TABLE bgcolor="<#t_color#>">
        <TR>
                <TD>Name:<a href="<#homepage#>"><B><#name#></B></a></TD>
                <TD><a href="<#download#>">Download</a></TD>
                <TD>Version: <B><#version#></B></TD>
        </TR>
        <TR>
                <TD colspan="3">Description: <#description#></TD>
        </TR>
    <tr>
        <td colspan="3">&nbsp;</tr>
    </tr>
        </TABLE>
        </TD>
''')

footer = T('''</TR>
</TABLE>
</BODY>
</HTML>
''')

html = T('''<#header#><#body#><#footer#>''')
