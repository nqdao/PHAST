__author__ = 'Daniel'

class User:	
	def __init__(self,routes):
		self.routes = routes
		self.location = ''
		self.dest_bixi = ''
		self.new_route = ''
		self.send_new_route = False
