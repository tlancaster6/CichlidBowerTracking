import argparse, cv2, random, pdb, datetime, subprocess, os, sys
import numpy as np
import pandas as pd
from multiprocessing.dummy import Pool as ThreadPool
from sklearn.cluster import DBSCAN
from sklearn.neighbors import radius_neighbors_graph
from sklearn.neighbors import NearestNeighbors
from HMMAnalyzer import HMMAnalyzer as HA


class Cluster_calculator:
	def __init__(self, args):
		self.args = args
		self.workers = args.Num_workers # Rename to make more readable

	def calculateClusters(self):
		self._validateVideo()
		self._createClusters()
		self._createAnnotationVideos()
		self._createAnnotationFrames()


	def _validateVideo(self):
		cap = cv2.VideoCapture(self.args.Movie_file)
		self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
		self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
		self.framerate = int(cap.get(cv2.CAP_PROP_FPS))
		self.frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
		cap.release()


	def _createClusters(self):
		print('  Creating clusters from HMM transitions,,Time: ' + str(datetime.datetime.now())) 
		# Convert into coords object and save it
		coords = np.load(self.args.HMM_transition_filename)

		# Remove coords with transitions that are too small
		coords = coords[coords[:,3] > self.args.Cl_min_magnitude]
		
		# Run data in batches to avoid RAM override
		sortData = coords[coords[:,0].argsort()][:,0:3] #sort data by time for batch processing, throwing out 4th column (magnitude)
		numBatches = int((sortData[-1,0] - sortData[0,0])/self.args.Cl_hours_in_batch/3600) + 1 #delta is number of hours to batch together. Can be fraction.
		sortData[:,0] = sortData[:,0]*self.args.Cl_timescale #scale time so that time distances between transitions are comparable to spatial differences
		labels = np.zeros(shape = (sortData.shape[0],1), dtype = sortData.dtype) # Initialize labels

		#Calculate clusters in batches to avoid RAM overuse
		curr_label = 0 #Labels for each batch start from zero - need to offset these 
		print('   ' + str(numBatches) + ' total batches. On batch: ', end = '', flush = True)
		for i in range(numBatches):
			print(str(i) + ',', end = '', flush = True)

			min_time, max_time = sortData[0,0] + i*self.args.Cl_hours_in_batch*self.args.Cl_timescale*3600, sortData[0,0] + (i+1)*self.args.Cl_hours_in_batch*self.args.Cl_timescale*3600 # Have to deal with rescaling of time. 3600 = # seconds in an hour
			hour_range = np.where((sortData[:,0] > min_time) & (sortData[:,0] <= max_time))
			min_index, max_index = hour_range[0][0], hour_range[0][-1] + 1
			X = NearestNeighbors(radius=self.args.Cl_tree_radius, metric='minkowski', p=2, algorithm='kd_tree',leaf_size=self.args.Cl_leaf_num,n_jobs=int(self.workers/2)).fit(sortData[min_index:max_index])
			dist = X.radius_neighbors_graph(sortData[min_index:max_index], self.args.Cl_tree_radius, 'distance')
			sub_label = DBSCAN(eps=self.args.Cl_eps, min_samples=self.args.Cl_min_points, metric='precomputed', n_jobs=int(self.workers/2)).fit_predict(dist)
			new_labels = int(sub_label.max()) + 1
			sub_label[sub_label != -1] += curr_label
			labels[min_index:max_index,0] = sub_label
			curr_label += new_labels

		print()
		# Concatenate and save information
		sortData[:,0] = sortData[:,0]/self.args.Cl_timescale
		labeledCoords = np.concatenate((sortData, labels), axis = 1).astype('int64')
		np.save(self.args.Cl_labeled_transition_filename, labeledCoords)
		print('  Concatenating and summarizing clusters,,Time: ' + str(datetime.datetime.now())) 

		df = pd.DataFrame(labeledCoords, columns=['T','X','Y','LID'])
		clusterData = df.groupby('LID').apply(lambda x: pd.Series({
			'VideoID': self.args.VideoID,
			'N': x['T'].count(),
			't': int(x['T'].mean()),
			'X': int(x['X'].mean()),
			'Y': int(x['Y'].mean()),
			't_span': int(x['T'].max() - x['T'].min()),
			'X_span': int(x['X'].max() - x['X'].min()),
			'Y_span': int(x['Y'].max() - x['Y'].min()),
			'MLClipCreated': 'No',
			'ClipCreated': 'No',
		})
		)

		clusterData['TimeStamp'] = clusterData.apply(lambda row: (self.args.Video_start_time + datetime.timedelta(seconds = int(row.t))), axis=1)
		clusterData['ClipName'] = clusterData.apply(lambda row: '__'.join([str(x) for x in [row.VideoID,row.name,row.N,row.t,row.X,row.Y]]), axis = 1)
		# Identify clusters to make clips for
		#self._print('Identifying clusters to make clips for', log = False)
		delta_xy = self.args.ML_videos_delta_xy
		delta_t = int(self.args.ML_videos_delta_t*self.framerate)
		smallClips, clipsCreated = 0,0 # keep track of clips with small number of pixel changes
		for row in clusterData.sample(n = clusterData.shape[0]).itertuples(): # Randomly go through the dataframe
			LID, N, t, x, y, time = row.Index, row.N, row.t, row.X, row.Y, row.TimeStamp
			if x - delta_xy < 0 or x + delta_xy >= self.height or y - delta_xy < 0 or y + delta_xy >= self.width:
				continue
			# Check temporal compatability (part a):
			elif self.framerate*t - delta_t < 0 or LID == -1:
				continue
			# Check temporal compatability (part b):
			else:
				clusterData.loc[clusterData.index == LID,'ClipCreated'] = 'Yes'
				if N < self.args.ML_videos_small_limit:
					if smallClips > self.args.ML_videos_number/20:
						continue
					smallClips += 1
				if clipsCreated < self.args.ML_videos_number:
					clusterData.loc[clusterData.index == LID,'ManualAnnotation'] = 'Yes'
					clipsCreated += 1

		clusterData.to_csv(self.args.Cl_labeled_cluster_filename, sep = ',')
		self.clusterData = clusterData
	def _createAnnotationVideos(self):
		hmmObj = HA(self.args.HMM_filename)
		delta_xy = self.args.ML_videos_delta_xy
		delta_t = int(self.args.ML_videos_delta_t*self.framerate)

		print('  Creating small video clips for classification,,Time: ' + str(datetime.datetime.now())) 

		# Clip creation is super slow so we do it in parallel
		self.clusterData = pd.read_csv(self.args.Cl_labeled_cluster_filename, sep = ',', index_col = 'LID')

		# Create clips for each cluster
		processes = []
		for row in self.clusterData[self.clusterData.ClipCreated == 'Yes'].itertuples():
			LID, N, t, x, y = [str(x) for x in [row.Index, row.N, row.t, row.X, row.Y]]
			outName = self.args.Cl_videos_directory + row.ClipName + '.mp4'
			command_stub = ['bash -c \"source activate CichlidBowerTracking; python']
			command = command_stub + ['Utils/createClip.py', self.args.Movie_file, outName, str(delta_xy), str(delta_t),
									  str(self.framerate)]
			command = ' '.join(command) + '\"'
			processes.append(subprocess.Popen(command, shell=True))
			if len(processes) == self.workers:
				for p in processes:
					p.communicate()
				processes = []
		
		print('  Creating small video clips for manual labeling,,Time: ' + str(datetime.datetime.now())) 

		# Create video clips for manual labeling - this includes HMM data
		cap = cv2.VideoCapture(self.args.Movie_file)
		labeledCoords = np.load(self.args.Cl_labeled_transition_filename)
		for row in self.clusterData[self.clusterData.ManualAnnotation == 'Yes'].itertuples():
			LID, N, t, x, y, clipname = row.Index, row.N, row.t, row.X, row.Y, row.ClipName
			
			outName_ml = self.args.ML_videos_directory + clipname + '_ManualLabel.mp4'
			outName_in = self.args.Cl_videos_directory + clipname + '.mp4'
			outName_out = self.args.ML_videos_directory + clipname + '.mp4'

			outAllHMM = cv2.VideoWriter(outName_ml, cv2.VideoWriter_fourcc(*"mp4v"), self.framerate, (4*delta_xy, 2*delta_xy))
			cap.set(cv2.CAP_PROP_POS_FRAMES, int(self.framerate*(t) - delta_t))
			HMMChanges = hmmObj.retDifference(self.framerate*(t) - delta_t, self.framerate*(t) + delta_t)
			clusteredPoints = labeledCoords[labeledCoords[:,3] == LID][:,1:3]

			for i in range(delta_t*2):
				ret, frame = cap.read()
				frame2 = frame.copy()
				frame[HMMChanges != 0] = [300,125,125]
				for coord in clusteredPoints: # This can probably be improved to speed up clip generation (get rid of the python loop)
					frame[coord[0], coord[1]] = [125,125,300]
				outAllHMM.write(np.concatenate((frame2[x-delta_xy:x+delta_xy, y-delta_xy:y+delta_xy], frame[x-delta_xy:x+delta_xy, y-delta_xy:y+delta_xy]), axis = 1))

			
			outAllHMM.release()

			subprocess.call(['cp', outName_in, outName_out])
			assert(os.path.exists(outName_out))
		cap.release()

	def _createAnnotationFrames(self):
		print('  Creating frames for manual labeling,,Time: ' + str(datetime.datetime.now())) 

		# Create frames for manual labeling
		cap = cv2.VideoCapture(self.args.Movie_file)

		first_frame = 0
		if self.args.Filter_start_time is not None:
			if self.args.Video_start_time < self.args.Filter_start_time:
				first_frame = int((self.args.Filter_start_time - self.args.Video_start_time).total_seconds()*self.framerate)
				last_frame = first_frame + int((self.args.Filter_end_time - self.args.Filter_start_time).total_seconds()*self.framerate)
			else:
				first_frame = 0
				last_frame = int((self.args.Filter_end_time - self.args.Video_start_time).total_seconds()*self.framerate)
		else:
			first_frame =0
			last_frame = self.frames
		last_frame = min(self.frames, last_frame)
		created_frames = set()
		for i in range(int(self.args.ML_frames_number)):
			try:
				frameIndex = random.randint(first_frame, last_frame)
				while frameIndex in created_frames:
					frameIndex = random.randint(first_frame, last_frame)
			except ValueError:
				print('Error with frameIndex: ', file = sys.stderr)
				break
			cap.set(cv2.CAP_PROP_POS_FRAMES, frameIndex)
			ret, frame = cap.read()
			a = cv2.imwrite(self.args.ML_frames_directory + self.args.VideoID + '_' + str(frameIndex) + '.jpg', frame)     # save frame as JPEG file
			created_frames.add(frameIndex)
			#cv2.imwrite(self.projFileManager.localManualLabelFramesDir[:-1] + '_pngs/' + self.lp.projectID + '_' + self.videoObj.baseName + '_' + str(frameIndex) + '.png', frame)     # save frame as PNG file      

 


parser = argparse.ArgumentParser(description='This script calculates an HMM for a single video')
parser.add_argument('--Movie_file', type = str, required = True, help = 'Name of movie file to analyze. Must be .mp4 video')
parser.add_argument('--Num_workers', type = int, default = 1, help = 'Transition magnitude to be included in cluster analysis')
parser.add_argument('--HMM_filename', type = str, required = True, help = 'Basename of output HMM files. ".txt" and ".npy" will be added to basename')
parser.add_argument('--HMM_transition_filename', type = str, required = True, help = 'Name of npy file containing all transitions with associated magnitude')
parser.add_argument('--Cl_labeled_transition_filename', type = str, required = True, help = 'Name of npy file containing all transitions assigned to clusters.')
parser.add_argument('--Cl_labeled_cluster_filename', type = str, required = True, help = 'Name of csv file containing summary information for all clusters')
parser.add_argument('--Cl_videos_directory', type = str, required = True, help = 'Name of directory to hold video clips for all clusters')
parser.add_argument('--ML_frames_directory', type = str, required = True, help = 'Name of directory to hold frames to annotate for machine learning purposes')
parser.add_argument('--ML_videos_directory', type = str, required = True, help = 'Name of directory to hold videos to annotate for machine learning purposes')
parser.add_argument('--Video_start_time', type=datetime.datetime.fromisoformat, required = True, help = 'Optional argument that indicates the start time of the video')
parser.add_argument('--Filter_start_time', type=datetime.datetime.fromisoformat, help = 'Optional argument that indicates the start time when the HMM should be run')
parser.add_argument('--Filter_end_time', type=datetime.datetime.fromisoformat, help = 'Optional argument that indicates the start time when the HMM should be run')

parser.add_argument('--VideoID', type=str, required = True, help = 'Alternative ID for video that was analyzed')

# Parameters for DBSCAN clustering
parser.add_argument('--Cl_min_magnitude', type = int, default = 0, help = 'Transition magnitude to be included in cluster analysis')
parser.add_argument('--Cl_tree_radius', type = int, default = 22, help = 'Tree radius for cluster analysis')
parser.add_argument('--Cl_leaf_num', type = int, default = 190, help = 'Leaf num for cluster analysis')
parser.add_argument('--Cl_timescale', type = int, default = 10, help = 'Tree radius for cluster analysis')
parser.add_argument('--Cl_eps', type = int, default = 18, help = 'Eps for cluster analysis')
parser.add_argument('--Cl_min_points', type = int, default = 90, help = 'Minimum number of points to create cluster')
parser.add_argument('--Cl_hours_in_batch', type = float, default = 1.0, help = 'Number of hours to calculate cluster per batch')

# Parameters for outputing video clips and frames for manual analysis and machine learning
parser.add_argument('--ML_frames_number', type = int, default = 500, help = 'Number of frames to create to annotate for machine learning purposes')
parser.add_argument('--ML_videos_number', type = int, default = 1200, help = 'Number of videos to create annotate for machine learning purposes')
parser.add_argument('--ML_videos_delta_xy', type = int, default = 100, help = '1/2 x and y size of each ml video created (in pixels)')
parser.add_argument('--ML_videos_delta_t', type = float, default = 2, help = '1/2 of t size of each ml video created (in seconds)')
parser.add_argument('--ML_videos_small_limit', type = int, default = 500, help = 'To prevent too many small videos to be used for manual labeling')


args = parser.parse_args()

cluster_obj = Cluster_calculator(args)
cluster_obj.calculateClusters()

