# this is the module that will be used to interface with the google maps API
import googlemaps
import json

class GoogleMapsInterface:

	my_key = 'AIzaSyBe888aBum7q2ISF2ru2uG-hkygBaxnyYI'

	def __init__(self):
		self.interface = googlemaps.Client(key=self.my_key)

	def get_directions(self,origin,destination,mode):
		# mode must be one of 'walking', 'biking' and 'transit' for our purposes
		# print "mode is {}".format(mode)
		# print "origin: {0}\ndest: {1}\nmode: {2}".format(origin,destination,mode)
		directions = self.interface.directions(origin,destination,mode=mode)
		return directions

	def get_geocode(self,location_string):
		geocode_json = self.interface.geocode(location_string)[0]
		lat = geocode_json["geometry"]["location"]["lat"]
		lng = geocode_json["geometry"]["location"]["lng"]
		return {"lat":lat,"lng":lng}
		