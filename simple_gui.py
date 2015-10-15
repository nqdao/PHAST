from Tkinter import *
import ImageTk
from math import *


class App:

    def __init__(self, master):

        frame = Frame(master)
        # frame.pack_propagate(0)
        frame.pack()

        self.photo = ImageTk.PhotoImage(file="puppy.jpg")

        self.input = Entry(frame, width=15)
        self.input.pack(side=RIGHT)

        self.button = Button(frame, text="QUIT", fg="red", command=frame.quit)
        self.button.pack(side=LEFT)

        self.output = Label(frame,width=12)
        self.output.pack(side=BOTTOM)

        # self.hi_there = Button(frame, text="Hello", command=self.say_hi)
        # self.hi_there.pack(side=LEFT)

        self.useless = Button(frame, anchor=NW,image=self.photo,compound=LEFT,text="Get Prime", command=self.compute_prime)
        self.useless.pack(side=LEFT)

    def say_hi(self):
        print "hi there, everyone!"

    def compute_prime(self):
    	try:
    		n = int(self.input.get())

	    	array = [2]
	    	test = 3
	    	while len(array) < n:
	    		prime = True
	    		for num in array:
	    			if test % num == 0:
	    				prime = False
	    				break
	    			if num > sqrt(test):
	    				break
	    		if prime:
	    			if len(array) + 1 == n:
	    				break
	    			else:
	    				array.append(test)

	    		test = test + 2

	    	self.output.config(text = str(test))

    	except:
    		print "Error, no number entered"


root = Tk()

app = App(root)

root.mainloop()
root.destroy() # optional; see description below