import pdb
import pandas as pd
from Modules.Annotations.ObjectLabeler import ObjectLabeler as OL

class ManualLabelFramesPreparer():
	# This class takes in directory information and a logfile containing depth information and performs the following:
	# 1. Identifies tray using manual input
	# 2. Interpolates and smooths depth data
	# 3. Automatically identifies bower location
	# 4. Analyze building, shape, and other pertinent info of the bower

	def __init__(self, fileManager, initials, number):

		self.__version__ = '1.0.0'

		self.fileManager = fileManager
		self.initials = initials
		self.number = number

	def validateInputData(self):
		fm_obj = FM(projectID = args.ProjectID)

		assert os.path.exists(self.fileManager.localAnalysisDir)
		assert os.path.exists(self.fileManager.localManualLabelFramesDir)
		assert os.path.exists(self.fileManager.localBoxedFishFile)
		"""self.uploads = [(self.fileManager.localTroubleshootingDir, self.fileManager.cloudTroubleshootingDir, '0'), 
						(self.fileManager.localAnalysisDir, self.fileManager.cloudAnalysisDir, '0'),
						(self.fileManager.localAllClipsDir, self.fileManager.cloudMasterDir, '1'),
						(self.fileManager.localManualLabelClipsDir, self.fileManager.cloudMasterDir, '1'),
						(self.fileManager.localManualLabelFramesDir, self.fileManager.cloudMasterDir, '1'),
						(self.fileManager.localManualLabelFramesDir[:-1] + '_pngs', self.fileManager.cloudMasterDir[:-1] + '_pngs', '1')
						]"""

	def labelFrames(self):

# Read in annotations and create csv file for all annotations with the same user and projectID
		previouslyLabeled_dt = pd.read_csv(self.fileManager.localBoxedFishFile)
		previouslyLabeled_dt = previouslyLabeled_dt[(previouslyLabeled.ProjectID == self.fileManager.projectID) & (self.previouslyLabeled_dt.User == self.initials)]
		previouslyLabeled_dt.to_csv(self.fileManager.localLabeledFramesFile, sep = ',', columns = ['ProjectID', 'Framefile', 'Nfish', 'Sex', 'Box', 'CorrectAnnotation', 'User', 'DateTime'])

		obj = OL(self.fileManager.localManualLabelFramesDir, self.fileManager.localLabeledFramesFile, self.number, self.projectID)


