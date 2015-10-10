# a module to obtain routes from bixi station information user starting location
# all coordinates assumed to be of the form [latitude, longitude]

import CVSTInterface
import os, math, json

class Bixis:

	STATIONS_FILE = "stations.json"

	def __init__(self):	
		self.routes = {}	
		self.CVST = CVSTInterface.CVSTInterface()
		self.stations = []
		if os.path.isfile(self.STATIONS_FILE):
			with open(self.STATIONS_FILE) as data_file:
				self.stations = json.load(data_file)
		else:
			self.populate_station_locations()
			with open(self.STATIONS_FILE,'w') as outfile:
				json.dump(self.stations, outfile, indent=4, sort_keys=True)

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
			station["coordinates"] = {"lat":lat, "lng":lng}

			station["max_docks"] = self.CVST.get_maximum_docks(station["station_id"])
			self.stations.append(station)

	def get_closest_stations(self,location, number_of_stations):
		closest = []
		for station in self.stations:
			distance = self.get_distance(location,station["coordinates"])
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
		# print dest
		return math.sqrt(((start["lat"] - dest["lat"])**2 + (start["lng"]-dest["lng"])**2))

	def print_stations(self):
		for station in self.CVST.stations:
			print "station {0}: ({1},{2})".format(station["station_id"],
				station["coordinates"]["lat"],station["coordinates"]["lng"])

	def sort_stations(self, stations_list):
		pass


# def main():
# 	bixis = BixiRoutes()
# 	closest = bixis.get_closest(UofT_location,7)
# 	for station in closest:
# 		print "station {0}:\n--------------\nlocation: ({1},{2})\ndistance: {3}\n".format(
# 			station["id"],station["coordinates"][0], station["coordinates"][1],station["distance"])

# if __name__ == "__main__":
# 	main()