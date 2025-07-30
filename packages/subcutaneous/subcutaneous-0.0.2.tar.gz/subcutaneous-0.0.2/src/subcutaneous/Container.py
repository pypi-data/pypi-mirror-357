def container(cls):
	def new(obj, *args, **kwargs):
		raise NotImplementedError(f"{obj} is a container, __new__ is not defined")

	def init(obj, *args, **kwargs):
		raise NotImplementedError(f"{obj} is a container, __init__ is not defined")

	def call(obj, *args, **kwargs):
		raise NotImplementedError(f"{obj} is a container, __call__ is not defined")

	for name, member in list(cls.__dict__.items()):
		if callable(member):
			setattr(cls, name, staticmethod(member))
	setattr(cls, "__new__", new)
	setattr(cls, "__init__", init)
	setattr(cls, "__call__", call)

	return cls
