# a module used to interface with CVST API in order to obtain information
# on bixi station information

import requests
import json

class CVSTInterface:

	BASE_URL = "http://portal.cvst.ca/api/0.1/bixi"

	def __init__(self):
		self.stations = []
		self.populate_station_locations()

	def populate_station_locations(self):
		temp_stations = requests.get("{}".format(self.BASE_URL)).json()
		for station in temp_stations:
			# determine lat and long (note that this will only work for locations
			# in both the north and western hemispheres)
			if station["coordinates"][0] < 0:
				lat = station["coordinates"][1]
				lng = station["coordinates"][0]
			else:
				lng = station["coordinates"][1]
				lat = station["coordinates"][0]

			del station["coordinates"]
			station["coordinates"] = {"lat":lat, "lng":lng}
			self.stations.append(station)

	def get_current_station_data(self, station_id_list):
		requested_stations = {}
		for station_id in station_id_list:
			requested_stations["{}".format(station_id)] = requests.get("{0}/{1}".format(
				self.BASE_URL,station_id)).json()[0]
		return requested_stations

	def get_historic_station_data(self, station_id_list, start_time, end_time):
		pass



