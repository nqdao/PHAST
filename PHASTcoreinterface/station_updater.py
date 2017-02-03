import Bixis

bixis = Bixis.Bixis("stations.json")

while True:
    updated_station_list = bixis.CVST.get_all_current_stations()
    for updated_station in updated_station_list:
        for station in bixis.stations:
            if updated_station["id"] == station["id"]:
                # print "updated_station ", updated_station["id"], "station", station["id"]
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
