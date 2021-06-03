import pdb, os
from cichlid_bower_tracking.helper_modules.object_labeler import ObjectLabeler as OL


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

		assert os.path.exists(self.fileManager.localManualLabelFramesDir)
		assert os.path.exists(self.fileManager.localNewLabeledFramesDir)
		assert os.path.exists(self.fileManager.localBoxedFishFile)
		assert os.path.exists(self.fileManager.localLabeledFramesProjectDir)

	def labelFrames(self):
		
		obj = OL(self.fileManager.localManualLabelFramesDir, self.fileManager.localNewLabeledFramesFile, self.number, self.fileManager.projectID, self.initials)

	def correctAnnotations(self, user1, user2):

		obj = AD(self.fileManager.localLabeledFramesProjectDir, self.fileManager.localBoxedFishFile, self.fileManager.projectID, user1, user2)

