# --------------------------------------------------------------------------- #
# HYPERLINKCTRL wxPython IMPLEMENTATION
# Ported From Angelo Mandato C++ Code By:
#
# Andrea Gavana, @ 27 Mar 2005
# Latest Revision: 05 Nov 2005, 22.30 CET
#
#
# Original Web Site (For The C++ Code):
#
# http://www.spaceblue.com/codedetail.php?CodeID=7
#
#
# Thanks to E. A. Tacao for his nice suggestions and improvements of the code.
#
# For all kind of problems, requests of enhancements and bug reports, please
# write to me at:
#
# andrea.gavana@agip.it
# andrea_gavan@tin.it
#
# Or, obviously, to the wxPython mailing list!!!
#
#
# End Of Comments
# --------------------------------------------------------------------------- #

"""
`HyperLinkCtrl` is a control for wxPython that acts like a hyper link
in a typical browser. Latest features include the ability to capture
your own Left, Middle, and Right click events to perform your own
custom event handling and ability to open link in a new or current
browser window.

Special thanks to Robin Dunn for the event binder for the 3 mouse buttons.


Latest Revision: Andrea Gavana @ 05 Nov 2005, 22.30 CET

"""

import wx
from wx.lib.stattext import GenStaticText as StaticText

# Import the useful webbrowser module for platform-independent results
import webbrowser

# Set no delay time to open the web page
webbrowser.PROCESS_CREATION_DELAY = 0

# To show a popup that copies the hyperlinks on the clipboard
wxHYPERLINKS_POPUP_COPY = 1000


#-----------------------------------#
#        HyperLinksEvents
#-----------------------------------#

# wxEVT_HYPERLINK_LEFT: Respond To A Left Mouse Button Event
# wxEVT_HYPERLINK_MIDDLE: Respond To A Middle Mouse Button Event
# wxEVT_HYPERLINK_RIGHT: Respond To A Right Mouse Button Event

wxEVT_HYPERLINK_LEFT = wx.NewEventType()
wxEVT_HYPERLINK_MIDDLE = wx.NewEventType()
wxEVT_HYPERLINK_RIGHT = wx.NewEventType()

EVT_HYPERLINK_LEFT = wx.PyEventBinder(wxEVT_HYPERLINK_LEFT, 1)
EVT_HYPERLINK_MIDDLE = wx.PyEventBinder(wxEVT_HYPERLINK_MIDDLE, 1)
EVT_HYPERLINK_RIGHT = wx.PyEventBinder(wxEVT_HYPERLINK_RIGHT, 1)


# ------------------------------------------------------------
# This class implements the event listener for the hyperlinks
# ------------------------------------------------------------

class HyperLinkEvent(wx.PyCommandEvent):
    """
    Event object sent in response to clicking on a `HyperLinkCtrl`.
    """

    def __init__(self, eventType, id):
        """ Default Class Constructor. """
        wx.PyCommandEvent.__init__(self, eventType, id)
        self._eventType = eventType


    def SetPosition(self, pos):
        """ Sets Event Position """
        self._pos = pos


    def GetPosition(self):
        """ Returns Event Position """
        return self._pos


# -------------------------------------------------
# This is the main HyperLinkCtrl implementation
# it user the StatiText from wx.lib.stattext
# because of its "quasi-dynamic" behavior
# -------------------------------------------------

class HyperLinkCtrl(StaticText):
    """
    `HyperLinkCtrl` is a control for wxPython that acts like a hyper
    link in a typical browser. Latest features include the ability to
    capture your own Left, Middle, and Right click events to perform
    your own custom event handling and ability to open link in a new
    or current browser window.

    Events
    ------
        ====================  =======================================
        EVT_HYPERLINK_LEFT    Sent when the left mouse button is
                              clicked, but only if `AutoBrowse` is set
                              to ``False``.
        EVT_HYPERLINK_MIDDLE  Sent when the middle mouse button is
                              clicked.
        EVT_HYPERLINK_RIGHT   Sent when the right mouse button is
                              clicked, but only if `DoPopup` is set
                              to ``False``.
        ====================  =======================================
    """

    def __init__(self, parent, id=-1, label="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, name="staticText", URL=""):
        """
        Default class constructor.

        Pass URL == "" to use the label as the url link to navigate to
        """

        StaticText.__init__(self, parent, id, label, pos, size,
                            style, name)

        if URL.strip() == "":
            self._URL = label
        else:
            self._URL = URL

        # Set Tooltip
        self.SetToolTip(wx.ToolTip(self._URL))

        # Set default properties
        # default: True
        self.ReportErrors()

        # default: True, True, True
        self.SetUnderlines()

        # default: blue, violet, blue
        self.SetColours()

        # default: False
        self.SetVisited()

        # default: False
        self.EnableRollover()

        # default: False
        self.SetBold()

        # default: wx.CURSOR_HAND
        self.SetLinkCursor()

        # default True
        self.AutoBrowse()

        # default True
        self.DoPopup()

        # default False
        self.OpenInSameWindow()

        # Set control properties and refresh
        self.UpdateLink(True)

        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvent)
        self.Bind(wx.EVT_MOTION, self.OnMouseEvent)


    def GotoURL(self, URL, ReportErrors=True, NotSameWinIfPossible=False):
        """
        Goto The Specified URL.

        :param ReportErrors: Use True to display error dialog if an
            error occurrs navigating to the URL.

        :param NotSameWinIfPossible: Use True to attempt to open the
            URL in new browser window.

        """

        logOff = wx.LogNull()

        try:
            webbrowser.open(URL, new=NotSameWinIfPossible)
            self.SetVisited(True)
            self.UpdateLink(True)

            return True

        except:
            self.DisplayError("Unable To Launch Browser.", ReportErrors)
            return False


    def OnMouseEvent(self, event):
        """ Captures mouse events for cursor, link colors and underlines. """

        if event.Moving():
            # Mouse Is Moving On The StaticText
            # Set The Hand Cursor On The Link
            self.SetCursor(self._CursorHand)

            if self._EnableRollover:
                fontTemp = self.GetFont()
                fontTemp.SetUnderlined(self._RolloverUnderline)
                if self._Bold:
                    fontTemp.SetWeight(wx.BOLD)

                needRefresh = False

                if self.GetFont() != fontTemp:
                    self.SetFont(fontTemp)
                    needRefresh = True

                if self.GetForegroundColour() != self._LinkRolloverColor:
                    self.SetForegroundColour(self._LinkRolloverColor)
                    needRefresh = True

                if needRefresh:
                    self.Refresh()

        else:
            # Restore The Original Cursor
            self.SetCursor(wx.NullCursor)
            if self._EnableRollover:
                self.UpdateLink(True)

            if event.LeftUp():
                # Left Button Was Pressed
                if self._AutoBrowse:
                    self.GotoURL(self._URL, self._ReportErrors,
                                 self._NotSameWinIfPossible)

                else:
                    eventOut = HyperLinkEvent(wxEVT_HYPERLINK_LEFT, self.GetId())
                    eventOut.SetEventObject(self)
                    eventOut.SetPosition(event.GetPosition())
                    self.GetEventHandler().ProcessEvent(eventOut)

                self.SetVisited(True)

            elif event.RightUp():
                # Right Button Was Pressed
                if self._DoPopup:
                    # Popups A Menu With The "Copy HyperLynks" Feature
                    menuPopUp = wx.Menu("", wx.MENU_TEAROFF)
                    menuPopUp.Append(wxHYPERLINKS_POPUP_COPY, "Copy HyperLink")
                    self.Bind(wx.EVT_MENU, self.OnPopUpCopy, id=wxHYPERLINKS_POPUP_COPY)
                    self.PopupMenu(menuPopUp, wx.Point(event.m_x, event.m_y))
                    menuPopUp.Destroy()
                    self.Unbind(wx.EVT_MENU, id=wxHYPERLINKS_POPUP_COPY)

                else:
                    eventOut = HyperLinkEvent(wxEVT_HYPERLINK_RIGHT, self.GetId())
                    eventOut.SetEventObject(self)
                    eventOut.SetPosition(event.GetPosition())
                    self.GetEventHandler().ProcessEvent(eventOut)

            elif event.MiddleUp():
                # Middle Button Was Pressed
                eventOut = HyperLinkEvent(wxEVT_HYPERLINK_MIDDLE, self.GetId())
                eventOut.SetEventObject(self)
                eventOut.SetPosition(event.GetPosition())
                self.GetEventHandler().ProcessEvent(eventOut)

        event.Skip()


    def OnPopUpCopy(self, event):
        """ Copy data from the HyperLink to the clipboard. """

        wx.TheClipboard.UsePrimarySelection(False)
        if not wx.TheClipboard.Open():
            return
        data = wx.TextDataObject(self._URL)
        wx.TheClipboard.SetData(data)
        wx.TheClipboard.Close()


    def UpdateLink(self, OnRefresh=True):
        """
        Updates the link.

        Changing text properties if:
            - User Specific Setting
            - Link Visited
            - New Link

        """

        fontTemp = self.GetFont()

        if self._Visited:
            self.SetForegroundColour(self._VisitedColour)
            fontTemp.SetUnderlined(self._VisitedUnderline)

        else:

            self.SetForegroundColour(self._LinkColour)
            fontTemp.SetUnderlined(self._LinkUnderline)

        if self._Bold:
            fontTemp.SetWeight(wx.BOLD)

        if self.GetFont() != fontTemp:
            self.SetFont(fontTemp)
            self.Refresh(OnRefresh)


    def DisplayError(self, ErrorMessage, ReportErrors=True):
        """
        Displays an error message (according to ReportErrors variable)
        in a MessageBox.
        """
        if ReportErrors:
            wx.MessageBox(ErrorMessage, "HyperLink Error", wx.OK | wx.CENTRE | wx.ICON_ERROR)


    def SetColours(self,
                   link=wx.Colour(0, 0, 255),
                   visited=wx.Colour(79, 47, 79),
                   rollover=wx.Colour(0, 0, 255)):
        """ Sets the colours for the link, the visited link and the mouse rollover.

        Defaults Are:
            - New Link: RED
            - Visited Link: VIOLET
            - Rollover: BLUE

        """
        self._LinkColour = link
        self._VisitedColour = visited
        self._LinkRolloverColor = rollover


    def GetColours(self):
        """
        Gets the colours for the link, the visited link and the mouse
        rollover.
        """
        return self._LinkColour, self._VisitedColour, self._LinkRolloverColor


    def SetUnderlines(self, link=True, visited=True, rollover=True):
        """ Underlines Properties. """
        self._LinkUnderline = link
        self._RolloverUnderline = rollover
        self._VisitedUnderline = visited


    def GetUnderlines(self):
        """
        Returns if link is underlined, if the mouse rollover is
        underlined and if the visited link is underlined.
        """
        return self._LinkUnderline, self._RolloverUnderline, self._VisitedUnderline


    def SetLinkCursor(self, cur=wx.CURSOR_HAND):
        """ Sets link cursor properties. """
        self._CursorHand = wx.StockCursor(cur)


    def GetLinkCursor(self):
        """ Gets the link cursor. """
        return self._CursorHand


    def SetVisited(self, Visited=False):
        """ Sets a link as visited. """

        self._Visited = Visited


    def GetVisited(self):
        """ Returns whether a link has been visited or not. """
        return self._Visited


    def SetBold(self, Bold=False):
        """ Sets the HyperLink in bold text. """
        self._Bold = Bold


    def GetBold(self):
        """ Returns whether the HyperLink has text in bold or not. """
        return self._Bold


    def SetURL(self, URL):
        """ Sets the HyperLink text to the specified URL. """
        self._URL = URL


    def GetURL(self):
        """ Retrieve the URL associated to the HyperLink. """
        return self._URL


    def OpenInSameWindow(self, NotSameWinIfPossible=False):
        """ Open multiple URL in the same window (if possible). """
        self._NotSameWinIfPossible = NotSameWinIfPossible


    def EnableRollover(self, EnableRollover=False):
        """ Enable/disable rollover. """
        self._EnableRollover = EnableRollover


    def ReportErrors(self, ReportErrors=True):
        """ Set whether to report browser errors or not. """
        self._ReportErrors = ReportErrors


    def AutoBrowse(self, AutoBrowse=True):
        """
        Automatically browse to URL when clicked. set to False to
        receive EVT_HYPERLINK_LEFT event.
        """
        self._AutoBrowse = AutoBrowse


    def DoPopup(self, DoPopup=True):
        """ Sets whether to show popup menu on right click or not. """
        self._DoPopup = DoPopup


# ----------------------------------------------------------------
# HyperLinksCtrl Demo
#
# Is Just A Frame With A Panel With 4 HyperLinks On It.
# Depending On The User Mouse Click, Different Actions Are Taken
# ----------------------------------------------------------------

# Icon For The Demo (Mondrian Standard wxPython Icon)

def GetMondrianData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00 \x00\x00\x00 \x08\x06\x00\
\x00\x00szz\xf4\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\x00qID\
ATX\x85\xed\xd6;\n\x800\x10E\xd1{\xc5\x8d\xb9r\x97\x16\x0b\xad$\x8a\x82:\x16\
o\xda\x84pB2\x1f\x81Fa\x8c\x9c\x08\x04Z{\xcf\xa72\xbcv\xfa\xc5\x08 \x80r\x80\
\xfc\xa2\x0e\x1c\xe4\xba\xfaX\x1d\xd0\xde]S\x07\x02\xd8>\xe1wa-`\x9fQ\xe9\
\x86\x01\x04\x10\x00\\(Dk\x1b-\x04\xdc\x1d\x07\x14\x98;\x0bS\x7f\x7f\xf9\x13\
\x04\x10@\xf9X\xbe\x00\xc9 \x14K\xc1<={\x00\x00\x00\x00IEND\xaeB`\x82'

def GetMondrianBitmap():
    return wx.BitmapFromImage(GetMondrianImage())

def GetMondrianImage():
    import cStringIO
    stream = cStringIO.StringIO(GetMondrianData())
    return wx.ImageFromStream(stream)

def GetMondrianIcon():
    icon = wx.EmptyIcon()
    icon.CopyFromBitmap(GetMondrianBitmap())
    return icon

# ---------------------------------------------------------------


class HyperLinksFrame(wx.Frame):

    def __init__(self, parent, id=-1, title="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize):

        wx.Frame.__init__(self, parent, id, title, pos, size)

        self.SetIcon(GetMondrianIcon())

        panel = LinksPanel(self, wx.ID_ANY)

        ID_EXIT = wx.NewId()
        ID_ABOUT = wx.NewId()

        file_menu = wx.Menu()

        file_menu.Append(ID_EXIT, "&Exit")

        help_menu = wx.Menu()

        help_menu.Append(ID_ABOUT, "&About")

        self.Bind(wx.EVT_MENU, self.OnClose, id=ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=ID_ABOUT)

        menu_bar = wx.MenuBar()

        menu_bar.Append(file_menu, "&File")
        menu_bar.Append(help_menu, "&Help")

        self.SetMenuBar(menu_bar)


    def OnAbout(self, event):

        strs = "HyperLinksCtrl\n\nC++ Implementation: Angelo Mandato,"
        strs = strs + " 2004    \n\nwxPython Port: Andrea Gavana, 11 May 2005     "
        wx.MessageBox(strs, "HyperLinksCtrl")


    def OnClose(self, event):

        self.Close()


class LinksPanel(wx.Panel):

    def __init__(self, parent, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize):

        wx.Panel.__init__(self, parent, id, pos, size)

        self.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False))

        sizer = wx.BoxSizer(wx.VERTICAL)

        # Creator credits
        text1 = wx.StaticText(self, -1, "HyperLinksCtrl Example By Andrea Gavana",
                                    (20,10), wx.DefaultSize, 0, "infotext1")
        text1.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD, False, 'Verdana'))

        sizer.Add((0,10))
        sizer.Add(text1, 0, wx.LEFT | wx.TOP | wx.BOTTOM, 10)

        text2 = wx.StaticText(self, -1, "Latest Revision: 11 May 2005",
                                    (20,10), wx.DefaultSize, 0, "infotext2")
        text2.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Verdana'))
        sizer.Add(text2, 0, wx.LEFT, 10)

        sizer.Add((0,25))

        # Default Web links:
        self._hyper1 = HyperLinkCtrl(self, wx.ID_ANY, "wxPython Main Page",
                                      (70,30), wx.DefaultSize, 0,
                                      "statictextlink2", "http://www.wxpython.org/")

        sizer.Add(self._hyper1, 0, wx.ALL, 10)
        # Web link with underline rollovers, opens in window
        self._hyper2 = HyperLinkCtrl(self, wx.ID_ANY, "My Home Page", (70,50),
                                      wx.DefaultSize, wx.TAB_TRAVERSAL ,
                                      "statictextlink2",
                                      "http://xoomer.virgilio.it/infinity77/")

        sizer.Add(self._hyper2, 0, wx.ALL, 10)
        self._hyper2.Bind(EVT_HYPERLINK_MIDDLE, self.OnMiddleLink)

        self._hyper2.SetColours(wx.NamedColour("BLUE"), wx.NamedColour("BLUE"),
                                wx.NamedColour("BLUE"))
        self._hyper2.EnableRollover(True)
        self._hyper2.SetUnderlines(False, False, True)
        self._hyper2.SetBold(True)
        self._hyper2.OpenInSameWindow(True) # middle click to open in window
        self._hyper2.SetToolTip(wx.ToolTip("Middle Click To Open In Browser Window"))
        self._hyper2.UpdateLink()

        # Intense link examples..
        self._hyper3 = HyperLinkCtrl(self, wx.ID_ANY, "wxPython Mail Archive", (70,70),
                                      wx.DefaultSize, 0, "statictextlink2",
                                      "http://lists.wxwidgets.org/")

        sizer.Add(self._hyper3, 0, wx.ALL, 10)
        self._hyper3.Bind(EVT_HYPERLINK_RIGHT, self.OnRightLink)

        self._hyper3.SetLinkCursor(wx.CURSOR_QUESTION_ARROW)
        self._hyper3.SetColours(wx.NamedColour("GREEN"), wx.NamedColour("RED"),
                                wx.NamedColour("YELLOW"))
        self._hyper3.SetUnderlines(False, False, False)

        self._hyper3.EnableRollover(True)
        self._hyper3.SetBold(True)
        self._hyper3.DoPopup(False)

        self._hyper3.UpdateLink()

        self._hyper4 = HyperLinkCtrl(self, wx.ID_ANY,
                                      "Open Google In Current Browser Window?",
                                      (70,90), wx.DefaultSize, 0, "statictextlink2",
                                      "http://www.google.com")

        sizer.Add(self._hyper4, 0, wx.ALL, 10)
        self._hyper4.Bind(EVT_HYPERLINK_LEFT, self.OnLink)

        self._hyper4.SetToolTip(wx.ToolTip("Click Link For Yes, No, Cancel Dialog"))
        self._hyper4.AutoBrowse(False)

        self.SetSizer(sizer)


    def OnLink(self, event):

        # Goto URL, demonstrates attempt to open link in current window:
        strs = "Open Google In Current Browser Window "
        strs = strs + "(NO Opens Google In Another Browser Window)?"
        nResult = wx.MessageBox(strs, "HyperLinkCtrl", wx.YES_NO |
                                wx.CANCEL | wx.ICON_QUESTION, self)

        if nResult == wx.YES:
            self._hyper4.GotoURL("http://www.google.com", True, True)
        elif nResult == wx.NO:
            self._hyper4.GotoURL("http://www.google.com", True, False)


    def OnRightLink(self, event):

        pos = event.GetPosition()
        menuPopUp = wx.Menu("", wx.MENU_TEAROFF)
        ID_MENU = wx.NewId()
        menuPopUp.Append(ID_MENU, "Close Main Dialog")
        self.Bind(wx.EVT_MENU, self.OnMenuClose, id=ID_MENU)
        self.PopupMenu(menuPopUp, self._hyper3.GetPosition())

        menuPopUp.Destroy()
        del menuPopUp


    def OnMiddleLink(self, event):

        self._hyper2.GotoURL("http://xoomer.virgilio.it/infinity77/",
                             True, True)


    def OnMenuClose(self, event):

        self.GetParent().Destroy()


def main():

    MyApp = wx.PySimpleApp()

    Frame = HyperLinksFrame(None, -1, "HyperLinkCtrl", pos=wx.DefaultPosition,
                            size=(400,300))

    MyApp.SetTopWindow(Frame)
    Frame.CenterOnScreen()
    Frame.Show()

    MyApp.MainLoop()


if __name__ == "__main__":

    main()
