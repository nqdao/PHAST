__author__ = 'Nhat-Quang'

import copy

INITIAL_URL = "https://maps.googleapis.com/maps/api/staticmap?center=CN+Tower,Toronto,ON&zoom=14&size=800x600&maptype=roadmap"
ROUTE_URL = "https://maps.googleapis.com/maps/api/staticmap?size=800x800"
API_KEY = "&key=AIzaSyA7LGD3TmN87_-Lr8sofhjaylZK1q87ra8"
PATH_TEMPLATE = ["&path=weight:10%7Ccolor:", "%7Cenc:"]
MARKER_TEMPLATE = ["&markers=color:", "%7C"]

url = copy.copy(ROUTE_URL)
url += "{0}{1}{2}{3},{4}".format(MARKER_TEMPLATE[0], "orange", MARKER_TEMPLATE[1], 1234, 5678)
print url

