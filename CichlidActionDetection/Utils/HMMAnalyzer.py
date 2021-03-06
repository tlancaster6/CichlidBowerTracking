import numpy as np
import matplotlib.pyplot as plt
import sys, pdb, datetime

class HMMAnalyzer:
	def __init__(self, filebase):

		# Data is (start_t, end_t, value, row, column)
		self.data = np.load(filebase + '.npy')

		with open(filebase + '.txt') as f:
			for line in f:
				if line.rstrip() != '':
					data, value = line.rstrip().split(': ')
					if data == 'Width':
						self.width = int(value)
					if data == 'Height':
						self.height = int(value)
					if data == 'Frames':
						self.frames = int(value)
					if data == 'FrameRate':
						self.resolution = float(value)
					if data == 'Video_start_time':
						self.videoStart = datetime.datetime.fromisoformat(value)
					if data == 'Filter_start_time':
						self.filterStartTime = datetime.datetime.fromisoformat(value)
					if data == 'Filter_end_time':
						self.filterStopTime = datetime.datetime.fromisoformat(value)
					if data == 'Filter_start_frame':
						self.filterStartFrame = int(value)
					if data == 'Filter_end_frame':
						self.filterStopFrame = int(value)

		self.t = None
		#self.l_diff = None
		#self.abs_stop = None
		#self.current_count = 0

	def retDBScanMatrix(self, densityFilter = 1):
		# This function creates a matrix that can be used by DBScan to cluster points
		#minMagnitude is the size of the color change for a pixel to need to have
		#densityFilter filters out time points that have to many changes occur across the frame (1 = 1% of all pixels)

		#print('DBScanMatrixCreation: ' + str(self.data.shape[0] - self.width*self.height) + ' raw transitions are found in the entire video', file = sys.stderr)
		
		#Threshold out timepoints that have too many changes
		time, counts = np.unique(self.data[:,0], return_counts = True)
		threshold = counts[0]*densityFilter/100 # This excludes frames where too many pixels are changing in a frame (i.e. lighting changes)
		badTimes = time[counts>threshold]

		allCoords = self.data[~np.isin(self.data[:,0], badTimes)][:,[0,3,4,5]].astype('uint64')
			
		#print('DBScanMatrixCreation: ' + str(allCoords.shape[0]) + ' HMM transitions passed magnitude and density filtering criteria', file = sys.stderr)
		return allCoords

	def retImage(self, t):
		t = int(t/self.resolution)
		if t > self.frames or t < 0:
			raise IndexError('Requested frame ' + str(t*self.resolution) + ' doesnt exist')
		if self.t == t:
			return self.cached_frame
		else:
			self.cached_frame = self.data[(self.data[:,0] <= t) & (self.data[:,1] >= t)][:,2].reshape((self.height, self.width)).astype('uint8')
			self.t = t
			return self.cached_frame
			
	def retDifference(self, start, stop, threshold = 0):
		start = int(start/self.resolution)
		stop = int(stop/self.resolution)
		#if (start,stop) == self.l_diff:
		#    return self.loc_changes
		indices = np.where((self.data[:,0] <= start) & (self.data[:,1] >= start))[0]
		start_data = self.data[indices]
		changes = np.zeros(shape = start_data.shape[0])
		count = 0
		while True:
			count += 1
			# Update indices for those that need it
			indices[start_data[:,1] < stop] += 1
			new_data = self.data[indices]
			diffs = np.abs(new_data[:,2] - start_data[:,2])
			if np.max(diffs) == 0:
				break
			changes[diffs > threshold] += 1
			start_data = new_data

		loc_changes = changes.reshape((self.height, self.width))
		l_diff = (start,stop)
		return loc_changes

	def absDifference(self, stop, threshold = 0):
		start = 0
		stop = int(stop/self.frameblock)
		#if stop == self.abs_stop:
		#    return self.abs_changes
		start_data = self.data[(self.data[:,0] <= start) & (self.data[:,1] >= start)]
		indices = np.where((self.data[:,0] <= start) & (self.data[:,1] >= start))[0]
		changes = np.zeros(shape = start_data.shape[0])
		count = 0
		while True:
			count += 1
			# Update indices for those that need it
			indices[start_data[:,1] < stop] += 1
			new_data = self.data[indices]
			diffs = np.abs(new_data[:,2] - start_data[:,2])
			if np.max(diffs) == 0:
				break
			changes[diffs > threshold] += 1
			start_data = new_data

		abs_changes = changes.reshape((self.height, self.width))
		abs_stop = stop
		return abs_changes

	def magDensity(self, frame, x0 = 20, t0 = 60):
		outdata = []
		
		diffs = abs(self.ret_image(frame).astype(int) - self.ret_image(max(frame - self.frameblock, 0)).astype(int))
		dens = self.ret_difference(max(frame - t0, 0), min(frame+t0,self.frames))
		xs, ys = np.where(diffs!=0)

		for x,y in zip(xs,ys):
			density = dens[max(0,x-x0): min(x+x0,self.width), max(0,y-x0): min(y+x0, self.height)].sum()
			outdata.append((diffs[x,y], density))

		return outdata
			
	
