import subprocess, pickle, os, shutil, pdb, scipy, datetime
from skimage import io
import pandas as pd


class ThreeDClassifierPreparer:
	# This class takes in directory information and a logfile containing depth information and performs the following:
	# 1. Identifies tray using manual input
	# 2. Interpolates and smooths depth data
	# 3. Automatically identifies bower location
	# 4. Analyze building, shape, and other pertinent info of the bower

	def __init__(self, fileManager):
		self.__version__ = '1.0.0'

		self.fileManager = fileManager

	def validateInputData(self):
		assert os.path.exists(self.fileManager.localAllClipsDir)

		assert os.path.exists(self.fileManager.localVideoModelFile)
		assert os.path.exists(self.fileManager.localVideoClassesFile)
		assert os.path.exists(self.fileManager.localVideoCommandsFile)
		
		self.localVideoProjectDictionary = self.local3DModelDir + 'videoToProject.csv'

			

	def predictLabels(self):

		# Create mapping from videos to projectID

		with open(self.localVideoProjectDictionary, 'w') as f:
			print('Location,MeanID', file = f)

			for videofile in [x.replace('.mp4','') for x in os.listdir(self.localAllClipsDir) if '.mp4' in x]:
				print(videofile, self.fileManager.projectID, file = f)

		# Run command
		command = ['python3', 'ClassifyVideos.py']
		command.extend(['--Input_videos_directory', self.fileManager.localAllClipsDir])
		command.extend(['--Videos_to_project_file', self.localVideoProjectDictionary])
		command.extend(['--Trained_model', self.fileManager.localVideoModelFile])
		command.extend(['--Trained_categories', self.fileManager.localVideoClassesFile])
		command.extend(['--Training_options', self.fileManager.localVideoCommandsFile])
		command.extend(['--Output_file', self.localVideoLabels])
		command.extend(['--Temporary_clips_directory', self.localConvertedClipsDir])
		command.extend(['--Temporary_output_directory', self.localVideoLabelsDir])


parser.add_argument('--Clips_temp_directory',
                    default=os.path.join(os.getenv("HOME"),'clips_temp'),
                    type = str, 
                    required = False, 
                    help = 'Location for temp clips to be stored')

parser.add_argument('--intermediate_temp_directory',
                    default=os.path.join(os.getenv("HOME"),'intermediate_temp'),
                    type = str, 
                    required = False, 
                    help = 'Location for temp files to be stored')

self.localVideoLabels

		command.extend(['--Num_workers', str(self.workers)])
		command.extend(['--Log', self.videoObj.localHMMFile + '.log'])
		command.extend(['--HMM_temp_directory', self.videoObj.localTempDir])
		command.extend(['--HMM_filename', self.videoObj.localHMMFile])
		command.extend(['--HMM_transition_filename', self.videoObj.localRawCoordsFile])
		command.extend(['--Cl_labeled_transition_filename', self.videoObj.localLabeledCoordsFile])
		command.extend(['--Cl_labeled_cluster_filename', self.videoObj.localLabeledClustersFile])
		command.extend(['--Cl_videos_directory', self.videoObj.localAllClipsDir])
		command.extend(['--ML_frames_directory', self.videoObj.localManualLabelFramesDir])
		command.extend(['--ML_videos_directory', self.videoObj.localManualLabelClipsDir])
		command.extend(['--Video_start_time', str(self.videoObj.startTime)])
		command.extend(['--VideoID', self.fileManager.lp.movies[0].baseName])
		
		os.chdir('CichlidActionDetection')
		subprocess.run(command)
		os.chdir('..')




