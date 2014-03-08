#   Programmer: limodou
#   E-mail:     limodou@gmail.com
#
#   Copyleft 2006 limodou
#
#   Distributed under the terms of the GPLv3 (GNU Public License)
#
#   NewEdit is free software; you can redistribute it and/or modify
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
import  os

import  wx

#----------------------------------------------------------------------

class FileBrowseButton(wx.Panel):
    """
    A control to allow the user to type in a filename or browse with
    the standard file dialog to select file
    """
    def __init__ (self, parent, id= -1,
                  pos = wx.DefaultPosition,
                  size = wx.DefaultSize,
                  style = wx.TAB_TRAVERSAL,
                  labelText= "",
                  buttonText= "...",
                  toolTip= "Type filename or click browse to choose file",
                  # following are the values for a file dialog box
                  dialogTitle = "Choose a file",
                  startDirectory = ".",
                  initialValue = "",
                  fileMask = "*.*",
                  fileMode = wx.OPEN,
                  # callback for when value changes (optional)
                  changeCallback= lambda x:x
        ):
        """
        :param labelText:      Text for label to left of text field
        :param buttonText:     Text for button which launches the file dialog
        :param toolTip:        Help text
        :param dialogTitle:    Title used in file dialog
        :param startDirectory: Default directory for file dialog startup
        :param fileMask:       File mask (glob pattern, such as *.*) to use in file dialog
        :param fileMode:       wx.OPEN or wx.SAVE, indicates type of file dialog to use
        :param changeCallback: Optional callback called for all changes in value of the control
        """

        # store variables
        self.labelText = labelText
        self.buttonText = buttonText
        self.toolTip = toolTip
        self.dialogTitle = dialogTitle
        self.startDirectory = startDirectory
        self.initialValue = initialValue
        self.fileMask = fileMask
        self.fileMode = fileMode
        self.changeCallback = changeCallback
        self.callCallback = True

        # create the dialog
        self.createDialog(parent, id, pos, size, style )
        # Setting a value causes the changeCallback to be called.
        # In this case that would be before the return of the
        # constructor. Not good. So a default value on
        # SetValue is used to disable the callback
        self.SetValue( initialValue, 0)


    def createDialog( self, parent, id, pos, size, style ):
        """Setup the graphic representation of the dialog"""
        wx.Panel.__init__ (self, parent, id, pos, size, style)

        box = wx.BoxSizer(wx.HORIZONTAL)

        self.label = self.createLabel( )
        box.Add(self.label, 0, wx.CENTER)

        self.textControl = self.createTextControl()
        box.Add(self.textControl, 1, wx.EXPAND|wx.CENTER, 2)

        self.browseButton = self.createBrowseButton()
        box.Add(self.browseButton, 0, wx.LEFT|wx.CENTER, 2)

        self.SetSizer(box)
        self.SetAutoLayout(True)
        box.Fit(self)

    def createLabel( self ):
        """Create the label/caption"""
        label = wx.StaticText(self, -1, self.labelText, style =wx.ALIGN_RIGHT )
        return label

    def createTextControl( self):
        """Create the text control"""
        textControl = wx.TextCtrl(self, -1)
        textControl.SetToolTipString( self.toolTip )
        if self.changeCallback:
            textControl.Bind(wx.EVT_TEXT, self.OnChanged)
            textControl.Bind(wx.EVT_COMBOBOX, self.OnChanged)
        return textControl

    def OnChanged(self, evt):
        if self.callCallback and self.changeCallback:
            self.changeCallback(evt)

    def createBrowseButton( self):
        """Create the browse-button control"""
        button =wx.Button(self, -1, self.buttonText, size=(22, 22))
        button.SetToolTipString( self.toolTip )
        button.Bind(wx.EVT_BUTTON, self.OnBrowse)
        return button


    def OnBrowse (self, event = None):
        """ Going to browse for file... """
        current = self.GetValue()
        directory = os.path.split(current)
        if os.path.isdir( current):
            directory = current
            current = ''
        elif directory and os.path.isdir( directory[0] ):
            current = directory[1]
            directory = directory [0]
        else:
            directory = self.startDirectory
        dlg = wx.FileDialog(self, self.dialogTitle, directory, current,
                            self.fileMask, self.fileMode|wx.CHANGE_DIR)

        if dlg.ShowModal() == wx.ID_OK:
            self.SetValue(dlg.GetPath())
        dlg.Destroy()


    def GetValue (self):
        """
        retrieve current value of text control
        """
        return self.textControl.GetValue()

    def SetValue (self, value, callBack=1):
        """set current value of text control"""
        save = self.callCallback
        self.callCallback = callBack
        self.textControl.SetValue(value)
        self.callCallback =  save


    def Enable (self, value):
        """ Convenient enabling/disabling of entire control """
        self.label.Enable (value)
        self.textControl.Enable (value)
        return self.browseButton.Enable (value)

    def GetLabel( self ):
        """ Retrieve the label's current text """
        return self.label.GetLabel()

    def SetLabel( self, value ):
        """ Set the label's current text """
        rvalue = self.label.SetLabel( value )
        self.Refresh( True )
        return rvalue

    def SetBackgroundColour(self, color):
        self.textControl.SetBackgroundColour(color)

class FileBrowseButtonWithHistory( FileBrowseButton ):
    """
    with following additions:
        __init__(..., history=None)

            history -- optional list of paths for initial history drop-down
                (must be passed by name, not a positional argument)
                If history is callable it will must return a list used
                for the history drop-down

            changeCallback -- as for FileBrowseButton, but with a work-around
                for win32 systems which don't appear to create wx.EVT_COMBOBOX
                events properly.  There is a (slight) chance that this work-around
                will cause some systems to create two events for each Combobox
                selection. If you discover this condition, please report it!

            As for a FileBrowseButton.__init__ otherwise.

        GetHistoryControl()
            Return reference to the control which implements interfaces
            required for manipulating the history list.  See GetHistoryControl
            documentation for description of what that interface is.

        GetHistory()
            Return current history list

        SetHistory( value=(), selectionIndex = None )
            Set current history list, if selectionIndex is not None, select that index

        """
    def __init__( self, *arguments, **namedarguments):
        self.history = namedarguments.get( "history" )
        if self.history:
            del namedarguments["history"]

        self.historyCallBack=None
        if callable(self.history):
            self.historyCallBack=self.history
            self.history=None
        FileBrowseButton.__init__(self, *arguments, **namedarguments)


    def createTextControl( self):
        """Create the text control"""
        textControl = wx.ComboBox(self, -1, style = wx.CB_DROPDOWN )
        textControl.SetToolTipString( self.toolTip )
        textControl.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)
        if self.changeCallback:
            textControl.Bind(wx.EVT_TEXT, self.changeCallback)
            textControl.Bind(wx.EVT_COMBOBOX, self.changeCallback)
        if self.history:
            history=self.history
            self.history=None
            self.SetHistory( history, control=textControl)
        return textControl


    def GetHistoryControl( self ):
        """
        Return a pointer to the control which provides (at least)
        the following methods for manipulating the history list:

            Append( item ) -- add item
            Clear() -- clear all items
            Delete( index ) -- 0-based index to delete from list
            SetSelection( index ) -- 0-based index to select in list

        Semantics of the methods follow those for the wxComboBox control
        """
        return self.textControl


    def SetHistory( self, value=(), selectionIndex = None, control=None ):
        """Set the current history list"""
        if control is None:
            control = self.GetHistoryControl()
        if self.history == value:
            return
        self.history = value
        # Clear history values not the selected one.
        tempValue=control.GetValue()
        # clear previous values
        control.Clear()
        control.SetValue(tempValue)
        # walk through, appending new values
        for path in value:
            control.Append( path )
        if selectionIndex is not None:
            control.SetSelection( selectionIndex )


    def GetHistory( self ):
        """Return the current history list"""
        if self.historyCallBack != None:
            return self.historyCallBack()
        else:
            return list( self.history )


    def OnSetFocus(self, event):
        """When the history scroll is selected, update the history"""
        if self.historyCallBack != None:
            self.SetHistory( self.historyCallBack(), control=self.textControl)
        event.Skip()


    if wx.Platform == "__WXMSW__":
        def SetValue (self, value, callBack=1):
            """ Convenient setting of text control value, works
                around limitation of wx.ComboBox """
            save = self.callCallback
            self.callCallback = callBack
            self.textControl.SetValue(value)
            self.callCallback =  save

            # Hack to call an event handler
            class LocalEvent:
                def __init__(self, string):
                    self._string=string
                def GetString(self):
                    return self._string
            if callBack==1:
                # The callback wasn't being called when SetValue was used ??
                # So added this explicit call to it
                self.changeCallback(LocalEvent(value))


class DirBrowseButton(FileBrowseButton):
    def __init__(self, parent, id = -1,
                 pos = wx.DefaultPosition, size = wx.DefaultSize,
                 style = wx.TAB_TRAVERSAL,
                 labelText = '',
                 buttonText = '...',
                 toolTip = 'Type directory name or browse to select',
                 dialogTitle = '',
                 startDirectory = os.getcwd(),
                 initialValue = "",
                 changeCallback = None,
                 dialogClass = wx.DirDialog,
                 newDirectory = True):
        FileBrowseButton.__init__(self, parent, id, pos, size, style,
                                  labelText, buttonText, toolTip,
                                  dialogTitle, startDirectory,
                                  initialValue,
                                  changeCallback = changeCallback)
        self.dialogClass = dialogClass
        self.newDirectory = newDirectory
    #

    def OnBrowse(self, ev = None):
        style=0

        if self.newDirectory:
            style|=wx.DD_NEW_DIR_BUTTON

        dialog = self.dialogClass(self,
                                  message = self.dialogTitle,
                                  defaultPath = self.startDirectory,
                                  style = style)

        if dialog.ShowModal() == wx.ID_OK:
            self.SetValue(dialog.GetPath())
        dialog.Destroy()
    #
