import datetime, os, subprocess, pdb

from Modules.FileManager import FileManager as FM
from Modules.DataPreparers.PrepPreparer import PrepPreparer as PrP
from Modules.DataPreparers.DepthPreparer import DepthPreparer as DP
from Modules.DataPreparers.ClusterPreparer import ClusterPreparer as CP
from Modules.DataPreparers.ThreeDClassifierPreparer import ThreeDClassifierPreparer as TDCP
from Modules.DataPreparers.ManualLabelVideoPreparer import ManualLabelVideoPreparer as MLVP
from Modules.DataPreparers.SummaryPreparer import SummaryPreparer as SP

class ProjectPreparer():
	# This class takes in a projectID and runs all the appropriate analysis

	def __init__(self, projectID, modelID = 'Model18_All', workers = None):
		self.projectID = projectID
		self.fileManager = FM(projectID = projectID, modelID = modelID)
		if not self._checkProjectID():
			raise Exception(projectID + ' is not valid.')
		self.workers = workers

	def _checkProjectID(self):
		projectIDs = subprocess.run(['rclone', 'lsf', self.fileManager.cloudMasterDir], capture_output = True, encoding = 'utf-8').stdout.split()
		if self.projectID + '/' in projectIDs:
			return True
		else:
			return False

	def downloadData(self, dtype, videoIndex = None):
		self.fileManager.downloadProjectData(dtype)

	def uploadData(self, dtype, videoIndex = None):
		self.fileManager.uploadProjectData(dtype, videoIndex)

	def runPrepAnalysis(self):
		prp_obj = PrP(self.fileManager)
		prp_obj.validateInputData()
		prp_obj.prepData()

	def runDepthAnalysis(self):
		dp_obj = DP(self.fileManager)
		dp_obj.validateInputData()
		dp_obj.createSmoothedArray()
		dp_obj.createRGBVideo()

	def runClusterAnalysis(self, videoIndex):
		cp_obj = CP(self.fileManager, videoIndex, self.workers)
		cp_obj.validateInputData()
		cp_obj.runClusterAnalysis()

	def run3DClassification(self):
		tdcp_obj = TDCP(self.fileManager)
		tdcp_obj.validateInputData()
		tdcp_obj.predictLabels()

	def manuallyLabelVideos(self, initials, number):
		mlv_obj = MLVP(self.fileManager, initials, number)
		mlv_obj.validateInputData()
		mlv_obj.labelVideos()

	def manuallyLabelFrames(self, initials, number):
		mlf_obj = MLFP(self.fileManager, initials, number)
		mlf_obj.validateInputData()
		mlf_obj.labelFrames()
	
	def runMLFishDetection(self):
		pass

	def runSummaryCreation(self):
		sc_obj = SP(self.fileManager)
		sc_obj.validateInputData()
		sc_obj.createFullSummary()

		# self.createUploadFile(sc_obj.uploads)
		# self.createAnalysisUpdate('Summary', sc_obj)

	def backupAnalysis(self):
		uploadCommands = set()

		uploadFiles = [x for x in os.listdir(self.fileManager.localUploadDir) if 'UploadData' in x]

		for uFile in uploadFiles:
			with open(self.fileManager.localUploadDir + uFile) as f:
				line = next(f)
				for line in f:
					tokens = line.rstrip().split(',')
					tokens[2] = bool(int(tokens[2]))
					uploadCommands.add(tuple(tokens))

		for command in uploadCommands:
			self.fileManager.uploadData(command[0], command[1], command[2])

		for uFile in uploadFiles:
			subprocess.run(['rm', '-rf', self.fileManager.localUploadDir + uFile])

		self.fileManager.uploadData(self.fileManager.localAnalysisLogDir, self.fileManager.cloudAnalysisLogDir, False)
		subprocess.run(['rm', '-rf', self.fileManager.localMasterDir])

	def localDelete(self):
		subprocess.run(['rm', '-rf', self.fileManager.localMasterDir])

	def createUploadFile(self, uploads):
		with open(self.fileManager.localUploadDir + 'UploadData_' + str(datetime.datetime.now().timestamp()) + '.csv', 'w') as f:
			print('Local,Cloud,Tar', file = f)
			for upload in uploads:
				print(upload[0] + ',' + upload[1] + ',' + str(upload[2]), file = f)

	def createAnalysisUpdate(self, aType, procObj):
		now = datetime.datetime.now()
		with open(self.fileManager.localAnalysisLogDir + 'AnalysisUpdate_' + str(now.timestamp()) + '.csv', 'w') as f:
			print('ProjectID,Type,Version,Date', file = f)
			print(self.projectID + ',' + aType + ',' + procObj.__version__ + '_' + os.getenv('USER') + ',' + str(now), file= f)
