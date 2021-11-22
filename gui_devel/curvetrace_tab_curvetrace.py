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


#####################################################################


# CURVETRACE tab:
class curvetrace_tab(wx.Panel):

	def __init__(self,app):
	
		# App configs:
		self._app = app
	
		# Init the panel:
		wx.Panel.__init__(self, app.frame_main.tabs)
				
		# x-axis ws.StaticBox
		self.x_axis = curvetrace_xaxis_StaticBox(self,self._app)
		
		# y-axis ws.StaticBox
		self.y_axis = curvetrace_yaxis_StaticBox(self,self._app)
		
		# curves ws.StaticBox
		self.curves = curvetrace_curves_StaticBox(self,self._app)
		
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
		vsizer.Add(self.y_axis.sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, GUI_STATICBOX_MARGIN_HOR)
		vsizer.AddSpacer(GUI_STATICBOX_MARGIN_VER)
		vsizer.AddStretchSpacer(prop=1)
		vsizer.Add(self.curves.sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, GUI_STATICBOX_MARGIN_HOR)
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
		super(curvetrace_xaxis_StaticBox, self).__init__(parent, label='Horizontal Axis')
	
		# App configs:
		self._app = app
		
		# x-axis parameter:
		self._parameter = wx.Choice(self, choices = DUT_PSU_LABELS)
		self._parameter.SetSelection (0)
		self._parameter.Bind(wx.EVT_CHOICE, self.on_parameter)
		
		# x-axis start/step/end/scaling:
		logging.debug('...add smart max/min limits for GUI based on axis parameter and PSU specs...')
		self._start = wx.SpinCtrlDouble( self, size=(150, -1), style=wx.ALIGN_RIGHT )
		self._end   = wx.SpinCtrlDouble( self, size=(150, -1), style=wx.ALIGN_RIGHT )
		self._step_number = wx.SpinCtrl( self, size=(150, -1), style=wx.ALIGN_RIGHT, min=1, max=1001, initial=10 )		
		self._start_label = wx.StaticText(self, label='Start (?):')
		self._end_label   = wx.StaticText(self, label='End (?):')
		self._step_scale  = wx.Choice(self, choices = X_STEP_SCALES)
		self._step_scale.SetSelection (0)
		self._step_preview = wx.StaticText(self, label='[show preview of step values here]')

		logging.debug('setting up x-axis controls -- change: look this up from the PSU / axis parameter and the DUT config/limits...')
		x_min_val    = 0;
		x_max_val    = 10;
		x_min_step   = 0.1;
		x_resolution = 0.001
		x_digits     = math.ceil(-math.log10(x_resolution))
		
		self._start.SetDigits(x_digits)
		self._start.SetIncrement(x_resolution)
		self._start.SetRange(x_min_val, x_max_val)
		self._start.SetValue(x_min_val)
		
		self._end.SetDigits(x_digits)
		self._end.SetIncrement(x_resolution)
		self._end.SetRange(x_min_val, x_max_val)
		self._end.SetValue(x_max_val)

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
		controls.Add( wx.StaticText(self, label='Step values (?):'),              (5, 0),   flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._step_preview,                                      (5, 1),   flag = wx.ALIGN_LEFT  | wx.ALIGN_CENTER_VERTICAL )

		# add some extra space at the bottom:
		controls.Add ( 1, 8,                                                   (6, 1) )

		# setup sizer for the box:
		self.sizer = wx.StaticBoxSizer(self, wx.VERTICAL)
		self.sizer.Add(controls, 0, wx.CENTER)

		# adjust values/limits/ranges of controls:
		self.ctrl_setup()
		
	def ctrl_setup (self):

		### self._step.SetDigits(x_digits)
		### self._step.SetIncrement(x_resolution)
		### self._step.SetRange(x_resolution, x_max_val-x_min_val)
		### self._step.SetValue(x_resolution)
		k = self._parameter.GetSelection ()
		self._start_label.SetLabel('Start (' + DUT_PSU_UNITS[k] + '):')	
		self._end_label.SetLabel('End (' + DUT_PSU_UNITS[k] + '):')	
		### self._step_label.SetLabel('Step size (' + DUT_PSU_UNITS[k] + '):')
		
		# steps preview:
		val = self.get_xaxis_steps()  # list of values
		val = ["%g" % x for x in val] # list of strings
		s   = ', '.join(val)
		self._step_preview.SetLabel(s)
		

	def on_parameter(self, event):
		logging.debug('Called on_parameter: adjust x-axis limit and units in the GUI, and maybe other things')
		self.ctrl_setup()
		
	def get_xaxis_steps(self):
		x1 = self._start.GetValue()
		x2 = self._end.GetValue()
		N  = self._step_number.GetValue()
		spacing = X_STEP_SCALES[self._step_scale.GetSelection()].upper()[0:3]
		if spacing not in ['LIN', 'LOG']:
			logging.error('Unknown step spacing ' + spacing + '. Assuming linear spacing...')
			spacing = 'LIN'
		if spacing == 'LIN':
			val = np.linspace(x1,x2,N)
		else:
			val = np.logspace(np.log10(x1),np.log10(x2),N)
			logging.debug('Need to check for x1, x2 == 0 when doing log scale...')
		return val


# wx-StaticBox for y axis
class curvetrace_yaxis_StaticBox(wx.StaticBox):

	def __init__(self,parent,app):
	
		# init the wx.StaticBox:
		super(curvetrace_yaxis_StaticBox, self).__init__(parent, label='Vertical Axis')
	
		# App configs:
		self._app = app
		
		# x-axis parameter:
		self._parameter = wx.Choice(self, choices = DUT_PSU_LABELS)
		self._parameter.SetSelection (1)
		self._parameter.Bind(wx.EVT_CHOICE, self.on_parameter)
		
		# y-axis limit:
		logging.debug('...add smart max/min limits for GUI based on axis parameter and PSU specs...')
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
		logging.debug('setting up y-axis controls -- change: look this up from the PSU / axis parameter and the DUT config/limits...')
		y_limit      = 3;
		y_resolution = 0.001
		y_digits     = math.ceil(-math.log10(y_resolution))
		
		self._limit.SetDigits(y_digits)
		self._limit.SetIncrement(y_resolution)
		self._limit.SetRange(0, y_limit)
		self._limit.SetValue(y_limit)		
		self._limit_label.SetLabel('Start (' + DUT_PSU_UNITS[self._parameter.GetSelection ()] + '):')	

	def on_parameter (self, event):
		logging.debug('Called on_parameter: adjust y-axis limit and units in the GUI, and maybe other things')
		self.ctrl_setup()
		


# wx-StaticBox for curves
class curvetrace_curves_StaticBox(wx.StaticBox):

	def __init__(self,parent,app):
	
		# init the wx.StaticBox:
		super(curvetrace_curves_StaticBox, self).__init__(parent, label='Curves')
	
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
		logging.debug('Called on_parameter: adjust curves limit and units in the GUI, and maybe other things')
		self.ctrl_setup()

