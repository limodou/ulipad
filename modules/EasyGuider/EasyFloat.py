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

import wx
import string

class FloatValidator(wx.PyValidator):
    def __init__(self, minimum=None, maximum=None,
                       minstrict=True, maxstrict=True,
                       zero=True,
                       valid=wx.Colour(red=255,green=255,blue=255),
                       invalid=wx.Colour(red=216,green=191,blue=216)):
        wx.PyValidator.__init__(self)

        self.minimum = minimum
        self.maximum = maximum
        if self.minimum >= self.maximum:
            self.maximum = None
        self.minstrict = minstrict
        self.maxstrict = maxstrict
        self.zero = zero
        self.valid = valid
        self.invalid = invalid
        self.stringList = string.digits + '-.'

        wx.EVT_CHAR(self, self.OnChar)

    def Clone(self):
        return FloatValidator(self.minimum, self.maximum,
                              self.minstrict, self.maxstrict,
                              self.zero,
                              self.valid, self.invalid)

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

    def Validate(self, win):
        tc = self.GetWindow()
        val = tc._getValue()
        #print val
        if tc.IsEnabled() and val == '':
            tc.SetBackgroundColour(self.invalid)
            tc.Refresh()
            return False
        elif tc.IsEnabled() and val != '':
            for x in val:
                if x not in self.stringList:
                    tc.SetBackgroundColour(self.invalid)
                    tc.Refresh()
                    return False
            if not self.IsInRange(float(val)):
                tc.SetBackgroundColour(self.invalid)
                tc.Refresh()
                return False

        tc.SetBackgroundColour(self.valid)
        tc.Refresh()

        return True

    def OnChar(self, event):
        key = event.GetKeyCode()
        tc = self.GetWindow()
        val = tc._getValue()
        inpoint = tc.GetInsertionPoint()

        if key == 8:
            if inpoint == 0:
                event.Skip()
                return
            elif inpoint == len(val):
                number = val[:-1]
                if number in ['', '-', '.']:
                    tc.SetBackgroundColour(self.invalid)
                    tc.Refresh()
                    event.Skip()
                    return
                else:
                    number = float(number)

                if self.IsInRange(number) == 1:
                    tc.SetBackgroundColour(self.valid)
                    tc.Refresh()
                    event.Skip()
                    return
                elif self.IsInRange(number) == 0:
                    tc.SetBackgroundColour(self.invalid)
                    tc.Refresh()
                    event.Skip()
                    return
            else:
                val1 = val[:inpoint-1]
                val2 = val[inpoint:]
                number = float(val1 + val2)

                if self.IsInRange(number) == 1:
                    tc.SetBackgroundColour(self.valid)
                    tc.Refresh()
                    event.Skip()
                    return
                elif self.IsInRange(number) == 0:
                    tc.SetBackgroundColour(self.invalid)
                    tc.Refresh()
                    event.Skip()
                    return

        if key == wx.WXK_DELETE:
            if inpoint == 0:
                number = val[1:]
                if number in ['', '-', '.']:
                    tc.SetBackgroundColour(self.invalid)
                    tc.Refresh()
                    event.Skip()
                    return
                else:
                    number = float(number)

                if self.IsInRange(number) == 1:
                    tc.SetBackgroundColour(self.valid)
                    tc.Refresh()
                    event.Skip()
                    return
                elif self.IsInRange(number) == 0:
                    tc.SetBackgroundColour(self.invalid)
                    tc.Refresh()
                    event.Skip()
                    return
            elif inpoint == len(val):
                event.Skip()
                return
            else:
                val1 = val[:inpoint]
                val2 = val[inpoint+1:]
                number = float(val1 + val2)

                if self.IsInRange(number) == 1:
                    tc.SetBackgroundColour(self.valid)
                    tc.Refresh()
                    event.Skip()
                    return
                elif self.IsInRange(number) == 0:
                    tc.SetBackgroundColour(self.invalid)
                    tc.Refresh()
                    event.Skip()
                    return

        if key < wx.WXK_SPACE or key > 255:
            event.Skip()
            return

        if chr(key) == '.':
            if inpoint == 0:
                event.Skip()
                return
            elif inpoint == len(val) and '.' not in val:
                event.Skip()
                return
            elif '.' not in val:
                event.Skip()
                return

        if chr(key) == '-':
            if inpoint == 0 and self.minimum < 0:
                event.Skip()
                return

        if chr(key) in string.digits:
            if inpoint == 0:
                number = float(chr(key) + val)
            elif inpoint == len(val):
                number = float(val + chr(key))
            else:
                val1 = val[:inpoint]
                val2 = val[inpoint:]
                number = float(val1 + chr(key) + val2)

            if self.IsInRange(number) == 1:
                tc.SetBackgroundColour(self.valid)
                tc.Refresh()
                event.Skip()
                return
            elif self.IsInRange(number) == 0:
                tc.SetBackgroundColour(self.invalid)
                tc.Refresh()
                event.Skip()
                return

        return

    def IsInRange(self, num):
        if self.minimum is None and self.maximum is None:
            return 1
        elif self.minimum is None and self.maximum is not None:
            return num <= self.maximum
        elif self.minimum is not None and self.maximum is None:
            return num >= self.miminum
        if num == 0.0 and not self.zero and self.minstrict:
            return -1
        elif num == 0.0 and not self.zero and not self.minstrict:
            return 0
        elif self.minimum <= num <= self.maximum:
            return 1
        elif (num < self.minimum and not self.minstrict) or \
             (num > self.maximum and not self.maxstrict):
            return 0

class FloatCtl(wx.TextCtrl):
    def __init__(self, parent, value, minimum=None, maximum=None, minstrict=False, maxstrict=False, zero=True):
        self.minimum = minimum
        self.maximum = maximum
        self.minstrict = minstrict
        self.maxstrict = maxstrict
        self.zero = zero
        flt = FloatValidator(minimum=minimum, maximum=minimum, minstrict=minstrict, maxstrict=minstrict, zero=zero)
        if not isinstance(value, float):
            wx.TextCtrl.__init__(self, parent, -1, value, validator=flt)
        else:
            wx.TextCtrl.__init__(self, parent, -1, str(value), validator=flt)
        self._getValue = self.GetValue
        self.GetValue = self._getValue
        self.SetValue = self._SetValue

    def _GetValue(self):
        text = wx.TextCtrl.GetValue(self)
        return float(text)

    def _SetValue(self, value):
        if not isinstance(value, float):
            wx.TextCtrl.SetValue(self, value)
        else:
            wx.TextCtrl.SetValue(self, str(value))
