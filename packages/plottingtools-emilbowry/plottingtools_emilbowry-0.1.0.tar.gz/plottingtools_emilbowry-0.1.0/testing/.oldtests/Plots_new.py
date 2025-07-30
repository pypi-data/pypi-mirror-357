class widgetContainer:
	pass


import ipywidgets as widgets
from IPython.display import display
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.colors as colors
import plotly.io as pio


pio.renderers.default = "notebook"


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


def _callableSync(obj, update_dict):
	if getattr(obj, "_callable", False):

		# allow assigining params as attributes for simple interfacing
		args = getattr(obj, "_args", ())
		kwds = getattr(obj, "_kwargs", dict()).copy()

		shared = set(kwds) & set(update_dict)
		for k in shared:
			kwds[k] = update_dict[k]
		return obj(*args, **kwds)
	return obj


def getTraceIndex(row, col, n_cols):

	return (row - 1) * n_cols + (col - 1)


class sliderContainer(widgetContainer):
	@staticmethod
	def _idx(val, data):
		return int(round((val - data[0]) / (data[1] - data[0])))

	@staticmethod
	def _closedIdx(data):
		def _inner(val):
			return sliderContainer._idx(val, data)

		return _inner

	@staticmethod
	def createSlider(*, value, _min, _max, step, description, continuous_update, **kwargs):
		slider = widgets.FloatSlider(
			value=value,
			min=_min,
			max=_max,
			step=step,
			description=description,
			continuous_update=continuous_update,
		)

		return slider

	def _createSlider(self, _slider_dict, **kwargs):
		slider_name = list(_slider_dict.keys())[0]
		slider_dict = list(_slider_dict.values())[0]
		slider_data = slider_dict["data"]
		creation_dict = dict(
			value=float(slider_data[0]),
			_min=float(slider_data.min()),
			_max=float(slider_data.max()),
			step=float(slider_data[1] - slider_data[0]),
			description=f"{slider_name}",
			continuous_update=slider_dict.get("continuous_update", False),
		)
		creation_dict.update(**kwargs)

		slider = sliderContainer.createSlider(**creation_dict)

		self.Sliders[slider_name] = slider
		self.Slider_idxFn[slider_name] = sliderContainer._closedIdx(slider_data)
		self.Sliders[slider_name].observe(self.refresh, names="value")

	@property
	def sliders(self):
		return list(self.Sliders.values())

	def __new__(cls, slider_dicts, update_functions, data, **kwargs):
		instance = object.__new__(cls)

		def _closed_init(slider_dicts, update_functions, data, **kwargs):
			def _inner(fig, **kwds):
				kwargs.update(kwds)
				instance.__init__(
					fig=fig,
					slider_dicts=slider_dicts,
					update_functions=update_functions,
					data=data,
					**kwargs,
				)

				return instance

			return _inner

		return _closed_init(slider_dicts, update_functions, data, **kwargs)

	def __init__(self, fig, slider_dicts, update_functions, data, **kwargs):

		self.fig = fig
		self.Sliders = dict()
		self.Slider_idxFn = dict()
		for i in slider_dicts:
			self._createSlider(i)
		for k, v in kwargs.items():
			setattr(self, k, v)
		self.updateFunctions = update_functions	# list probably
		self.data = data
		self.controls = widgets.VBox(self.sliders)	# , layout=widgets.Layout(width="100%")
		self.container = widgets.VBox([self.controls, self.fig])

	def _refreshSliders(self, *args, **kwargs):
		slider_indices = dict()
		Slider_Values = dict()
		for k, v in self.Sliders.items():
			value = v.value
			slider_indices[k] = self.Slider_idxFn[k](value)
			Slider_Values[k] = value
		return slider_indices, Slider_Values

	def _updateFigure(self, slider_indices, values, *args, **kwargs):

		for fn in self.updateFunctions:
			fn(fig=self.fig, data=self.data, **locals())

	def refresh(self, *args, **kwargs):
		self.__call__(*args, **kwargs)

	def __call__(self, *args, **kwargs):
		slider_indices, Slider_Values = self._refreshSliders(*args, **kwargs)
		with self.fig.batch_update():
			self._updateFigure(slider_indices, Slider_Values)


@container
class Figure_Methods:
	EMPTY = [BaseTraceType("empty")]

	def getTraceIndex(row, col, n_cols):

		return (row - 1) * n_cols + (col - 1)

	def inverseTraceIndex(index, n_cols):

		_row = index // n_cols	# [NOTE] actual row is _row +1
		_col = index % n_cols	# [NOTE] actual col is _col +1
		return _row, _col

	def formatHetrogenous(traces, removeNone=True):

		arr = np.array(traces, dtype=object)
		if np.ndim(arr) == 0:
			return None
		elif np.ndim(arr) == 1:
			pass
		else:
			for r in range(np.ndim(arr)):
				arr = np.hstack(arr)
		if removeNone:
			return arr[arr != None].tolist()

		return arr.tolist()

	def flattenHetrogenous(traces):
		if np.ndim(np.array(traces, dtype=object)) <= 1:
			return traces
		else:
			return np.concatenate(np.array(traces, dtype=object))

	def getTracesSize(traces):
		arr = np.array(traces, dtype=object)
		if np.ndim(arr) <= 1:
			return 1
		return np.size(arr[arr != None])

	def getSuffix(idx):
		axis_idx = ""
		if idx == 0:
			return axis_idx
		return str(idx + 1)

	def _updateFigure(fig, trace, idx, *args, **kwargs):
		suffix = Figure_Methods.getSuffix(idx)

		if "z" in trace:
			trace._orphan_props["scene"] = f"scene{suffix}"

			if fig._grid_ref:

				try:
					n_cols = len(fig._grid_ref[0])
					row, col = Figure_Methods.inverseTraceIndex(idx, n_cols)
					if not fig._grid_ref[row][col][0].subplot_type == "scene":
						# [NOTE] using NotImplementedError as a low probability of intercept raise
						raise NotImplementedError

				except NotImplementedError as e:

					y_domain = fig.layout[f"yaxis{suffix}"]["domain"]
					x_domain = fig.layout[f"xaxis{suffix}"]["domain"]
					scene = {"domain": {"x": x_domain, "y": y_domain}}
					fig.layout[f"scene{suffix}"] = scene

					# [NOTE]  The figure attributes `yaxis{suffix}` and `xaxis{suffix}` don't need to be kept to preserve indexing
					fig.layout.pop(f"yaxis{suffix}", None)
					fig.layout.pop(f"xaxis{suffix}", None)

		fig._data[idx] = trace._orphan_props

		return fig

	def processOrphan(orphan, idx):
		suffix = Figure_Methods.getSuffix(idx)
		orphan_update = dict()

		if "z" in orphan:
			orphan_update.update({"scene": f"scene{suffix}"})
			orphan_update.update({"zaxis": f"z{suffix}"})

		orphan_update = {"xaxis": f"x{suffix}", "yaxis": f"y{suffix}"}

		orphan._orphan_props.update(orphan_update)
		return orphan

	def _appendData(fig, data, idx, *args, **kwargs):
		suffix = Figure_Methods.getSuffix(idx)

		for k, v in data.items():
			if k != "uid":
				_data = getattr(fig.data[idx], k, [])
				if _data is None:
					_data = []
				_data = list(_data)

				_data.extend(v)
				fig.data[idx][k] = _data
			if k == "uid":
				fig.data[idx][k] = v

		return fig

	def _modifyFigure(fig, trace, idx, *args, _modification_type="append", **kwargs):
		target_trace = fig.data[idx]
		if target_trace.type != trace.type:
			fig = Figure_Methods._updateFigure(fig, trace, idx, *args, **kwargs)
		else:
			data = {"x": trace.x, "y": trace.y}
			if "z" in trace:
				data["z"] = trace["z"]
			if "uid" in trace:

				data["uid"] = trace["uid"]
			if _modification_type == "append":

				fig = Figure_Methods._appendData(fig, data, idx, *args, **kwargs)

		return fig

	def modifyFigure(fig, flat_traces, idx=0, *args, **kwargs):
		orphaned = []
		if isinstance(flat_traces, BaseTraceType):
			fig = Figure_Methods._modifyFigure(fig, flat_traces, idx=idx)
			return fig, orphaned
		elif isinstance(flat_traces, list):
			trace = flat_traces[0]
			fig, orphans = Figure_Methods.modifyFigure(fig, trace, idx=idx)
			orphaned.append(orphans)

			_ophans = flat_traces[1:]	# [NOTE] unformatted hence _ prefix
			for o in list(_ophans):
				orphaned.append(Figure_Methods.processOrphan(o, idx=idx))
		elif isinstance(flat_traces, np.ndarray):
			for i, trace in enumerate(flat_traces):
				fig, orphans = Figure_Methods.modifyFigure(fig, trace, idx=i + idx)
			orphaned.append(orphans)
		elif flat_traces is None:
			pass
		else:
			raise TypeError(f"Unknown Trace Type: {type(flat_traces)} | Trace: {flat_traces}")

		orphaned = Figure_Methods.flattenHetrogenous(orphaned)
		return fig, orphaned

	def initialiseFigure(traces, *, fig_parameters, fig_type, **kwargs):
		size = Figure_Methods.getTracesSize(traces)
		if size > 1:

			subplot_parameters = fig_parameters
			fig_parameters = dict()
		fig = go.Figure(data=[None] * size, skip_invalid=True, **fig_parameters)

		if size > 1:
			dimensions = [len(traces), len(traces[0])]

			rows = (dimensions[0:1] or [1])[0]
			cols = (dimensions[1:2] or [1])[0]
			fig = make_subplots(figure=fig, rows=rows, cols=cols, **subplot_parameters)

		return fig

	def addOrphans(fig, orphans):
		flat_traces = Figure_Methods.formatHetrogenous(orphans)
		if np.size(np.array(flat_traces, dtype=object)) == 0:
			return fig
		if orphans is None:
			return fig

		fig.add_traces(orphans)
		return fig


class Plots_New:

	DEFAULT_COLORS = colors.DEFAULT_PLOTLY_COLORS
	LEN_DEFAULT_COLORS = len(DEFAULT_COLORS)

	@staticmethod
	def createGraph(graph_parameters, display_graph=True, **kwargs):

		traces = graph_parameters["traces"]
		fig_parameters = graph_parameters.get("fig_parameters", dict())
		fig_type = graph_parameters.get("fig_type", None)
		layout = graph_parameters.get("layout", dict())

		fig = Figure_Methods.initialiseFigure(
			traces, fig_parameters=fig_parameters, fig_type=fig_type, **kwargs
		)

		flat_traces = Figure_Methods.flattenHetrogenous(traces)
		with fig.batch_update():

			fig, orphans = Figure_Methods.modifyFigure(fig, flat_traces, **kwargs)
			fig = Figure_Methods.addOrphans(fig, orphans)

			if fig_type == "Widget":
				fig = go.FigureWidget(fig)
		fig.update_layout(layout)

		functions = graph_parameters.get("functions", None)
		fig_functions = graph_parameters.get("fig_functions", None)
		if fig_functions:
			for k, v in fig_functions.items():
				func = getattr(fig, k)	# [1.XXX] Cant remember why we can pull it from the fig
				func = _callableSync(func, locals())

				func(v, **kwargs)

		if functions:
			for k, v in functions.items():
				func = getattr(fig, k)	# [1.XXX]
				# func = _callableSync(func,locals())
				func(fig, v, **kwargs)

		if display_graph:
			if fig_type == "Widget":
				# [TODO] add superclass figureContainer, ensure _container is related to this
				_container = graph_parameters.get("container", None)
				_container = _container(fig)
				if isinstance(_container, widgetContainer):
					display(_container.container)
				else:
					display(_container)

			else:
				fig.show()

		return fig

	@staticmethod
	def graphScatter(data, *, normalise_x_axis=False, **kwargs):
		Y = data[0]
		try:
			X = data[1]
		except:
			X = list(range(len(Y)))
		if X is None:
			X = list(range(len(Y)))

		trace = go.Scatter(x=X, y=Y, **kwargs)

		layout = dict(
			barmode="overlay",
			bargap=0,
		)
		graph_parameters = {
			"traces": trace,
			"layout": layout,
		}

		return graph_parameters

	@staticmethod
	def graphVariational(data, **kwargs):

		def getKwargVars(**kwargs):

			alpha_name = kwargs["alpha_name"] if "alpha_name" in kwargs else "alpha"

			beta_name = kwargs["beta_name"] if "beta_name" in kwargs else "beta"

			function_name = kwargs["function_name"] if "function_name" in kwargs else "function"

			alpha_range = (
				kwargs["alpha_range"] if "alpha_range" in kwargs else (0, alpha_len - 1)
			)
			beta_range = kwargs["beta_range"] if "beta_range" in kwargs else (0, beta_len - 1)
			return alpha_name, beta_name, alpha_range, beta_range, function_name

		dimensions = np.shape(data)
		if dimensions[0] > 2:
			_matrix = data
		else:
			raise

		alpha_len, beta_len = len(_matrix), len(_matrix[0])
		alpha_name, beta_name, alpha_range, beta_range, function_name = getKwargVars(**kwargs)

		matrix = np.stack(_matrix.tolist())	# beta × alpha × T

		ymax = np.max(_matrix.tolist())
		X = matrix[0][0].shape[0]

		x = np.arange(X)

		Alpha = np.linspace(*alpha_range, alpha_len)

		Beta = np.linspace(*beta_range, beta_len)

		Xalpha, Yalpha = np.meshgrid(x, Alpha)	# left surface  (beta fixed)
		Xbeta, Ybeta = np.meshgrid(x, Beta)	# right surface (alpha fixed)

		beta_idx, alpha_idx = 0, 0

		alpha_surface = go.Surface(
			z=matrix[beta_idx],
			x=Xalpha,
			y=Yalpha,
			colorscale="Viridis",
			cmin=0,
			cmax=ymax,
			showscale=True,
		)

		beta_surface = go.Surface(
			z=matrix[:, alpha_idx],
			x=Xbeta,
			y=Ybeta,
			colorscale="Viridis",
			cmin=0,
			cmax=ymax,
			showscale=True,
		)

		scatter = go.Scatter(
			x=x, y=matrix[beta_idx, alpha_idx], mode="lines", uid="variational_scatter"
		)

		camera = dict(
			eye=dict(x=-1.8, y=-1.8, z=1.0),
			up=dict(x=0.0, y=0.0, z=1.0),
			center=dict(x=0.0, y=0.0, z=0.0),
		)
		fig_parameters = dict(
			specs=[	# [TODO] Remove Specs since it is infereable now
				[{"type": "surface"}, {"type": "surface"}],
				[{"colspan": 2, "type": "xy"}, None],
			],
			vertical_spacing=0.08,
			row_heights=[0.75, 0.25],
		)

		layout = dict(
			width=1400,
			height=850,
			scene=dict(
				xaxis_title="x",
				yaxis_title=f"{alpha_name}",
				zaxis_title=f"{function_name}",
				camera=camera,
			),
			scene2=dict(
				xaxis_title="x",
				yaxis_title=f"{beta_name}",
				zaxis_title=f"{function_name}",
				camera=camera,
			),
		)

		def beta_update(*, fig, slider_indices, data, **kwargs):
			i = slider_indices[f"{beta_name}"]
			fig.data[0].z = data[i]

		def alpha_update(*, fig, slider_indices, data, **kwargs):
			j = slider_indices[f"{alpha_name}"]

			fig.data[0].z = data[:, j]

		def timeseries_update(*, fig, slider_indices, data, **kwargs):
			i = slider_indices[f"{beta_name}"]
			j = slider_indices[f"{alpha_name}"]

			fig.data[2].y = data[i, j]

		def title_update(*, fig, slider_indices, data, values, **kwargs):
			i = slider_indices[f"{beta_name}"]
			j = slider_indices[f"{alpha_name}"]
			beta_val = values[f"{beta_name}"]
			alpha_val = values[f"{alpha_name}"]

			_function_name = kwargs.get("function_name", f"{function_name}")

			fig.layout.title.text = (
				f"{_function_name} –  {alpha_name} = {alpha_val:.2f}, " f"{beta_name} = {beta_val:.2f}"
			)

		update_fns = [beta_update, alpha_update, timeseries_update, title_update]
		alpha_slider_dict = {f"{alpha_name}": {"data": Alpha}}
		beta_slider_dict = {f"{beta_name}": {"data": Beta}}
		slider_dicts = [beta_slider_dict, alpha_slider_dict]
		wContainer = sliderContainer(slider_dicts, update_fns, matrix)

		graph_parameters = {
			"traces": [[alpha_surface, beta_surface], [scatter, None]],
			"layout": layout,
			"fig_type": "Widget",
			"fig_parameters": fig_parameters,	# Not strictly necessary for specs
			"container": wContainer,
		}
		return graph_parameters
