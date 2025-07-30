from ModuleMethods import modulemethod
from types import ModuleType


class State(type):
	Valid_Methods = {
		"tick",
		"event",
		"view",
		"_runner",
		"_worker",
		"pullFunction",
		"getItems",
	}
	Valid_Dunder = {"__TICK__", "__EVENT__", "__VIEW__"}

	def isBuiltIn(name):
		if name in State.Valid_Dunder:
			return False
		return name.startswith("__") and name.endswith("__")

	@staticmethod
	def getSinglton(name):

		def module_getattribute(self, key):

			attr = object.__getattribute__(self, key)

			if hasattr(attr, "__get__"):
				return attr.__get__(self, type(self))
			return attr

		a = type("_state", (ModuleType,), {"__getattribute__": module_getattribute})

		a.__call__ = State.__call__
		singleton = a(f"{name}")

		return singleton

	@modulemethod
	def tick(obj, x, y):
		obj.x = x
		obj.y = y
		run_type = "__TICK__"

		return obj._runner(run_type)

	@modulemethod
	def event(obj, x, y, trigger):

		run_type = "__EVENT__"
		obj.trigger = trigger
		return obj._runner(run_type)

	@modulemethod
	def _runner(obj, run_type):
		# D = getattr(obj, run_type)
		D = obj.__dict__[run_type]

		for k, v in D.items():
			if k != "return":
				obj._worker(v)

		if "return" in D.keys():
			obj._worker(D["return"])

			params = list(D["return"].keys())
			items = tuple(obj.getItems(params))
			for i in items:
				yield i[1]

	@modulemethod
	def _worker(obj, rule_dict):
		for k, v in rule_dict.items():
			item = k
			if "condition" in v:
				if obj.pullFunction(v["condition"]):
					if "value" in v:
						i = getattr(obj, v["value"])
						setattr(obj, k, i)
						# setattr(obj, k, v["value"])

					if "rule" in v:
						r = obj.pullFunction(v["rule"])
						setattr(obj, k, r)

			else:
				if "value" in v:
					i = getattr(obj, v["value"])

					setattr(obj, k, i)
				if "rule" in v:
					r = obj.pullFunction(v["rule"])
					setattr(obj, k, r)

	@modulemethod
	def pullFunction(obj, func):
		# parameter_names = func.__code__.co_varnames
		t = func.__code__.co_argcount + func.__code__.co_kwonlyargcount
		parameter_names = func.__code__.co_varnames[:t]

		params = list(obj.getItems(parameter_names))
		if len(params) >= 1:
			r = func(**dict(params))
			return r

	@modulemethod
	def getItems(obj, parameters):
		for k in parameters:
			yield (k, getattr(obj, k))

	Valid_Dunder = {"__TICK__", "__EVENT__", "__VIEW__"}

	def isBuiltIn(name):
		if name in State.Valid_Dunder:
			return False
		return name.startswith("__") and name.endswith("__")

	def __call__(obj, name=None, **kwargs):

		instance = State.getSinglton([name, obj.__name__][not name])
		D = dict(obj.__dict__)
		D.update(kwargs)

		for k, v in D.items():
			if not callable(v) and not State.isBuiltIn(k):
				setattr(instance, k, v)

			if callable(v) and k in State.Valid_Methods:
				if k in State.__dict__:
					setattr(instance, v, State.__dict__[k])


		return instance

	def __new__(obj, name=None, bases=None, ns=None, **kwargs):
		return State.__call__(obj, name, **ns)

