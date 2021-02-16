import subprocess, os, pdb
import pandas as pd

class ThreeDModelPreparer():
	# This class takes in directory information and a logfile containing depth information and performs the following:
	# 1. Identifies tray using manual input
	# 2. Interpolates and smooths depth data
	# 3. Automatically identifies bower location
	# 4. Analyze building, shape, and other pertinent info of the bower

	def __init__(self, fileManager, purpose, projects, modelID, oldModelID):

		self.__version__ = '1.0.0'

		self.fileManager = fileManager
		self.projects = projects


	def validateInputData(self):
		
		assert os.path.exists(self.fileManager.localLabeledClipsDir)
		assert os.path.exists(self.fileManager.localLabeledClipsFile)
		assert os.path.exists(self.fileManager.local3DModelDir)
		assert os.path.exists(self.fileManager.local3DModelTempDir)

	def create3DModel(self):
		# Filter out annotated videos so they only include projects requested
		dt = pd.read_csv(self.fileManager.localLabeledClipsFile)
		dt['ProjectID'] = dt.ClipName.str.split('__').str[0]
		dt = dt[dt.ProjectID.isin(self.projects)]
		dt = dt.rename(columns = {'ClipName':'VideoFile', 'ManualLabel':'Label'})
		dt.to_csv(self.fileManager.localVideosProjectsFile)

		command = ['python3', 'TrainModel.py']
		command.extend(['--Videos_directory', self.fileManager.localLabeledClipsDir])
		command.extend(['--Videos_file', self.fileManager.localVideoProjectsFile])
		command.extend(['--Results_directory', self.fileManager.local3DModelTempDir])
		command.extend(['--Purpose', 'denovo'])
		command.extend(['--gpu', '2'])
		command.extend(['--projectMeans'])
		
		os.chdir('VideoClassifier')
		command = "source activate CichlidActionClassification; " + ' ' .join(command)
		subprocess.run('bash -c \"' + command + '\"', shell = True)
		os.chdir('..')



		"""self.local3DModelDir = self.localMLDir + 'VideoModels/' + self.vModelID + '/'

		self.localVideoModelFile = self.local3DModelDir + 'model.pth'
		self.localVideoClassesFile = self.local3DModelDir + 'classInd.txt'
		self.localModelCommandsFile = self.local3DModelDir + 'commands.log'
		self.localVideoProjectsFile = self.local3DModelDir + 'videoToProject.csv'
		self.localVideoLabels = self.local3DModelDir + 'confusionMatrix.csv'"""