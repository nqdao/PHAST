import Bixis
import GoogleMapsInterface, ConfidenceCalculator
import json
import os
import time
import sys
import subprocess
import CheckFileThread
import socket
import pytz, datetime

# test locations
test_locs = {
    "destination": '370 Queen St W, Toronto, ON',
    "origin": {
        "lat": 43.659865,
        "lng": -79.396703
    }
}

HOST = ''
PORT = 6644

class Routing:

    def __init__(self, user_id, stations_file, client_filename, origin, destination):
        self.finished = False   # used for the file checking thread for exiting
        self.station_id = -1
        self.user_id = user_id
        self.dest_stations = []
        self.num_origin_stations = 10
        self.num_destination_stations = 3
        self.total_routes = 4
        self.local = pytz.timezone("Canada/Eastern")
        self.calc = ConfidenceCalculator.ConfidenceCalculator()
        self.client_filename = client_filename  # coreclient.py
        self.bixis = Bixis.Bixis(stations_file)
        self.bixi_station_file = stations_file
        self.gmaps = GoogleMapsInterface.GoogleMapsInterface()
        self.origin = self.convert_string_to_geocode(origin)
        self.destination = self.convert_string_to_geocode(destination)
        self.routes = self.get_routes()

        # 
        # "routes" :                   
        #     [{  
        #         "summary" : "",     
        #         "distance": "",
        #         "duration": "",
        #         "confidence": "",
        #         "steps" : [...],
        #     }, ...] 

    def get_routes(self, reroute=False, reroute_location=None):
        S_S1_routes = []
        S1_D1_routes = []
        D1_D_routes = []
        S_D_routes = []

        if not reroute:
            # get the 10 closest stations to origin with at least 2 bikes
            origin_stations = self.viable_locations(self.origin,self.num_origin_stations,least=2, least_test="bikes")

            # find the walking directions to each of the 10 origin stations
            for station in origin_stations:
                #get route
                route = self.gmaps.get_directions(self.origin,station["coordinates"],'walking')[0]

                S_S1_routes.append({"id": station["id"],"route": route})


            # find the probability that these stations will have bikes upon arrival
            S_S1_routes = self.pare_by_confidence(S_S1_routes, 0.8)

            print origin_stations
            sys.exit(1)

            # remove the origin stations that were removed in the above paring
            removed = 0
            # for 

            # pare down to 3 closest origin stations to walking destination
            origin_stations = self.bixis.get_closest_stations(self.destination,origin_stations,3)

            # remove the routes for the stations that were removed in the above paring


            # find the 5 closest stations to destination with at least 5 slots
            destination_stations = self.viable_locations(self.destination,self.num_destination_stations,
                least=5, least_test="docks")

            # find walking directions from each station to destination station
            for station in destination_stations:
                #get route
                route = self.gmaps.get_directions(station["coordinates"],
                    self.destination,'walking')[0]

                D1_D_routes.append({"id": station["id"],"route": route})

            # find biking direction from each starting station to each destination station
            for S1 in origin_stations:
                for D1 in destination_stations:
                    route = self.gmaps.get_directions(S1["coordinates"],D1["coordinates"],
                        'bicycling')[0]

                    S1_D1_routes.append({"origin_id": S1["id"], "destination_id": D1["id"], "route":route})

            # the walk should always be the first route in the list
            walk = self.gmaps.get_directions(self.origin,self.destination,'walking')[0]
            # print_json(walk)
            S_D_routes.append({"type": "WALKING", "summary":walk["summary"],
                "distance": walk["legs"][0]["distance"]["value"], "duration":walk["legs"][0]["duration"]["value"], 
                "confidence": "1", "steps": walk["legs"][0]["steps"]})

            unsorted_routes = []

            # determine travel time for each path from two walking legs and one biking leg
            for first_leg in S_S1_routes:
                for second_leg in S1_D1_routes:
                    for third_leg in D1_D_routes:
                        # only combine routes that share stations
                        if (first_leg["id"] == second_leg["origin_id"]) and (third_leg["id"] == second_leg["destination_id"]):

                            # print_json(first_leg)

                            # print "*"*40

                            # print_json(second_leg)

                            # print "*"*40

                            # print_json(third_leg)

                            # print first_leg["route"]["legs"][0]
                            # print second_leg["route"]["legs"][0]
                            # print third_leg["route"]["legs"][0]


                            total_time = first_leg["route"]["legs"][0]["duration"]["value"] + \
                                second_leg["route"]["legs"][0]["duration"]["value"] + \
                                third_leg["route"]["legs"][0]["duration"]["value"]

                            time_to_D1 = first_leg["route"]["legs"][0]["duration"]["value"] + \
                                second_leg["route"]["legs"][0]["duration"]["value"]

                            # our confidence level that the destination station will be available at the time of arrival
                            # print "testing confidence with parameters:\nstation id: {0}\nArrival time (UNIX): {1}".format(third_leg["id"],int(time.time())+time_to_D1)
                            # confidence = self.bixis.calculate_confidence(third_leg["id"],int(time.time())+time_to_D1)
                            # print "resulting confidence: {}\n".format(confidence)
                            confidence = 0.99
                            total_distance = first_leg["route"]["legs"][0]["distance"]["value"] + second_leg["route"]["legs"][0]["distance"]["value"] + third_leg["route"]["legs"][0]["distance"]["value"]

                            travel = {"start_walk": first_leg["route"], "bicycling": second_leg["route"],"end_walk": third_leg["route"]}

                            combined_steps = first_leg["route"]["legs"][0]["steps"] + second_leg["route"]["legs"][0]["steps"] + third_leg["route"]["legs"][0]["steps"] 

                            # print second_leg["route"]

                            unsorted_routes.append({"type": "BIXI", "summary":second_leg["route"]["summary"],"distance": total_distance,
                                "duration":total_time, "confidence": confidence, "steps": combined_steps, "destination_id":third_leg["id"]})


            # find the top three bixi routes based on total time
            for i in range(self.total_routes):         
                count = 0
                min_time = 99999999
                best_index = 0
                for route in unsorted_routes:
                    if route["duration"] < min_time:
                        min_time = route["duration"]
                        best_index = count
                    count = count + 1

                self.dest_stations.append(unsorted_routes[best_index]["destination_id"])
                S_D_routes.append(unsorted_routes.pop(best_index))



            # print_json(S_D_routes)
            # print bus["route"]["legs"][0]["distance"]["value"]
            # print bus["route"]["legs"][0]["duration"]["value"]
            # print bus["route"]["summary"]
            # print bus["route"]["legs"][0]["steps"]

        if reroute:
            # here, the original end station that the user had selected has had its last space filled up

            # find the 2 closest stations to destination with at least 3 slots
            destination_stations = self.viable_locations(self.destination,2,
                least=3, least_test="docks")

            # find walking directions from each station to destination station
            for station in destination_stations:
                #get route
                route = self.gmaps.get_directions(station["coordinates"], self.destination,'walking')[0]

                D1_D_routes.append({"id": station["id"],"route": route})

            # find biking direction from the current location to each destination station
            for D1 in destination_stations:
                route = self.gmaps.get_directions(reroute_location,D1["coordinates"],'bicycling')[0]

                S1_D1_routes.append({"destination_id": D1["id"], "route":route})

            # package travel information based on two legs of journey
            max_confidence = 0
            for second_leg in S1_D1_routes:
                for third_leg in D1_D_routes:
                    # only combine routes that share stations
                    if (third_leg["id"] == second_leg["destination_id"]):

                        # print_json(first_leg)

                        # print "*"*40

                        # print_json(second_leg)

                        # print "*"*40

                        # print_json(third_leg)

                        # print first_leg["route"]["legs"][0]
                        # print second_leg["route"]["legs"][0]
                        # print third_leg["route"]["legs"][0]


                        total_time = second_leg["route"]["legs"][0]["duration"]["value"] + third_leg["route"]["legs"][0]["duration"]["value"]
                        time_to_D1 = second_leg["route"]["legs"][0]["duration"]["value"]
                        confidence = self.bixis.calculate_confidence(third_leg["id"],int(time.time())+time_to_D1)

                        #only send the user the path we are the most confident about
                        if confidence > max_confidence:

                            travel = {"bicycling": second_leg["route"],"end_walk": third_leg["route"]}

                            S_D_routes = [{"stations": {"end": third_leg["id"]},"path":travel,"time":total_time, "confidence": confidence}]

                        

                            # our confidence level that the destination station will be available at the time of arrival
                            # print "testing confidence with parameters:\nstation id: {0}\nArrival time (UNIX): {1}".format(third_leg["id"],int(time.time())+time_to_D1)
                            # print "resulting confidence: {}\n".format(confidence)

                            # total_distance = second_leg["route"]["legs"][0]["distance"]["value"] + third_leg["route"]["legs"][0]["distance"]["value"]

                            # combined_steps = second_leg["route"]["legs"][0]["steps"] + third_leg["route"]["legs"][0]["steps"] 

                            # # print second_leg["route"]

                            # S_D_routes = {"summary":second_leg["route"]["summary"],"distance": total_distance,
                            #     "duration":total_time, "confidence": confidence, "steps": combined_steps, "destination_station": third_leg["id"]}

        return S_D_routes

    def station_selection(self,selection):
        # the selection of a station to end at should spawn a thread that will monitor the stations
        # json file and see if that station goes to 0 empty docks
        if type(selection) is int:
            selection = selection - 1
            self.station_id = self.dest_stations[selection]
            print "station {} selected".format(self.station_id)
        else:
            print "error, expecting int"
            sys.exit(1)


        self.file_check_thread = CheckFileThread.CheckFileThread(self.check_file)
        self.file_check_thread.start()

    def pare_by_confidence(self, routes, threshold):
        # routes should be list of dictionaries in the form of 
        # [{"id": station["id"],"route": route},.....,{"id": station["id"],"route": route}]
        probs = []

        for route in routes:
            # get the total time in seconds that it takes to walk to the station
            walk_time = route["route"]["legs"][0]["duration"]["value"] + 30     #add 30 seconds to account for calculation and selection

            # get the datetime object for the time walk_time seconds from now
            end_time = datetime.datetime.fromtimestamp(time.time() + walk_time)
            local_dt = self.local.localize(end_time,is_dst = None)
            utc_dt = local_dt.astimezone(pytz.utc)
            end_time = "{0}:{1}:{2}".format(utc_dt.hour,utc_dt.minute,utc_dt.second)

            # find the probability that there are sufficient bikes at the arrival time
            # and add this information to the probabilities list
            probs.append(self.calc.get_probability(route["id"],end_time))

        new_routes = []

        for i in range(len(routes)):
            print probs[i]
            if probs[i] > threshold:
                routes[i]["probability"] = probs[i]
                new_routes.append(routes[i])

        return new_routes

    def update_route(self):
        # we need to find the current location of the user to update the route
        command = {"action": "get_location","details":{ "user_id": self.user_id}}
        location_details = self.send_message(command)
        print_json(location_details)
        #make sure that the returned dictionary is properly formatted
        if location_details["action"] == "location":
            location = location_details["details"]["location"]
            if ('lng' in location.keys()) and ('lat' in location.keys()):
                # obtain the best new route and send the message about the update to the edge
                self.routes = self.get_routes(reroute=True,reroute_location=location)
                message = {"action": "new_route", "details":{"user_id":self.user_id, "route":self.routes}}
                dummy = self.send_message(message)
                # restart the file checking process
                print_json(self.routes)
                self.station_selection = self.routes[0]["stations"]["end"]
            else:
                print "expecting details key to contain lng and lat"
                sys.exit(1)
        else:
            print "Error in returned location json"
            sys.exit(1)

    def send_message(self, message):
        dataout = json.dumps(message)   

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT)) 

        s.sendall(dataout)

        datain = s.recv(8192)
        s.close()
        parsed_json = json.loads(datain)

        return parsed_json

    def viable_locations(self,location, number_of_locations, least=0,least_test=None):

        return self.bixis.get_closest_stations(location,self.bixis.stations, 
            number_of_locations, least=least,least_test=least_test)

    def convert_string_to_geocode(self,location_string):
        if isinstance(location_string, basestring):
            location_string = self.gmaps.get_geocode(location_string)        
        return location_string

    def build_directions_matrix(self, start=None,dest=None):

        if start != None and dest != None:
            start_subset = self.viable_locations(start,5)
            dest_subset = self.viable_locations(dest,5)

        for station1 in start_subset:           
            self.bixis.routes[station1["station_id"]] = {}
            for station2 in dest_subset:
                if station1["station_id"] is not station2["station_id"]:
                    print "Obtaining route from station {0} to station {1}".format(
                        station1["station_id"], station2["station_id"])
                    self.bixis.routes[station1["station_id"]][station2["station_id"]] = \
                        self.gmaps.get_directions(station1["coordinates"], station2["coordinates"],
                            'bicycling')

    def export_routes_to_file(self,filename):
        with open(filename, 'w') as outfile:
            json.dump(self.routes, outfile, indent=4, sort_keys=True)

    def force_finish(self):
        self.finished = False

    def print_route(self,route_json):
        legs = ["1st", "2nd", "3rd"]
        for leg in legs:
            print "{} leg:\n".format(leg)
            print json.dumps(route_json[leg], indent=4, sort_keys=True)
            print "\n{}\n".format("*"*50)

    def check_file(self):
        last_update = os.stat(self.bixi_station_file)[8]
        while not self.finished:
            if os.stat(self.bixi_station_file)[8] != last_update:

                last_update = os.stat(self.bixi_station_file)[8]
                print "stations file changed"
                time.sleep(0.5)
                # the file has been edited, open it and check if our station has gone to 0 open docks
                self.bixis.read_stations_file()
                if self.bixis.is_empty(self.station_id):
                    # reroute and then die
                    self.update_route()
                    # print "it's empty"
                    break


            time.sleep(1)

def main():
    # test_routes = Routing(1, "stations.json", "coreclient.py", test_locs["origin"], test_locs["destination"])
    # test_routes.export_routes_to_file("test_paths.json")

    testing = Routing(1, "stations.json", "coreclient.py", test_locs["origin"], test_locs["destination"])
    testing.station_selection(2)
    print "selected station if is {}".format(testing.station_id)


def print_json(json_object):
    print json.dumps(json_object, indent=4, sort_keys=True)
    print "\n"
# path = test_routes.build_path(start,dest)
# test_routes.print_route(path)


if __name__ == "__main__":
    main()
