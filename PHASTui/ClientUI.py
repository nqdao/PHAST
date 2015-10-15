__author__ = 'Nhat-Quang'

import wx, os
import wx.html2
import urllib
import json, socket, copy


class Gui(wx.Frame):
    HOST, PORT = "142.150.208.139", 6633
    ORIGIN = "University of Toronto"
    LOCATION_LIST = [(0, 0), (1, 1), (2, 2), (10, 10)]
    INITIAL_URL = "https://maps.googleapis.com/maps/api/staticmap?center=CN+Tower,Toronto,ON&zoom=14&size=900x700&maptype=roadmap"
    ROUTE_URL = "https://maps.googleapis.com/maps/api/staticmap?size=900x700"
    API_KEY = "&key=AIzaSyA7LGD3TmN87_-Lr8sofhjaylZK1q87ra8"
    PATH_TEMPLATE = ["&path=weight:10%7Ccolor:", "%7Cenc:"]
    MARKER_TEMPLATE = ["&markers=color:", "%7C"]
    steps = []
    iterator = 0    # iterate through steps list to keep track of where user is along the route

    def __init__(self, parent, title):
        super(Gui, self).__init__(parent, title=title, size=(1300, 750))

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

        # TODO: this button is only here for SAVI design cmap demo purposes
        self.proceed_button = wx.Button(panel, label="Proceed to next step", size=(150, 50))
        self.proceed_button.Bind(wx.EVT_BUTTON, self.demo_monitor_communication)
        input_box.Add(self.proceed_button, flag=wx.LEFT | wx.TOP, border=10)
        self.instruction = wx.StaticText(panel, label="Instruction here")
        input_box.Add(self.instruction, flag=wx.LEFT | wx.TOP, border=10)

        img_box = wx.BoxSizer(wx.HORIZONTAL)
        self.img = wx.StaticBitmap(panel, -1, wx.Bitmap(self.img_file, wx.BITMAP_TYPE_ANY))
        img_box.Add(self.img, flag=wx.LEFT | wx.BOTTOM | wx.RIGHT | wx.EXPAND, border=10)

        radio_box = wx.BoxSizer(wx.VERTICAL)
        self.route_1 = wx.Button(panel, label='Choose 1')
        self.route_2 = wx.Button(panel, label='Choose 2')
        self.route_3 = wx.Button(panel, label='Choose 3')
        self.route_4 = wx.Button(panel, label='Choose 4')
        self.route_1_desc = wx.StaticText(panel, label="Route 1 description")
        self.route_2_desc = wx.StaticText(panel, label="Route 2 description")
        self.route_3_desc = wx.StaticText(panel, label="Route 3 description")
        self.route_4_desc = wx.StaticText(panel, label="Route 4 description")

        radio_box.Add(self.route_1_desc, flag=wx.RIGHT | wx.TOP, border=10)
        radio_box.Add(self.route_1, flag=wx.RIGHT | wx.TOP, border=75)
        radio_box.Add(self.route_2_desc, flag=wx.RIGHT | wx.TOP, border=10)
        radio_box.Add(self.route_2, flag=wx.RIGHT | wx.TOP, border=75)
        radio_box.Add(self.route_3_desc, flag=wx.RIGHT | wx.TOP, border=10)
        radio_box.Add(self.route_3, flag=wx.RIGHT | wx.TOP, border=75)
        radio_box.Add(self.route_4_desc, flag=wx.RIGHT | wx.TOP, border=10)
        radio_box.Add(self.route_4, flag=wx.RIGHT | wx.TOP, border=75)

        img_box.Add(radio_box, flag=wx.RIGHT, border=10)

        sizer.Add(input_box, flag=wx.LEFT | wx.RIGHT, border=10)
        sizer.Add((-1, 25))
        sizer.Add(img_box, 1, wx.EXPAND | wx.LEFT | wx.BOTTOM, 20)

        panel.SetSizer(sizer)
        self.display_map()
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

        # with open("test_bixi_route.json") as test:
        #     routes = json.load(test)
        #     print self.route_to_url(routes)
        #     self.display_map(self.route_to_url(routes))

        if route_selections['action'] != 'routes':
            print "ERROR: expecting routes from server"
            return


        # display and let user select route
        self.route_options(route_selections['details']['routes'])

    def display_map(self, url="{0}{1}".format(INITIAL_URL, API_KEY)):
        if os.path.isfile(self.img_file):
            urllib.urlretrieve(url, self.img_file)
            self.img.SetBitmap(wx.Bitmap(self.img_file, wx.BITMAP_TYPE_ANY))
        self.img.Refresh()

    def route_options(self, routes):
        self.route_1_desc.SetLabel("{0} summary: {1}\n"
                                   "distance: {2}\n"
                                   "duration: {3}".format("Transit", routes['bus']['summary'], routes['bus']['distance'],
                                                          routes['bus']['duration']))
        self.route_1.Bind(wx.EVT_BUTTON, lambda event: self.route_selection(event, 1))
        self.route_2_desc.SetLabel("{0} summary: {1}\n"
                                   "distance: {2}\n"
                                   "duration: {3}\n"
                                   "confidence: {4}".format("Bixi 1", routes['bixi'][0]['summary'],
                                                            routes['bixi'][0]['distance'],
                                                            routes['bixi'][0]['duration'],
                                                            routes['bixi'][0]['confidence']))
        self.route_2.Bind(wx.EVT_BUTTON, lambda event: self.construct_route_selection(event, 2))
        self.route_3_desc.SetLabel("{0} summary: {1}\n"
                                   "distance: {2}\n"
                                   "duration: {3}\n"
                                   "confidence: {4}".format("Bixi 2", routes['bixi'][1]['summary'],
                                                            routes['bixi'][1]['distance'],
                                                            routes['bixi'][1]['duration'],
                                                            routes['bixi'][1]['confidence']))
        self.route_3.Bind(wx.EVT_BUTTON, lambda event: self.construct_route_selection(event, 2))
        self.route_3_desc.SetLabel("{0} summary: {1}\n"
                                   "distance: {2}\n"
                                   "duration: {3}\n"
                                   "confidence: {4}".format("Bixi 3", routes['bixi'][2]['summary'],
                                                            routes['bixi'][2]['distance'],
                                                            routes['bixi'][2]['duration'],
                                                            routes['bixi'][2]['confidence']))
        self.route_4.Bind(wx.EVT_BUTTON, lambda event: self.construct_route_selection(event, 2))

    def route_to_url(self, route_info):
        self.steps = route_info['steps']
        url = copy.copy(self.ROUTE_URL)
        for i in range(len(self.steps)):
            if self.steps[i]['travel_mode'] == "WALKING":
                if i == 0:
                    # make start marker at this point GREEN
                   url += "{0}{1}{2}{3},{4}".format(self.MARKER_TEMPLATE[0], "green", self.MARKER_TEMPLATE[1],
                                                   self.steps[i]['start_location']['lat'],
                                                   self.steps[i]['start_location']['lng'])
                elif self.steps[i-1]['travel_mode'] == "BICYCLING" or self.steps[i-1]['travel_mode'] == "TRANSIT":
                    # make bike/bus destination marker BLUE
                    url += "{0}{1}{2}{3},{4}".format(self.MARKER_TEMPLATE[0], "blue", self.MARKER_TEMPLATE[1],
                                                   self.steps[i-1]['end_location']['lat'],
                                                   self.steps[i-1]['end_location']['lng'])
                elif i == len(self.steps) - 1:
                    # make final destination marker RED
                    url += "{0}{1}{2}{3},{4}".format(self.MARKER_TEMPLATE[0], "red", self.MARKER_TEMPLATE[1],
                                                   self.steps[i]['end_location']['lat'],
                                                   self.steps[i]['end_location']['lng'])

                #make a path color BLUE
                url += "{0}{1}{2}{3}".format(self.PATH_TEMPLATE[0], "blue", self.PATH_TEMPLATE[1],
                                          self.steps[i]['polyline']['points'])
            elif self.steps[i]['travel_mode'] == "BICYCLING":
                if self.steps[i-1]['travel_mode'] == "WALKING":
                    # make start bike marker BLUE
                    url += "{0}{1}{2}{3},{4}".format(self.MARKER_TEMPLATE[0], "blue", self.MARKER_TEMPLATE[1],
                                                     self.steps[i]['start_location']['lat'],
                                                     self.steps[i]['start_location']['lng'])

                # make a path color ORANGE
                url += "{0}{1}{2}{3}".format(self.PATH_TEMPLATE[0], "orange", self.PATH_TEMPLATE[1],
                                          self.steps[i]['polyline']['points'])
            elif self.steps[i]['travel_mode'] == "TRANSIT":
                if self.steps[i-1]['travel_mode'] == "WALKING":
                    # make start bike marker BLUE
                    url += "{0}{1}{2}{3},{4}".format(self.MARKER_TEMPLATE[0], "blue", self.MARKER_TEMPLATE[1],
                                                     self.steps[i]['start_location']['lat'],
                                                     self.steps[i]['start_location']['lng'])

                # make a path color RED
                url += "{0}{1}{2}{3}".format(self.PATH_TEMPLATE[0], "red", self.PATH_TEMPLATE[1],
                                             self.steps[i]['polyline']['points'])
            else:
                print "Transportation mode not supported"
                return None

        url += self.API_KEY
        print url
        return url

    def monitor_communication(self):
        data_in = json.loads(self.s.recv(1024))
        while data_in['action'] != "done":
            if data_in['action'] == 'route_info':
                # update map to show selected route
                self.display_map(self.route_to_url(data_in['details']['route']))
            elif data_in['action'] == 'new_route':
                # update to show new route
                self.display_map(self.route_to_url(data_in['details']['route']))

            self.s.sendall(json.dumps(self.construct_location_response(self.iterator)))
            data_in = json.loads(self.s.recv(1024))

        print json.dumps(data_in)
        wx.MessageBox('You have arrived at your destination', 'Arrived', wx.OK | wx.ICON_EXCLAMATION)
        self.s.close()

    def demo_monitor_communication(self, event):
        self.instruction.SetLabel(self.steps[self.iterator]['html_instructions'])
        self.s.sendall(json.dumps(self.construct_location_response(self.iterator + 1)))
        data_in = json.loads(self.s.recv(1024))
        if data_in['action'] == 'route_info':
            # update map to show selected route
            self.display_map(self.route_to_url(data_in['details']['route']))
        elif data_in['action'] == 'new_route':
            # update to show new route
            self.display_map(self.route_to_url(data_in['details']['route']))
        elif data_in['action'] == 'done':
            wx.MessageBox('You have arrived at your destination', 'Arrived', wx.OK | wx.ICON_EXCLAMATION)
            self.s.close()
            self.iterator = 0
            return

        self.iterator += 1

    def construct_new_trip_request(self, destination, origin=ORIGIN):
        data_out = {'action': "new_trip", 'details': {"user_id": 0, "origin": origin, "destination": destination}}
        return data_out

    def route_selection(self, event, select):
        data_out = {'action': "selection", 'details': {'user_id': 0, 'selection': select}}
        print "selected {0}".format(select)
        self.s.sendall(json.dumps(data_out))

        # commented out for demo simulation
        # self.monitor_communication()

    def construct_location_response(self, i):
        data_out = {'action': "location", 'details': {'user_id': 0, 'location': {'lat': self.steps[i]['start_location']['lat'],
                                                                                 'lng': self.steps[i]['start_location']['lng']}}}
        return data_out

if __name__ == '__main__':
    app = wx.App()
    window = Gui(None, title='PHAST')
    app.MainLoop()
