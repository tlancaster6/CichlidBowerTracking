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
					

	def predictLabels(self):

		# Create mapping from videos to projectID

		with open(self.fileManager.localVideoProjectDictionary, 'w') as f:
			print('Location,MeanID', file = f)

			for videofile in [x.replace('.mp4','') for x in os.listdir(self.fileManager.localAllClipsDir) if '.mp4' in x]:
				print(videofile + ',' + self.fileManager.projectID, file = f)

		# Run command
		command = ['python3', 'ClassifyVideos.py']
		command.extend(['--Input_videos_directory', self.fileManager.localAllClipsDir])
		command.extend(['--Videos_to_project_file', self.fileManager.localVideoProjectDictionary])
		command.extend(['--Trained_model', self.fileManager.localVideoModelFile])
		command.extend(['--Trained_categories', self.fileManager.localVideoClassesFile])
		command.extend(['--Training_options', self.fileManager.localVideoCommandsFile])
		command.extend(['--Output_file', self.fileManager.localVideoLabels])
		command.extend(['--Temporary_clips_directory', self.fileManager.localConvertedClipsDir])
		command.extend(['--Temporary_output_directory', self.fileManager.localVideoLabelsDir])

		print(' '.join(command))

		#os.chdir('CichlidActionClassification')
		#subprocess.run(command)
		#os.chdir('..')




