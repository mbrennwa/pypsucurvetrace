import matplotlib.pyplot as plt
# import numpy as np
from numpy import random
import time
import multiprocessing

# set up plotting environment
plt.ion()
plt.show()


# plotting routine (will run in a separate process):
def plotter(q):
	while True:
		
		# get new data from the queue:
		print('Plotter: Waiting for new plotting data...')
		y = q.get()
		
		# plot new data (or terminate process):
		if y is None:
			print('Plotter: Terminating the plotter...')
			break
		if len(y) > 0:
			print('Plotter: Plotting new data...')
			plt.plot(y)
		
		# wait a bit before the next update
		plt.pause(0.1)


# main program

# set up separate process for data plotting:
queue = multiprocessing.Queue() # queue for data exchange with the plotting process
plt_proc = multiprocessing.Process(target=plotter, args=(queue,)) # plotting process
plt_proc.start() # start the plotting process

N = 10
for i in range(N):

	# collect data:
	print('\nMain: Acquiring new data (' + str(i+1) + '/' + str(N) + ')...')
	time.sleep(1) # 'fake' delay for 'fake' data acquisition
	y = random.random(10)
	# print(y)
	
	# send data over to the plotter process:
	queue.put(y)

# Let the plotter know that we're done:
queue.put(None)

# Wait for the plotter to finish:
queue.close()
queue.join_thread()
plt_proc.join()
