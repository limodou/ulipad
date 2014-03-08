#!/usr/bin/env python
#   Programmer: limodou
#   E-mail:     limodou@gmail.com
#
#   Copyleft 2007 limodou
#
#   Distributed under the terms of the GPLv3 (GNU Public License)
#
#   meide is free software; you can redistribute it and/or modify
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

import wx

DEBUG = False

#############################################
# event mapping
# they'll be used in bind() and binds() methods
# if you pass a event which doesn't in this mapping dict, then
# meide will use it directly. So you can pass a real event object
# just like wx.EVT_BUTTON to bind() and binds() methods
#############################################

eve_mapping = {
    'click':wx.EVT_BUTTON,
    'check':wx.EVT_CHECKBOX,
    'change':wx.EVT_TEXT,
    'enter':wx.EVT_TEXT_ENTER,
}

class ImplementException(Exception): pass
class UnsupportException(Exception): pass
class ValidateFailException(Exception): pass
class ErrorException(Exception): pass

#############################################
# common function
#############################################

def create(win, layout, fit=1, namebinding=None):
    """
    build layout and all sub-elements.
    win is target window object, and layout will be applied to it
    fit == 0 will not change the window size
        == 1 will change height size to best size
        == 2 will change width and height both size to best size
    """
    layout.create(win, namebinding)
    win.SetSizer(layout.obj)
    win.SetAutoLayout(True)
    if fit == 1:
        win.SetSize((win.GetSize()[0], win.GetBestSize()[1]))
    elif fit == 2:
        win.SetSize(win.GetBestSize())

def simple_buttons(buttons=None):
    """
    buttons is a tuple list, each element should be:
        ('caption', id, 'name')
    if buttons is None, then the buttons will be default 'OK' and 'Cancel'
    """
    if not buttons:
        buttons = [('OK', wx.ID_OK, 'btnOk'), ('Cancel', wx.ID_CANCEL, 'btnCancel')]
    h = HBox()
    for caption, id, name in buttons:
        h.add(Button(caption, id=id), name=name)
    return h

def DefaultValidateCallback(message):
    """
    Default callback function. When validator failed, and user doesn't define a
    callback function, this function will be invoked.
    """
    wx.MessageBox(message, "Validate Error")

#############################################
# Elements class definition
#############################################

def _bind_name(f):
    """
    Binding an element or its underlying wx widget to window object, so that you 
    can use win.name to visit the element or its underlying wx widget. It 
    equals layout.find(name) and layout.find(name).get_widget(). It supports two
    fashion: element binding and widget binding, so you should carefully use them.
    
    namebinding could be 'element' or 'widget' or None, if the value is 'element', then
    bind the element to window object and if the value is 'widget', then bind
    the underlying widget to window object
    """
    def _f(self, win, namebinding=None):
        r = f(self, win, namebinding)
        if not namebinding:
            return r
        if namebinding not in ('element', 'widget'):
            raise ErrorException('The namebinding parameter must be "element" or "widget".')
        if self.name and not self.name.startswith('_id'):
            if namebinding == 'element':
                setattr(win, self.name, self)
            else:
                setattr(win, self.name, self.get_widget())
        return r
    return _f

def _print_flag(flag):
    flags = [(wx.LEFT, 'left'), (wx.RIGHT, 'right'),
        (wx.TOP, 'top'), (wx.BOTTOM, 'bottom'),
        (wx.ALL, 'all'), (wx.ALIGN_CENTER, 'align_center'),
        (wx.ALIGN_CENTER_HORIZONTAL, 'align_center_horizontal'),
        (wx.ALIGN_CENTER_VERTICAL, 'align_center_vertical')]
    s = []
    for f, v in flags:
        if flag & f == f:
            s.append(v)
    return ','.join(s)

def _p(*args):
    if DEBUG:
        for i in args:
            print i,
        print
        
class Element(object):
    """
    Base class of all meide elements
    It has some class attributs:
        
        proportion 
            if you don't specify a proportion value in add() function, then
            meide will use this proportion. And if you indicate a size parameter in 
            one element, for example, Button('OK', size=(80, -1)). meide will match
            this proportion and size to guess the real proportion and EXPAND flag option
            
            (0, 0) will not change the size of current element
            (-1, 0) will auto expand the height for VBox, may expand the width for HBox
            (0, -1) will auto exapnd the width for VBox, may expand the height for HBox
            (-1, -1) will auto exapnd the width and height
            
        has_value
            if a element can be set a value and return a value, you can set `has_value`
            as `True`. If `has_value` is `True`, the Element class must implement 
            SetValue() and GetValue() functions.
            
        default_kwargs
            All meide element corresponding a real wx widget class, for example:
            Label => wx.StaticText, Button => wx.Button, so when you defining a meide
            Element, you can also pass other parameters defined in wx widget constructor
            function to meide Element constructor function. And for some reasons,
            you may want to set some default parameters to the wx widgets constructor,
            then you can define this attribute, so that when meide begins to create
            the instance of the Element, it will pass these default_kwargs also 
            to the constructor function. And user can override them through passing
            the same parameters in the Element contructor function.
                
    """
    proportion = (0, 0)
    has_value = False
    default_kwargs = {}
    
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        self.args = args
        self.obj = None
        self.widget = None
        self.events = []
        self.win = None
        self.name = ''
        self.tip = ''
        self.attr_size = None
        self.created = False
        
    def _create_obj(self, win):
        """
        Private function. All child Element class must to implement this function, 
        and this function need to return a real underlying wx widget object.
        """
        raise ImplementException('Unimplemented')
    
    @_bind_name
    def create(self, win, namebinding=None):
        """
        This function will really create the underlying wx widgets according the 
        element class type, then binding the events to it. And it'll extrace `size` 
        parameter from the `kwargs`, then meide will use it later to match with 
        `proportion` class attribute
        
        `win` is the window object where you want to put elements on
        
        After you invoke it, the underlying widgets of elements will really be
        created.
        """
        _p('>>> Create', self.__class__.__name__)
        #create object
        if self.win is win:
            if self.created: return self
        else:
            self.created = False
        self.win = win
        self.obj = obj = self._create_obj(win)
        
        #set external attributes
        if 'size' in self.kwargs:
            self.attr_size = self.kwargs['size']
        elif hasattr(self, 'size'):
            self.attr_size = self.size
        
        self._do_bind()
        self._set_tooltip()
        self.created = True
        return self
    
    def GetValue(self):
        """
        Return the value of current element. And `has_value` attribute of this element
        must be `True`.
        """
        if self.has_value:
            return self.get_obj().GetValue()
    
    def SetValue(self, value):
        """
        Set a value to current element. And `has_value` attribute of this element
        must be `True`.
        """
        if self.has_value:
            self.get_obj().SetValue(value)

    def bind(self, event_name, func):
        """
        Bind a single event to current element. 
        
        event_name could be a string name according eve_mapping, and if you pass
        a non-string object, meide will use it directly. And you should know, meide
        will not immediately bind the event to underlying widget, the event binding
        is happened when you invoking create() function. So you must bind event 
        before create() invoke, this is very important.
        
        Bind support lazy binding. So if you'v created the element, when you binding
        an event to a function, the binding is executed immediately. But if not,
        you can bind the event later. And the same process with binds.
        """
        if self.created:
            self._bind_event(event_name, func)
        for i, v in enumerate(self.events):
            eve_name, func = v
            if eve_name == event_name:
                del self.events[i]
                break
        self.events.append((event_name, func))
        return self
        
    def binds(self, *events):
        """
        Bind multiple event at once.
        
        events is a tuple list, it looks like:
            
            (event_name, func), (event_name, func), ...
            
        binds method also support lazy binding.
        """
        for eve in events:
            self.bind(*eve)
        return self
        
    def _set_tooltip(self):
        if self.tip:
            obj = self.get_obj()
            if hasattr(obj, 'SetToolTip'):
                obj.SetToolTip(wx.ToolTip(self.tip))
            else:
                obj = self.get_widget()
                if hasattr(obj, 'SetToolTip'):
                    obj.SetToolTip(wx.ToolTip(self.tip))
        
    def tooltip(self, tip):
        """
        Set a tooltip to an object. And this object must have SetToolTip method.
        """
        self.tip = tip
        if self.created:
            self._set_tooltip()
        return self
    
    def get_obj(self):
        """
        Return the underlying wx widget object. And if the element is a layout Element,
        it'll be a sizer object.
        """
        return self.obj
    
    def get_widget(self):
        """
        Return the real underlying wx widget object. It's different from the get_obj(),
        because you may add a combined widgets as a single object, it will be
        a `object`, but the mainly control maybe one of these sub widgets. And
        meide will use it to invoke SetFocus() and SetBackgroundColour(). They will
        be used in validate process. If the self.widget is None, then it'll use 
        self.obj. So the most cases, the widget and the object are the same. So
        only when you add a combined widget to Element you just need to set widget
        attribute.
        """
        return self.widget or self.obj
    
    def _bind_event(self, eve, func):
        """
        Bind one event to an function
        """
        obj = self.get_widget()
        try:
            if isinstance(eve, str):
                e = eve_mapping[eve]
            else:
                e = eve
        except:
            raise UnsupportException("This event type [%s] doesn't been supported" % eve)
        try:
            e(obj, obj.GetId(), func)
        except:
            e(obj, func)
        
    def _do_bind(self, events=None):
        """
        Private function used to do the real bind work. It'll be invoked in create().
        """
        if not events:
            events = self.events
        for eve, func in events:
            self._bind_event(eve, func)
            
    def _get_kwargs(self, kw):
        """
        Private function used to merge the default kwargs parameters and the user 
        passed parameters in Element contructor function
        """
        kwargs = self.default_kwargs.copy()
        kwargs.update(kw)
        return kwargs

    def _get_proportion(self):
        return self.proportion
    
    def SetFocus(self):
        control = self.get_widget()
        if hasattr(control, 'SetFocus'):
            control.SetFocus()
    
class ValidateMixin(object):
    """
    A mixin class can be used to process validate.
    """
    def __init__(self):
        self.validate_callback = DefaultValidateCallback
        self.validators = []
          
    def register_validate_callback(self, callback):
        """
        If this callback is assigned, then when validate failed, it'll be invoked.
        """
        self.validate_callback = callback
        
    def validate(self):
        """
        Validate current element.
        """
        win = self.get_widget()
        value = self.GetValue()
        for func in self.validators:
            try:
                func(value)
                if hasattr(win, 'SetBackgroundColour'):
                    win.SetBackgroundColour(
                         wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
                if hasattr(win, 'Refresh'):
                    win.Refresh()
            except ValidateFailException, e:
                if self.validate_callback:
                    self.validate_callback(str(e))
                    if hasattr(win, 'SetBackgroundColour'):
                        win.SetBackgroundColour('pink')
                    if hasattr(win, 'SetFocus'):
                        win.SetFocus()
                    if hasattr(win, 'Refresh'):
                        win.Refresh()
                    
                return False
        return True
    
    def validator(self, validator_funcs):
        """
        Add validators to current element object
        """
        self.validators = validator_funcs
        return self
    
class LayoutValidateMixin(ValidateMixin):
    def validate(self):
        """
        Validate the value. You can directly invoke this function. It'll validate
        all elements of it, then validate its own validators. So if there are child
        layout objects, they will be validated first.
        """
        def _validate(layout):
            value = layout.GetValue()
            
            for name in self.orders:
                element = self.elements[name]
                if isinstance(element, ValidateMixin):
                    if not element.validate():
                        return False
            
            
            for func in layout.validators:
                try:
                    func(value)
                except ValidateFailException, e:
                    if self.validate_callback:
                        self.validate_callback(str(e))
                        
                    return False

            return True
        
        return _validate(self)
        
    def validator(self, validator_funcs):
        """
        Add validators to current element object
        """
        self.validators = validator_funcs
        return self
    
class LayoutBase(Element, LayoutValidateMixin):
    """
    Layout class is just a sizer class.
    """
    proportion = (-1, -1)
    has_value = True
    
    def __init__(self, padding=4, namebinding=None, auto_layout=False, *args, **kwargs):
        """
        padding is used as default border value.
        namebinding is a flag, indicate that if binding the element name to a 
        window object after invoke create() method.
        
        namebinding should be 'element', 'widget', None
        """
        Element.__init__(self, *args, **kwargs)
        LayoutValidateMixin.__init__(self)
        
        self.elements = {}
        self.elements_args = {}
        self.orders = []
        self.padding = padding
        self.namebinding = namebinding
        self.auto_layout_flag = auto_layout
        self._id = 0
        
    def _prepare_element(self, element):
        """
        Private function used to wrap an element. If the element is an Element
        class name but not a real Element object, then create it. If the element
        is not a instance of Element, then wrap it as a SimpleElement or 
        SimpleValueElement according whether the element has GetValue() and SetValue()
        functions.
        """
        if isinstance(element, type) and issubclass(element, Element):
            element = element()
        if not isinstance(element, Element):
            if hasattr(element, 'SetValue') and hasattr(element, 'GetValue'):
                element = SimpleValueElement(element)
            else:
                element = SimpleElement(element)
        return element
    
    def add(self, element, name='', proportion=None, flag=None, border=None):
        """
        Add a element to it. 
        
        element
            It could be any Element object, or event Element class name. And you 
            can also pass a real wx widget object. meide will automatically
            wrap it to a SimpleElement or a SimpleValueElement according whether 
            the element has GetValue() and SetValue() functions.
            
        name
            If you don't specify a name parameter, then meide will create one for 
            you. The format is '_id_%d', and %d will automatically increase. So
            every element will have a name, and you can use this name to get the
            element back via find(name).
        
        proportion, flag, border
            Just like the same parameters of sizer class. `propertion` and `flag`
            will effect with `proportion` class attribute.
            
            If they are `None`, then meide will guess the suitable value for them.
            `proportion` via _guess_proportion()
            `flag` via _guess_expand() and _get_flag()
            `border` via padding
                
        add method supports lazy execution. So if you'v created the element, when
        you invoking add() method, the widget which is being added is created
        immediately, but if not, the widget will be created when you invoking
        create() function.
        """
        if not name:
            self._id += 1
            name = '_id_%d' % self._id
        element = self._prepare_element(element)
        self.elements[name] = element
        element.name = name
        args = {'proportion':proportion, 'flag':flag, 'border':border}
        self.elements_args[name] = args
        self.orders.append(name)
        if self.created:
            self._create_element(name, element, args, len(self.orders) - 1)
            self._layout()
        return element
        
    def get_sizer(self):
        """
        If you want to get the sizer object from a layout object, you can use this
        function.
        """
        return self.obj
    
    def _create_sizer(self, win):
        """
        Private function used by child class to create the real wx sizer object.
        """
        raise ImplementException('Unimplemented!')
    
    @_bind_name
    def create(self, win, namebinding=None):
        _p('>>> Create', self.__class__.__name__)
        if namebinding is not None:
            self.namebinding = namebinding
        #create object
        if self.win is win:
            if self.created: return self
        else:
            self.created = False
        self.win = win
        self.obj = obj = self._create_obj(win)
        #create childen widgets
        for i, name in enumerate(self.orders):
            self._create_element(name, self.elements[name], self.elements_args[name],
                i)
        self._do_bind()
        self.created = True
        if self.auto_layout_flag:
            self.auto_layout()
        self._init()
        return self
    
    def _create_element(self, name, element, args, i):
        e = element
        _p('... Create', name, 'type=%s' % element.__class__.__name__, 'pos=%d' % i)
        e.create(self.win, self.namebinding)
        
        #calculate flag
        flag = 0
        if args['flag'] is not None:
            flag = args['flag']
        else:
            if i == 0:
                flag = flag | self._get_flag(0)
            if i == len(self.orders) - 1:
                flag = flag | self._get_flag(1)
            else:
                flag = flag | self._get_flag(2)
            
            flag |= self._guess_expand(e)
            
        #calculate proportion
        proportion = 0
        if args['proportion'] is not None:
            proportion = args['proportion']
        else:
            proportion = self._guess_proportion(e)
            
        #calculate border
        border = self.padding
        if args['border'] is not None:
            border = args['border']
        
        sizer = self.get_sizer()
        #add obj
        self._add_element(self.win, sizer, name, e, args, i, proportion, flag, border)

    def _create_obj(self, win):
        return self._create_sizer(win)
    
    def _add_element(self, win, sizer, name, e, args, i, proportion, flag, border):
        """
        Private function used to add a element object to current layout object.
        Child class can overwrite it.
        """
        _p('parent=%s' % self.name, 'pos=%d' % i, 'name=%s' % name, '[', _print_flag(flag), ']', proportion, border)
        sizer.Add(e.obj, proportion, flag, border)
        
    def _guess_proportion(self, obj):
        """
        Private function used to guess the proportion value, according the `proportion`
        class attribute, `proportion` and `size` parameters in add() function.
        """
        if hasattr(obj, 'attr_size') and obj.attr_size and hasattr(obj, 'proportion'):
            #vertical direction decide the proportion, assume the sizer is vertical
            if obj.attr_size[1] == -1 and obj._get_proportion()[1] == -1:
                return 1
        elif obj._get_proportion()[1] == -1:
            return 1
        return 0
    
    def _guess_expand(self, obj):
        """
        Private function used to guess the EXPAND option, according the `proportion`
        class attribute, and `size` parameters in add() function. It'll be merged
        with `flag` parameter in add() function.
        """
        if hasattr(obj, 'attr_size') and obj.attr_size and hasattr(obj, 'proportion'):
            #vertical direction decide the proportion, assume the sizer is vertical
            if obj.attr_size[0] == -1 and obj._get_proportion()[0] == -1:
                return wx.EXPAND
        elif obj._get_proportion()[0] == -1:
            return wx.EXPAND
        return 0
    
    def SetValue(self, value):
        for name, v in value.items():
            obj = self.find(name)
            if obj and hasattr(obj, 'has_value') and obj.has_value:
                if callable(v):
                    v = v()
                v = obj._validate_value(v)
                obj.SetValue(v)
            
    def GetValue(self):
        d = {}
        for name, obj in self.elements.items():
            if obj.has_value:
                v = obj.GetValue()
                if isinstance(v, dict):
                    if v:
                        d.update(v)
                else:
                    d[name] = v
        return d
    
    def _get_flag(self, pos):
        """
        Private function used to create flag value according the order of the
        processing element
        
        pos == 0 the first element
            == 1 the middle element
            == 2 the last element
        """
        if pos == 0:
            return wx.LEFT | wx.TOP | wx.RIGHT | wx.BOTTOM
        if pos == 1:
            return wx.LEFT | wx.BOTTOM | wx.RIGHT
        else:
            return wx.LEFT | wx.RIGHT | wx.BOTTOM
        
    def bind(self, name, event_name, func):
        if self.created:
            self._bind_event(name, event_name, func)
        
        for i, v in enumerate(self.events):
            n, eve_name, func = v
            if n == name and eve_name == event_name:
                del self.events[i]
                break

        self.events.append((name, event_name, func))
        return self
        
    def binds(self, events):
        for eve in events:
            self.bind(*eve)
        return self
        
    def _bind_event(self, name, eve, func):
        obj = self.find(name).get_widget()
        if obj:
            try:
                if isinstance(eve, str):
                    e = eve_mapping[eve]
                else:
                    e = eve
            except:
                raise UnsupportException("This event type [%s] doesn't been supported" % eve)
            e(obj, obj.GetId(), func)
        
    def _do_bind(self):
        for name, eve, func in self.events:
            self._bind_event(name, eve, func)
        #process elements events
        for e in self.elements.values():
            e._do_bind()

    def find(self, name):
        """
        Return the element object according the name. If there is no such a element
        object existed according to the name, then `None` returned.
        """
        v = self._process(name)
        if not v:
            return None
        else:
            return v[1]
    
    def __contains__(self, name):
        return bool(self.find(name))
    
    def auto_layout(self):
        """
        Just like create() function, it can be used to create layout object immediately
        and automatically set itself as a sizer of the win object.
        """
        self.win.SetSizer(self.get_sizer())
        self.win.SetAutoLayout(True)
        
        self.auto_layout_flag = True
        return self
        
    def auto_fit(self, fit=1):
        if fit == 1:
            self.win.SetSize((self.win.GetSize()[0], self.win.GetBestSize()[1]))
        elif fit == 2:
            self.win.SetSize(self.win.GetBestSize())
        return self
    
    def _layout(self):
        if self.auto_layout_flag:
            self.layout()
            
    def layout(self):
        """
        Just like sizer's Layout() method.
        """
        self.get_sizer().Layout()
        
    def _process(self, name, obj=None):
        """
        Search the name in elements, and return the parent layout and element object.
        """
        if obj is None:
            obj = self
        if name in obj.elements:
            element = obj.elements[name]
            return obj, element
        else:
            for e in obj.elements.values():
                if isinstance(e, LayoutBase):
                    o = self._process(name, e)
                    if o: return o
            
    def hide(self, name):
        v = self._process(name)
        if v:
            layout, element = v
            layout.get_sizer().Hide(element.get_obj())
            self._layout()
            
    def show(self, name):
        v = self._process(name)
        if v:
            layout, element = v
            layout.get_sizer().Show(element.get_obj())
            self._layout()
            
    def remove(self, name):
        v = self._process(name)
        if v:
            layout, element = v
            obj = element.get_obj()
            layout.get_sizer().Detach(obj)
            self._layout()
            del layout.elements[name]
            del layout.elements_args[name]
            layout.orders.remove(name)
            for i, v in enumerate(layout.events[:]):
                n, eve, func = v
                if n == name:
                    del layout.events[i] 
            return obj
    
    def is_shown(self, name):
        if not self.created:
            return False
        
        v = self._process(name)
        if v:
            layout, element = v
            return layout.get_sizer().IsShown(element.get_obj())
        
    def _init(self):
        pass
    
    def SetFocus(self, focus_ctrl_name=None):
        control = None
        if focus_ctrl_name:
            control = self.find(focus_ctrl_name)
        else:
            def get_first_focus_ctrl(layout):
                for name in layout.orders:
                    obj = layout.elements[name]
                    if isinstance(obj, LayoutBase):
                        return get_first_focus_ctrl(obj)
                    elif hasattr(obj.get_widget(), 'SetFocus'):
                        return obj
            control = get_first_focus_ctrl(self)
        if control:
            control = control.get_widget()
            if hasattr(control, 'SetFocus'):
                control.SetFocus()
        
class HBox(LayoutBase):
    """
    Just like wx.BoxSizer(wx.HORIZONTAL)
    """
    
    proportion = (-1, 0)

    def __init__(self, padding=4, namebinding=None, vertical_center=True, *args, **kwargs):
        LayoutBase.__init__(self, padding, namebinding, *args, **kwargs)
        self.vertical_center = vertical_center
        
    def _create_sizer(self, win):
        return wx.BoxSizer(wx.HORIZONTAL)
    
    def _guess_proportion(self, obj):
        if hasattr(obj, 'attr_size') and obj.attr_size and hasattr(obj, 'proportion'):
            if obj.attr_size[0] == -1 and obj._get_proportion()[0] == -1:
                return 1
        elif obj._get_proportion()[0] == -1:
            return 1
        return 0
    
    def _guess_expand(self, obj):
        if hasattr(obj, 'attr_size') and obj.attr_size and hasattr(obj, 'proportion'):
            if obj.attr_size[1] == -1 and obj._get_proportion()[1] == -1:
                return wx.EXPAND
        elif obj._get_proportion()[1] == -1:
            return wx.EXPAND
        return 0
    
    def _get_flag(self, pos):
        flag = 0
        if self.vertical_center:
            flag = wx.ALIGN_CENTER_VERTICAL
        if pos == 0:
            return flag | wx.LEFT | wx.TOP | wx.RIGHT | wx.BOTTOM
        if pos == 1:
            return flag | wx.TOP | wx.BOTTOM | wx.RIGHT
        else:
            return flag | wx.TOP | wx.RIGHT | wx.BOTTOM
            
class VBox(LayoutBase):
    """
    Just like wx.BoxSizer(wx.VERTICAL)
    """
    
    proportion = (-1, -1)
    
    def __init__(self, padding=4, namebinding=None, horizontal_center=False, *args, **kwargs):
        LayoutBase.__init__(self, padding, namebinding, *args, **kwargs)
        self.horizontal_center = horizontal_center
        
    def _create_sizer(self, win):
        return wx.BoxSizer(wx.VERTICAL)
    
    def _get_flag(self, pos):
        flag = 0
        if self.horizontal_center:
            flag = wx.ALIGN_CENTER_HORIZONTAL
        if pos == 0:
            return flag | wx.LEFT | wx.TOP | wx.RIGHT | wx.BOTTOM
        else:
            return flag | wx.LEFT | wx.BOTTOM | wx.RIGHT
    
class Grid(LayoutBase):
    """
    Just like wx.GridBagSizer
    """
    
    proportion = (-1, 0)
    
    def __init__(self, vgap=2, hgap=2, padding=4, growablecol=None, growablerow=None, *args, **kwargs):
        """
        vgap and hgap are the same as GridBagSizer
        growablecol is used to indicate which col could be automatically growable.
        growablecol could be a single integer value or an integer list or tuple.
        """
        LayoutBase.__init__(self, padding, *args, **kwargs)
        self.vgap = vgap
        self.hgap = hgap
        self.growablecol = growablecol
        self.growablerow = growablerow
        if self.growablecol is None:
            self.growablecol = []
        elif isinstance(self.growablecol, int):
            self.growablecol = [self.growablecol]
        if self.growablerow is None:
            self.growablerow = []
        elif isinstance(self.growablerow, int):
            self.growablerow = [self.growablerow]
        
    def _get_proportion(self):
        if self.growablerow:
            return self.proportion[0], -1
        return self.proportion
        
    def _create_sizer(self, win):
        sizer = wx.GridBagSizer(self.vgap, self.hgap)
        return sizer
    
    def _init(self):
        self.add_growable_col(self.growablecol)
        self.add_growable_row(self.growablerow)
        
    def add_growable_col(self, col):
        if self.created:
            sizer = self.get_sizer()
            if col is not None:
                if isinstance(col, (list, tuple)):
                    for i in col:
                        sizer.AddGrowableCol(i)
                else:
                    sizer.AddGrowableCol(col)
        if isinstance(col, (list, tuple)):
            for i in col:
                if i not in self.growablecol:
                    self.growablecol.append(i)
        else:
            if col not in self.growablecol:
                self.growablecol.append(col)
        
    def add_growable_row(self, row):
        if self.created:
            sizer = self.get_sizer()
            if row is not None:
                if isinstance(row, (list, tuple)):
                    for i in row:
                        sizer.AddGrowableRow(i)
                else:
                    sizer.AddGrowableRow(row)
        if isinstance(row, (list, tuple)):
            for i in row:
                if i not in self.growablerow:
                    self.growablerow.append(i)
        else:
            if row not in self.growablerow:
                self.growablerow.append(row)
        
    
    def add(self, pos, element, name='', proportion=None, flag=None, border=None, span=None):
        """
        This function also has a span parameter, the same as GridBagSizer, you
        can refer it.
        """
        if not name:
            self._id += 1
            name = '_id_%d' % self._id
        element = self._prepare_element(element)
        self.elements[name] = element
        element.name = name
        args = {'pos':pos, 'proportion':proportion, 
            'flag':flag, 'border':border, 'span':span}
        self.elements_args[name] = args
        self.orders.append(name)
        if self.created:
            self._create_element(name, element, args, len(self.orders) - 1)
            self._layout()
        return element
    
    def _add_element(self, win, sizer, name, e, args, i, proportion, flag, border):
        if args['span'] is not None:
            span = args['span']
        else:
            span = wx.DefaultSpan
        sizer.Add(e.obj, args['pos'], span, flag, border)
        
class HGroup(HBox):
    """
    Just like wx.StaticBoxSizer(wx.HORIZONTAL)
    """

    def __init__(self, title, *args, **kwargs):
        HBox.__init__(self, *args, **kwargs)
        self.title = title
        
    def _create_sizer(self, win):
        return wx.StaticBoxSizer(wx.StaticBox(win, -1, self.title),
            wx.HORIZONTAL)
    
class VGroup(VBox):
    """
    Just like wx.StaticBoxSizer(wx.VERTICAL)
    """
    
    def __init__(self, title, *args, **kwargs):
        VBox.__init__(self, *args, **kwargs)
        self.title = title
        
    def _create_sizer(self, win):
        return wx.StaticBoxSizer(wx.StaticBox(win, -1, self.title),
            wx.VERTICAL)
        
class SimpleGrid(Grid):
    """
    A simplified GridBagSizer. Each row will can only one or two cols. And if there
    are two cols, the first col will be the Label info of the second control.
    Sometimes, you may don't want two cols row but one col row, so you can specify
    the `span` in the add() function. And there will be only one col in that row, 
    and the Label and control will be aligned vertical. So this feature maybe suitable
    for textarea, list, tree, etc.
    """
    def __init__(self, vgap=2, hgap=2, padding=4, *args, **kwargs):
        Grid.__init__(self, vgap, hgap, padding, 1, *args, **kwargs)
        
    def add(self, label, element, name='', proportion=None, flag=None, border=None, span=False):
        """
        The span parameter in here is not the same as Grid. It's a boolean value,
        if True, current row will have only one col, otherwise there are still two
        cols.
        """
        if not name:
            self._id += 1
            name = '_id_%d' % self._id
        element = self._prepare_element(element)
        self.elements[name] = element
        element.name = name
        if span:
            span = (1, 2)
        args = {'proportion':proportion, 
            'flag':flag, 'border':border, 'span':span, 'label':label}
        self.elements_args[name] = args
        self.orders.append(name)
        if self.created:
            self._create_element(name, element, args, len(self.orders) - 1)
            self._layout()
        return element
    
    def _add_element(self, win, sizer, name, e, args, i, proportion, flag, border):
        if args['span']:
            span = args['span']
            box = VBox()
            if args['label']:
                box.add(Label(args['label']))
            box.add(e.obj, name=name, proportion=proportion, flag=flag, border=border)
            box.create(win, self.namebinding)
            sizer.Add(box.obj, (i, 0), span, flag, border)
        else:
            span = wx.DefaultSpan
            if args['label'] is not None:
                label = Label(args['label'])
                label.create(win, self.namebinding)
                sizer.Add(label.obj, (i, 0), span, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, border)
            sizer.Add(e.obj, (i, 1), span, flag, border)
    
class EasyElement(Element):
    """
    EasyElement is used to wrap a wx widget to an Element object. And EasyElement
    default has not value, so you can see some child classes like Label, Button 
    inherit from it.
    
    And if your element class need a value and also supply SetValue() and GetValue()
    functions, you can inherit from ValueElement(it's a child class of EasyElement too).
    
    klass
        The underlying wx widget class name. It could be a string value and a real
        class object. If it's a string, then meide will use getattr(wx, klass) to 
        get the class object. So if the class is not in wx module(e.g. in wx submodule)
        you should import the module and use class object directly but not a string.
        
    style
        When creating the underlying wx widget, meide will merge this style and the
        `style` parameter in Element constructor function. So if you want some style
        always exist, you can assign it a value.
    """
    klass = ''
    style = 0
    
    def __init__(self, *args, **kwargs):
        """
        args and kwargs will pass to underlying wx widget constructor function.
        """
        Element.__init__(self, *args, **kwargs)
        
    def _create_obj(self, win):
        if self.klass:
            klass = self.klass
        else:
            klass = self.__class__.__name__
        if isinstance(klass, str):
            cls = getattr(wx, klass, None)
        else:
            cls = klass
        if cls:
            #prepare parameters
            parent = None
            if 'parent' in self.kwargs:
                parent = self.kwargs['parent']
                del self.kwargs['parent']
            if not parent:
                parent = win
            if 'id' in self.kwargs:
                id = self.kwargs['id']
                del self.kwargs['id']
            else:
                id = -1
            if self.style:
                self.kwargs['style'] = self.kwargs.get('style', 0) | self.style
                
            #create object
            obj = cls(parent, id, *self.args, **self._get_kwargs(self.kwargs))
            
            return obj
        else:
            raise UnsupportException('Unsupport widget type [%s]' % self.klass)

class Label(EasyElement):
    klass = 'StaticText'

class Button(EasyElement):
    klass = 'Button'
  
class List(EasyElement):
    from ui.List import List
    klass = List
    proportion = (-1, -1)
    
    def __init__(self, columns, *args, **kwargs):
        EasyElement.__init__(self, columns, *args, **kwargs)
        
class CheckList(List):
    from ui.List import CheckList
    klass = CheckList

class ListBox(EasyElement):
    klass = 'ListBox'
    proportion = (-1, -1)
        
class Tree(EasyElement):
    klass = 'TreeCtrl'
    proportion = (-1, -1)
        
class SimpleElement(EasyElement):
    """
    Wrap class used to encapsulate a non-value widget to Element object.
    """
    def __init__(self, obj):
        EasyElement.__init__(self)
        self.obj = obj
        
    def _create_obj(self, win):
        return self.obj

class SimpleValueElement(SimpleElement, ValidateMixin):
    """
    Wrap class used to encapsulate a value widget to Element object.
    """
    has_value = True
    default_value = ''

    def __init__(self, obj):
        SimpleElement.__init__(self, obj)
        ValidateMixin.__init__(self)
        
    def _create_obj(self, win):
        return self.obj
    
class ValueElement(EasyElement, ValidateMixin):
    """
    An Element class which has value in it. So the `has_value` class attribute is
    `True`. 
    
    default_value
        If user doesn't pass a value(leave the value parameter is None), then use
        this `default_value` to initialize the widget object.
    
    validator_funcs
        You can set several validator functions to current element. The validator
        function signature is like:
            
            def func(value)
            
        if validation is failed, you need to raise a ValidateFailException. You
        can see the example in test_validate.py.
        
        This class attribute is used for default validator function list.
    """
    has_value = True
    default_value = ''
    
    def __init__(self, value=None, *args, **kwargs):
        """
        The first paramter of each ValueElement is always `value`. And ValueElement
        supports lazy value calculte, so you can pass a callable object ,and when
        creating the object, the callable will be automatically calculated.
        """
        EasyElement.__init__(self, *args, **kwargs)
        ValidateMixin.__init__(self)
        self.value = value
        
    @_bind_name
    def create(self, win, namebinding):
        """
        The mainly difference is after create the Element object, ValueElement will
        invoke the SetValue() to initialize the underlying widget object.
        """
        _p('>>> Create', self.__class__.__name__)
        #create object
        if self.win is win:
            if self.created: return self
        else:
            self.created = False
        self.win = win
        self.obj = obj = self._create_obj(win)
        if self.value is None:
            value = self._get_default_value()
        else:
            #support lazy value calculate
#            if callable(self.value):
#                value = self.value()
#            else:
#                value = self._validate_value(self.value)
            value = self.value
            if callable(self.value):
                value = self.value()
            value = self._validate_value(value)
            
        self.SetValue(value)
        
        #set external attributes
        if 'size' in self.kwargs:
            self.attr_size = self.kwargs['size']
        elif hasattr(self, 'size'):
            self.attr_size = self.size
    
        self._do_bind()
        self._set_tooltip()
        self.created = True
        return self
    
    def _get_default_value(self):
        return self.default_value
    
    def _validate_value(self, value):
        return value
    
class Text(ValueElement):
    """
    Single line text widget.
    """
    klass = 'TextCtrl'
    proportion = (-1, 0)
    
class Password(Text):
    style = wx.TE_PASSWORD
    
class MultiText(Text):
    """
    Multiple lines text widget.
    """
    style = wx.TE_MULTILINE
    proportion = (-1, -1)

class Int(ValueElement):
    from wx.lib.intctrl import IntCtrl
    klass = IntCtrl
    default_value = 0
    
    def _validate_value(self, value):
        if not value:
            return 0
        return int(value)
    
class IntSpin(Int):
    klass = 'SpinCtrl'
    default_value = 0
    
class Check(ValueElement):
    klass = 'CheckBox'
    default_value = False
    
    def __init__(self, value=None, label='', *args, **kwargs):
        ValueElement.__init__(self, label=label, *args, **kwargs)
        self.value = value
        
    def _validate_value(self, value):
        if isinstance(value, str):
            if value.lower() in ('true', 'yes', 'on'):
                value = True
            else:
                value = False
        else:
            value = bool(value)
        return value
    
class Check3D(Check):
    style = wx.CHK_3STATE
    default_value = 0
    
    def SetValue(self, value):
        self.get_obj().Set3StateValue(value)

    def GetValue(self):
        return self.get_obj().Get3StateValue()
 
class ComboBox(ValueElement):
    klass = 'ComboBox'
    proportion = (-1, 0)
    style = wx.TE_PROCESS_ENTER

    def __init__(self, value=None, choices=[], *args, **kwargs):
        ValueElement.__init__(self, value, choices=choices, *args, **kwargs)
    
class SingleChoice(ValueElement):
    klass = 'ComboBox'
    style = wx.CB_READONLY 
    proportion = (-1, 0)
    
    def __init__(self, value=None, choices=[], *args, **kwargs):
        if isinstance(choices, (list, tuple)):
            if isinstance(choices[0], (list, tuple)):
                value_dict = dict(choices)
                value_list = [x[0] for x in choices]
            else:
                value_list = choices
                if isinstance(value, int):
                    value_dict = dict(zip(choices, list(range(len(choices)))))
                else:
                    value_dict = dict(zip(choices, choices))
        else:
            value_dict = choices
            value_list = sorted(choices.values())
        
        self.value_dict = value_dict
        self.value_list = value_list
        ValueElement.__init__(self, value, choices=value_list, *args, **kwargs)
        
    def SetValue(self, value):
        key = [k for k, v in self.value_dict.items() if v == value][0]
        self.get_obj().SetValue(key)
        
    def GetValue(self):
        value = self.get_obj().GetValue()
        return self.value_dict[value]

    def _get_default_value(self):
        return self.value_dict[self.value_list[0]]
    
class MultiChoice(ValueElement):
    klass = 'CheckListBox'
    proportion = (-1, -1)
    default_value = []
    
    def __init__(self, value=None, choices=[], *args, **kwargs):
        if isinstance(choices, (list, tuple)):
            if isinstance(choices[0], (list, tuple)):
                value_dict = dict(choices)
                value_list = [x[0] for x in choices]
            else:
                value_list = choices
                if isinstance(value, int):
                    value_dict = dict(zip(choices, list(range(len(choices)))))
                else:
                    value_dict = dict(zip(choices, choices))
        else:
            value_dict = choices
            value_list = sorted(choices.values())
        
        self.value_dict = value_dict
        self.value_list = value_list
        ValueElement.__init__(self, value, choices=value_list, *args, **kwargs)
        
    def _create_obj(self, win):
        self.args = self.args[1:]
        return ValueElement._create_obj(self, win)
        
    def SetValue(self, value):
        for i, k in enumerate(self.value_list):
            if self.value_dict[k] in value:
                self.get_obj().Check(i)
            else:
                self.get_obj().Check(i, False)

    def GetValue(self):
        value = []
        for i, k in enumerate(self.value_list):
            if self.get_obj().IsChecked(i):
                value.append(self.value_dict[k])
        return value

class Date(ValueElement):
    klass = 'DatePickerCtrl'
    style = wx.DP_DROPDOWN | wx.DP_SHOWCENTURY

    def GetValue(self):
        import datetime
        
        date = self.get_obj().GetValue()
        return datetime.date(date.Year, date.Month+1, date.Day)
    
    def _get_default_value(self):
        return wx.DateTime.Now()
    
    def _validate_value(self, value):
        import time, datetime
        
        date = value
        if isinstance(value, str):
            d = time.strptime(value, "%Y-%m-%d")
            date = wx.DateTimeFromTimeT(time.mktime(d))
        elif isinstance(value, (datetime.datetime, datetime.date)):
            date = wx.DateTimeFromTimeT(time.mktime(value.timetuple()))
        return date
    
class Time(ValueElement):
    def _create_obj(self, win):
        import wx.lib.masked as masked
        
        self.widget = obj = masked.TimeCtrl(win, -1, name="timectrl", fmt24hr=True)
        h = obj.GetSize().height
        spin2 = wx.SpinButton(win, -1, wx.DefaultPosition, size=(-1, h), style=wx.SP_VERTICAL)
        obj.BindSpinButton(spin2)
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(obj, 0, wx.ALIGN_CENTRE)
        box.Add(spin2, 0, wx.ALIGN_CENTRE)
        return box
    
    def SetValue(self, value):
        self.widget.SetValue(value)
        
    def GetValue(self):
        import datetime
        
        value = self.widget.GetValue()
        time = map(int, value.split(':'))
        return datetime.time(*time)
    
    def _get_default_value(self):
        return wx.DateTime.Now()
    
    def _validate_value(self, value):
        import time, datetime
        
        date = value
        if isinstance(value, str):
            d = time.strptime(value, "%H:%M:%S")
            date = wx.DateTimeFromTimeT(time.mktime(d))
        elif isinstance(value, datetime.datetime):
            date = wx.DateTimeFromTimeT(time.mktime(value.timetuple()))
        return date
    
class OpenFile(ValueElement):
    proportion = (-1, 0)
    
    def __init__(self, value='', *args, **kwargs):
        kwargs['initialValue'] = value
        ValueElement.__init__(self, value, *args, **kwargs)
        
    def SetValue(self, value):
        ValueElement.SetValue(self, value)
    
    def _create_obj(self, win):
        from ui.FileBtnCtrl import FileBrowseButton
        
        obj = FileBrowseButton(win, -1, *self.args, **self._get_kwargs(self.kwargs))
        return obj
    
class SaveFile(OpenFile):
    def _create_obj(self, win):
        from ui.FileBtnCtrl import FileBrowseButton
        
        if 'fileMode' not in self.kwargs:
            self.kwargs['fileMode'] = wx.SAVE
        obj = FileBrowseButton(win, -1, *self.args, **self._get_kwargs(self.kwargs))
        return obj
    
class Dir(OpenFile):
    def _create_obj(self, win):
        from ui.FileBtnCtrl import DirBrowseButton
        
        obj = DirBrowseButton(win, -1, *self.args, **self._get_kwargs(self.kwargs))
        return obj

class Radio(ValueElement):
    klass = 'RadioButton'
    default_value = False
        
class HRadioBox(ValueElement):
    klass = 'RadioBox'
    style = wx.RA_SPECIFY_COLS
    default_value = 0
    kwargs = {'majorDimension':1}
    
    def __init__(self, value=None, title='', choices=[], *args, **kwargs):
        """
        Create a radio box
        """
        ValueElement.__init__(self, label=title, choices=choices, *args, **kwargs)
    
    def SetValue(self, value):
        self.get_obj().SetSelection(value)
        
    def GetValue(self):
        return self.get_obj().GetSelection()
        
class VRadioBox(HRadioBox):
    style = wx.RA_SPECIFY_ROWS
    
#########################################################
# Frames and Dialogs
#########################################################

class FrameBase(object):
    """
    FrameBase is a mixin class. So if a panel-like widget want to process layout
    object, it can inherit from it.
    """
    def __init__(self, parent, layout, value=None, fit=1, callback=None):
        """
        callback
            After creating the layout, and if there is a available callback object,
            it'll call this function. So you can do some initialization works in 
            callback function.
        fit
            It's just like the `fit` parameter in create() function.
        value
            For a layout, a `value` will be a dict, and the key will be the name of
            each ValueElement object. If the `value` is not `None`, then after creating
            the layout, it'll automatically invoke SetValue() to initialize 
            all ValueElement objects. 
        """
        self.parent = parent
        self.layout = layout
        self.value = value
        self.fit = fit
        self.callback = callback
        
        self._create()
        if value:
            self.layout.SetValue(value)
        if callback and callable(callback):
            callback(self)
        
    def _create(self):
        create(self, self.layout, self.fit)
        
    def GetValue(self):
        return self.layout.GetValue()
    
    def SetValue(self, value):
        self.layout.SetValue(value)
    
class Dialog(wx.Dialog, FrameBase):
    def __init__(self, parent, layout, title='', value=None, fit=1, callback=None,
            style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER, **kwargs):
        wx.Dialog.__init__(self, parent, -1, title, style=style, **kwargs)
        FrameBase.__init__(self, parent, layout, value, fit, callback)
        
    def do_validate(self):
        """
        User can use this method to validate the value, and you should invoke it 
        before you close the dialog or when you want to validate the value.
        """
        if not self.layout.validate(): return
        if self.IsModal():
            self.EndModal(wx.ID_OK)
        else:
            self.SetReturnCode(wx.ID_OK)
            self.Show(False)
        
class Panel(wx.Panel, FrameBase):
    def __init__(self, parent, layout, title='', value=None, fit=1, callback=None,
            style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER, **kwargs):
        wx.Panel.__init__(self, parent, -1, style=style, **kwargs)
        FrameBase.__init__(self, parent, layout, value, fit, callback)
        self.title = title
        
class SimpleDialog(Dialog):
    """
    A very simple Dialog class. And you only need to define a layout, it'll 
    automatically create a Ok and Cancel button for you. So I think it'll be
    very handly for simple dialoy need Ok and Cancel button.
    """
    def __init__(self, parent, layout, title='', value=None, fit=1, callback=None,
            style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER, **kwargs):
        Dialog.__init__(self, parent, layout, title, value, fit, callback,
            style, **kwargs)
    
    def _create(self):
        box = VBox()
        box.add(self.layout)
        box.add(simple_buttons(), flag=wx.ALIGN_CENTER|wx.BOTTOM)
        self.layout = box
        box.bind('btnOk', 'click', self.OnOk)
        Dialog._create(self)
        box.find('btnOk').get_obj().SetDefault()
        
    def OnOk(self, event):
        self.do_validate()
        
def NotBlankValidator(value):
    """
    A validator used to check a field should not be empty.
    """
    if not value:
        raise ValidateFailException('This field could not be empty!')
        
