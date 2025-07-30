from .ModuleMethods import modulemethod, ModuleFactory


def state(cls):
	name = cls.__name__
	ns = cls.__dict__
	bases = tuple()
	return State(name, bases, ns)


class State(ModuleFactory):
	Valid_Methods = {
		"tick",
		"event",
		"view",
		"_runner",
		"_worker",
		"pullFunction",
		"getItems",
	}
	Valid_Attrs = {"__TICK__", "__EVENT__", "__VIEW__"}

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
