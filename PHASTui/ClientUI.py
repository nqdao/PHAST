__author__ = 'Nhat-Quang'

import wx, os
import wx.html2
import urllib


class Gui(wx.Frame):

    def __init__(self, parent, title):
        super(Gui, self).__init__(parent, title=title,
            size=(800, 600))
        panel = wx.Panel(self)
        self.url = "https://maps.googleapis.com/maps/api/staticmap?center=CN+Tower,Toronto,ON&zoom=13&" \
                   "size=800x600&maptype=roadmap&key=AIzaSyA7LGD3TmN87_-Lr8sofhjaylZK1q87ra8"
        self.img_file = "googlemap.png"
        self.location_box = wx.TextCtrl(panel, size=(300, 20))
        self.comp_button = wx.Button(panel, label="Compute", size=(100, 50))
        self.comp_button.Bind(wx.EVT_BUTTON, self.compute_route)
        self.img = wx.StaticBitmap(self, -1, wx.Bitmap(self.img_file, wx.BITMAP_TYPE_ANY))
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.location_box)
        sizer.Add(self.comp_button)
        sizer.Add(self.img)

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
            self.img = wx.StaticBitmap(self, -1, wx.Bitmap(self.img_file, wx.BITMAP_TYPE_ANY))
        self.img.Refresh()

if __name__ == '__main__':
    app = wx.App()
    window = Gui(None, title='PHAST')
    app.MainLoop()
