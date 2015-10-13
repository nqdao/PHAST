import Bixis
import GoogleMapsInterface
import json
import os
import time

# test locations
test_locs = {
    "dest": '370 Queen St W, Toronto, ON',
    "start": {
        "lat": 43.659865,
        "lng": -79.396703
    }
}

class Routing:

    def __init__(self, stations_file, start, destination):
        self.finished = False   # used for the file checking thread for exiting
        self.bixis = Bixis.Bixis(stations_file)
        self.gmaps = GoogleMapsInterface.GoogleMapsInterface()
        self.start = self.convert_string_to_geocode(start)
        self.destination = self.convert_string_to_geocode(destination)
        self.routes = self.get_routes()

    def get_routes(self):
        S_S1_routes = []
        S1_D1_routes = []
        D1_D_routes = []
        S_D_routes = {"bixi": []}

        # get the 6 closest stations to origin with at least 2 bikes
        origin_stations = self.viable_locations(self.start,6,least=3, least_test="bikes")

        # print origin_stations[1]

        # pare down to 3 closest origin stations to walking destination
        origin_stations = self.bixis.get_closest_stations(self.destination,origin_stations,3)

        # find the walking directions to each of the 3 origin stations
        for station in origin_stations:
            #get route
            route = self.gmaps.get_directions(self.start,station["coordinates"],'walking')[0]

            S_S1_routes.append({"station_id": station["station_id"],"route": route})

        # find the 5 closest stations to destination with at least 5 slots
        destination_stations = self.viable_locations(self.destination,5,
            least=5, least_test="docks")

        # find walking directions from each station to destination station
        for station in destination_stations:
            #get route
            route = self.gmaps.get_directions(station["coordinates"],
                self.destination,'walking')[0]

            D1_D_routes.append({"station_id": station["station_id"],"route": route})

        # find biking direction from each starting station to each destination station
        for S1 in origin_stations:
            for D1 in destination_stations:
                route = self.gmaps.get_directions(S1["coordinates"],D1["coordinates"],
                    'bicycling')[0]

                S1_D1_routes.append({"origin_id": S1["station_id"], 
                    "destination_id": D1["station_id"], "route":route})

        # determine travel time for each path from two walking legs and one biking leg
        for first_leg in S_S1_routes:
            for second_leg in S1_D1_routes:
                for third_leg in D1_D_routes:
                    # only combine routes that share stations
                    if (first_leg["station_id"] == second_leg["origin_id"]) and \
                        (third_leg["station_id"] == second_leg["destination_id"]):

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

                        travel = {"start_walk": first_leg["route"], "bicycling": second_leg["route"], 
                            "end_walk": third_leg["route"]}

                        S_D_routes["bixi"].append({"stations": {"start":first_leg["station_id"],
                            "end": third_leg["station_id"]},"path":travel,"time":total_time})

        # find confidence value for each path based on arrival time
        # for path in S_D_routes["bixi"]:
        #     path["confidence"] = get_confidence(path["end"],int(time.time())+path["time"])

        # finally, get the bus route
        S_D_routes["bus"] = self.gmaps.get_directions(self.start,self.destination,'transit')[0]

        return S_D_routes

    def build_path(self,start_location,destination_location):
        # 1) find closest bixis to start
        start_bixi = self.viable_locations(start_location,1)[0]

        # 2) find closest bixi to destination
        end_bixi = self.viable_locations(destination_location,1)[0]

        # 3) obtain path between start and bixi1
        first_leg = self.gmaps.get_directions(start_location,
            start_bixi["coordinates"],'walking')[0]

        # 4) obtain path between bixi1 an bixi2
        second_leg = self.gmaps.get_directions(start_bixi["coordinates"],
            end_bixi["coordinates"],'bicycling')[0]

        # 5) obtain path between bixi2 and destination
        third_leg = self.gmaps.get_directions(end_bixi["coordinates"],
            destination_location,'walking')[0]

        # 6) return a json containing clearly demarcated steps and action ('walking','bicycling')
        return {"1st":first_leg,"2nd":second_leg,"3rd":third_leg}

    def viable_locations(self,location, number_of_locations, least=0,least_test=None):
        # print "before location:\t{}".format(location)
        # else:
        #   geocode = location

        return self.bixis.get_closest_stations(location,self.bixis.stations, 
            number_of_locations, least=least,least_test=least_test)

    def convert_string_to_geocode(self,location_string):
        if isinstance(location_string, basestring):
            location_string = self.gmaps.get_geocode(location_string)        
        return location_string

    def build_directions_matrix(self, start=None,dest=None):
        # for station1 in self.bixis.CVST.stations:         
        #   self.bixis.routes[station1["station_id"]] = {}
        #   for station2 in self.bixis.CVST.stations:
        #       if station1["station_id"] is not station2["station_id"]:
        #           print "Obtaining route from station {0} to station {1}".format(
        #               station1["station_id"], station2["station_id"])
        #           self.bixis.routes[station1["station_id"]][station2["station_id"]] = \
        #               self.gmaps.get_directions(station1["coordinates"], station2["coordinates"],
        #                   'bicycling')

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

    def check_if_file_updated(self):
        last_update = os.stat(self.bixi_station_file)[8]
        while not self.finished:
            if os.stat(self.bixi_station_file)[8] != last_update:
                self.check_file()
            time.sleep(1)

    def check_file(self):
        with open(self.bixi_station_file,'r') as bixi_file:
            self.bixis.stations = json.load(bixi_file)

        """ do some other stuff """

def main():
    test_routes = Routing()
    test_routes.build_directions_matrix(test_locs["start"], test_locs["dest"])
    test_routes.export_routes_to_file(test_routes.bixis.routes, "test_paths.json")


def print_json(json_object):
    print json.dumps(json_object, indent=4, sort_keys=True)
# path = test_routes.build_path(start,dest)
# test_routes.print_route(path)

if __name__ == "__main__":
    main()
