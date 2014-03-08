#       Programmer:     limodou
#       E-mail:         limodou@gmail.com
#
#       Copyleft 2006 limodou
#
#       Distributed under the terms of the GPL (GNU Public License)
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
#       $Id: Resource.py 1457 2006-08-23 02:12:12Z limodou $

"""Resource processing module"""

import wx
import wx.xrc
from wx.xrc import XRCID
from Debug import debug
import common

def loadfromresfile(resfile, parent, winclass, resname, *args, **kwargs):
    """Load resource from file"""

    res = wx.xrc.EmptyXmlResource()
    res.Load(common.encode_string(resfile))
    if issubclass(winclass, wx.Dialog):
        xmlhandler = xmlDefaultHandler(parent, winclass, 'wxDialog', *args, **kwargs)
        res.InsertHandler(xmlhandler)
        res.LoadDialog(parent, resname)
    elif issubclass(winclass, wx.Frame):
        xmlhandler = xmlDefaultHandler(parent, winclass, 'wxFrame', *args, **kwargs)
        res.InsertHandler(xmlhandler)
        res.LoadFrame(winclass, resname)
    elif issubclass(winclass, wx.Panel):
        xmlhandler = xmlDefaultHandler(parent, winclass, 'wxPanel', *args, **kwargs)
        res.InsertHandler(xmlhandler)
        res.LoadPanel(winclass, resname)

    return xmlhandler.obj

def loadfromres(resourceText, parent, winclass, resname, *args, **kwargs):
    """Load resource from string
    only support three kinds: Frame, Dialog, Panel
    parent          parent window
    winclass        the created object class
    resname         the name of resource"""

    res = wx.xrc.EmptyXmlResource()
    res.LoadFromString(resourceText)
    if issubclass(winclass, wx.Dialog):
        xmlhandler = xmlDefaultHandler(parent, winclass, 'wxDialog', *args, **kwargs)
        res.InsertHandler(xmlhandler)
        res.LoadDialog(parent, resname)
    elif issubclass(winclass, wx.Frame):
        xmlhandler = xmlDefaultHandler(parent, winclass, 'wxFrame', *args, **kwargs)
        res.InsertHandler(xmlhandler)
        res.LoadFrame(winclass, resname)
    elif issubclass(winclass, wx.Panel):
        xmlhandler = xmlDefaultHandler(parent, winclass, 'wxPanel', *args, **kwargs)
        res.InsertHandler(xmlhandler)
        res.LoadPanel(winclass, resname)

    return xmlhandler.obj

class xmlDefaultHandler(wx.xrc.XmlResourceHandler):
    def __init__(self, parentwin, winclass, classname, *args, **kwargs):
        wx.xrc.XmlResourceHandler.__init__(self)
        self.parentwin = parentwin
        self.winclass = winclass
        self.classname = classname
        self.args = args
        self.kwargs = kwargs
        self.ids = []
        self.obj = None

        # Specify the styles recognized by objects of this type
        self.AddStyle("wxDEFAULT_DIALOG_STYLE",         wx.DEFAULT_DIALOG_STYLE)
        self.AddStyle("wxSTAY_ON_TOP",                          wx.STAY_ON_TOP)
        self.AddStyle("wxDIALOG_MODAL",                         wx.DIALOG_MODAL)
        self.AddStyle("wxDIALOG_MODELESS",                      wx.DIALOG_MODELESS)
        self.AddStyle("wxCAPTION",                                      wx.CAPTION)
        self.AddStyle("wxSYSTEM_MENU",                          wx.SYSTEM_MENU)
        self.AddStyle("wxRESIZE_BORDER",                        wx.RESIZE_BORDER)
        self.AddStyle("wxRESIZE_BOX",                           wx.RESIZE_BOX)
        self.AddStyle("wxTHICK_FRAME",                          wx.THICK_FRAME)
        self.AddStyle("wxNO_3D",                                        wx.NO_3D)
        self.AddStyle("wxTAB_TRAVERSAL",                        wx.TAB_TRAVERSAL)
        self.AddStyle("wxCLIP_CHILDREN",                        wx.CLIP_CHILDREN)
        self.AddStyle("wxSIMPLE_BORDER",                        wx.SIMPLE_BORDER)
        self.AddStyle("wxDOUBLE_BORDER",                        wx.DOUBLE_BORDER)
        self.AddStyle("wxSUNKEN_BORDER",                        wx.SUNKEN_BORDER)
        self.AddStyle("wxRAISED_BORDER",                        wx.RAISED_BORDER)
        self.AddStyle("wxSTATIC_BORDER",                        wx.STATIC_BORDER)
        self.AddStyle("wxNO_BORDER",                            wx.NO_BORDER)
        self.AddStyle("wxTRANSPARENT_WINDOW",           wx.TRANSPARENT_WINDOW)
        self.AddStyle("wxWANTS_CHARS",                          wx.WANTS_CHARS)
        self.AddStyle("wxNO_FULL_REPAINT_ON_RESIZE",wx.NO_FULL_REPAINT_ON_RESIZE)

#               self.AddWindowStyles();

    # This method and the next one are required for XmlResourceHandlers
    def CanHandle(self, node):
        id = node.GetPropVal('name', '')
        if id:
            self.ids.append(id)
            debug.info("\t%s\t%s" % (node.GetPropVal('class', ''), id))
        return self.IsOfClass(node, self.classname)

    def DoCreateResource(self):

        debug.info("[Resource] class %s 's object..." % self.GetName())

        # Now create the object
        if issubclass(self.winclass, wx.Dialog):
            obj = self.winclass(self.parentwin,
                    self.GetID(),
                    self.GetText('title'),
                    self.GetPosition(),
                    self.GetSize(),
                    self.GetStyle()
                    )
        elif issubclass(self.winclass, wx.Frame):
            obj = self.winclass(self.parentwin,
                    self.GetID(),
                    self.GetText('title'),
                    self.GetPosition(),
                    self.GetSize(),
                    self.GetStyle()
                    )
        elif issubclass(self,winclass, wx.Panel):
            obj = self.winclass(self.parentwin,
                    self.GetID(),
                    self.GetPosition(),
                    self.GetSize(),
                    self.GetStyle(),
                    self.GetName(),
                    )

        # These two things should be done in either case:
        # Set standard window attributes
        self.SetupWindow(obj)
        # Create any child windows of this node
        self.CreateChildren(obj)

        # Create IDs
        for id in self.ids:
            setattr(obj, id, XRCID(id))
            setattr(obj, 'obj_'+id, self.parentwin.FindWindowById(XRCID(id)))

        # Call object init
        obj.init(*self.args, **self.kwargs)

        self.obj = obj

        return obj
