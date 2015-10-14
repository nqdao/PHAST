from Bixis import Bixis
import time

bixis = Bixis("stations.json")
station_id = 13
now = int(time.time())
print bixis.calculate_confidence(station_id, now)

