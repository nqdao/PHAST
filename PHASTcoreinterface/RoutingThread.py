import threading
import time
import Routing
import json

exitFlag = 0

class RoutingThread (threading.Thread):
    def __init__(self, threadID, locations):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.origin = locations["origin"]
        self.destination = locations["destination"]
        self.processor = Routing.Routing()

    def run(self):
        print "UUID {}".format(self.threadID)
        start = self.processor.viable_locations(self.origin,1)
        print start
        end = self.processor.viable_locations(self.destination,1)
        print end
        print "Exiting {}".format(self.threadID)

# # Create new threads
# thread1 = myThread(1, "Thread-1", 1)
# thread2 = myThread(2, "Thread-2", 2)

# Start new Threads
# thread1.start()
# thread2.start()

# print "Exiting Main Thread"