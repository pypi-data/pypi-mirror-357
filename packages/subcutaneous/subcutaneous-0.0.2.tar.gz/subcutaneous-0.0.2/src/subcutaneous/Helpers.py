

def isIterable(obj):
	if isinstance(obj, str):
		return False
	try:
		iter(obj)
		obj[0]
		return True
	except Exception:
		return False




def conditionally_defined(func=None, *args, condition=None, **kwargs):

	def _cond_def_true(func):
		return conditionally_defined(func, condition=True, **kwargs)

	def _replace_func(*args, **kwargs):
		# [Exist State 1]
		# replace with outer func

		return func


	if callable(condition):

		condition = condition(*args, **kwargs)

	### wrapper entry
	if func is not None and condition is None:
		# [Entry State 1]
		# Entry state `@conditionally_defined(function)` where EXISTS in outer namespace
		# function exists so it is true
		return _replace_func

	if condition is None and func is None:
		# [Entry State 2]  Entry state `@conditionally_defined(function)` where does NOT exist in outer namespace
		# condition to define is TRUE
		return _cond_def_true	# recursive call with True condition

	if func is None and condition:
		# [Entry State 3]
		# Only condition provided, function ASSUME must be elsewhere defined in namespace
		return _replace_func

	if func and condition:
		# [Exist State 2]
		# replace with inner function
		return func

	# [Exist State 3] Condition is False do not define!!!
	return None
