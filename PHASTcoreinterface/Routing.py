import Bixis
import GoogleMapsInterface
import json
import os
import time
import sys
import subprocess
import CheckFileThread

# test locations
test_locs = {
    "destination": '370 Queen St W, Toronto, ON',
    "origin": {
        "lat": 43.659865,
        "lng": -79.396703
    }
}

class Routing:

    EDGE = "10.2.8.3"
    PORT = 6633

    def __init__(self, user_id, stations_file, client_filename, origin, destination):
        self.finished = False   # used for the file checking thread for exiting
        self.station_id = -1
        self.user_id = user_id
        self.num_origin_stations = 2
        self.num_destination_stations = 2
        self.client_filename = client_filename  # coreclient.py
        self.bixis = Bixis.Bixis(stations_file)
        self.gmaps = GoogleMapsInterface.GoogleMapsInterface()
        self.origin = self.convert_string_to_geocode(origin)
        self.destination = self.convert_string_to_geocode(destination)
        self.routes = self.get_routes()
        self.dest_stations = []

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
        S_D_routes = {"bixi": []}

        if not reroute:
            # get the 6 closest stations to origin with at least 2 bikes
            origin_stations = self.viable_locations(self.origin,self.num_origin_stations,least=3, least_test="bikes")

            # print origin_stations[1]

            # pare down to 3 closest origin stations to walking destination
            origin_stations = self.bixis.get_closest_stations(self.destination,origin_stations,3)

            # find the walking directions to each of the 3 origin stations
            for station in origin_stations:
                #get route
                route = self.gmaps.get_directions(self.origin,station["coordinates"],'walking')[0]

                S_S1_routes.append({"id": station["id"],"route": route})

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
                            print "testing confidence with parameters:\nstation id: {0}\nArrival time (UNIX): {1}".format(third_leg["id"],int(time.time())+time_to_D1)
                            confidence = self.bixis.calculate_confidence(third_leg["id"],int(time.time())+time_to_D1)
                            print "resulting confidence: {}\n".format(confidence)

                            total_distance = first_leg["route"]["legs"][0]["distance"]["value"] + second_leg["route"]["legs"][0]["distance"]["value"] + third_leg["route"]["legs"][0]["distance"]["value"]

                            travel = {"start_walk": first_leg["route"], "bicycling": second_leg["route"],"end_walk": third_leg["route"]}

                            combined_steps = first_leg["route"]["legs"][0]["steps"] + second_leg["route"]["legs"][0]["steps"] + third_leg["route"]["legs"][0]["steps"] 

                            # print second_leg["route"]

                            S_D_routes["bixi"].append({"summary":second_leg["route"]["summary"],"distance": total_distance,
                                "duration":total_time, "confidence": confidence, "steps": combined_steps, "destination_station": first_leg["id"]})

                            self.dest_stations.append(third_leg["id"])

            # finally, get the bus route
            S_D_routes["bus"] = self.gmaps.get_directions(self.origin,self.destination,'transit')[0]

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

                S1_D1_routes.append({"origin_id": S1["id"], "destination_id": D1["id"], "route":route})

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

                        #only send the user the path we are the most confident about
                        if confidence > max_confidence:

                            travel = {"bicycling": second_leg["route"],"end_walk": third_leg["route"]}

                            S_D_routes["bixi"] = [{"stations": {"end": third_leg["id"]},"path":travel,"time":total_time, "confidence": confidence}]

                        time_to_D1 = second_leg["route"]["legs"][0]["duration"]["value"]

                        # our confidence level that the destination station will be available at the time of arrival
                        # print "testing confidence with parameters:\nstation id: {0}\nArrival time (UNIX): {1}".format(third_leg["id"],int(time.time())+time_to_D1)
                        confidence = self.bixis.calculate_confidence(third_leg["id"],int(time.time())+time_to_D1)
                        # print "resulting confidence: {}\n".format(confidence)

                        total_distance = second_leg["route"]["legs"][0]["distance"]["value"] + third_leg["route"]["legs"][0]["distance"]["value"]

                        combined_steps = second_leg["route"]["legs"][0]["steps"] + third_leg["route"]["legs"][0]["steps"] 

                        # print second_leg["route"]

                        S_D_routes = {"summary":second_leg["route"]["summary"],"distance": total_distance,
                            "duration":total_time, "confidence": confidence, "steps": combined_steps, "destination_station": third_leg["id"]}

        return S_D_routes

    def station_selection(self,selection):
        # the selection of a station to end at should spawn a thread that will monitor the stations
        # json file and see if that station goes to 0 empty docks
        if type(selection) is int:
            self.station_id = self.dest_stations[selection]
        else:
            print "error, expecting int"
            sys.exit(1)

        self.file_check_thread = CheckFileThread.CheckFileThread(self.check_file)
        self.file_check_thread.start()

    def update_route(self):
        # we need to find the current location of the user to update the route
        command = {"action": "get_location","details":{ "user_id": self.user_id}}
        location_json = self.send_message(json.dumps(command))
        location_details = json.loads(location_json)
        #make sure that the returned dictionary is properly formatted
        if location_details["action"] == "location":
            location = location_details["details"]
            if ('lng' in location.keys()) and ('lat' in location.keys()):
                # obtain the best new route and send the message about the update to the edge
                self.routes = self.get_routes(reroute=True,reroute_location=location)
                message = {"action": "new_route", "details":{"user_id":self.user_id, "route":self.routes}}
                self.send_message(json.dumps(message))
                # restart the file checking process
                self.station_selection = self.routes["bixi"][0]["stations"]["end"]
            else:
                print "expecting details key to contain lng and lat"
                sys.exit(1)
        else:
            print "Error in returned location json"
            sys.exit(1)

    def send_message(self, message):
        command = " $ {0} {1} {2} {3}".format(self.client_filename,self.EDGE,self.PORT, message)
        print command
        return subprocess.check_output([self.client_filename,self.EDGE,self.PORT, message])

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
                time.sleep(0.5)
                # the file has been edited, open it and check if our station has gone to 0 open docks
                self.bixis.read_stations_file()
                if self.bixis.is_empty(self.station_id):
                    # reroute and then die
                    self.update_route()
                    break

            time.sleep(1)

def main():
    test_routes = Routing(1, "stations.json", "coreclient.py", test_locs["origin"], test_locs["destination"])
    test_routes.export_routes_to_file("test_paths.json")


def print_json(json_object):
    print json.dumps(json_object, indent=4, sort_keys=True)
# path = test_routes.build_path(start,dest)
# test_routes.print_route(path)

    end = "{0}T{1}EST".format("".join(date), "".join(time))

if __name__ == "__main__":
    main()
