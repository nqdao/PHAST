# a module used to interface with CVST API in order to obtain information
# on bixi station information

import requests
import json
import os.path
import datetime
from requests.auth import HTTPBasicAuth


class CVSTInterface:

    BASE_URL = "http://portal.cvst.ca/api/0.1/bixi"

    def __init__(self):
        self.user = "design_camp"
        self.password = "cvst_2015"

    def __execute_command(self,command):
        return requests.get(command,auth=HTTPBasicAuth(self.user, self.password))        

    def get_current_station_data(self, station_id_list):
        requested_stations = {}
        for station_id in station_id_list:
            command = "{0}/{1}".format(self.BASE_URL, station_id)
            requested_stations["{}".format(station_id)] = self.__execute_command(command).json()[0]
        return requested_stations

    def get_all_current_stations(self):
        command = self.BASE_URL
        return __execute_command(command).json()

    def get_maximum_docks(self, station_id):
        dt = datetime.datetime.now()
        date = [str(dt.year), str(dt.month), str(dt.day)]
        time = [str(dt.hour), str(dt.minute)]
        for item in date:
            if len(item) < 2:
                item = "0{}".format(item)
        for item in time:
            if len(item) < 2:
                item = "0{}".format(item)

        end = "{0}T{1}EST".format("".join(date), "".join(time))

        station_back_info = self.get_historic_station_data(station_id, end_time=end,
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

        if (start_time is None) or (end_time is None):
            print "Start and end times required"
            return -1

        if type(station_id_list) == list:
            for station_id in station_id_list:
                command = "{0}/{1}?starttime={2}&endtime={3}".format(self.BASE_URL,station_id, 
                    start_time,end_time)
                stations_to_return.append(self.__execute_command(command).json())
        else:
            # print "{0}/{1}?timestamp={2}".format(self.BASE_URL,station_id_list,end_time)
            command = "{0}/{1}?starttime={2}&endtime={3}".format(self.BASE_URL,station_id_list, 
                start_time,end_time)
            stations_to_return.append(self.__execute_command(command).json())

        # print stations_to_return
        return stations_to_return

    def continuous_update(self):
        while True:
            new_update = self.get_all_current_stations()




def main():
    test = CVSTInterface()
    print test.get_maximum_docks("10")


if __name__ == "__main__":
    main()
