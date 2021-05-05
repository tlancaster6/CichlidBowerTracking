import subprocess, pickle, os, shutil, pdb, scipy, datetime
from skimage import io
import pandas as pd


class MLClusterPreparer:
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
		
		self.uploads = [(self.projFileManager.localAnalysisDir, self.projFileManager.cloudAnalysisDir, 0)]
			

	def predictVideoLabels(self):
		self._identifyVideoClasses()
		self._prepareClips()
		self._predictLabels()
		# Add code to run other repository

