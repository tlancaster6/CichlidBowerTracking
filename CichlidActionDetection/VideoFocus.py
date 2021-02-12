import argparse, subprocess, datetime, os, pdb, sys, shutil
from pathlib import Path

parser = argparse.ArgumentParser(description='This script identifies regions of a large video that contains sand manipulation events')
# Input data
parser.add_argument('--Movie_file', type = str, required = True, help = 'Name of movie file to analyze. Must be .mp4 video')
parser.add_argument('--Num_workers', type = int, default = 0, help = 'Number of threads to run')
parser.add_argument('--Log', type = str, required = True, help = 'Log file to keep track of versions + parameters used')

# Temp directories that wlil be deleted at the end of the analysis
parser.add_argument('--HMM_temp_directory', type = str, required = True, help = 'Location for temp files to be stored. Should not be in a location that is automatically synced (e.g. Dropbox folder)')

# Output data
parser.add_argument('--HMM_filename', type = str, required = True, help = 'Basename of output HMM files. ".txt" and ".npy" will be added to basename')
parser.add_argument('--HMM_transition_filename', type = str, required = True, help = 'Name of npy file containing all transitions with associated magnitude')
parser.add_argument('--Cl_labeled_transition_filename', type = str, required = True, help = 'Name of npy file containing all transitions assigned to clusters.')
parser.add_argument('--Cl_labeled_cluster_filename', type = str, required = True, help = 'Name of csv file containing summary information for all clusters')
parser.add_argument('--Cl_videos_directory', type = str, required = True, help = 'Name of directory to hold video clips for all clusters')
parser.add_argument('--ML_frames_directory', type = str, required = True, help = 'Name of directory to hold frames to annotate for machine learning purposes')
parser.add_argument('--ML_videos_directory', type = str, required = True, help = 'Name of directory to hold videos to annotate for machine learning purposes')

# Parameters to filter when HMM is run on
parser.add_argument('--VideoID', type=str, required = True, help = 'Required argument that gives a short ID for the video')
parser.add_argument('--Video_start_time', type=datetime.datetime.fromisoformat, required = True, help = 'Required argument that indicates the start time of the video')
parser.add_argument('--Filter_start_time', type=datetime.datetime.fromisoformat, help = 'Optional argument that indicates the start time when the Clusters should be run')
parser.add_argument('--Filter_end_time', type=datetime.datetime.fromisoformat, help = 'Optional argument that indicates the start time when the Clusters should be run')

# Parameters for calculating HMM 
parser.add_argument('--HMM_blocksize', type = int, default = 5, help = 'Blocksize (in minutes) to decompress video for hmm analysis')
parser.add_argument('--HMM_mean_window', type = int, default = 120, help = 'Number of seconds to calculate mean over for filtering out large pixel changes for hmm analysis')
parser.add_argument('--HMM_mean_filter', type = float, default = 7.5, help = 'Grayscale change in pixel value for filtering out large pixel changes for hmm analysis')
parser.add_argument('--HMM_window', type = int, default = 10, help = 'Used to reduce the number of states for hmm analysis')
parser.add_argument('--HMM_seconds_to_change', type = float, default =1800, help = 'Used to determine probablility of state transition in hmm analysis')
parser.add_argument('--HMM_non_transition_bins', type = float, default = 2, help = 'Used to prevent small state transitions in hmm analysis')
parser.add_argument('--HMM_std', type = float, default = 100, help = 'Standard deviation of pixel data in hmm analysis')

# Parameters for DBSCAN clustering
parser.add_argument('--Cl_min_magnitude', type = int, default = 0, help = 'Transition magnitude to be included in cluster analysis')
parser.add_argument('--Cl_tree_radius', type = int, default = 22, help = 'Tree radius for cluster analysis')
parser.add_argument('--Cl_leaf_num', type = int, default = 190, help = 'Leaf num for cluster analysis')
parser.add_argument('--Cl_timescale', type = int, default = 10, help = 'Tree radius for cluster analysis')

#parser.add_argument('--Cl_neighbor_radius', type = int, default = 22, help = 'Tree radius for cluster analysis')
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

# Validate data
def check_args(args):
	bad_data = False
	if '.mp4' not in args.Movie_file:
		print('Movie_file must be mp4 file')
		bad_data = True
	if '.npy' not in args.HMM_transition_filename:
		print('HMM_transition_filename must have npy extension')
		bad_data = True
	if '.npy' not in args.Cl_labeled_transition_filename:
		print('Cl_labeled_transition_filename must have npy extension')
		bad_data = True
	if '.csv' not in args.Cl_labeled_cluster_filename:
		print('Cl_labeled_cluster_filename must have csv extension')
		bad_data = True
	if bad_data:
		raise Exception('Error in argument input.')

	else:
		for key, value in vars(args).items():
			if 'directory' in key:
				path = Path(value)
				vars(args)[key] = path
				if path.exists():
					shutil.rmtree(path)
				os.makedirs(path)
			elif 'filename' in key or 'log' in key:
				path = Path(value)
				vars(args)[key] = path
				if not path.parent.exists():
					os.makedirs(path.parent)

		# if args.HMM_temp_directory[-1] != '/':
		# 	args.HMM_temp_directory += '/'
		# if os.path.exists(args.HMM_temp_directory):
		# 	subprocess.run(['rm','-rf', args.HMM_temp_directory])
		# os.makedirs(args.HMM_temp_directory)
		# if args.Cl_videos_directory[-1] != '/':
		# 	args.Cl_videos_directory += '/'
		# if not os.path.exists(args.Cl_videos_directory):
		# 	os.makedirs(args.Cl_videos_directory)
		# if args.ML_frames_directory[-1] != '/':
		# 	args.ML_frames_directory += '/'
		# if not os.path.exists(args.ML_frames_directory):
		# 	os.makedirs(args.ML_frames_directory)
		# if args.ML_videos_directory[-1] != '/':
		# 	args.ML_videos_directory += '/'
		# if not os.path.exists(args.ML_videos_directory):
		# 	os.makedirs(args.ML_videos_directory)

		# for ofile in [args.HMM_filename, args.HMM_transition_filename, args.Cl_labeled_transition_filename, args.Cl_labeled_cluster_filename, args.Log]:
		# 	odir = ofile.split(ofile.split('/')[-1])[0]
		# 	if not os.path.exists(odir) and odir != '':
		# 		os.makedirs(odir)

check_args(args)

with open(args.Log, 'w') as f:
	for key, value in vars(args).items():
		print(key + ': ' + str(value), file = f)
	print('PythonVersion: ' + sys.version.replace('\n', ' '), file = f)
	import pandas as pd
	print('PandasVersion: ' + pd.__version__, file = f)
	import numpy as np
	print('NumpyVersion: ' + np.__version__, file = f)
	import hmmlearn
	print('HMMLearnVersion: ' + hmmlearn.__version__, file = f)
	import scipy
	print('ScipyVersion: ' + scipy.__version__, file = f)
	import cv2
	print('OpenCVVersion: ' + cv2.__version__, file = f)
	import sklearn
	print('SkLearnVersion: ' + sklearn.__version__, file = f)


# Filter out HMM related arguments
HMM_args = {}
for key, value in vars(args).items():
	if 'HMM' in key or 'Video' in key or 'Movie' in key or 'Num' in key or 'Filter' in key: 
		if value is not None:
			HMM_args[key] = value

# subprocess.run('conda activate CichlidBowerTracking && python -V', shell=True)

HMM_command = ['exec', 'bash', '&&', 'conda', 'activate', 'CichlidBowerTracking', '&&', 'python', str(Path('Utils', 'calculateHMM.py'))]
for key, value in HMM_args.items():
	HMM_command.extend(['--' + key, '\"'+str(value)+'\"' if ' ' in str(value) else str(value)])
HMM_command = ' '.join(HMM_command)

print(HMM_command)
subprocess.run(HMM_command, shell=True)

cluster_args = {}
for key, value in vars(args).items():
	if 'HMM' not in key or 'filename' in key:
		if key != 'Log':
			if value is not None:
				cluster_args[key] = value


cluster_command = ['exec', 'bash', '&&', 'conda', 'activate', 'CichlidBowerTracking', '&&', 'python', str(Path('Utils', 'calculateClusters.py'))]
for key, value in cluster_args.items():
	cluster_command.extend(['--' + key, '\"'+str(value)+'\"' if ' ' in str(value) else str(value)])
cluster_command = ' '.join(cluster_command)
subprocess.run(cluster_command, shell=True)
