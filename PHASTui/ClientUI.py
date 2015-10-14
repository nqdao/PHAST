__author__ = 'Nhat-Quang'

import wx, os
import wx.html2
import urllib
import json, socket, sys


class Gui(wx.Frame):
    HOST, PORT = "142.150.208.139", 6633
    ORIGIN = "University of Toronto"
    LOCATION_LIST = [(0, 0), (1, 1), (2, 2), (10, 10)]

    def __init__(self, parent, title):
        super(Gui, self).__init__(parent, title=title,
            size=(1000, 750))

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


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
        if self.location_box.IsEmpty():
            wx.MessageBox('Empty Destination', 'Error', wx.OK | wx.ICON_ERROR)
            return
        destination = self.location_box.GetValue()
        print destination
        self.s.connect((self.HOST,self.PORT))
        self.s.sendall(json.dumps(self.construct_new_trip_request(destination, origin)))
        route_selections = json.loads(self.s.recv(1024))
        #display and let user select route

        self.display_map()

    def display_map(self):
        if os.path.isfile(self.img_file):
            urllib.urlretrieve(self.url, self.img_file)
            self.img.SetBitmap(wx.Bitmap(self.img_file, wx.BITMAP_TYPE_ANY))
        self.img.Refresh()

    def monitor_communication(self):
        data_in = json.loads(self.s.recv(1024))
        while(data_in['action'] == "done"):
            self.s.sendall(json.dumps(self.construct_location_response()))
            data_in = json.loads(self.s.recv(1024))

        print json.dumps(data_in)
        self.s.close()

    @staticmethod
    def construct_new_trip_request(self, destination, origin=ORIGIN):
        data_out = {'action': "new_trip", 'details': {"user_id": 0, "origin": origin, "destination": destination}}
        return data_out

    @staticmethod
    def construct_route_selection(self, routes, select):
        data_out = {'action': "selection", 'details': {'user_id': 0, 'selection': select}}
        return data_out

    @staticmethod
    def construct_location_response(self, i):
        data_out = {'action': "location", 'details': {'user_id': 0, 'location': {'lat': self.LOCATION_LIST[i][0],
                                                                                 'lng': self.LOCATION_LIST[i][1]}}}
        return data_out

if __name__ == '__main__':
    app = wx.App()
    window = Gui(None, title='PHAST')
    app.MainLoop()
