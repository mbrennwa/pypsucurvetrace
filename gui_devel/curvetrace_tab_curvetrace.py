##########################
# GUI for CURVETRACE Tab #
##########################


try:
	import wx
	import logging
	import math
	import numpy as np
	
	from curvetrace_constants import GUI_STATICBOX_MARGIN_HOR, GUI_STATICBOX_MARGIN_VER, DUT_PSU_PARAMETERS, DUT_PSU_LABELS, DUT_PSU_UNITS, X_STEP_SCALES
	
except ImportError as e:
	logging.error( 'Could not import: ' + str(e) )
	raise



# for GUI mockup without real PSU units:
_PSU1_MIN = 0.0
_PSU1_MAX = 32.0
_PSU1_RESOLUTION = 0.001





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
		self.x_axis = curvetrace_xaxis_StaticBox(self,self._app)
		
		# Secondary parameter:	
		# curves ws.StaticBox
		self.curves = curvetrace_curves_StaticBox(self,self._app)
		
		# Measured parameter:
		# y-axis ws.StaticBox
		self.y_axis = curvetrace_yaxis_StaticBox(self,self._app)
		
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
class curvetrace_xaxis_StaticBox(wx.StaticBox):

	def __init__(self,parent,app):
	
		# init the wx.StaticBox:
		super(curvetrace_xaxis_StaticBox, self).__init__(parent, label='Primary Parameter (x-axis)')
	
		# App configs:
		self._app = app
		
		# x-axis parameter:
		self._parameter = wx.Choice(self, choices = DUT_PSU_LABELS)
		self._parameter.SetSelection (0)
		self._parameter.Bind(wx.EVT_CHOICE, self.on_parameter)
		
		# x-axis start/step/end/scaling:
		logging.debug('...add smart max/min limits for GUI based on axis parameter and PSU specs...')
		self._start = wx.SpinCtrlDouble( self, size=(150, -1), style=wx.ALIGN_RIGHT, initial=_PSU1_MIN )
		self._end   = wx.SpinCtrlDouble( self, size=(150, -1), style=wx.ALIGN_RIGHT, initial=_PSU1_MAX )
		self._step_number = wx.SpinCtrl( self, size=(150, -1), style=wx.ALIGN_RIGHT, min=1, max=1001, initial=int(_PSU1_MAX)+1 )		
		self._start_label = wx.StaticText(self, label='Start (?):')
		self._end_label   = wx.StaticText(self, label='End (?):')
		self._step_scale  = wx.Choice(self, choices = X_STEP_SCALES)
		self._step_scale.SetSelection (0)
		self._step_preview = wx.StaticText(self, label='[show preview of step values here]')
		self._step_preview_label = wx.StaticText(self, label='Step values (?):')

		# set digits and increments:
		digits = math.ceil(-math.log10(_PSU1_RESOLUTION)) # number of digits corresponding to PSU resolution
		self._start.SetDigits(digits)
		self._start.SetIncrement(_PSU1_RESOLUTION)
		self._end.SetDigits(digits)
		self._end.SetIncrement(_PSU1_RESOLUTION)

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
		self.ctrl_setup()
		
		
	def get_step_scale(self):
		# return scaling of x steps (either 'LIN' or 'LOG')
		spacing = X_STEP_SCALES[self._step_scale.GetSelection()].upper()[0:3]
		if spacing not in ['LIN', 'LOG']:
			logging.error('Unknown step spacing ' + spacing + '. Assuming linear spacing...')
			spacing = 'LIN'
		return spacing

		
	def ctrl_setup(self):

		# Set min/max/resolution depending on PSU1 and LIN or LOG scale:
		logging.debug('Using dummy values for PSU1 min/max/resolution for now...')
		sc = self.get_step_scale()	
		if sc == 'LIN':
			x_min = _PSU1_MIN
			x_max = _PSU1_MAX
		elif sc == 'LOG':
			x_min = max(abs(_PSU1_MIN), _PSU1_RESOLUTION)
			x_max = max(abs(_PSU1_MAX), _PSU1_RESOLUTION)
		else:
			logging.error('Unknown x-step scaling: ' + sc)
			
		self._start.SetRange(x_min, x_max)
		self._end.SetRange(x_min, x_max)




		k = self._parameter.GetSelection ()
		self._start_label.SetLabel('Start (' + DUT_PSU_UNITS[k] + '):')	
		self._end_label.SetLabel('End (' + DUT_PSU_UNITS[k] + '):')
		self._step_preview_label.SetLabel('Steps (' + DUT_PSU_UNITS[k] + '):')

		
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
		logging.debug('Called on_parameter: adjust x-axis limit and units in the GUI, and maybe other things')
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
			logging.error('Unknown step spacing ' + spacing + '.')

		# make val unique:
		if val[0] > val[-1]:
			val = np.unique(val)[::-1]
		else:
			val = np.unique(val)

		return tuple(val)


# wx-StaticBox for y axis
class curvetrace_yaxis_StaticBox(wx.StaticBox):

	def __init__(self,parent,app):
	
		# init the wx.StaticBox:
		super(curvetrace_yaxis_StaticBox, self).__init__(parent, label='Measured Parameter (y-axis)')
	
		# App configs:
		self._app = app
		
		# x-axis parameter:
		self._parameter = wx.Choice(self, choices = DUT_PSU_LABELS)
		self._parameter.SetSelection (1)
		self._parameter.Bind(wx.EVT_CHOICE, self.on_parameter)
		
		# y-axis limit:
		logging.debug('...add smart max/min limits for GUI based on PSU specs...')
		self._limit = wx.SpinCtrlDouble( self, size=(150, -1), style=wx.ALIGN_RIGHT )
		self._limit_label = wx.StaticText(self, label='Limit (?):')

		# Arrange controls:
		controls = wx.GridBagSizer(10,10)
		
		# x-axis parameter:
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
		self._limit_label.SetLabel('Limit (' + DUT_PSU_UNITS[self._parameter.GetSelection ()] + '):')	

	def on_parameter (self, event):
		self.ctrl_setup()
		


# wx-StaticBox for curves
class curvetrace_curves_StaticBox(wx.StaticBox):

	def __init__(self,parent,app):
	
		# init the wx.StaticBox:
		super(curvetrace_curves_StaticBox, self).__init__(parent, label='Secondary Parameter (curves)')
	
		# App configs:
		self._app = app
		
		# x-axis parameter:
		self._parameter = wx.Choice(self, choices = ['U\u2081','I\u2081','U\u2082','I\u2082'])
		self._parameter.SetSelection (2)
		self._parameter.Bind(wx.EVT_CHOICE, self.on_parameter)
		
		# curves start/step/end:
		logging.debug('...add smart max/min limits for GUI based on axis parameter and PSU specs...')
		self._start = wx.SpinCtrlDouble( self, size=(150, -1), style=wx.ALIGN_RIGHT )
		self._end   = wx.SpinCtrlDouble( self, size=(150, -1), style=wx.ALIGN_RIGHT )
		self._step  = wx.SpinCtrlDouble( self, size=(150, -1), style=wx.ALIGN_RIGHT )
		self._start_label = wx.StaticText(self, label='Start (?):')
		self._end_label   = wx.StaticText(self, label='End (?):')
		self._step_label  = wx.StaticText(self, label='Step size (?):')

		# Arrange controls:
		controls = wx.GridBagSizer(10,10)
		
		# x-axis parameter:
		controls.Add( wx.StaticText(self, label='Parameter:'),                 (0, 0),   flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._parameter,                                         (0, 1),   flag = wx.ALIGN_LEFT  | wx.ALIGN_CENTER_VERTICAL )
		
		# x-axis start/step/end:
		controls.Add( self._start_label,                                       (1, 0),   flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._start,                                             (1, 1),   flag = wx.ALIGN_LEFT  | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._step_label,                                        (2, 0),   flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._step,                                              (2, 1),   flag = wx.ALIGN_LEFT  | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._end_label,                                         (3, 0),   flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._end,                                               (3, 1),   flag = wx.ALIGN_LEFT  | wx.ALIGN_CENTER_VERTICAL )

		# add some extra space at the bottom:
		controls.Add ( 1, 8,                                                   (4, 1) )

		# setup sizer for the box:
		self.sizer = wx.StaticBoxSizer(self, wx.VERTICAL)
		self.sizer.Add(controls, 0, wx.CENTER)

		# adjust values/limits/ranges of controls:
		self.ctrl_setup()
		
	def ctrl_setup (self):
		logging.debug('setting up curves controls -- change: look this up from the PSU / axis parameter and the DUT config/limits...')
		min_val    = 0;
		max_val    = 10;
		min_step   = 0.1;
		resolution = 0.001
		digits     = math.ceil(-math.log10(resolution))
		
		self._start.SetDigits(digits)
		self._start.SetIncrement(resolution)
		self._start.SetRange(min_val, max_val)
		self._start.SetValue(min_val)
		
		self._end.SetDigits(digits)
		self._end.SetIncrement(resolution)
		self._end.SetRange(min_val, max_val)
		self._end.SetValue(max_val)

		self._step.SetDigits(digits)
		self._step.SetIncrement(resolution)
		self._step.SetRange(resolution, max_val-min_val)
		self._step.SetValue(resolution)

		k = self._parameter.GetSelection ()
		self._start_label.SetLabel('Start (' + DUT_PSU_UNITS[k] + '):')	
		self._end_label.SetLabel('End (' + DUT_PSU_UNITS[k] + '):')	
		self._step_label.SetLabel('Step size (' + DUT_PSU_UNITS[k] + '):')			
		
	def on_parameter (self, event):
		self.ctrl_setup()

