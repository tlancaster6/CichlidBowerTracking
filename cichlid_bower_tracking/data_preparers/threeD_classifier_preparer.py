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
		assert os.path.exists(self.fileManager.localModelCommandsFile )

	def predictLabels(self):


		# Create mapping from videos to projectID

		with open(self.fileManager.localVideoProjectDictionary, 'w') as f:
			print('VideoFile,Label,ProjectID', file = f)

			for videofile in [x.replace('.mp4','') for x in os.listdir(self.fileManager.localAllClipsDir) if '.mp4' in x]:
				print(videofile + ',,' + self.fileManager.projectID, file = f)

		# Run command
		command = ['python3', 'ClassifyVideos.py']
		command.extend(['--Input_videos_directory', self.fileManager.localAllClipsDir])
		command.extend(['--Videos_to_project_file', self.fileManager.localVideoProjectDictionary])
		command.extend(['--Trained_model', self.fileManager.localVideoModelFile])
		command.extend(['--Training_log', self.fileManager.localModelCommandsFile])
		command.extend(['--Output_file', self.fileManager.localVideoLabels])
		command.extend(['--Results_directory', self.fileManager.localConvertedClipsDir])
		command.extend(['--Temporary_output_directory', self.fileManager.localVideoLabelsDir])

		print(' '.join(command))


		if not os.path.isdir('VideoClassifier'):
			subprocess.run(['git', 'clone', 'https://www.github.com/ptmcgrat/VideoClassifier'])

		#command = "source activate CichlidActionClassification; " + ' ' .join(command)
		command = "source " + os.getenv('HOME') + "/anaconda3/etc/profile.d/conda.sh; conda activate CichlidActionClassification; " + ' '.join(command)
		os.chdir('VideoClassifier')
		subprocess.run(['git', 'pull'])
		subprocess.run('bash -c \"' + command + '\"', shell = True)
		os.chdir('..')

		#os.chdir('CichlidActionClassification')
		#subprocess.run(command)
		#os.chdir('..')




