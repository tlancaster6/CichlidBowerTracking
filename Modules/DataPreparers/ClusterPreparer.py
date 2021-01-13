import subprocess, os, pdb


class ClusterPreparer():
	# This class takes in directory information and a logfile containing depth information and performs the following:
	# 1. Identifies tray using manual input
	# 2. Interpolates and smooths depth data
	# 3. Automatically identifies bower location
	# 4. Analyze building, shape, and other pertinent info of the bower

	def __init__(self, fileManager, videoIndex, workers):

		self.__version__ = '1.0.0'

		self.fileManager = fileManager
		self.videoObj = self.fileManager.returnVideoObject(videoIndex)
		self.workers = workers
		self.videoIndex = videoIndex


	def validateInputData(self):
		
		assert os.path.exists(self.videoObj.localVideoFile)
		assert os.path.exists(self.fileManager.localTroubleshootingDir)
		assert os.path.exists(self.fileManager.localAnalysisDir)
		assert os.path.exists(self.fileManager.localTempDir)
		assert os.path.exists(self.fileManager.localAllClipsDir)
		assert os.path.exists(self.fileManager.localManualLabelClipsDir)
		assert os.path.exists(self.fileManager.localManualLabelFramesDir)


		"""self.uploads = [(self.fileManager.localTroubleshootingDir, self.fileManager.cloudTroubleshootingDir, '0'), 
						(self.fileManager.localAnalysisDir, self.fileManager.cloudAnalysisDir, '0'),
						(self.fileManager.localAllClipsDir, self.fileManager.cloudMasterDir, '1'),
						(self.fileManager.localManualLabelClipsDir, self.fileManager.cloudMasterDir, '1'),
						(self.fileManager.localManualLabelFramesDir, self.fileManager.cloudMasterDir, '1'),
						(self.fileManager.localManualLabelFramesDir[:-1] + '_pngs', self.fileManager.cloudMasterDir[:-1] + '_pngs', '1')
						]"""

	def runClusterAnalysis(self):
		command = ['python3', 'CichlidActionDetection/VideoFocus.py']
		command.extend(['--Movie_file', self.videoObj.localVideoFile])
		command.extend(['--Num_workers', str(self.workers)])
		command.extend(['--Log', self.videoObj.localHMMFile + '.log'])
		command.extend(['--HMM_temp_directory', self.videoObj.localTempDir])
		command.extend(['--HMM_filename', self.videoObj.localHMMFile])
		command.extend(['--HMM_transition_filename', self.videoObj.localRawCoordsFile])
		command.extend(['--Cl_labeled_transition_filename', self.videoObj.localLabeledCoordsFile])
		command.extend(['--Cl_labeled_cluster_filename', self.videoObj.localLabeledClustersFile])
		command.extend(['--Cl_videos_directory', self.fileManager.localAllClipsDir])
		command.extend(['--ML_frames_directory', self.fileManager.localManualLabelFramesDir])
		command.extend(['--ML_videos_directory', self.fileManager.localManualLabelClipsDir])
		command.extend(['--Video_start_time', str(self.videoObj.startTime)])
		command.extend(['--VideoID', self.fileManager.lp.movies[0].baseName])

		subprocess.run(command)



