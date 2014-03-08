"""

WinReg - An object-oriented wrapper of the _winreg module.

Copyright (C) 2001,2002 Ollie Rutherfurd <oliver@rutherfurd.net>

License: Python license.

example usage:

# register a new file extension and and setup
# the shell\open command to be the same as 'txt' files.
>>> from winreg import *
>>> hkcr = Key(HKCR)
>>> keyname = hkcr['.txt'].value
>>> cmd = hkcr[keyname]['shell\\open\\command'].value
>>> _type = hkcr[keyname]['shell\\open\\command'].values[0].type
>>> cmdvalue = hkcr.add('XYZ.File\\shell\\open\\command').set(None, cmd, _type)
>>> namevalue = hkcr.add('.xzy').set(None,'XYZ.File')
>>> # now remove the newly created entries
...
>>> hkcr['.xzy'].delete()
>>> hkcr['XYZ.File'].delete()
>>>

$Id: winreg.py,v 1.2 2002/04/23 00:42:21 oliver Exp $

"""

import _winreg, types
from _winreg import HKEY_CLASSES_ROOT, \
	HKEY_CURRENT_CONFIG, HKEY_CURRENT_USER, \
	HKEY_DYN_DATA, HKEY_LOCAL_MACHINE, \
	HKEY_PERFORMANCE_DATA, HKEY_USERS
from _winreg import REG_BINARY, REG_DWORD, REG_DWORD_BIG_ENDIAN, \
	REG_DWORD_LITTLE_ENDIAN, REG_EXPAND_SZ, REG_MULTI_SZ, REG_SZ

__all__ = ['Key', 
	'KeyNotFound', 'PermissionDenied', 'ValueNotFound',
	'ALL_ACCESS', 'READ_ACCESS',
	'HKCR','HKCC','HKCU','HKDD','HKPD','HKLM',
	'REG_BINARY', 'REG_DWORD', 'REG_DWORD_BIG_ENDIAN', 'REG_DWORD_LITTLE_ENDIAN', 'REG_EXPAND_SZ', 'REG_MULTI_SZ', 'REG_SZ']

__version__ = '0.3'

class KeyNotFound(Exception):
	"""Exception raised when trying to access a Key that doesn't exist"""
	pass

class ValueNotFound(Exception):
	"""Exception raised when trying to access a Value that doesn't exist"""
	pass

class PermissionDenied(Exception):
	"""Exception raised when user doesn't have permission for an action"""
	pass

# no reason to type out full names all the time
HKCR = HKEY_CLASSES_ROOT
HKCC = HKEY_CURRENT_CONFIG
HKCU = HKEY_CURRENT_USER
HKDD = HKEY_DYN_DATA
HKPD = HKEY_PERFORMANCE_DATA
HKLM = HKEY_LOCAL_MACHINE

ALL_ACCESS = _winreg.KEY_ALL_ACCESS
READ_ACCESS = _winreg.KEY_READ

# TODO: add an example for .pys files
# TODO: change magic numbers to constants
# TODO: make repr of objects more user-friendly

class Key(object):

	"""
	Registry Key class.

	This is the only class exposed directly by winreg. Everything
	else should be accessed via method and properties of this class.

	example:

	>>> from winreg import *
	>>> hkcr = Key(HKCR)
	>>> pyfile = hkcr['.py'].value
	>>> pyopen = hkcr[pyfile]['shell\\open\\command'].value
	>>>
	"""

	def __init__(self, key, subkey='', access=ALL_ACCESS):
		# QUESTION: keep a weak ref to the parent?
		# QUESTION: allow full path to be specified in key?
		if isinstance(key, types.StringTypes):
			key = getattr(_winreg, key)

		self.key = key
		self.access = access
		self.name = subkey.split('\\')[-1]
		# TODO: need to do this better (to try to get full path)
		#self.path = subkey	

		try:
			self.hkey = _winreg.OpenKey(key, subkey, 0, self.access)
		except WindowsError, err:
			if err.errno == 2:
				# TODO: try to determine complete name
				raise KeyNotFound(subkey)
			elif err.errno == 5:
				raise PermissionDenied(subkey)
			raise

		self.keys = Keys(self.hkey, self.access)
		self.values = Values(self.hkey)

	def add(self, name):
		"""Adds a subkey to this Key.

		NOTE: this is just a shortcut to Key.keys.add().
		"""
		return self.keys.add(name)

	def delete(self):
		"""delete key and all subkeys from the registry."""
		for key in self:
			key.delete()

	def set(self, name, value, _type=None):
		"""Sets a value on the Key.

		NOTE: this is just a shortcut to Key.values.set()."""
		return self.values.set(name,value,_type)

	def getvalue(self):
		"""Returns the default value, or None if it is not set.

		NOTE: it does NOT return a value object, but the value attribute
		of the value object (as it is meant to be a shortcut).
		"""
		try:
			return self.values[0].value
		except IndexError:
			return None

	def setvalue(self, value):
		"""Sets the value of the default value, returns Value object"""
		return self.values[0].set(None,value)

	value = property(getvalue, setvalue, None, """Get or Set the default value of the Key (returns None if not set)""")

	def __contains__(self,key):
		"""checks for existance of a child key."""
		return key in self.keys

	def __getitem__(self,key):
		"""returns a subkey by index or name."""
		return self.keys[key]

	def __int__(self):
		"""returns the hkey for the Key."""
		return self.hkey

	def __iter__(self):
		"""creates a subkey iterator."""
		return KeyIterator(self.keys)

	def __len__(self):
		"""Number of subkeys for Key."""
		return len(self.keys)


class Keys(object):

	"""Collection of subkeys for a Key.

	"""

	def __init__(self, hkey, access):
		self.hkey = hkey
		self.access = access

	def add(self, name):
		"""Add a named Key, returns Key object"""
		_winreg.CreateKey(self.hkey, name)
		return Key(self.hkey, name, self.access)

	def __contains__(self, key):
		"""checks for existance of a Key, by name or index"""
		try:
			if self[key] != None:
				return 1
		except KeyNotFound:
			return 0

	def __getitem__(self, key):
		"""Returns a Key by index or name.

		Slice notation can also be used to return a list of Keys

		TODO: slice values out of range should not generate an exception.
		"""

		if isinstance(key, types.IntType):
			try:
				if key < 0:
					key = len(self) + key
				# enum key will return the name of the key
				return Key(self.hkey, _winreg.EnumKey(self.hkey, key), self.access)
			except EnvironmentError:
				raise IndexError, key
		elif isinstance(key, types.SliceType):
			return [self[i] for i in range((key.start != None) and key.start or 0, \
				(key.stop == None) and len(self) or key.stop, \
				(key.step == None) and 1 or key.step)]
		elif isinstance(key, types.StringTypes):
			try:
				return Key(self.hkey, key, self.access)
			except WindowsError, err:
				if err.errno == 2:
					raise KeyNotFound(key)
				elif err.errno == 5:
					raise PermissionDenied(key)
				raise
		else:
			raise ValueError(key)

	def __iter__(self):
		"""creates a KeyIterator"""
		return KeyIterator(self)

	def __len__(self):
		"""number of keys"""
		return _winreg.QueryInfoKey(self.hkey)[0]


class Values(object):
	"""Set of value for a Key.

	Should be accessed via 'values' property of Key class.
	"""

	def __init__(self, hkey):
		self.hkey = hkey

	def set(self, name, value, _type=None):
		# QUESTION: should value be first, so name can be optional?
		"""Add or set a named value.

		If _type is not specified the following is assumed:

			Strings = REG_SZ
			Int = REG_DWORD
			Tuple or List = REG_MULTI_SZ

		NOTE: use None, 0, or '' to set the default value for a Key.

		"""
		if isinstance(_type, types.NoneType):
			if isinstance(value, types.StringTypes):
				_type = REG_SZ
			elif isinstance(value, types.IntType):
				_type = REG_DWORD
			elif isinstance(value, types.TupleType):
				value = list(value)
				_type = REG_MULTI_SZ
			elif isinstance(value, types.ListType):
				_type = REG_MULTI_SZ
			else:
				raise ValueError, "Unable to guess type for value: %s, please specify" % `value`

		_winreg.SetValueEx(self.hkey, name, None, _type, value)

		return Value(self.hkey, name)	# return the value

	def __getitem__(self, key):

		"""return a value by name of index

		NOTE: Slice notation can also be used to get a list of Values.

		TODO: slice values that are out of range should not generate an exception
		"""

		if isinstance(key, types.StringTypes + (types.NoneType,)):
			return Value(self.hkey, key)
		elif isinstance(key, types.IntType):
			try:
				if key < 0:
					key = len(self) + key
				name = _winreg.EnumValue(self.hkey, key)[0]
				return Value(self.hkey, name)
			except WindowsError, err:
				if err.errno == 259:
					raise IndexError, key
				raise
		elif isinstance(key, types.SliceType):
			return [self[v] for v in range((key.start != None) and key.start or 0, \
				(key.stop == None) and len(self) or key.stop, \
				(key.step == None) and 1 or key.step)]
		else:
			raise TypeError, key

	def __contains__(self, key):
		"""Checks for existance of a Value, by name of index."""
		try:
			if self[key] != None:
				return 1
		except ValueNotFound:
			return 0

	def __iter__(self):
		"""Creates a ValueIterator"""
		return ValueIterator(self)

	def __len__(self):
		"""Number of values"""
		return _winreg.QueryInfoKey(self.hkey)[1]


class Value(object):

	"""
	Registry Value class.

	Should be accessed via 'values' propery to Key class.
	"""

	def __init__(self, hkey, name):
		# check for existence of value
		try:
			_winreg.QueryValueEx(hkey, name)
			self._hkey = hkey
			self._name = name
		except WindowsError, err:
			if err.errno == 2:
				raise ValueNotFound(name)
			elif err.errno == 5:
				raise PermissionDenied(name)
			raise

	def getvalue(self):
		"""returns value"""
		return _winreg.QueryValueEx(self._hkey, self._name)[0]
	def setvalue(self, value):
		"""sets the value

		If type the type does not match the existing value type,
		an exception will be raised.
		"""
		_winreg.SetValueEx(int(self._hkey), self.name, None, self.type, value)
	value = property(getvalue, setvalue, None, """Get or Set the value of a Value.""")

	def gettype(self):
		"""Returns the type of the value"""
		return _winreg.QueryValueEx(self._hkey, self._name)[1]
	type = property(gettype, None, None, """Get the type of a Value.""")

	def getname(self):
		"""Returns the name of the value"""
		return self._name
	name = property(getname, None, None, """Get the name of a Value.""")

	def delete(self):
		"""Removes the value"""
		_winreg.DeleteValue(self._hkey, self.name)


class KeyIterator(object):

	"""
	Iterator for a Key's subkeys

	>>> from winreg import *
	>>> key = Key(HKCR,r'*\\shellex\\ContextMenuHandlers')
	>>> list_one = []
	>>> list_two = []
	>>> i = iter(key.keys)
	>>> for x in range(len(key.keys)):
	...     list_one.append(key[x].name)
	...     list_two.append(i.next().name)
	...
	>>> try:
	...     i.next()
	... except StopIteration:
	...    print 'one too far!'
	one too far!
	>>> list_one.sort(); list_two.sort()
	>>> assert len(list_one) == len(list_two), 'len(list_one)->%d != len(list_two)->%d' % (len(list_one), len(list_two),)
	>>> for x in range(len(list_one)):
	...     assert list_one[x] == list_two[x], 'on loop %d, %s != %s' % (x, list_one[x], list_two[x],)
	...
	>>>

	"""

	def __init__(self, key):
		self.key = key
		self.index = 0

	def next(self):
		while 1:
			try:
				self.index += 1
				return self.key[self.index - 1]
			except IndexError:
				raise StopIteration


class ValueIterator(object):

	"""Iterator for a Key's values

	>>> from winreg import *
	>>> k = Key(HKLM, r'Software\\Microsoft\\Command Processor')
	>>> count = 0
	>>> for v in k.values:
	...     if v.name != k.values[count].name:
	...         print 'FAILURE: %s != %s' % (v.name, k.values[counts].name,)
	...     if v.value != k.values[count].value:
	...         print 'FAILURE: %s != %s' % (v.value, k.values[counts].value,)
	...     count += 1
	...
	>>> if len(k.values):
	...     if v.name != k.values[-1].name:
	...         print 'FAILURE: %s != %s' % (v.name, k.values[-1].name,)
	...
	>>> len(k.values) == count
	1

	Make sure a StopIteration exception is raised if we iterate too far.

	>>> i = iter(k.values)
	>>> for x in range(len(k.values)):
	...     n = i.next()
	...
	>>> n = i.next()
	Traceback (most recent call last):
	    ...
	StopIteration
	>>>

	"""

	def __init__(self, values):
		self.values = values
		self.index = 0

	def next(self):
		while 1:
			try:
				self.index += 1
				return self.values[self.index - 1]
			except IndexError:
				raise StopIteration


def _dodoctest():
	import doctest, winreg
	doctest.testmod(winreg)


if __name__ == '__main__':

	try:
		_dodoctest()
	except KeyboardInterrupt:
		pass

# :indentSize=4:lineSeparator=\r\n:noTabs=false:tabSize=4:
