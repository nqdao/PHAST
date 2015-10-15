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

        radio_box = wx.BoxSizer(wx.VERTICAL)
        self.route_1 = wx.Button(panel, label='Choose Bixi')
        self.route_2 = wx.Button(panel, label='Choose Bus')
        self.route_1_desc = wx.StaticText(panel, label="Bixi route description")
        self.route_2_desc = wx.StaticText(panel, label="Bus route description")

        radio_box.Add(self.route_1_desc, flag=wx.RIGHT | wx.TOP, border=10)
        radio_box.Add(self.route_1, flag=wx.RIGHT | wx.TOP, border=50)
        radio_box.Add(self.route_2_desc, flag=wx.RIGHT | wx.TOP, border=10)
        radio_box.Add(self.route_2, flag=wx.RIGHT | wx.TOP, border=40)

        img_box.Add(radio_box, flag=wx.RIGHT, border=10)

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
        self.s.connect((self.HOST, self.PORT))
        self.s.sendall(json.dumps(self.construct_new_trip_request(destination)))

        # #receive routes from comm
        route_selections = json.loads(self.s.recv(1024))
        with open("test_routes.json") as test:
            route_selections = json.load(test)
        if route_selections['action'] != 'routes':
            print "ERROR: expecting routes from server"
            return

        #display and let user select route
        self.route_options(route_selections['details']['routes'])
        self.display_map()

    def display_map(self):
        if os.path.isfile(self.img_file):
            urllib.urlretrieve(self.url, self.img_file)
            self.img.SetBitmap(wx.Bitmap(self.img_file, wx.BITMAP_TYPE_ANY))
        self.img.Refresh()

    def route_options(self, routes):
        self.route_1_desc.SetLabel("{0}\n"
                              "distance: {1}\n"
                              "duration: {2}\n"
                              "confidence: {3}".format("Bixi", routes['bixi']['distance'], routes['bixi']['duration'],
                                                       routes['bixi']['confidence']))
        self.route_1.Bind(wx.EVT_BUTTON, lambda event: self.route_selection(event, "bixi"))
        self.route_2_desc.SetLabel("{0}\n"
                              "distance: {1}\n"
                              "duration: {2}".format("Bus", routes['bus']['distance'], routes['bus']['duration']))
        self.route_2.Bind(wx.EVT_BUTTON, lambda event: self.construct_route_selection(event, "bus"))

    def monitor_communication(self):
        data_in = json.loads(self.s.recv(1024))
        while data_in['action'] != "done":
            if data_in['action'] == 'new_route':
                #update map to show new route
                self.display_map()

            self.s.sendall(json.dumps(self.construct_location_response()))
            data_in = json.loads(self.s.recv(1024))

        print json.dumps(data_in)
        wx.MessageBox('You have arrived at your destination', 'Arrived', wx.OK | wx.ICON_EXCLAMATION)
        self.s.close()

    @staticmethod
    def construct_new_trip_request(self, destination, origin=ORIGIN):
        data_out = {'action': "new_trip", 'details': {"user_id": 0, "origin": origin, "destination": destination}}
        return data_out

    def route_selection(self, event, select):
        data_out = {'action': "selection", 'details': {'user_id': 0, 'selection': select}}
        print "selected {0}".format(select)
        self.s.sendall(json.dumps(data_out))
        self.monitor_communication()


    @staticmethod
    def construct_location_response(self, i):
        data_out = {'action': "location", 'details': {'user_id': 0, 'location': {'lat': self.LOCATION_LIST[i][0],
                                                                                 'lng': self.LOCATION_LIST[i][1]}}}
        return data_out

if __name__ == '__main__':
    app = wx.App()
    window = Gui(None, title='PHAST')
    app.MainLoop()
