def _callableSync(obj, update_dict):
	if getattr(obj, "_callable", False):
		# clumsily allowing args to propagate
		args = getattr(obj, "_args", ())
		kwds = getattr(obj, "_kwargs", dict()).copy()

		shared = set(kwds) & set(update_dict)
		for k in shared:
			kwds[k] = update_dict[k]
		return obj(args, **kwds)
	return obj


def interface_required(func):

	def _wrapper(*args, **kwargs):
		try:
			sys.modules["Inference"]
		except KeyError:
			raise ImportError("Interface module is required for this functionality.")
		return func(*args, **kwargs)

	return _wrapper	# hello
