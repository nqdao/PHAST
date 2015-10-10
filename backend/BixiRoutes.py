# a module to obtain routes from bixi station information user starting location
# all coordinates assumed to be of the form [latitude, longitude]

import math
import CVSTInterface

class BixiRoutes:

	def __init__(self):
		self.CVST = CVSTInterface.CVSTInterface()
		self.routes = {}

	def get_closest(self,location, number_of_stations):
		closest = []
		for station in self.CVST.stations:
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