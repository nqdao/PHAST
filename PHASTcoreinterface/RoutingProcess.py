import Bixis
import GoogleMapsInterface
import json

# test locations
test_locs = {
    "dest": '370 Queen St W, Toronto, ON',
    "start": {
        "lat": 43.659865,
        "lng": -79.396703
    }
}


class RoutingProcess:
    def __init__(self):
        self.bixis = Bixis.Bixis()
        self.gmaps = GoogleMapsInterface.GoogleMapsInterface()

    def build_path(self, start_location, destination_location):
        # 1) find closest bixi to start
        start_bixi = self.viable_locations(start_location, 1)[0]

        # 2) find closest bixi to destination
        end_bixi = self.viable_locations(destination_location, 1)[0]

        # 3) obtain path between start and bixi1
        first_leg = self.gmaps.get_directions(start_location,
                                              start_bixi["coordinates"], 'walking')[0]

        # 4) obtain path between bixi1 an bixi2
        second_leg = self.gmaps.get_directions(start_bixi["coordinates"],
                                               end_bixi["coordinates"], 'bicycling')[0]

        # 5) obtain path between bixi2 and destination
        third_leg = self.gmaps.get_directions(end_bixi["coordinates"],
                                              destination_location, 'walking')[0]

        # 6) return a json containing clearly demarcated steps and action ('walking','bicycling')
        return {"1st": first_leg, "2nd": second_leg, "3rd": third_leg}

    def viable_locations(self, location, number_of_locations):
        # print "before location:\t{}".format(location)
        if isinstance(location, basestring):
            location = self.convert_string_to_geocode(location)
        # else:
        # 	geocode = location

        # print "after location:\t{}".format(location)
        return self.bixis.get_closest_stations(location, number_of_locations)

    # add check for free spaces later

    def convert_string_to_geocode(self, location_string):
        geocode = self.gmaps.get_geocode(location_string)
        return geocode

    def build_directions_matrix(self, start=None, dest=None):
        # for station1 in self.bixis.CVST.stations:
        # 	self.bixis.routes[station1["station_id"]] = {}
        # 	for station2 in self.bixis.CVST.stations:
        # 		if station1["station_id"] is not station2["station_id"]:
        # 			print "Obtaining route from station {0} to station {1}".format(
        # 				station1["station_id"], station2["station_id"])
        # 			self.bixis.routes[station1["station_id"]][station2["station_id"]] = \
        # 				self.gmaps.get_directions(station1["coordinates"], station2["coordinates"],
        # 					'bicycling')

        if start != None and dest != None:
            start_subset = self.viable_locations(start, 5)
            dest_subset = self.viable_locations(dest, 5)

        for station1 in start_subset:
            self.bixis.routes[station1["station_id"]] = {}
            for station2 in dest_subset:
                if station1["station_id"] is not station2["station_id"]:
                    print "Obtaining route from station {0} to station {1}".format(
                        station1["station_id"], station2["station_id"])
                    self.bixis.routes[station1["station_id"]][station2["station_id"]] = \
                        self.gmaps.get_directions(station1["coordinates"], station2["coordinates"],
                                                  'bicycling')

    def export_routes_to_file(self, routes_json, filename):
        with open(filename, 'w') as outfile:
            json.dump(routes_json, outfile, indent=4, sort_keys=True)

    def print_route(self, route_json):
        legs = ["1st", "2nd", "3rd"]
        for leg in legs:
            print "{} leg:\n".format(leg)
            print json.dumps(route_json[leg], indent=4, sort_keys=True)
            print "\n{}\n".format("*" * 50)


def main():
    test_routes = Routing()
    test_routes.build_directions_matrix(test_locs["start"], test_locs["dest"])
    test_routes.export_routes_to_file(test_routes.bixis.routes, "test_paths.json")


# path = test_routes.build_path(start,dest)
# test_routes.print_route(path)

if __name__ == "__main__":
    main()
