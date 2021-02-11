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
		command = ['python', 'VideoFocus.py']
		command.extend(['--Movie_file', str(self.videoObj.localVideoFile)])
		command.extend(['--Num_workers', str(self.workers)])
		command.extend(['--Log', str(self.videoObj.localHMMFile) + '.log'])
		command.extend(['--HMM_temp_directory', str(self.videoObj.localTempDir)])
		command.extend(['--HMM_filename', str(self.videoObj.localHMMFile)])
		command.extend(['--HMM_transition_filename', str(self.videoObj.localRawCoordsFile)])
		command.extend(['--Cl_labeled_transition_filename', str(self.videoObj.localLabeledCoordsFile)])
		command.extend(['--Cl_labeled_cluster_filename', str(self.videoObj.localLabeledClustersFile)])
		command.extend(['--Cl_videos_directory', str(self.videoObj.localAllClipsDir)])
		command.extend(['--ML_frames_directory', str(self.videoObj.localManualLabelFramesDir)])
		command.extend(['--ML_videos_directory', str(self.videoObj.localManualLabelClipsDir)])
		command.extend(['--Video_start_time', str(self.videoObj.startTime)])
		command.extend(['--VideoID', str(self.fileManager.lp.movies[0].baseName)])

		if not os.path.exists('CichlidActionDetection'):
			subprocess.run('git clone https://github.com/ptmcgrat/CichlidActionDetection')
		os.chdir('CichlidActionDetection')
		subprocess.run(command)
		os.chdir('..')



