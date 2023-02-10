import wx
from io import BytesIO
import schemdraw
import schemdraw.elements as elm
             
class TestFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None)
        p = wx.Panel(self)
        fgs = wx.FlexGridSizer(cols=1)
        d = schemdraw.Drawing()
        d.add(elm.Resistor())
        d.add(elm.SourceV())
        data = d.get_imagedata('png')
        stream = BytesIO(data)
        img = wx.ImageFromStream(stream)
        sb = wx.StaticBitmap(p, -1, wx.BitmapFromImage(img))
        fgs.Add(sb)
        p.SetSizerAndFit(fgs)
        self.Fit()

app = wx.PySimpleApp()
frm = TestFrame()
frm.Show()
app.MainLoop()
