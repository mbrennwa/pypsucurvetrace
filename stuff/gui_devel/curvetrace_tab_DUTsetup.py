##########################
# GUI for DUT Setup tab #
##########################


try:
	import wx
	import logging
	import matplotlib
	matplotlib.use('Agg') # Set the backend here
	import schemdraw
	import schemdraw.elements as elm

except ImportError as e:
	logging.error( 'Could not import: ' + str(e) )
	raise


#####################################################################


# DUT Setup tab:
class DUTsetup_tab(wx.Panel):

	def __init__(self,app):
	
		# App configs:
		self._app = app
	
		# Init the panel:
		wx.Panel.__init__(self, app.frame_main.tabs)
		
		# Add a dummy text label:
		box = wx.BoxSizer(wx.VERTICAL)
		lbl = wx.StaticText(self,-1,style = wx.ALIGN_CENTER)
		lbl.SetLabel("This tab\n is for\n setup of the\n DUT limits\n and connections\n and optional temperature setting.\n\n\n BUTTON to load DUT config file")
		box.Add(lbl,0,wx.ALIGN_CENTER)

		# Add a dummy circuit / symbol:
		c = schemdraw.Drawing()
		# c.draw(backend='svg')
		c += elm.Resistor().label('100KΩ')
		
		png_bytes = drawing.get_imagedata('svg')
		
		bmp = wx.Bitmap.FromPNGData(png_bytes)

		logging.debug('Need to figure out how to add the circuit symobol to the wx panel...')

class Panel(wx.Panel):
    def __init__(self, parent, path):
        super(Panel, self).__init__(parent, -1)
        bitmap = wx.Bitmap(path)
        bitmap = scale_bitmap(bitmap, 300, 200)
        control = wx.StaticBitmap(self, -1, bitmap)
        control.SetPosition((10, 10))
