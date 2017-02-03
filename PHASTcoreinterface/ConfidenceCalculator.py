import CVSTInterface
import time, os, json, re, math, sys
import numpy as np
import matplotlib.pyplot as plt

class ConfidenceCalculator():

    FILENAME = "BixiPMFs.json"
    MAXSIZE  = 120
    
    def __init__(self):
        self.interface = CVSTInterface.CVSTInterface()
        # print self.interface
        self.sleep_time = 1
        self.stations = {}
        self.read_stations_file()        

    def update_pmfs(self):
         end = int(time.time())
         start = end - 60*24*60*60 #two months
         for i in range(1,100):
            test = self.interface.get_historic_station_data(i,start_time=start,end_time=end)

            # if test

    def get_probability(self, station_id,time ):
        weights = [0.5,0.35,0.15]
        # print self.stations[station_id]["times"]
        time_pdf = self.stations[str(station_id)]["times"][self.round_time(time)]
        total = sum(time_pdf)
        prob = 0
        for i in range(3):
            prob =+ weights[i]*(time_pdf[i]/total)

        return 1 - prob

    def continuous_update(self):
        while True:
            new_update = self.get_all_current_stations()
            time.sleep(self.sleep_time)

    def read_stations_file(self):
        if os.path.isfile(self.FILENAME):            
            with open(self.FILENAME) as data_file:
                self.stations = json.load(data_file)
        else:
            self.populate_stations()
            self.load_initial_statistics()
            with open(self.FILENAME,'w') as outfile:
                json.dump(self.stations, outfile, indent=4, sort_keys=True)

    def populate_stations(self):
        # print self.interface
        stations_json = self.interface.get_all_current_stations()
        # print_json(stations_json)
        for station in stations_json:
            station_id = int(station["id"])
            if station_id not in self.stations:
                self.stations[station_id] = {"max_docks": station["empty_docks"] + station["bikes"], 
                    "times": {}}
                for i in range(0,24*60,5):
                    hours = int(math.floor(i / 60))
                    minutes = i - hours * 60

                    my_time = self.clean_time(hours,minutes)

                    # print my_time
                    # time.sleep(0.01)

                    self.stations[station_id]["times"][my_time] = [0] * (1 + self.stations[station_id]["max_docks"])
                # print_json(self.stations[station["id"]]["times"])

    def load_initial_statistics(self):
        for station in self.stations:
            # walk through all the stations and get their info
            print "finding info for station {}".format(station)
            # get data going back several months
            test_data = self.interface.get_current_station_data(station)
            # move through each of the data items which show time and dock/bike numbers 
            for item in test_data:
                # find formatted time as just XX:XX:XX
                my_time = re.split(" ", item["date_time"])
                for element in my_time:
                    if ":" in element:
                        my_time = element
                        break

                # get the proper timestamp for the list
                my_time = self.round_time(my_time)

                if my_time is not None:
                    test_station = self.stations[station]
                    
                    # try:
                    # make sure there are the proper number of docks at each time
                    # there seems to be a problem in the system whereby at some points
                    # there are different number of docks
                    num_options = len(test_station["times"][my_time])
                    if item["empty_docks"] + 1 > num_options:

                        print "adding {0} items to an array of size {1}".format(item["empty_docks"] + 1 - 
                            num_options, num_options)
                        for i in range(test_station["max_docks"], item["empty_docks"]):
                            for test_time in test_station["times"]:
                                test_station["times"][test_time].append(0)
                            print "added item, length = {}".format(len(test_station["times"][my_time]))

                        test_station["max_docks"] = item["empty_docks"]

                    test_station["times"][my_time][item["empty_docks"]] += 1
                    # except:
                    #     print "empty_docks: {0}, max_docks: {1}".format(item["empty_docks"], test_station["max_docks"])
                    #     time.sleep(3)

                    # except:
                    #     print "problem with time {}".format(my_time)
                    #     print "possible options were"
                    #     print sorted((self.stations[station]["times"]).keys())
                    #     time.sleep(1)
                            

            # time.sleep(10)

    def round_time(self,my_time):
        # print my_time
        hours, minutes, seconds = re.split(":",my_time)

        hours = int(hours)
        minutes = int(minutes)

        remainder = minutes % 5

        minutes = minutes - remainder

        
        # print my_time
        return self.clean_time(hours,minutes)

    def clean_time(self,hours,minutes):
        hours = int(hours)
        minutes = int(minutes)

        if hours < 10:
            hours = "0{}".format(hours)

        if minutes < 10:
            minutes = "0{}".format(minutes)

        return "{0}:{1}".format(hours,minutes)

    def sorted_times_in_seconds(self, times_list):
        times_to_return = []
        for time in times_list:
            hours,minutes = re.split(":",time)
            times_to_return.append(int(hours)*60+int(minutes))

        return sorted(times_to_return)

    def animate_pdf(self,station_id, pause_time, start_time=None,end_time=None): 

        if type(station_id) is int:
            station_id = str(station_id)
        #obtain station info
        this_station = self.stations[station_id] 
        # get the list of possible data retreival times
        times_list = this_station["times"]

        # cycling through the list in chronological order
        for test_time in self.sorted_times_in_seconds(times_list):
            time_string = self.hoursmins_to_colon(test_time)
            print "Empty docks PDF for station {0} at time {1}".format(station_id, time_string)
            #get the total number of additions to this list
            total = sum(times_list[time_string])

            #walk through the list of possible numbers of empty docks
            for i in range(0,len(times_list[time_string])):
                # find the number of spaces we will need to represent this value
                num_spaces = int(round((self.MAXSIZE-1)*times_list[time_string][i]/total))
                if num_spaces > 0: 
                    print "{0}:\t|{1}+".format(i,' '*(num_spaces-1))
                else:
                    print "{0}:\t+".format(i)      

            time.sleep(pause_time)  

    def hoursmins_to_colon(self,time):
        hours = int(math.floor(time /60))
        mins = time % 60

        if hours < 10:
            hours = "0{}".format(hours)

        if mins < 10:
            mins = "0{}".format(mins)

        return "{0}:{1}".format(hours,mins)

    def find_minimum(self):
        minimum_docks_likelihood = {"percentage": 0, "station": None, "time": None}

        for station_id in self.stations:
            station = self.stations[station_id]
            for test_time in station["times"]:
                value_list = station["times"][test_time]
                total = sum(value_list)
                if value_list[0] > minimum_docks_likelihood["percentage"]:
                    minimum_docks_likelihood["percentage"] = value_list[0]
                    minimum_docks_likelihood["station"] = station_id
                    minimum_docks_likelihood["time"] = test_time

        return minimum_docks_likelihood


def print_json(json_object):
    print json.dumps(json_object, indent=4, sort_keys=True)
    print "\n"

def save_json(json_object, filename):
    with open(filename, 'w') as outfile:
        json.dump(json_object, outfile, indent=4, sort_keys=True)

def find_closest_key(test_key, key_list):
    closest = None
    difference = 5
    test_time = 60*int(re.split(":",test_key)[0]) + int(re.split(":",test_key)[1])
    for key in key_list:
        key_time = 60*int(re.split(":",key)[0]) + int(re.split(":",key)[1])
        if abs(test_time-key_time) < difference:
            time = key
            difference = abs(test_time-key_time)



    
def main():
    calculator = ConfidenceCalculator()
    calculator.animate_pdf(sys.argv[1],0.1)

    # print_json(calculator.stations, "stations.json")

if __name__=="__main__":
    main()
