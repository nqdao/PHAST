# a module used to interface with CVST API in order to obtain information
# on bixi station information

import requests
import json
import os.path
import datetime

class CVSTInterface:

	BASE_URL = "http://portal.cvst.ca/api/0.1/bixi"
	STATIONS_FILE = "stations.txt"

	def __init__(self):
		self.stations = []
		if os.path.isfile(self.STATIONS_FILE):
			with open(self.STATIONS_FILE) as data_file:
				stations_json = json.load(data_file)
			for station in stations_json:
				self.stations.append(station)
		else:
			self.populate_station_locations()
			with open(self.STATIONS_FILE,'w') as outfile:
				json.dump(self.stations, outfile, indent=4, sort_keys=True)

	def populate_station_locations(self):
		temp_stations = requests.get("{}".format(self.BASE_URL)).json()
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

			station["max_docks"] = self.get_maximum_docks(station["station_id"])
			self.stations.append(station)

	def get_current_station_data(self, station_id_list):
		requested_stations = {}
		for station_id in station_id_list:
			requested_stations["{}".format(station_id)] = requests.get("{0}/{1}".format(
				self.BASE_URL,station_id)).json()[0]
		return requested_stations

	def get_maximum_docks(self,station_id):
		dt = datetime.datetime.now()
		date = [str(dt.year),str(dt.month),str(dt.day)]
		time = [str(dt.hour),str(dt.minute)]
		for item in date:
			if len(item) < 2:
				item = "0{}".format(item)
		for item in time:
			if len(item) < 2:
				item = "0{}".format(item)

		end = "{0}T{1}EST".format("".join(date),"".join(time))

		station_back_info = self.get_historic_station_data(station_id,end_time=end,
			key="empty_docks")[0]

		max_docks = 0

		for previous in station_back_info:
			# print "{0}\n{1}\n".format(previous["date_time"],previous["empty_docks"])
			if previous["empty_docks"] > max_docks:
				max_docks = previous["empty_docks"]

		return max_docks


	def get_historic_station_data(self, station_id_list, start_time=None, end_time=None, key=None):
		# times should be string in the form of "<YYYY><MM><DD>T<HH><MM><Timezone>""
		stations_to_return = []

		if type(station_id_list) == list:
			for station_id in station_id_list:
				stations_to_return.append(requests.get("{0}/{1}?timestamp={2}".format(self.BASE_URL,
					station_id,end_time)).json())
		else:
			# print "{0}/{1}?timestamp={2}".format(self.BASE_URL,station_id_list,end_time)
			stations_to_return.append(requests.get("{0}/{1}?timestamp={2}".format(self.BASE_URL,
					station_id_list,end_time)).json())

		# print stations_to_return
		return stations_to_return

def main():
	test = CVSTInterface()
	print test.get_maximum_docks("10")

if __name__ == "__main__":
	main()
