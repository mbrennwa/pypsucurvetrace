import wx
from io import BytesIO, StringIO
from base64 import b64decode
import schemdraw
import schemdraw.elements as elm

             
class TestFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Loading Images")
        p = wx.Panel(self)

        fgs = wx.FlexGridSizer(cols=2, hgap=10, vgap=10)
        
       	## img1 = wx.Image("testy.png", wx.BITMAP_TYPE_ANY)
            
        d = schemdraw.Drawing()
        d.add(elm.Resistor())
        d.add(elm.Capacitor())
        d.add(elm.Diode())
        data = d.get_imagedata('png')
        stream = BytesIO(data)
            
        img1 = wx.ImageFromStream(stream)
            
        w = img1.GetWidth()
        h = img1.GetHeight()
        
        print(w)
        print(h)



        sb1 = wx.StaticBitmap(p, -1, wx.BitmapFromImage(img1))

        fgs.Add(sb1)

        p.SetSizerAndFit(fgs)
        self.Fit()

app = wx.PySimpleApp()
frm = TestFrame()
frm.Show()
app.MainLoop()
