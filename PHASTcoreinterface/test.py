from Bixis import Bixis
import time
from datetime import datetime

bixis = Bixis("stations.json")
station_id = 13
now = int(time.time())

print datetime.fromtimestamp(time.time()), datetime.fromtimestamp(time.time()).weekday()
print bixis.calculate_confidence(station_id, now)

