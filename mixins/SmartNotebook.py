import wx

class ring:
    """
    A data structure base on list, but it is a ring
    and support to iterate infinite.
    """
    def __init__(self):
        self._ring = []
        self._pos = 0

    def __len__(self):
        return len(self._ring)

    def __str__(self):
        return str(self._ring)

    def __repr__(self):
        return repr(self._ring)

    def __getitem__(self, key):
        return self._ring[key]

    def __setitem__(self, key, value):
        self._ring[key] = value

    def __getslice__(self, a, b):
        return self._ring[a:b]

    def __setslice__(self, a, b, c):
        self._ring[a:b] = c

    def __eq__(self, a):
        return self._ring == a

    def add(self, data, pos=-1):
        if pos == -1:
            pos = len(self._ring)
        if 0 <= pos <= len(self._ring):
            self._ring.insert(pos, data)
            return pos
        else:
            raise ValueError("pos is out of range")

    def remove(self, pos):
        if -len(self._ring) <= pos < len(self._ring):
            del self._ring[pos]
        else:
            raise ValueError("pos is out of range")

    def find(self, value):
        try:
            return self._ring.index(value)
        except:
            return -1

    def forward(self, offset=1):
        if 0 < len(self._ring):
            self._pos = (self._pos + offset) % len(self._ring)
            return self._ring[self._pos]
        else:
            raise ValueError("no data in ring")

    def backward(self, offset=1):
        return self.forward(-offset)

    def current(self):
        return self.forward(0)

    def move(self, frm, to):
        if 0 <= frm < len(self._ring)\
        and 0 <= to < len(self._ring):
            if frm > to:
                self._ring[to], self._ring[to+1:frm+1] = self._ring[frm], self._ring[to:frm]
            elif frm < to:
                self._ring[to], self._ring[frm:to] = self._ring[frm], self._ring[frm+1:to+1]
        else:
            raise ValueError("frm or to is out of range")


class SmartNotebook(wx.Notebook):
    """
    Extend the wx.Notebook to remember the sequence
    when user switched between tabs.
    For instance,
    1) When initializing a notebook, we have three tabs: A, B, C;
    A is visible, and the sequence is A->B->C.
    i). Press Ctrl-Tab, then highlight tab is switched to B; thus
            the sequence becomes B->A->C.
            Press Ctrl-Tab again, the next tab shoule be A; the sequence
            becomes A->B->C.
    ii). Hold Ctrl, press Tab twice, the highlight Tab is moved to C,
             the sequence becomes C->A->B
    iii). Hold Ctrl, press Tab three times, the highlight Tab is still A.
              the sequence won't be changed.
    2) When adding a new tab, that tab is added to the tail of the existing
    sequence. For example, D is added into the NoteBook; then the new sequence
    is A->B->C->D, if D is selected, D->A->B->C.
    3) When removing a highlight tab, the tab next to it will be highlighten.
    The removed tab must be removed from the sequence.
    In conclusion,
    1) When switching between tabs, the selected tab will be moved to the first
    position.
    2) When adding a new tab, that tab is inserted into header of the sequence
    if it is selected.
    3) When removing a tab, if it is highlight, then next tab is activated.
    """
    def init(self):
        self._ring = ring()
        self._map = []
        self._left = False
        self._ctrl = False
        self._shift = False
        self._ignoreevent = False
        self._setselection = False

    def __init__(self, *args, **kwargs):
        wx.Notebook.__init__(self, *args, **kwargs)

        self.init()

        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.onpagechanging)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onpagechanged)
        self.Bind(wx.EVT_KEY_DOWN, self.onkeydown)
        self.Bind(wx.EVT_KEY_UP, self.onkeyup)
        self.Bind(wx.EVT_LEFT_DOWN, self.onleftdown)
        self.Bind(wx.EVT_LEFT_UP, self.onleftup)

    def onleftup(self, e):
        self._left = False
        e.Skip()

    def onleftdown(self, e):
        self._left = True
        e.Skip()

    def onkeydown(self ,e):
        self._ctrl = e.ControlDown()
        self._shift = e.ShiftDown()
        e.Skip()

    def onkeyup(self, e):
        if self._ctrl and not e.ControlDown():
            self._ring.move(self._map[self.GetSelection()], 0)
            self.refreshmap()
            self._ring._pos = 0
        self._ctrl = e.ControlDown()
        self._shift = e.ShiftDown()
        e.Skip()

    def onpagechanging(self ,e):
        if not self._setselection and not self._ignoreevent and not self._left:
            # Consider such a condition:
            # The page is a text ctrl and owns the focus, the ctrl down
            # message is handle by it, thus NoteBook doesn't catch that
            # event.
            #
            # set _ctrl, _shift manually if _ctrl is false
            if not self._ctrl:
                self._ctrl = True
                self._shift = \
                    e.GetSelection()==(e.GetOldSelection()-1)%self.GetPageCount()
            if not self._shift:
                select = self._ring.forward()
            else:
                select = self._ring.backward()
            e.Veto()
            self._ignoreevent = True
            self._SetSelection(select)
        else:
            e.Skip()

    def forward(self):
        select = self._ring.forward()
        self._SetSelection(select)

    def backward(self):
        select = self._ring.backward()
        self._SetSelection(select)

    def onpagechanged(self, e):
        if not self._ignoreevent:
            self._ring.move(self._map[e.GetSelection()], 0)
            self.refreshmap()
            self._ring._pos = 0
        else:
            self._ignoreevent = False
        e.Skip()

    def AddPage(*args, **kwargs):
        """
        Add the index of the tab to header of the sequence
        if it is selected; otherwise add it to the tail.
        """
        self = args[0]
        self._ignoreevent = True
        rt = wx.Notebook.AddPage(*args, **kwargs)
        self._ignoreevent = False
        if rt and 0 < len(args):
            self.addtotail(self.GetPageCount()-1)
            select = False
            if 3 < len(args):
                select = args[3]
            elif kwargs.has_key("select"):
                select = kwargs["select"]
            if select:
                self.select(self.GetPageCount()-1)
                self._SetSelection(self.GetPageCount()-1) #force the notebook to update
        return rt;

    def InsertPage(*args, **kwargs):
        self = args[0]
        self._ignoreevent = True
        rt = wx.Notebook.InsertPage(*args, **kwargs)
        self._ignoreevent = False
        if rt and 1 < len(args):
            args[0].addtotail(args[1])
            select = False
            if 4 < len(args):
                select = args[4]
            elif kwargs.has_key("select"):
                select = kwargs["select"]
            if select:
                self.select(args[1])
                self._SetSelection(args[1]) #force the notebook to update
            else:
                self.select(self.GetSelection())
        return rt

    def addtotail(self, newindex):
        # update the existing ring
        for i in range(len(self._ring._ring)):
            if self._ring._ring[i] >= newindex: self._ring._ring[i]+=1
        # add the new index to the tail of ring
        self._ring.add(newindex)
        # Refresh the map
        self.refreshmap()

    def refreshmap(self):
        for i in range(len(self._map), len(self._ring)):
            self._map.append(0) # append trivial number to increase the size
        for i in self._ring._ring:
            self._map[self._ring._ring[i]] = i

    def select(self, index):
        self._ring.move(self._map[index], 0)
        self._ring._pos = 0
        self.refreshmap()

    def printring(self):
        print self._ring

    def DeletePage(*args, **kwargs):
        args[0]._setselection = True
        rt = wx.Notebook.DeletePage(*args, **kwargs)
        args[0]._setselection = False
        if rt and 1 < len(args):
            args[0].deletepage(args[1])
        return rt

    def RemovePage(*args, **kwargs):
        args[0]._setselection = True
        rt = wx.Notebook.RemovePage(*args, **kwargs)
        args[0]._setselection = False
        if rt and 1 < len(args):
            args[0].deletepage(args[1])
        return rt

    def DeleteAllPages(*args, **kwargs):
        args[0]._setselection = True
        rt = wx.Notebook.DeleteAllPages(*args, **kwargs)
        args[0]._setselection = False
        if rt:
            args[0].init()
        return rt

    def AdvanceSelection(*args, **kwargs):
        args[0]._setselection = True
        rt = wx.Notebook.AdvanceSelection(*args, **kwargs)
        args[0]._setselection = False
        return rt

    def SetSelection(*args, **kwargs):
        args[0]._setselection = True
        rt = wx.Notebook.SetSelection(*args, **kwargs)
        args[0]._setselection = False
        return rt

    def _SetSelection(*args, **kwargs):
        return wx.Notebook.SetSelection(*args, **kwargs)

    def deletepage(self, tabindex):
        if 0 <= tabindex <= self.GetPageCount():
            self._ring.remove(self._ring.find(tabindex))
            for i in range(len(self._ring)):
                if self._ring[i] > tabindex: self._ring[i] -= 1
            self.refreshmap()
