# a module to obtain routes from bixi station information user starting location
# all coordinates assumed to be of the form [latitude, longitude]

import CVSTInterface
import os, math, json
import time


class Bixis:

    def __init__(self, stations_file):
        self.routes = {}
        self.CVST = CVSTInterface.CVSTInterface()
        self.stations = []

        # open up and store the stations if the db file containing their general information
        # already exists.
        # should the db file not exist, build it.
        
        # if os.path.isfile(self.STATIONS_FILE):
        with open(stations_file) as data_file:
            self.stations = json.load(data_file)
            # else:
            # 	self.populate_station_locations()
            # 	with open(self.STATIONS_FILE,'w') as outfile:
            # 		json.dump(self.stations, outfile, indent=4, sort_keys=True)

    def populate_station_locations(self):
        temp_stations = self.CVST.get_all_current_stations()
        for station in temp_stations:
            # determine lat and long (note that this will only work for locations
            # in both the north and western hemispheres)
            print "working on station {}".format(station["station_id"])
            if station["coordinates"][0] < 0:
                lat = station["coordinates"][1]
                lng = station["coordinates"][0]
            else:
                lng = station["coordinates"][1]
                lat = station["coordinates"][0]

            del station["coordinates"]
            station["coordinates"] = {"lat": lat, "lng": lng}

            station["max_docks"] = self.CVST.get_maximum_docks(station["station_id"])
            self.stations.append(station)

    def get_closest_stations(self, location, stations_list, 
                                number_of_stations, least=0,
                                least_test=None):

        closest = []
        # print stations_list[0]
        for station in stations_list:
            # only test for a minimum number of bikes if least bikes has been set
            if least_test == "bikes":
                if station["max_docks"] - station["empty_docks"] >= least:
                    distance = self.get_distance(location, station["coordinates"])
                    if len(closest) < number_of_stations:
                        closest.append({"station_id": station["station_id"], "distance": distance,
                                        "coordinates": station["coordinates"]})
                    else:
                        max_location = 0
                        index = 0
                        for close_station in closest:
                            if close_station["distance"] > closest[max_location]["distance"]:
                                max_location = index
                            index = index + 1

                        if distance < closest[max_location]["distance"]:
                            del closest[max_location]
                            closest.append({"station_id": station["station_id"], "distance": distance,
                                            "coordinates": station["coordinates"]})

            elif least_test == "docks":
                if station["empty_docks"] >= least:
                    distance = self.get_distance(location, station["coordinates"])
                    if len(closest) < number_of_stations:
                        closest.append({"station_id": station["station_id"], "distance": distance,
                                        "coordinates": station["coordinates"]})
                    else:
                        max_location = 0
                        index = 0
                        for close_station in closest:
                            if close_station["distance"] > closest[max_location]["distance"]:
                                max_location = index
                            index = index + 1

                        if distance < closest[max_location]["distance"]:
                            del closest[max_location]
                            closest.append({"station_id": station["station_id"], "distance": distance,
                                            "coordinates": station["coordinates"]})
            else:
                distance = self.get_distance(location, station["coordinates"])
                if len(closest) < number_of_stations:
                    closest.append({"station_id": station["station_id"], "distance": distance,
                                    "coordinates": station["coordinates"]})
                else:
                    max_location = 0
                    index = 0
                    for close_station in closest:
                        if close_station["distance"] > closest[max_location]["distance"]:
                            max_location = index
                        index = index + 1

                    if distance < closest[max_location]["distance"]:
                        del closest[max_location]
                        closest.append({"station_id": station["station_id"], "distance": distance,
                                        "coordinates": station["coordinates"]})

        return closest

    def get_distance(self, start, dest):
        # print start
        # print dest.
        return math.sqrt(((start["lat"] - dest["lat"]) ** 2 + (start["lng"] - dest["lng"]) ** 2))

    def print_stations(self):
        for station in self.CVST.stations:
            print "station {0}: ({1},{2})".format(station["station_id"],
                    station["coordinates"]["lat"], station["coordinates"]["lng"])

    def sort_stations(self, stations_list):
        pass

    def calculate_confidence(self, station_id, arrival_time):
        #arrival_time is in UNIX time
        seconds_in_day = 86400
        update_interval = 300
        start_interval = arrival_time - 120
        end_interval = arrival_time + 180
        historical_data = self.CVST.get_current_station_data(station_id)
        print len(historical_data)
        empty_docks_list = []
        for days in range(1, 11):
            print days
            for entry in historical_data:
                print entry["timestamp"], start_interval - days*seconds_in_day, end_interval - days*seconds_in_day

                if (start_interval - days*seconds_in_day) < entry["timestamp"] < (end_interval - days*seconds_in_day):
                    empty_docks_list.append(entry["empty_docks"])
                    break
                elif entry["timestamp"] == (end_interval - days*seconds_in_day) or \
                                        entry["timestamp"] - update_interval == (start_interval - days*seconds_in_day):
                    empty_docks_list.append(entry["empty_docks"])
                    print entry["timestamp"], start_interval - days*seconds_in_day, end_interval - days*seconds_in_day
                    break

        #confidence = 1 - self.poisson(0, self.mean(empty_docks_list))
        confidence = 0
        return confidence

    @staticmethod
    def poisson(actual, mean):
        p = math.exp(-mean)
        for i in xrange(actual):
            p *= mean
            p /= i+1
        return p

    @staticmethod
    def mean(l):
        return sum(l)/len(l)

# def main():
# 	bixis = BixiRoutes()
# 	closest = bixis.get_closest(UofT_location,7)
# 	for station in closest:
# 		print "station {0}:\n--------------\nlocation: ({1},{2})\ndistance: {3}\n".format(
# 			station["id"],station["coordinates"][0], station["coordinates"][1],station["distance"])

# if __name__ == "__main__":
# 	main()

if __name__ == '__main__':
    bixis = Bixis()
    while True:
        updated_station_list = bixis.CVST.get_all_current_stations()
        for updated_station in updated_station_list:
            for station in bixis.stations:
                if updated_station["station_id"] == station["station_id"]:
                    print "updated_station ", updated_station["station_id"], "station", station["station_id"]
                    for key in updated_station:
                        if key == "coordinates":
                            station["coordinates"]["lat"] = updated_station["coordinates"][1]
                            station["coordinates"]["lng"] = updated_station["coordinates"][0]
                        else:
                            station[key] = updated_station[key]

        print "updating CVST data"
        with open(bixis.STATIONS_FILE, 'w') as outfile:
            json.dump(bixis.stations, outfile, indent=4, sort_keys=True)
        time.sleep(10)
