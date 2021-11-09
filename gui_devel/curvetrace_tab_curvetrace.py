##########################
# GUI for CURVETRACE Tab #
##########################


try:
	import wx
	import logging
	
	from curvetrace_constants import GUI_STATICBOX_MARGIN_HOR, GUI_STATICBOX_MARGIN_VER
		
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
		
		# Add a dummy text label:
		### box = wx.BoxSizer(wx.VERTICAL)
		### lbl = wx.StaticText(self,-1,style = wx.ALIGN_CENTER)
		### lbl.SetLabel("This tab\n is for\n control of the\n curve tracing.")
		### box.Add(lbl,0,wx.ALIGN_CENTER)
		### self.SetSizer(box) 
		
		# x-axis ws.StaticBox
		self.x_axis = curvetrace_xaxis_StaticBox(self,self._app)
		
		# y-axis ws.StaticBox
		self.y_axis = curvetrace_yaxis_StaticBox(self,self._app)
		
		# curves ws.StaticBox
		self.curves = curvetrace_curves_StaticBox(self,self._app)
		
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
		self.SetSizer(vsizer)



# wx-StaticBox for x axis
class curvetrace_xaxis_StaticBox(wx.StaticBox):

	def __init__(self,parent,app):
	
		# init the wx.StaticBox:
		super(curvetrace_xaxis_StaticBox, self).__init__(parent, label='Horizontal Axis')
	
		# App configs:
		self._app = app
		
		# x-axis parameter:
		self._parameter = wx.Choice(self, choices = ['U\u2081','I\u2081','U\u2082','I\u2082'])
		self._parameter.SetSelection (0)
		self._parameter.Bind(wx.EVT_CHOICE, self.on_parameter)
		
		# x-axis start/step/end:
		logging.debug('...add smart max/min limits for GUI based on axis parameter and PSU specs...')
		self._start = wx.SpinCtrlDouble( self, size=(150, -1), style=wx.ALIGN_RIGHT )
		self._end   = wx.SpinCtrlDouble( self, size=(150, -1), style=wx.ALIGN_RIGHT )
		self._step  = wx.SpinCtrlDouble( self, size=(150, -1), style=wx.ALIGN_RIGHT )

		# Arrange controls:
		controls = wx.GridBagSizer(10,10)
		
		# x-axis parameter:
		controls.Add( wx.StaticText(self, label='Parameter: '),                (0, 0),   flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._parameter,                                         (0, 1),   flag = wx.ALIGN_LEFT  | wx.ALIGN_CENTER_VERTICAL )
		
		# x-axis start/step/end:
		controls.Add( wx.StaticText(self, label='Start: '),                    (1, 0),   flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._start,                                             (1, 1),   flag = wx.ALIGN_LEFT  | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( wx.StaticText(self, label='Step size: '),                (2, 0),   flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._step,                                              (2, 1),   flag = wx.ALIGN_LEFT  | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( wx.StaticText(self, label='End: '),                      (3, 0),   flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._end,                                               (3, 1),   flag = wx.ALIGN_LEFT  | wx.ALIGN_CENTER_VERTICAL )

		# add some extra space at the bottom:
		controls.Add ( 1, 8,                                                   (4, 1) )

		# setup sizer for the box:
		self.sizer = wx.StaticBoxSizer(self, wx.VERTICAL)
		self.sizer.Add(controls, 0, wx.CENTER)

		# adjust values/limits/ranges of controls:
		self.x_axis_ctrl_setup()
		
	def x_axis_ctrl_setup (self):
		logging.debug('setting up x-axis controls -- change: look this up from the PSU / axis parameter and the DUT config/limits...')
		x_min_val    = 0;
		x_max_val    = 10;
		x_min_step   = 0.1;
		x_resolution = 0.001
		x_digits     = 3
		
		self._start.SetDigits(x_digits)
		self._start.SetIncrement(x_resolution)
		self._start.SetRange(x_min_val, x_max_val)
		self._start.SetValue(x_min_val)
		
		self._end.SetDigits(x_digits)
		self._end.SetIncrement(x_resolution)
		self._end.SetRange(x_min_val, x_max_val)
		self._end.SetValue(x_max_val)

		self._step.SetDigits(x_digits)
		self._step.SetIncrement(x_resolution)
		self._step.SetRange(x_resolution, x_max_val-x_min_val)
		self._step.SetValue(x_resolution)
		

	def on_parameter (self, event):
		logging.debug('Called on_parameter: adjust x-axis limit and units in the GUI, and maybe other things')



# wx-StaticBox for y axis
class curvetrace_yaxis_StaticBox(wx.StaticBox):

	def __init__(self,parent,app):
	
		# init the wx.StaticBox:
		super(curvetrace_yaxis_StaticBox, self).__init__(parent, label='Vertical Axis')
	
		# App configs:
		self._app = app
		
		# x-axis parameter:
		self._parameter = wx.Choice(self, choices = ['U\u2081','I\u2081','U\u2082','I\u2082'])
		self._parameter.SetSelection (1)
		self._parameter.Bind(wx.EVT_CHOICE, self.on_parameter)
		
		# x-axis start/step/end:
		logging.debug('...add smart max/min limits for GUI based on axis parameter and PSU specs...')
		self._limit = wx.SpinCtrlDouble( self, size=(150, -1), style=wx.ALIGN_RIGHT )
		
		# Arrange controls:
		controls = wx.GridBagSizer(10,10)
		
		# x-axis parameter:
		controls.Add( wx.StaticText(self, label='Parameter: '),                (0, 0),   flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._parameter,                                         (0, 1),   flag = wx.ALIGN_LEFT  | wx.ALIGN_CENTER_VERTICAL )
		
		# x-axis start/step/end:
		controls.Add( wx.StaticText(self, label='Limit: '),                    (1, 0),   flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._limit,                                             (1, 1),   flag = wx.ALIGN_LEFT  | wx.ALIGN_CENTER_VERTICAL )

		# add some extra space at the bottom:
		controls.Add ( 1, 8,                                                   (2, 1) )

		# setup sizer for the box:
		self.sizer = wx.StaticBoxSizer(self, wx.VERTICAL)
		self.sizer.Add(controls, 0, wx.CENTER)

		# adjust values/limits/ranges of controls:
		self.y_axis_ctrl_setup()
		
	def y_axis_ctrl_setup (self):
		logging.debug('setting up y-axis controls -- change: look this up from the PSU / axis parameter and the DUT config/limits...')
		y_limit      = 3;
		y_resolution = 0.001
		y_digits     = 3
		
		self._limit.SetDigits(y_digits)
		self._limit.SetIncrement(y_resolution)
		self._limit.SetRange(0, y_limit)
		self._limit.SetValue(y_limit)		

	def on_parameter (self, event):
		logging.debug('Called on_parameter: adjust y-axis limit and units in the GUI, and maybe other things')



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
		
		# x-axis start/step/end:
		logging.debug('...add smart max/min limits for GUI based on axis parameter and PSU specs...')
		self._start = wx.SpinCtrlDouble( self, size=(150, -1), style=wx.ALIGN_RIGHT )
		self._end   = wx.SpinCtrlDouble( self, size=(150, -1), style=wx.ALIGN_RIGHT )
		self._step  = wx.SpinCtrlDouble( self, size=(150, -1), style=wx.ALIGN_RIGHT )

		# Arrange controls:
		controls = wx.GridBagSizer(10,10)
		
		# x-axis parameter:
		controls.Add( wx.StaticText(self, label='Parameter: '),                (0, 0),   flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._parameter,                                         (0, 1),   flag = wx.ALIGN_LEFT  | wx.ALIGN_CENTER_VERTICAL )
		
		# x-axis start/step/end:
		controls.Add( wx.StaticText(self, label='Start: '),                    (1, 0),   flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._start,                                             (1, 1),   flag = wx.ALIGN_LEFT  | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( wx.StaticText(self, label='Step size: '),                (2, 0),   flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._step,                                              (2, 1),   flag = wx.ALIGN_LEFT  | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( wx.StaticText(self, label='End: '),                      (3, 0),   flag = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL )
		controls.Add( self._end,                                               (3, 1),   flag = wx.ALIGN_LEFT  | wx.ALIGN_CENTER_VERTICAL )

		# add some extra space at the bottom:
		controls.Add ( 1, 8,                                                   (4, 1) )

		# setup sizer for the box:
		self.sizer = wx.StaticBoxSizer(self, wx.VERTICAL)
		self.sizer.Add(controls, 0, wx.CENTER)

		# adjust values/limits/ranges of controls:
		self.curves_ctrl_setup()
		
	def curves_ctrl_setup (self):
		logging.debug('setting up curves controls -- change: look this up from the PSU / axis parameter and the DUT config/limits...')
		min_val    = 0;
		max_val    = 10;
		min_step   = 0.1;
		resolution = 0.001
		digits     = 3
		
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
		
	def on_parameter (self, event):
		logging.debug('Called on_parameter: adjust curves limit and units in the GUI, and maybe other things')

