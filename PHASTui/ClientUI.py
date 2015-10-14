__author__ = 'Nhat-Quang'

import wx, os
import wx.html2
import urllib


class Gui(wx.Frame):

    def __init__(self, parent, title):
        super(Gui, self).__init__(parent, title=title,
            size=(1000, 750))
        self.server_host = "142.150.208.139"
        self.server_port = 6633
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.url = "https://maps.googleapis.com/maps/api/staticmap?center=CN+Tower,Toronto,ON&zoom=14&" \
                   "size=800x600&maptype=roadmap&key=AIzaSyA7LGD3TmN87_-Lr8sofhjaylZK1q87ra8"
        self.img_file = "googlemap.png"

        input_box = wx.BoxSizer(wx.HORIZONTAL)
        self.location_box = wx.TextCtrl(panel, size=(300, 20))
        self.comp_button = wx.Button(panel, label="Compute", size=(100, 50))
        self.comp_button.Bind(wx.EVT_BUTTON, self.compute_route)
        input_box.Add(self.location_box, flag=wx.LEFT | wx.TOP | wx.RIGHT, border=10)
        input_box.Add(self.comp_button, flag=wx.LEFT | wx.TOP, border=10)

        img_box = wx.BoxSizer(wx.HORIZONTAL)
        self.img = wx.StaticBitmap(panel, -1, wx.Bitmap(self.img_file, wx.BITMAP_TYPE_ANY))
        img_box.Add(self.img, flag=wx.LEFT | wx.BOTTOM | wx.RIGHT | wx.EXPAND, border=10)

        sizer.Add(input_box, flag=wx.LEFT | wx.RIGHT, border=10)
        sizer.Add((-1, 25))
        sizer.Add(img_box, 1, wx.EXPAND | wx.LEFT | wx.BOTTOM, 20)

        panel.SetSizer(sizer)

        self.Center()
        self.Show()

    def compute_route(self, event):
        text = self.location_box.GetValue()
        print text
        self.display_map()

    def display_map(self):
        if os.path.isfile(self.img_file):
            urllib.urlretrieve(self.url, self.img_file)
            self.img.SetBitmap(wx.Bitmap(self.img_file, wx.BITMAP_TYPE_ANY))
        self.img.Refresh()

if __name__ == '__main__':
    app = wx.App()
    window = Gui(None, title='PHAST')
    app.MainLoop()
