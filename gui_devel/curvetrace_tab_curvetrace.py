##########################
# GUI for CURVETRACE Tab #
##########################


try:
	import wx
	import logging
	import math
	import numpy as np
	
	from curvetrace_constants import GUI_STATICBOX_MARGIN_HOR, GUI_STATICBOX_MARGIN_VER, DUT_PSU_PARAMETERS, DUT_PSU_LABELS, DUT_PSU_UNITS, STEP_SCALES
	
except ImportError as e:
	logging.error( 'Could not import: ' + str(e) )
	raise







#####################################################################


# CURVETRACE tab:
class curvetrace_tab(wx.Panel):

	def __init__(self,app):
	
		# App configs:
		self._app = app
	
		# Init the panel:
		wx.Panel.__init__(self, app.frame_main.tabs)
		
		# Primary parameter:	
		# x-axis ws.StaticBox
		self.x_axis = curvetrace_controlled_parameter_StaticBox(self, self._app, 'Primary Parameter (x-axis)', 'U1')
		
		# Secondary parameter:	
		# curves ws.StaticBox
		self.curves = curvetrace_controlled_parameter_StaticBox(self, self._app, 'Secondary Parameter (curves)', 'U2')
		
		# Measured parameter:
		# y-axis ws.StaticBox
		self.y_axis = curvetrace_measured_parameter_StaticBox(self, self._app, 'Measured parameter (y-axis)', 'I1')
		
		# Button to run curve tracing:
		run_btn = wx.Button(self, label="Run...", size=(80,60))
		run_btn.Bind(wx.EVT_BUTTON, self.on_run_btn)
				
		# Arrange boxes in main_sizer:
		vsizer = wx.BoxSizer(wx.VERTICAL)
		vsizer.AddSpacer(GUI_STATICBOX_MARGIN_VER)
		vsizer.AddStretchSpacer(prop=1)
		
		vsizer.Add(self.x_axis.sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, GUI_STATICBOX_MARGIN_HOR)
		vsizer.AddSpacer(GUI_STATICBOX_MARGIN_VER)
		vsizer.AddStretchSpacer(prop=1)
		
		vsizer.Add(self.curves.sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, GUI_STATICBOX_MARGIN_HOR)
		vsizer.AddSpacer(GUI_STATICBOX_MARGIN_VER)
		vsizer.AddStretchSpacer(prop=1)
		
		vsizer.Add(self.y_axis.sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, GUI_STATICBOX_MARGIN_HOR)
		vsizer.AddSpacer(GUI_STATICBOX_MARGIN_VER)
		vsizer.AddStretchSpacer(prop=1)
		
		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		hsizer.AddStretchSpacer(1)
		hsizer.Add(run_btn, 0)
		hsizer.AddStretchSpacer(1)
		
		vsizer.Add(hsizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, GUI_STATICBOX_MARGIN_HOR)	
		vsizer.AddSpacer(GUI_STATICBOX_MARGIN_VER)
		vsizer.AddStretchSpacer(prop=1)
		self.SetSizer(vsizer)
		
	def on_run_btn(self, e):
		logging.debug('Called on_run_btn')



# wx-StaticBox for x axis
class curvetrace_controlled_parameter_StaticBox(wx.StaticBox):

	def __init__(self, parent, app, label, default_par):
	
		# init the wx.StaticBox:
		super(curvetrace_controlled_parameter_StaticBox, self).__init__(parent, label=label)
	
		# App configs and objects:
		self._app = app
		
		# parameter choice:
		kpar = DUT_PSU_PARAMETERS.index(default_par)
		self._parameter = wx.Choice(self, choices = DUT_PSU_LABELS)
		self._parameter.SetSelection(kpar)
		self._parameter.Bind(wx.EVT_CHOICE, self.on_parameter)
		
		# x-axis start/step/end/scaling:
		logging.debug('...add smart max/min limits for GUI based on axis parameter and PSU specs...')

		# parameter scaling:
		self._step_scale  = wx.Choice(self, choices = STEP_SCALES)
		self._step_scale.SetSelection(0)

		self._start = wx.SpinCtrlDouble( self, size=(150, -1), style=wx.ALIGN_RIGHT )
		self._end   = wx.SpinCtrlDouble( self, size=(150, -1), style=wx.ALIGN_RIGHT )
		self._step_number = wx.SpinCtrl( self, size=(150, -1), style=wx.ALIGN_RIGHT )		
		self._start_label = wx.StaticText(self, label='Start (?):')
		self._end_label   = wx.StaticText(self, label='End (?):')
		self._step_preview = wx.StaticText(self, label='[show preview of step values here]')
		self._step_preview_label = wx.StaticText(self, label='Step values (?):')

		# bind events for updating things:
		self._start.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_parameter)
		self._end.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_parameter)
		self._step_number.Bind(wx.EVT_SPINCTRL, self.on_parameter)
		self._step_scale.Bind(wx.EVT_CHOICE, self.on_parameter)
		
		# Arrange controls:
		controls = wx.GridBagSizer(10,10)
		
		# x-axis parameter:
		controls.Add( wx.StaticText(self, label='Parameter:'),                 (0, 0),   flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._parameter,                                         (0, 1),   flag = wx.ALIGN_LEFT  | wx.ALIGN_CENTER_VERTICAL )
		
		# x-axis start/step/end:
		controls.Add( self._start_label,                                       (1, 0),   flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._start,                                             (1, 1),   flag = wx.ALIGN_LEFT  | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._end_label,                                         (2, 0),   flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._end,                                               (2, 1),   flag = wx.ALIGN_LEFT  | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( wx.StaticText(self, label='Number of steps:'),           (3, 0),   flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._step_number,                                       (3, 1),   flag = wx.ALIGN_LEFT  | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( wx.StaticText(self, label='Step spacing:'),              (4, 0),   flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._step_scale,                                        (4, 1),   flag = wx.ALIGN_LEFT  | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._step_preview_label,                                (5, 0),   flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._step_preview,                                      (5, 1),   flag = wx.ALIGN_LEFT  | wx.ALIGN_CENTER_VERTICAL )

		# add some extra space at the bottom:
		controls.Add ( 1, 8,                                                   (6, 1) )

		# setup sizer for the box:
		self.sizer = wx.StaticBoxSizer(self, wx.VERTICAL)
		self.sizer.Add(controls, 0, wx.CENTER)

		# adjust values/limits/ranges of controls:
		self.ctrl_setup(do_init=True)
		
		
	def get_PSU_parameter(self):
		return DUT_PSU_PARAMETERS[ self._parameter.GetSelection() ]
	
	
	def get_PSU_unit(self):
		return DUT_PSU_UNITS[ self._parameter.GetSelection() ]
	
	
	def get_PSU_min(self):
		p = self.get_PSU_parameter()
		if p == 'U1':
			val = self._app.PSU1.VMIN
		elif p == 'I1':
			val = self._app.PSU1.IMIN
		elif p == 'U2':
			val = self._app.PSU2.VMIN
		elif p == 'I2':
			val = self._app.PSU2.IMIN
		else:
			raise ValueError('Unknown parameter ' + p + '.')
		return val


	def get_PSU_max(self):
		p = self.get_PSU_parameter()
		if p == 'U1':
			val = self._app.PSU1.VMAX
		elif p == 'I1':
			val = self._app.PSU1.IMAX
		elif p == 'U2':
			val = self._app.PSU2.VMAX
		elif p == 'I2':
			val = self._app.PSU2.IMAX
		else:
			raise ValueError('Unknown parameter ' + p + '.')
		return val


	def get_PSU_res(self):
		p = self.get_PSU_parameter()
		if p == 'U1':
			val = self._app.PSU1.VRESSET
		elif p == 'I1':
			val = self._app.PSU1.IRESSET
		elif p == 'U2':
			val = self._app.PSU2.VRESSET
		elif p == 'I2':
			val = self._app.PSU2.IRESSET
		else:
			raise ValueError('Unknown parameter ' + p + '.')
		return val
		
		
	def get_step_scale(self):
		# return scaling of x steps (either 'LIN' or 'LOG')
		spacing = STEP_SCALES[self._step_scale.GetSelection()].upper()[0:3]
		if spacing not in ['LIN', 'LOG']:
			logging.error('Unknown step spacing ' + spacing + '. Assuming linear spacing...')
			spacing = 'LIN'
		return spacing

		
	def ctrl_setup(self, do_init=False):
	
		# determine min/max/stepsize depending on PSU and step spacing/scaling:
		x_res = self.get_PSU_res()
		sc = self.get_step_scale()	
		if sc == 'LIN':
			x_min = self.get_PSU_min()
			x_max = self.get_PSU_max()
			n_max = (x_max - x_min) / x_res + 1
		elif sc == 'LOG':
			x_min = max(abs(self.get_PSU_min()), x_res)
			x_max = max(abs(self.get_PSU_max()), x_res)
			# determine n_max such that the smallest step (between first and second value) is equivalent to the PSU resolution
			# note that logspace(a,b,N) = 10.^linspace(a,b,N), then consider the delta of the first two values to find the following equation:
			n_max = math.floor(1 + (np.log10(x_max)-np.log10(x_min)) / (np.log10(x_res + x_min) - np.log10(x_min)))
		else:
			logging.error('Unknown x-step scaling: ' + sc)

		# Set min/max/resolution/etc.:
		self._start.SetRange(x_min, x_max)
		self._end.SetRange(x_min, x_max)
		self._step_number.SetRange(1, n_max)
		digits = math.ceil(-math.log10(x_res)) # number of digits corresponding to PSU resolution
		self._start.SetDigits(digits)
		self._start.SetIncrement(x_res)
		self._end.SetDigits(digits)
		self._end.SetIncrement(x_res)
		
		# set initial values (only if do_init, i.e., whenn called from __init__):
		if do_init:
			self._start.SetValue(x_min)
			self._end.SetValue(x_max)
			self._step_number.SetValue(n_max)

		# set units in labels:
		unit = self.get_PSU_unit()
		self._start_label.SetLabel('Start (' + unit + '):')	
		self._end_label.SetLabel('End (' + unit + '):')
		self._step_preview_label.SetLabel('Steps (' + unit + '):')

		# steps preview:
		val = self.get_axis_steps()  # list of values
		val = ["%g" % x for x in val] # list of strings
		s   = ', '.join(val)
		max_len = 36
		if len(s) > max_len:
			# find position of last comma separator that fits into max_len:
			k = [pos for pos, char in enumerate(s) if char == ',' and pos < max_len][-1]
			if k == []:
				k = max_len
			s = s[0:k+1] + '...'
		self._step_preview.SetLabel(s)
		

	def on_parameter(self, event):
		self.ctrl_setup()
	
	
	def get_axis_steps(self):
		x1 = self._start.GetValue()
		x2 = self._end.GetValue()
		N  = self._step_number.GetValue()
		sc = self.get_step_scale()
		if sc == 'LIN':
			val = np.linspace(x1,x2,N)
		elif sc == 'LOG':
		# log scale
			if x1 == x2:
				val = (x1,)
			elif N == 1:
				val = (x1,)
			else:
				if x1 == 0:
					x1  = abs(x2)**(1/(N-1)) * np.sign(x2)
					val = (0,) + tuple(np.logspace(np.log10(x1),np.log10(x2),N-1))
				elif x2 == 0:
					x2  = abs(x1)**(1/(N-1)) * np.sign(x1)
					if abs(x1) > 1:
						val = tuple(np.logspace(np.log10(x1),np.log10(x2),N-1)) + (0,)
					else:
						val = tuple(np.logspace(np.log10(x1),np.log10(x2),N-1)) + (0,)
				else:
					val = np.logspace(np.log10(x1),np.log10(x2),N)
			
		else:
			raise ValueError('Unknown step spacing ' + spacing + '.')

		# make val unique:
		if val[0] > val[-1]:
			val = np.unique(val)[::-1]
		else:
			val = np.unique(val)
		
		# round values to resolution of PSU:
		res = self.get_PSU_res()
		val = res * np.round(val/res)

		return tuple(val)


# wx-StaticBox for y axis
class curvetrace_measured_parameter_StaticBox(wx.StaticBox):

	def __init__(self, parent, app, label, default_par):
	
		# init the wx.StaticBox:
		super(curvetrace_measured_parameter_StaticBox, self).__init__(parent, label=label)
	
		# App configs:
		self._app = app
		
		# parameter choice:
		kpar = DUT_PSU_PARAMETERS.index(default_par)
		self._parameter = wx.Choice(self, choices = DUT_PSU_LABELS)
		self._parameter.SetSelection (kpar)
		self._parameter.Bind(wx.EVT_CHOICE, self.on_parameter)

		# y-axis limit:
		logging.debug('...add smart max/min limits for GUI based on PSU specs, like with controlled parameter box...')
		self._limit = wx.SpinCtrlDouble( self, size=(150, -1), style=wx.ALIGN_RIGHT )
		self._limit_label = wx.StaticText(self, label='Limit (?):')

		# Arrange controls:
		controls = wx.GridBagSizer(10,10)
		
		# y-axis parameter:
		controls.Add( wx.StaticText(self, label='Parameter:'),                 (0, 0),   flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._parameter,                                         (0, 1),   flag = wx.ALIGN_LEFT  | wx.ALIGN_CENTER_VERTICAL )
		
		# x-axis start/step/end:
		controls.Add( self._limit_label,                                       (1, 0),   flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._limit,                                             (1, 1),   flag = wx.ALIGN_LEFT  | wx.ALIGN_CENTER_VERTICAL )

		# add some extra space at the bottom:
		controls.Add ( 1, 8,                                                   (2, 1) )

		# setup sizer for the box:
		self.sizer = wx.StaticBoxSizer(self, wx.VERTICAL)
		self.sizer.Add(controls, 0, wx.CENTER)

		# adjust values/limits/ranges of controls:
		self.ctrl_setup()
		
	def ctrl_setup (self):
		y_limit      = 3;
		y_resolution = 0.001
		y_digits     = math.ceil(-math.log10(y_resolution))
		
		self._limit.SetDigits(y_digits)
		self._limit.SetIncrement(y_resolution)
		self._limit.SetRange(0, y_limit)
		self._limit.SetValue(y_limit)
		
		logging.debug('curvetrace_yaxis_StaticBox: UNDER CONSTRUCTION -- use similar get_PSU_xyz methods as in x-axis')
		
		self._limit_label.SetLabel('Limit (' + DUT_PSU_UNITS[self._parameter.GetSelection ()] + '):')	

	def on_parameter (self, event):
		self.ctrl_setup()
