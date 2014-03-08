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
#   $Id: Print.py 1457 2006-08-23 02:12:12Z limodou $
   
import wx.html
import os

class MyPrinter(wx.html.HtmlEasyPrinting):

    def __init__(self, mainframe):
        wx.html.HtmlEasyPrinting.__init__(self)
        self.mainframe = mainframe

    def convertText(self, text):
        #htmlify the text:
        text = ("<html><body link=\"#FFFFFF\" vlink=\"#FFFFFF\" alink=\"#FFFFFF\">" 
            + text 
            + "</body></html>")

        return text

    def Print(self, text, filename):
        self.SetHeader(filename)
        self.PrintText(self.convertText(text), os.path.dirname(filename))

FONTSIZE = 10

class TextDocPrintout(wx.Printout):
    def __init__(self, text, title, margins, printlinenumber=True):
        wx.Printout.__init__(self)
        
        self.text = text
        self.margins = margins
        self.title = title
        self.printlinenumber = printlinenumber

    def HasPage(self, page):
        return page <= self.numPages

    def GetPageInfo(self):
        return (1, self.numPages, 1, self.numPages)

    def CalculateScale(self, dc):
        # Scale the DC such that the printout is roughly the same as
        # the screen scaling.
        ppiPrinterX, ppiPrinterY = self.GetPPIPrinter()
        ppiScreenX, ppiScreenY = self.GetPPIScreen()
        logScale = float(ppiPrinterX)/float(ppiScreenX)

        # Now adjust if the real page size is reduced (such as when
        # drawing on a scaled wx.MemoryDC in the Print Preview.)  If
        # page width == DC width then nothing changes, otherwise we
        # scale down for the DC.
        pw, ph = self.GetPageSizePixels()
        dw, dh = dc.GetSize()
        scale = logScale * float(dw)/float(pw)

        # Set the DC's scale.
        dc.SetUserScale(scale, scale)

        # Find the logical units per millimeter (for calculating the
        # margins)
        self.logUnitsMM = float(ppiPrinterX)/(logScale*25.4)


    def CalculateLayout(self, dc):
        # Determine the position of the margins and the
        # page/line height
        topLeft, bottomRight = self.margins
        dw, dh = dc.GetSize()
        self.x1 = topLeft.x * self.logUnitsMM
        self.y1 = topLeft.y * self.logUnitsMM
        self.x2 = dc.DeviceToLogicalXRel(dw) - bottomRight.x * self.logUnitsMM
        self.y2 = dc.DeviceToLogicalYRel(dh) - bottomRight.y * self.logUnitsMM

        # use a 1mm buffer around the inside of the box, and a few
        # pixels between each line
        self.pageHeight = self.y2 - self.y1 - 2*self.logUnitsMM
        font = wx.Font(FONTSIZE, wx.TELETYPE, wx.NORMAL, wx.NORMAL)
        dc.SetFont(font)
        self.lineHeight = dc.GetCharHeight()
        self.linesPerPage = int(self.pageHeight/self.lineHeight)
        self.colsPerPage = int((self.x2 - self.x1)/dc.GetCharWidth())

    def OnPreparePrinting(self):
        # calculate the number of pages
        dc = self.GetDC()
        self.CalculateScale(dc)
        self.CalculateLayout(dc)
        
        def textwrap(ustr, width=80, leadingspace=6):
            import unicodedata
            
            if not ustr:
                return []
            
            lines = []
            i = 0
            buf = []
            for c in ustr:
                if unicodedata.east_asian_width(c) != 'Na':
                    d = 2
                else:
                    d = 1
                if i+d <= width:
                    buf.append(c)
                    i += d
                else:
                    lines.append(''.join(buf))
                    buf = [leadingspace*' ' + c]
                    i = d + leadingspace
            if buf:
                lines.append(''.join(buf))
            
            return lines
            
        self.lines = []
        import re
        i = 1
        for line in re.split(r'\r\n|\r|\n', self.text):
            if self.printlinenumber:
                line = "%-6d" % i + line
                i += 1
                leading = 6
            else:
                leading = 0
            lines = textwrap(line, self.colsPerPage, leading)
            if not lines:
                self.lines.append('')
            else:
                self.lines.extend(lines)
        
        self.numPages = len(self.lines) / self.linesPerPage
        if len(self.lines) % self.linesPerPage != 0:
            self.numPages += 1


    def OnPrintPage(self, page):
        dc = self.GetDC()
        self.CalculateScale(dc)
        self.CalculateLayout(dc)

        # draw a page outline at the margin points
        dc.SetPen(wx.Pen("black", 0))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)

        dc.DrawLine(self.x1, self.y1, self.x2, self.y1)
        dc.DrawLine(self.x1, self.y2, self.x2, self.y2)

        #print title and date
        if self.title:
            tlw, tlh = dc.GetTextExtent(self.title)
            dc.DrawText(self.title, self.x1, self.y1-self.lineHeight)
         
        import time
        date = time.strftime('%Y-%m-%d %H:%M')
        tlw, tlh = dc.GetTextExtent(date)
        dc.DrawText(date, self.x2-tlw, self.y1-self.lineHeight-2)
        
        # Draw the text lines for this page
        line = (page-1) * self.linesPerPage
        x = self.x1 + self.logUnitsMM
        y = self.y1 + self.logUnitsMM
        while line < (page * self.linesPerPage):
            dc.DrawText(self.lines[line], x, y)
            y += self.lineHeight
            line += 1
            if line >= len(self.lines):
                break
            
        page = tr("Page %d of %d") % (page, self.numPages)
        tlw, tlh = dc.GetTextExtent(date)
        dc.DrawText(page, (self.x1 + self.x2 - tlw )/2, self.y2+2)
        
        return True

class SimpleDocPrinter(wx.Printout):
    def __init__(self, frame):
        wx.Printout.__init__(self)
        
        self.frame = frame
        self.margins = (wx.Point(15,15), wx.Point(15,15))
        self.pdata = wx.PrintData()

    def PageSetup(self):
        data = wx.PageSetupDialogData()
        data.SetPrintData(self.pdata)
    
        data.SetDefaultMinMargins(True)
        data.SetMarginTopLeft(self.margins[0])
        data.SetMarginBottomRight(self.margins[1])
    
        dlg = wx.PageSetupDialog(self.frame, data)
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetPageSetupData()
            self.pdata = wx.PrintData(data.GetPrintData()) # force a copy
            self.pdata.SetPaperId(data.GetPaperId())
            self.margins = (data.GetMarginTopLeft(),
                            data.GetMarginBottomRight())
        dlg.Destroy()
    
    def PrintSetup(self):
        data = wx.PrintDialogData(self.pdata)
        dlg = wx.PrintDialog(self, data)
        dlg.GetPrintDialogData().SetSetupDialog(True)
        dlg.ShowModal();
        data = dlg.GetPrintDialogData()
        self.pdata = wx.PrintData(data.GetPrintData()) # force a copy
        dlg.Destroy()
    
    def PrintPreview(self, text, filename):
        data = wx.PrintDialogData(self.pdata)
        print1 = TextDocPrintout(text, filename, self.margins, self.frame.pref.print_line_number)
        print2 = TextDocPrintout(text, filename, self.margins, self.frame.pref.print_line_number)
        preview = wx.PrintPreview(print1, print2, data)
        if not preview.Ok():
            wx.MessageBox(tr("Unable to create PrintPreview!"), tr("Error"))
        else:
            # create the preview frame such that it overlays the app frame
            frame = wx.PreviewFrame(preview, self.frame, tr("Print Preview - %s") % \
                filename, self.frame.GetPosition(), self.frame.GetSize())
            frame.Initialize()
            frame.Show()
    
    def Print(self, text, filename):
        data = wx.PrintDialogData(self.pdata)
        printer = wx.Printer(data)
        useSetupDialog = True
        print1 = TextDocPrintout(text, filename, self.margins, self.frame.pref.print_line_number)
        if not printer.Print(self.frame, print1, useSetupDialog) \
           and printer.GetLastError() == wx.PRINTER_ERROR:
            wx.MessageBox(
                tr("There was a problem printing.\n"
                "Perhaps your current printer is not set correctly?"),
                tr("Printing Error"), wx.OK)
        else:
            data = printer.GetPrintDialogData()
            self.pdata = wx.PrintData(data.GetPrintData()) # force a copy

        
        