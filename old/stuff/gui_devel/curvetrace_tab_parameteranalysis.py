##################################
# GUI for Parameter Analysis tab #
##################################


try:
	import wx
	import logging
		
except ImportError as e:
	logging.error( 'Could not import: ' + str(e) )
	raise


#####################################################################


# Parameter Analysis tab:
class parameteranalysis_tab(wx.Panel):

	def __init__(self,app):
	
		# App configs:
		self._app = app
	
		# Init the panel:
		wx.Panel.__init__(self, app.frame_main.tabs)
		
		# Add a dummy text label:
		box = wx.BoxSizer(wx.VERTICAL)
		lbl = wx.StaticText(self,-1,style = wx.ALIGN_CENTER)
		lbl.SetLabel("This tab\n is for\n control of\n DUT parameter\n analysis:\n\n gain (mu), transconductance (gm), etc. at specified operating point")
		box.Add(lbl,0,wx.ALIGN_CENTER)
		self.SetSizer(box) 
