##################
# Main GUI stuff #
##################

try:
	import logging	
	import wx
	from curvetrace_tab_curvetrace        import curvetrace_tab	
	from curvetrace_tab_parameteranalysis import parameteranalysis_tab	
	from curvetrace_tab_DUTsetup          import DUTsetup_tab
	from curvetrace_tab_settings          import settings_tab
	from curvetrace_constants             import MAIN_WINDOW_WIDTH_INI, MAIN_WINDOW_HEIGHT_INI

except ImportError as e:
	logging.error( 'Could not import: ' + str(e) )
	raise


#####################################################################


# for GUI mockup without real PSU units:
class PSU_for_mockup:
	
	def __init__(self, Umin, Umax, Ures, Imin, Imax, Ires):
		self.VMIN    = Umin
		self.VMAX    = Umax
		self.VRESSET = Ures
		self.IMIN    = Imin
		self.IMAX    = Imax
		self.IRESSET = Ires


#####################################################################


# class curvetrace_app(wx.Frame):
class curvetrace_app(wx.App):

	def __init__(self):
		
		# Error display flag
		self._error_displaying = False
		
		# wx.App init:
		wx.App.__init__(self)

		# Init DUT configuration (still empty, will be loaded later):
		self.DUT_config = None
		
		# Init PSU configuration (still empty, will be loaded later):
		self.PSU1 = None
		self.PSU2 = None
		
		# Init HEATERBLOCK configuration (still empty, will be loaded later):
		self.HEATERBLOCK_config = None
		
		# Main GUI frame:
		self.frame_main = frame_main(self)
				
		# Tell the wxApp that this is the "main" frame of the wx.App
		self.SetTopWindow(self.frame_main) 
				
		# Frame for CURVETRACE data plots:
		### self.frame_curves_plot = frame_curves_plot(self)
		self.frame_curves_plot = None


	def startup(self):
		logging.info('Called startup! Should read and process configuration here...')
		self.PSU1 = PSU_for_mockup(Umin=0.0, Umax=32.0, Ures=0.01,  Imin=0.0, Imax=5.0, Ires=0.01)
		self.PSU2 = PSU_for_mockup(Umin=0.0, Umax=12.0, Ures=0.001, Imin=0.0, Imax=2.0, Ires=0.001)
		self.frame_main.configure_gui()


#####################################################################


# Main frame
class frame_main(wx.Frame):

	def __init__(self,app):
		
		# Create the window:
		windowstyle = wx.DEFAULT_FRAME_STYLE
		wx.Frame.__init__(self, None, title="PyPSU Curve Trace", size=(MAIN_WINDOW_WIDTH_INI,MAIN_WINDOW_HEIGHT_INI), style=windowstyle)

		# App configs:
		self._app = app
		
		# Bind close event (icon in window top bar, "Quit" menu in main menu):
		self.Bind(wx.EVT_CLOSE, self.on_close_event)
		
		# Create "busy display" dialog box:
		#### self.busy_box = busy_display(self)
				
		# Create the notebook ("tabs holder")
		self.tabs = wx.Notebook(self)
		### self.tabs.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.on_tab_change) # event hook to call before page is changed
		
		# sizer / widget arrangement within the window:
		self._sizer = wx.BoxSizer(wx.VERTICAL)

		# add TextCtrl for status logging:
		### self._log_box                = wx.TextCtrl(self, wx.ID_ANY, '', style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH )	
		### self._log_box.num_lines      = 0        # Number of text lines in the TextCtrl
		### self._sizer.Add(self._log_box, 1, wx.EXPAND ) # add the logging / warning panel to the sizer
		### self.SetSizer(self._sizer) # apply the sizer to the panel		

	def configure_gui(self):
		# configure the frame/gui according to the instrument configuration
	
		# Create the tabs:
		self.curvetrace_tab        = curvetrace_tab(self._app)
		self.parameteranalysis_tab = parameteranalysis_tab(self._app)
		self.DUTsetup_tab          = DUTsetup_tab(self._app)
		self.settings_tab          = settings_tab(self._app)
				
		# Add the tabs to the notebook:
		self.tabs.AddPage(self.curvetrace_tab,        "Curve Trace")
		self.tabs.AddPage(self.parameteranalysis_tab, "Parameter Analysis")
		self.tabs.AddPage(self.DUTsetup_tab,          "DUT Setup")
		self.tabs.AddPage(self.settings_tab,          "Settings")
		
		# Update the window layout with the newly created / configured tabs and controls:
		self._sizer.Prepend(self.tabs, 0, wx.EXPAND) # add the notebook (the "tabs") to the sizer, on top of the already existing logging / warning panel
		self.SetMinSize( self._sizer.ComputeFittingWindowSize(self) ) # set minimal window size	according to the sizer with the newly configured tabs and added controls	
		self.Layout() # update the window layout

		# Set window to center of screen (if the windowing system supports it), and show the window on the screen:
		self.CenterOnScreen()
		self.Show()

		logging.info( 'GUI configuration completed.' )
		
	def on_close_event(self, event):
		dlg = wx.MessageDialog(self, "Do you really want to close this application?", "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
		result = dlg.ShowModal()
		dlg.Destroy()
		if result == wx.ID_OK:			
			# exit the program:
			self.exit()

	def log_message(self, message, overwrite_previous_line = False, typ = 'LOG'):
	
		# optional: delete the last line in the log/warn panel:
		if overwrite_previous_line:
			if self._log_box.num_lines > 0:
				l = self._log_box.GetLineLength(self._log_box.num_lines-1) + 1
				self._log_box.Remove(self._log_box.GetLastPosition()-l, self._log_box.GetLastPosition()+1)
				self._log_box.num_lines = self._log_box.num_lines-1
	
		# add new log message to GUI display
		if len(message) > 0:
			m = message.splitlines() # split multi-line messages
			if len(m) > 1:
				for msg in m:
					self.log_message(msg, typ = typ)
			else:
				if typ.upper() == 'WARN':
					message = 'WARNING >> ' + message
					self._log_box.SetDefaultStyle(wx.TextAttr(self._log_box.warn_textcolor, self._background_color))
				else:
					self._log_box.SetDefaultStyle(wx.TextAttr(self._log_box.log_textcolor, self._background_color))
				if self._log_box.num_lines > 0:
					message = "\n" + message
				self._log_box.AppendText(message)
				self._log_box.num_lines = self._log_box.num_lines + 1
			
			self.trunc_messagelog() # make sure the message log is not too long
	
	def trunc_messagelog(self):
		while self._log_box.num_lines > MAX_MESSAGE_LINES:
			l = self._log_box.GetLineLength(0) + 1
			self._log_box.Remove(0, l)
			self._log_box.num_lines = self._log_box.num_lines-1			

	def exit(self):
		# exit the program
		self.startup = None # make sure the startup thread is gone (it should not exist anymore, but just in case...)
				
		# Cancel all plotting timers:
		try:
			self._app.frame_MS_plots.plot_timer.cancel()
		except:
			pass
		try:
			self._app.frame_SENSORS_plots.plot_timer.cancel()
		except:
			pass
		
		
		
		
		
		# Terminate ctrl_updater thread for the MS and inlets panels:
		### self._app.frame_main.MS_tab.ctrl_updater.terminate()
		### self._app.frame_main.inlets_tab.ctrl_updater.terminate()

		# Destroy plot frames:
		### self._app.frame_MS_plots.Destroy()
		### self._app.frame_SENSORS_plots.Destroy()
		
		# Destroy main frame:
		wx.CallAfter(self.Destroy)


#####################################################################


# MS plots frame
class frame_plots_MS(wx.Frame):
	def __init__(self,app):
		
		# Create the window:		
		wx.Frame.__init__(self, parent=app.frame_main, title='miniRUEDI Data', style=wx.DEFAULT_FRAME_STYLE)

		self._app = app

		# Init time stamps of last plot updates:
		self._timestamp_last_MS_plot = -1
		
		# Bind close icon in window top bar to event on_close_event:
		self.Bind(wx.EVT_CLOSE, self.on_close_event)
		
		# Create a panel to hold the plots
		p  = wx.Panel(self)
		p.SetBackgroundColour(wx.NullColour)
		
		# Set up figure (2x1 plot showing the MS peakbuffer in the upper panel and scan data in lower panel)
		self.figure = plt.figure()
		self.axes_peakbuffer = self.figure.add_subplot(2,1,1)
		self.axes_scan = self.figure.add_subplot(2,1,2)
				
		self.canvas = FigureCanvas(p, -1, self.figure)
		self.canvas.SetMinSize(wx.Size(MS_PLOTS_MINSIZE_H,MS_PLOTS_MINSIZE_V)) # set min size for the plot canvas
		self.figure.tight_layout(pad=1, rect=(0.12, 0.02, 0.99, 0.975))
		plt.subplots_adjust(hspace=0.5)
					
		# sizer / widget arrangement within the window:
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.canvas, 1, wx.EXPAND)
		p.SetSizer(sizer) # apply the sizer to the panel
		sizer.SetSizeHints(self) # inform frame about size hints for the panel (min. plot canvas size and stuff)

		# install wx.Timer to update the data plot:
		self.Bind(wx.EVT_TIMER, self.on_plot_peakbuffer) # bind to TIMER event
		self.plot_timer = wx.Timer(self) # timer to trigger plots

		# run plotting timer at specified millisecond interval
		wx.CallAfter(self.plot_timer.Start,500)
		
	def configure_gui(self):
		if len(self._app.config.MS.label()) > 0:
			self.SetTitle(self._app.config.MS.label() + ' Data')
		else:
			self.SetTitle('MS Data')
		# Update plots (empty data)
		plot_peakbuffer(self._app)
		plot_scan(self._app)

	def on_plot_peakbuffer(self, event):
		if self.IsShown():
			# The window is not hidden
			if self._app.config.MS.peakbuffer_get_timestamp() > self._timestamp_last_MS_plot:
				# update the plot:
				plot_peakbuffer(self._app)
				self._timestamp_last_MS_plot = misc.now_UNIX()
	
	def on_close_event(self, event):
		# Don't close (destroy) the window, just hide it (so it can be shown if needed again):
		self.hide_window()
		
	def show_window(self):
		# analogous to frame_plots_SENSORS.show_window(), just call self.Show()
		self.Show()
		self.SetSize((self.GetSize().width, self.GetSize().height+1)) # workaround to make sure plot panels are properly painted/updated on Wayland
		self.SetSize((self.GetSize().width, self.GetSize().height-1)) # workaround to make sure plot panels are properly painted/updated on Wayland
		self._app.frame_main.MS_tab.MS_plots_box.update_plot_show_button()
	
	def hide_window(self):
		self.Hide()
		self._app.frame_main.MS_tab.MS_plots_box.update_plot_show_button()


#####################################################################


# SENSORS plot frame
class frame_plots_SENSORS(wx.Frame):

	def __init__(self,app):

		# Create the window:
		wx.Frame.__init__(self, parent=app.frame_main, title="Inlet Sensors Data", size=(600,600), style=wx.DEFAULT_FRAME_STYLE)

		self._app = app
		
		# Init time stamps of last plot updates:
		self._timestamp_last_SENSORS_plot = -1
		
		# Bind close icon in window top bar to event on_close_event:
		self.Bind(wx.EVT_CLOSE, self.on_close_event)
		
		# List of sensors included in the plot (one T+P pair for each panel):
		self.sensors = [] # empty list to start with
		self.labels  = [] # empty list to start with
		
		# Init empty plot things:
		self.figure = None
		self.axes = None
		self.canvas = None

		# install wx.Timer to update the data plot:
		self.Bind(wx.EVT_TIMER, self.on_plot) # bind to TIMER event
		self.plot_timer = wx.Timer(self)      # timer to trigger plots, will be started later
		
	def configure_gui(self):

		for l in self._app.config.SAMPLE_LINES:
			if (l.TSENS is not None) or (l.PSENS is not None):
				self.sensors.append( (l.TSENS, l.PSENS) )
				self.labels.append(l.LABEL)
		
		if len(self.sensors) > 0:
			# Create a panel to hold the plots
			p  = wx.Panel(self)
			p.SetBackgroundColour(wx.NullColour)

			# Set up figure (with two y axes: left=temperature, right=pressure)
			self.figure = plt.figure()
			self.axes = []
			for k in range(len(self.sensors)):
				ax_left  = self.figure.add_subplot(len(self.sensors),1,k+1)	
				ax_right = ax_left.twinx()  # instantiate a second axes that shares the same x-axis
				self.axes.append( [ax_left,ax_right] ) # add the axes pair
						
			self.canvas = FigureCanvas(p, -1, self.figure)
			self.canvas.SetMinSize(wx.Size(SENSORS_PLOTS_MINSIZE_H,(len(self.sensors)+1)*SENSORS_PLOTS_MINSIZE_V_PER_PANEL)) # set min size for the plot canvas
			if len(self.sensors) > 1: plt.subplots_adjust(hspace=0.2)

			# sizer / widget arrangement within the window:
			sizer = wx.BoxSizer(wx.VERTICAL)
			sizer.Add(self.canvas, 1, wx.EXPAND)
			p.SetSizer(sizer) # apply the sizer to the panel
			sizer.SetSizeHints(self) # inform frame about size hints for the panel (min. plot canvas size and stuff)
			
			# run plotting timer at specified millisecond interval
			wx.CallAfter(self.plot_timer.Start,500)
			
			# trigger forced update:
			self.on_plot(event = None, force_update = True)
		
	def on_plot(self, event, force_update = False):
	
		do_update = force_update
		
		if self.IsShown():
			# The window is not hidden, so check if update is needed:			
			for l in self.sensors:
				if l[0] is not None:
					if l[0].tempbuffer_get_timestamp() > self._timestamp_last_SENSORS_plot:
						do_update = True
						break
				if l[1] is not None:
					if l[1].pressbuffer_get_timestamp() > self._timestamp_last_SENSORS_plot:
						do_update = True
						break

		# Update the plot if needed:
		if do_update:
			self._timestamp_last_SENSORS_plot = misc.now_UNIX()
			plot_sensors(self._app)

	def on_close_event(self, event):
		# Don't close (destroy) the window, just hide it (so it can be shown if needed again):
		self.hide_window()

	def show_window(self):
		if len(self.sensors) > 0:
			self.Show()
			self.SetSize((self.GetSize().width, self.GetSize().height+1)) # workaround to make sure plot panels are properly painted/updated on Wayland
			self.SetSize((self.GetSize().width, self.GetSize().height-1)) # workaround to make sure plot panels are properly painted/updated on Wayland

		if self._app.frame_main.inlets_tab.SENSORS_box is not None:
			self._app.frame_main.inlets_tab.SENSORS_box.update_plot_show_button()

	def hide_window(self):
		self.Hide()
		if self._app.frame_main.inlets_tab.SENSORS_box is not None:
			self._app.frame_main.inlets_tab.SENSORS_box.update_plot_show_button()


#####################################################################


# "Busy Box" display
class busy_display(wx.Dialog):
	# A dialog box to show a message about a background process that will take a while, so the user knows what's going on.

	def __init__(self, parent):
		# Create the dialog box
		wx.Dialog.__init__(self, parent, style = wx.SIMPLE_BORDER )
		self._panel = wx.Panel(self, -1)
		self._msg = wx.StaticText(self._panel, label='Please wait...', style=wx.ALIGN_CENTRE_HORIZONTAL )
		h_sizer = wx.BoxSizer(wx.HORIZONTAL)
		h_sizer.Add(self._msg, 0, wx.CENTER)
		self._main_sizer = wx.BoxSizer(wx.VERTICAL)
		self._main_sizer.Add((0,0), 1, wx.EXPAND)
		self._main_sizer.Add(h_sizer, 0, wx.CENTER)
		self._main_sizer.Add((0,0), 1, wx.EXPAND)
		self._panel.SetSizer(self._main_sizer)
		# self.setup('Plase wait...')
		self._is_active = False
		
	def setup(self, infotext):
		self._msg.SetLabel(infotext)
		siz = self._main_sizer.ComputeFittingWindowSize(self)
		siz.IncBy(wx.Size(80,50))
		self.SetSize(siz)
		self.Center()
	
	def activate(self, message = 'Please wait...'):
		# Show the dialog in modal mode
		if not self._is_active:
			self.setup(message)
			self._is_active = True
			self.ShowModal()
		
	def deactivate(self):
		# End the modal dialog (from the long-running process thread)
		if self._is_active:
			self.EndModal(0)
			self._is_active = False


#####################################################################


# Handle "Fatal Error" messages
global ERROR_DISPLAYED
ERROR_DISPLAYED = False

import traceback
def fatal_error(msg, exc_info = None):
	global ERROR_DISPLAYED
	
	# Check if there is not already an error message being displayed:
	if not ERROR_DISPLAYED:
		
		ERROR_DISPLAYED = True		

		# Show error message, then exit the program
		if not type(msg) == str:
			msg = 'Unknown error'
		elif len(msg) == 0:
			msg = 'Unknown error'
		
		if exc_info is not None:
			if exc_info[0] is not None:
				if msg[-1:] == '.':
					msg = msg[0:-1]
				msg = msg + ':\n' +  str(exc_info[0]) + '\n' + str(exc_info[1])
				fname = os.path.split(exc_info[2].tb_frame.f_code.co_filename)[1]
				msg = msg  + '\n' + fname + ', line ' + str(exc_info[2].tb_lineno)
		
		else:
			if msg[-1:] != '.':
				msg = msg + '.'
					
		# Print error message to STDOUT:
		print_error(msg)
		
		# Show error message in GUI:
		try:
			dlg = wx.MessageDialog(None, msg, 'Error', wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
		except:
			dlg.Destroy()
			pass
		
		ERROR_DISPLAYED = False
		# hard exit (do not use sys.exit(...), which will not exit not called from the main thread):
		os._exit(1)
