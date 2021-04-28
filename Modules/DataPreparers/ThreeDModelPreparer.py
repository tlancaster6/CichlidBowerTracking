import subprocess, os, pdb, shutil
import pandas as pd

class ThreeDModelPreparer():
	# This class takes in directory information and a logfile containing depth information and performs the following:
	# 1. Identifies tray using manual input
	# 2. Interpolates and smooths depth data
	# 3. Automatically identifies bower location
	# 4. Analyze building, shape, and other pertinent info of the bower

	def __init__(self, fileManager, purpose, projects, modelID, gpu, projectMeans):

		self.__version__ = '1.0.0'

		self.fileManager = fileManager
		self.fileManager.createDirectory(self.fileManager.local3DModelDir)
		self.fileManager.createDirectory(self.fileManager.local3DModelTempDir)
		
		self.projects = projects
		self.gpu = gpu
		self.projectMeans = projectMeans

	def validateInputData(self):
		
		assert os.path.exists(self.fileManager.localLabeledClipsDir)
		assert os.path.exists(self.fileManager.localLabeledClipsFile)
		assert os.path.exists(self.fileManager.local3DModelDir)
		assert os.path.exists(self.fileManager.local3DModelTempDir)

	def create3DModel(self):
		# Filter out annotated videos so they only include projects requested
		dt = pd.read_csv(self.fileManager.localLabeledClipsFile, index_col = 0)
		dt['ProjectID'] = dt.ClipName.str.split('__').str[0]
		dt['Dataset'] = ''
		if self.projects[0].lower() != 'all':
			dt.loc[~dt.ProjectID.isin(self.projects),'Dataset'] = 'Validate'
		dt['ClipName'] = dt.ClipName + '.mp4'
		dt = dt.rename(columns = {'ClipName':'VideoFile', 'ManualLabel':'Label'})
		dt.to_csv(self.fileManager.localVideoProjectsFile)

		command = ['python3', 'TrainModel.py']
		command.extend(['--Videos_directory', self.fileManager.localLabeledClipsDir])
		command.extend(['--Videos_file', self.fileManager.localVideoProjectsFile])
		command.extend(['--Results_directory', self.fileManager.local3DModelTempDir])
		command.extend(['--Purpose', 'denovo'])
		command.extend(['--gpu', str(self.gpu)])
		if self.projectMeans:
			command.extend(['--projectMeans'])

		
		#command = "source activate CichlidActionClassification; " + ' ' .join(command)
		command = "source " + os.getenv('HOME') + "/anaconda3/etc/profile.d/conda.sh; conda activate CichlidActionClassification; " + ' '.join(command)
		os.chdir('VideoClassifier')
		subprocess.run('bash -c \"' + command + '\"', shell = True)
		os.chdir('..')

		with open(os.path.join(self.fileManager.local3DModelTempDir,'val.log')) as f:
			print('Epoch\tAccuracy')
			for line in f:
				try:
					if int(line.split()[0]) % 5 == 0:
						print(line.split()[0] + '\t' + line.rstrip().split()[-1])
				except ValueError:
					continue
			epoch = 1
			while epoch % 5 != 0:
				epoch = int(input('Choose epoch to use'))
			# Move files
			shutil.copy(os.path.join(self.fileManager.local3DModelTempDir,'val.log'), self.local3DModelTempDir)
			shutil.copy(os.path.join(self.fileManager.local3DModelTempDir,'epoch_' + str(epoch) + '.pth'), self.localVideoModelFile)
			shutil.copy(os.path.join(self.fileManager.local3DModelTempDir,'epoch_' + str(epoch) + 'confusion_matrix.csv'), self.localVideoLabels)
			shutil.copy(os.path.join(self.fileManager.local3DModelTempDir,'TrainingLog.txt'), self.localModelCommandsFile)
			shutil.copy(os.path.join(self.fileManager.local3DModelTempDir,'VideoSplit.csv'), self.localVideoProjectsFile)
			shutil.copy(os.path.join(self.fileManager.local3DModelTempDir,'MissingVideos.csv'), self.local3DModelTempDir)
	
