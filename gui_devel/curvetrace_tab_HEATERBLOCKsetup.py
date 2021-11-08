#################################
# GUI for HEATERBLOCK Setup tab #
#################################


try:
	import wx
	import logging
		
except ImportError as e:
	logging.error( 'Could not import: ' + str(e) )
	raise


#####################################################################


# DUT Setup tab:
class HEATERBLOCKsetup_tab(wx.Panel):

	def __init__(self,app):
	
		# App configs:
		self._app = app
	
		# Init the panel:
		wx.Panel.__init__(self, app.frame_main.tabs)
		
		# Add a dummy text label:
		box = wx.BoxSizer(wx.VERTICAL)
		lbl = wx.StaticText(self,-1,style = wx.ALIGN_CENTER)
		lbl.SetLabel("This tab\n is for\n setup of the\n HEATERBLOCK\n stuff.")
		box.Add(lbl,0,wx.ALIGN_CENTER)
		self.SetSizer(box) 
