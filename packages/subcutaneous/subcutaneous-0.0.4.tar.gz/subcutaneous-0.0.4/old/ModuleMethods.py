from types import ModuleType


class ModuleListener:
	def __init__(self, func, varnames=None):
		self.f = func
		self.varnames = varnames

	def __get__(self, instance, owner):
		# if self.varnames:
		# 	return self._create_bound_property(instance)
		return self._create_bound_method(instance)

	def _create_bound_method(self, instance):

		def bound_method(*args, **kwargs):
			return self.f(instance, *args, **kwargs)

		return bound_method

		# def _create_bound_property(self, instance):
		# 	a = self.f(instance)
		# 	r = dict()
		# 	for i in range(len(a)):
		# 		if isinstance(a[i], dict):
		# 			for k, v in a[i].items():
		# 				r[k] = v
		# 		else:
		# 			r[self.varnames[i]] = a[i]
		# newmod = instance(r)
		return newmod


def modulemethod(func):
	r = ModuleListener(func)
	return r


class ModuleFactory(type):
	Valid_Methods = {}
	Valid_Attrs = {}

	def isBuiltIn(name):
		if name in ModuleFactory.Valid_Dunder:
			return False
		return name.startswith("__") and name.endswith("__")

	@staticmethod
	def getSinglton(name):

		def module_getattribute(self, key):

			attr = object.__getattribute__(self, key)

			if hasattr(attr, "__get__"):
				return attr.__get__(self, type(self))
			return attr

		a = type("_mod", (ModuleType,), {"__getattribute__": module_getattribute})

		a.__call__ = ModuleFactory.__call__
		singleton = a(f"{name}")

		return singleton

	def __call__(obj, name=None, **kwargs):

		instance = ModuleFactory.getSinglton([name, obj.__name__][not name])
		D = dict(obj.__dict__)
		D.update(kwargs)

		for k, v in D.items():
			if not callable(v) and not ModuleFactory.isBuiltIn(k):
				setattr(instance, k, v)

			if callable(v) and k in ModuleFactory.Valid_Methods:
				if k in ModuleFactory.__dict__:
					setattr(instance, v, ModuleFactory.__dict__[k])

		return instance

	def __new__(obj, name=None, bases=None, ns=None, **kwargs):
		return ModuleFactory.__call__(obj, name, **ns)


def module(cls):
	name = cls.__name__
	ns = cls.__dict__
	bases = tuple()
	return ModuleFactory(name, bases, ns)
