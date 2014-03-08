#   Programmer: limodou
#   E-mail:     limodou@gmail.com
#
#   Copyleft 2006 limodou
#
#   Distributed under the terms of the GPL (GNU Public License)
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
#   Update
#   2008/08/27
#       * Fix the result of dir, openfile, savefile will be converted to '/'

import wx
from EasyList import EasyList
from wx.lib.intctrl import IntCtrl
from EasyUtils import *
from IElement import IElement
from EasyGlobal import element_register
import os

class EasyIntElement(IElement):
    def __init__(self, parent, value, message='', externinfo=None, size=(-1, -1), enabledflag=None):
        """create an Int input control

        @type value: number or string
        @para m value: initial value
        @type externinfo: tuple or list
        @param externinfo: {"min":0, "max":100}
        @type size: tuple
        @param size: control's size
        """
        IElement.__init__(self, parent, 'int', message, externinfo, size, enabledflag)

        if not isinstance(value, int):
            try:
                value = int(value)
            except ValueError:
                value = 0

        if externinfo:
            obj = wx.SpinCtrl(parent, min=externinfo["min"], max=externinfo["max"])
        else:
            obj = IntCtrl(parent)
        self.obj = obj
        self.setValue(value)

    def setValue(self, value):
        if not value:
            value = 0
        self.obj.SetValue(value)

    def getValue(self):
        return self.obj.GetValue()

element_register('int', EasyIntElement)

class EasyBoolElement(IElement):
    def __init__(self, parent, value, message='', externinfo=None, size=(-1, -1), enabledflag=None):
        """create an Bool input control

        @type value: number or string
        @para m value: initial value
        @type externinfo: None
        @param externinfo: not used
        @type size: tuple
        @param size: control's size
        """
        IElement.__init__(self, parent, 'bool', message, externinfo, size, enabledflag)

        if isinstance(value, (str, unicode)):
            if value.lower() in ['y', '1', 'yes', 'ok']:
                value = True
            else:
                value = False
        else:
            value = value

        obj = wx.CheckBox(parent, -1, '')
        self.obj = obj
        self.setValue(value)

    def setValue(self, value):
        if not value:
            value = False
        self.obj.SetValue(value)

    def getValue(self):
        return self.obj.GetValue()

    def getAlignFlag(self, flag):
        flag |= wx.EXPAND
        return flag

element_register('bool', EasyBoolElement)

class EasySingleElement(IElement):
    def __init__(self, parent, value, message='', externinfo=None, size=(-1, -1), enabledflag=None):
        """create an Single input control

        @type value: number or string
        @para m value: initial value
        @type externinfo: list or tuple or dict
        @param externinfo: choice value may be ('one', 'two'),
        @type size: tuple
        @param size: control's size
        """
        IElement.__init__(self, parent, 'single', message, externinfo, size, enabledflag)

        if not externinfo:
            raise EasyException, 'Externinfo value cannot be None. You should supply a externinfo value list or tuple or dict'
        if not isinstance(externinfo, (list, tuple, dict)):
            raise EasyException, 'You should supply a externinfo value list or tuple or dict'

        if isinstance(externinfo, (list, tuple)):
            if isinstance(externinfo[0], (list, tuple)):
                value_dict = dict(externinfo)
                value_list = [x[0] for x in externinfo]
            else:
                value_list = externinfo
                value_dict = dict(zip(externinfo, externinfo))
        else:
            value_dict = externinfo
            value_list = sorted(externinfo.keys())

        self.value_dict = value_dict
        self.value_list = value_list
        obj = wx.ComboBox(parent, -1, '', choices = value_list, style = wx.CB_DROPDOWN|wx.CB_READONLY )
        key = [k for k, v in value_dict.items() if v == value][0]
        self.obj = obj
        self.setValue(key)

    def setValue(self, value):
        if not value:
            value = self.value_list[0]
        self.obj.SetValue(value)

    def getValue(self):
        value = self.obj.GetValue()
        return self.value_dict[value]

element_register('single', EasySingleElement)

class EasyStringElement(IElement):
    def __init__(self, parent, value, message='', externinfo=None, size=(-1, -1), enabledflag=None):
        """create an String input control

        @type value: number or string
        @para m value: initial value
        @type externinfo: None
        @param externinfo: not used
        @type size: tuple
        @param size: control's size
        """
        IElement.__init__(self, parent, 'string', message, externinfo, size, enabledflag)

        obj = wx.TextCtrl(parent, -1, value)
        self.obj = obj
        #self.setValue(value)

    def setValue(self, value):
        if not value:
            value = ''
        self.obj.SetValue(value)

    def getValue(self):
        return self.obj.GetValue()

    def getAlignFlag(self, flag):
        flag |= wx.EXPAND
        return flag

element_register('string', EasyStringElement)

class EasyPasswordElement(EasyStringElement):
    def __init__(self, parent, value, message='', externinfo=None, size=(-1, -1), enabledflag=None):
        """create an Password input control

        @type value: number or string
        @para m value: initial value
        @type externinfo: None
        @param externinfo: not used
        @type size: tuple
        @param size: control's size
        """
        IElement.__init__(self, parent, 'password', message, externinfo, size, enabledflag)

        obj = wx.TextCtrl(parent, -1, value, style=wx.TE_PASSWORD)
        self.obj = obj
        #self.setValue(value)

element_register('password', EasyPasswordElement)

class EasyLinesElement(IElement):
    def __init__(self, parent, value, message='', externinfo=None, size=(-1, -1), enabledflag=None):
        """create an Lines input control

        @type value: number or string
        @para m value: initial value
        @type externinfo: None
        @param externinfo: not used
        @type size: tuple
        @param size: control's size
        """
        IElement.__init__(self, parent, 'lines', message, externinfo, size, enabledflag)

        self.box = wx.BoxSizer(wx.VERTICAL)
        if message:
            self.box.Add(wx.StaticText(parent, -1, message), 0, wx.EXPAND|wx.BOTTOM, border=3)
        obj = wx.TextCtrl(parent, -1, value, style=wx.TE_MULTILINE)
        self.box.Add(obj, 1, wx.EXPAND, border=0)

        self.obj = obj
        #self.setValue(value)

    def setValue(self, value):
        if not value:
            value = ''
        self.obj.SetValue(value)

    def getValue(self):
        return self.obj.GetValue()

    def isLarge(self):
        return True

    def getContainer(self):
        return self.box

element_register('lines', EasyLinesElement)

class EasyStaticElement(IElement):
    def __init__(self, parent, value, message='', externinfo=None, size=(-1, -1), enabledflag=None):
        """create an Static input control

        @type value: number or string
        @para m value: initial value
        @type externinfo: None
        @param externinfo: not used
        @type size: tuple
        @param size: control's size
        """
        IElement.__init__(self, parent, 'static', message, externinfo, size, enabledflag)

        obj = wx.StaticText(parent, -1, value)

        self.obj = obj
        #self.setValue(value)

    def setValue(self, value):
        if not value:
            value = ''
        self.obj.SetLabel(value)

    def getValue(self):
        return self.obj.GetLabel()

    def getAlignFlag(self, flag):
        return wx.ALIGN_CENTER_VERTICAL

element_register('static', EasyStaticElement)

class EasyListElement(IElement):
    def __init__(self, parent, value, message='', externinfo=None, size=(-1, -1), enabledflag=None):
        """create an List input control

        @type value: number or string
        @para m value: initial value
        @type externinfo: None
        @param externinfo: not used
        @type size: tuple
        @param size: control's size
        """
        IElement.__init__(self, parent, 'list', message, externinfo, size, enabledflag)

        self.box = wx.BoxSizer(wx.VERTICAL)
        if message:
            self.box.Add(wx.StaticText(parent, -1, message), 0, wx.EXPAND)
        obj = EasyList(parent, externinfo, value)
        self.box.Add(obj, 1, wx.EXPAND, border=0)

        self.obj = obj
#        self.setValue(value)

    def setValue(self, value):
        if not value:
            value = []
        self.obj.SetValue(value)

    def getValue(self):
        return self.obj.GetValue()

    def isLarge(self):
        return True

    def getContainer(self):
        return self.box

element_register('list', EasyListElement)

class EasyFloatElement(IElement):
    def __init__(self, parent, value, message='', externinfo=None, size=(-1, -1), enabledflag=None):
        """create an Float input control

        @type value: number or string
        @para m value: initial value
        @type externinfo: None
        @param externinfo: not used
        @type size: tuple
        @param size: control's size
        """
        IElement.__init__(self, parent, 'float', message, externinfo, size, enabledflag)

        from EasyFloat import FloatCtl
        obj = FloatCtl(parent, value)

        self.obj = obj
        #self.setValue(value)

    def setValue(self, value):
        if not value:
            value = 0.0
        self.obj.SetValue(value)

    def getValue(self):
        return self.obj.GetValue()

element_register('float', EasyFloatElement)

class EasyDateElement(IElement):
    def __init__(self, parent, value, message='', externinfo=None, size=(-1, -1), enabledflag=None):
        """create an Date input control

        @type value: string
        @para m value: initial value (yyyy-mm-dd)
        @type externinfo: None
        @param externinfo: not used
        @type size: tuple
        @param size: control's size
        """
        IElement.__init__(self, parent, 'date', message, externinfo, size, enabledflag)

        obj = wx.DatePickerCtrl(parent, size=(120,-1), style=wx.DP_DROPDOWN | wx.DP_SHOWCENTURY)
        self.obj = obj

        self.setValue(value)

    def setValue(self, value):
        import time

        if not value:
            date = wx.DateTimeFromTimeT(time.time())
        else:
            d = time.strptime(value, "%Y-%m-%d")
            date = wx.DateTimeFromTimeT(time.mktime(d))
        self.obj.SetValue(date)

    def getValue(self):
        date = self.obj.GetValue()
        return date.FormatISODate()

element_register('date', EasyDateElement)

class EasyTimeElement(IElement):
    def __init__(self, parent, value, message='', externinfo=None, size=(-1, -1), enabledflag=None):
        """create an Time input control

        @type value: string
        @para m value: initial value (hh:mm:ss)
        @type externinfo: None
        @param externinfo: not used
        @type size: tuple
        @param size: control's size
        """
        IElement.__init__(self, parent, 'time', message, externinfo, size, enabledflag)

        import wx.lib.masked as masked

        obj = masked.TimeCtrl(parent, -1, name="timectrl", fmt24hr=True)
        h = obj.GetSize().height
        spin2 = wx.SpinButton(parent, -1, wx.DefaultPosition, size=(-1, h), style=wx.SP_VERTICAL)
        obj.BindSpinButton(spin2)
        self.box = wx.BoxSizer( wx.HORIZONTAL )
        self.box.Add( obj, 0, wx.ALIGN_CENTRE )
        self.box.Add( spin2, 0, wx.ALIGN_CENTRE )

        self.obj = obj

        self.setValue(value)

    def setValue(self, value):
        import time

        if not value:
            date = wx.DateTimeFromTimeT(time.time())
        else:
            d = time.strptime(value, "%H:%M:%S")
            date = wx.DateTimeFromTimeT(time.mktime(d))
        self.obj.SetValue(date)

    def getValue(self):
        return self.obj.GetValue()

    def getContainer(self):
        return self.box

element_register('time', EasyTimeElement)

class EasyOpenFileElement(IElement):
    def __init__(self, parent, value, message='', externinfo=None, size=(-1, -1), enabledflag=None):
        """create an OpenFile input control

        @type value: string
        @para m value: initial value
        @type externinfo: None
        @param externinfo: not used
        @type size: tuple
        @param size: control's size
        """
        IElement.__init__(self, parent, 'openfile', message, externinfo, size, enabledflag)

        import EasyFileBtnCtrl as filebrowse

        obj = filebrowse.FileBrowseButton(parent, -1, labelText='', buttonText="...")

        self.obj = obj

        self.setValue(value)

    def setValue(self, value):
        if not value:
            value = ''
        self.obj.SetValue(value)

    def getValue(self):
        return os.path.normpath(self.obj.GetValue())

    def getAlignFlag(self, flag):
        flag |= wx.EXPAND
        return flag

element_register('openfile', EasyOpenFileElement)

class EasySaveFileElement(IElement):
    def __init__(self, parent, value, message='', externinfo=None, size=(-1, -1), enabledflag=None):
        """create an SaveFile input control

        @type value: string
        @para m value: initial value
        @type externinfo: None
        @param externinfo: not used
        @type size: tuple
        @param size: control's size
        """
        IElement.__init__(self, parent, 'savefile', message, externinfo, size, enabledflag)

        import EasyFileBtnCtrl as filebrowse

        obj = filebrowse.FileBrowseButton(parent, -1, labelText='', buttonText="...", fileMode = wx.SAVE)

        self.obj = obj

        self.setValue(value)

    def setValue(self, value):
        if not value:
            value = ''
        self.obj.SetValue(value)

    def getValue(self):
        return os.path.normpath(self.obj.GetValue())

    def getAlignFlag(self, flag):
        flag |= wx.EXPAND
        return flag

element_register('savefile', EasyOpenFileElement)

class EasyDirElement(IElement):
    def __init__(self, parent, value, message='', externinfo=None, size=(-1, -1), enabledflag=None):
        """create an Dir input control

        @type value: string
        @para m value: initial value
        @type externinfo: None
        @param externinfo: not used
        @type size: tuple
        @param size: control's size
        """
        IElement.__init__(self, parent, 'dir', message, externinfo, size, enabledflag)

        import EasyFileBtnCtrl as filebrowse

        obj = filebrowse.DirBrowseButton(parent, -1, labelText='', buttonText="...")

        self.obj = obj

        self.setValue(value)

    def setValue(self, value):
        if not value:
            value = ''
        self.obj.SetValue(value)

    def getValue(self):
        return os.path.normpath(self.obj.GetValue())

    def getAlignFlag(self, flag):
        flag |= wx.EXPAND
        return flag

element_register('dir', EasyDirElement)

class EasyMultiElement(IElement):
    def __init__(self, parent, value, message='', externinfo=None, size=(-1, -1), enabledflag=None):
        """create an Multi input control

        @type value: []
        @para m value: initial value
        @type externinfo: None
        @param externinfo: not used
        @type size: tuple
        @param size: control's size
        """
        IElement.__init__(self, parent, 'multi', message, externinfo, size, enabledflag)

        if not externinfo:
            raise EasyException, 'Externinfo value cannot be None. You should supply a externinfo value list or tuple or dict'
        if not isinstance(externinfo, (list, tuple, dict)):
            raise EasyException, 'You should supply a externinfo value list or tuple or dict'

        if isinstance(externinfo, (list, tuple)):
            if isinstance(externinfo[0], (list, tuple)):
                value_dict = dict(externinfo)
                value_list = [x[0] for x in externinfo]
            else:
                value_list = externinfo
                value_dict = dict(zip(externinfo, externinfo))
        else:
            value_dict = externinfo
            value_list = sorted(externinfo.keys())

        self.value_list = value_list
        self.value_dict = value_dict
        obj = wx.CheckListBox(parent, -1, choices = value_list, size=size)
        self.obj = obj

        self.setValue(value)

    def setValue(self, value):
        if not value:
            value = []
        for i, k in enumerate(self.value_list):
            if self.value_dict[k] in value:
                self.obj.Check(i)
            else:
                self.obj.Check(i, False)

    def getValue(self):
        value = []
        for i, k in enumerate(self.value_list):
            if self.obj.IsChecked(i):
                value.append(self.value_dict[k])

        return value

element_register('multi', EasyMultiElement)

class EasyRichListElement(IElement):
    def __init__(self, parent, value, message='', externinfo=None, size=(-1, -1), enabledflag=None):
        """create an RichList input control

        @type value: number or string
        @para m value: initial value
        @type externinfo: None
        @param externinfo: not used
        @type size: tuple
        @param size: control's size
        """
        IElement.__init__(self, parent, 'richlist', message, externinfo, size, enabledflag)

        from EasyRichList import EasyRichList

        self.box = wx.BoxSizer(wx.VERTICAL)
        if message:
            self.box.Add(wx.StaticText(parent, -1, message), 0, wx.EXPAND)
        obj = EasyRichList(parent, externinfo, value)
        self.box.Add(obj, 1, wx.EXPAND, border=0)

        self.obj = obj

    def setValue(self, value):
        if not value:
            value = []
        self.obj.SetValue(value)

    def getValue(self):
        return self.obj.GetValue()

    def isLarge(self):
        return True

    def getContainer(self):
        return self.box

element_register('richlist', EasyRichListElement)
