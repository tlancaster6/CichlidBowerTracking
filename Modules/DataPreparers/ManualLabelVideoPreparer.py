import subprocess, os
import pdb, datetime, os, subprocess, argparse, random, cv2
import pandas as pd


class ManualLabelVideoPreparer():
	# This class takes in directory information and a logfile containing depth information and performs the following:
	# 1. Identifies tray using manual input
	# 2. Interpolates and smooths depth data
	# 3. Automatically identifies bower location
	# 4. Analyze building, shape, and other pertinent info of the bower

	def __init__(self, fileManager, initials, number):

		self.__version__ = '1.0.0'

		self.fileManager = fileManager
		self.initials = initials

		# 10 categories of annotation plus quit and skip commands
		self.commands = ['c','f','p','t','b','m','s','x','o','d','q','k']
		self.commands_help = "Type 'c': build scoop; 'f': feed scoop; 'p': build spit; 't': feed spit; 'b': build multiple; 'm': feed multiple; 'd': drop sand; s': spawn; 'o': fish other; 'x': nofish other; 'q': quit; 'k': skip"

	def validateInputData(self):
		fm_obj = FM(projectID = args.ProjectID)

		assert os.path.exists(self.fileManager.localAnalysisDir)
		assert os.path.exists(self.fileManager.localManualLabelClipsDir)
		assert os.path.exists(self.fileManager.localLabeledClipsFile)
		assert os.path.exists(self.fileManager.localNewLabeledVideosFile)

		"""self.uploads = [(self.fileManager.localTroubleshootingDir, self.fileManager.cloudTroubleshootingDir, '0'), 
						(self.fileManager.localAnalysisDir, self.fileManager.cloudAnalysisDir, '0'),
						(self.fileManager.localAllClipsDir, self.fileManager.cloudMasterDir, '1'),
						(self.fileManager.localManualLabelClipsDir, self.fileManager.cloudMasterDir, '1'),
						(self.fileManager.localManualLabelFramesDir, self.fileManager.cloudMasterDir, '1'),
						(self.fileManager.localManualLabelFramesDir[:-1] + '_pngs', self.fileManager.cloudMasterDir[:-1] + '_pngs', '1')
						]"""

	def labelVideos(self):
		temp_csv = fm_obj.localAnalysisDir + 'NewAnnotations.csv'

		# Read in annotations and create csv file for all annotations with the same user and projectID
		previouslyLabeled_dt = pd.read_csv(self.fileManager.localLabeledClipsFile, index_col = 'LID')
		newlyLabeled_dt = pd.DataFrame(columns =previouslyLabeled_dt.columns)

		# Identify clips that can be labeled
		clips = [x for x in os.listdir(self.fileManager.localManualLabelClipsDir) if 'ManualLabel.mp4' in x]

		print(self.commands_help)
		
		annotatedClips = 0 # Keep track of all the new clips that have been labeled
		random.shuffle(clips) # Shuffle the clips so that it's a random sample

		for f in clips:

			if not previouslyLabeled_dt.loc[previouslyLabeled_dt.ClipName == f]['ManualLabel'].empty:
				print('Skipping ' + f + ' since it is already labeled', file = sys.stderr)
				continue
	
			cap = cv2.VideoCapture(self.fileManager.localManualLabelClipsDir + f) # Open video object and display it
	
			while(True):

				ret, frame = cap.read()
				if not ret:
					cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
					continue
				cv2.imshow(self.commands_help,cv2.resize(frame,(0,0),fx=4, fy=4))
				info = cv2.waitKey(25)
	
				if info in [ord(x) for x in self.commands]:
					for i in range(1,10):
						cv2.destroyAllWindows()
						cv2.waitKey(1)
					break

			if info == ord('q'):
				return

			if info == ord('k'):
				continue #skip

			newlyLabeled_dt.loc[len(newlyLabeled_dt)] = [f.replace('_ManualLabel.mp4',''), chr(info), self.initials, str(datetime.datetime.now())] # Create new annotation

			newlyLabeled_dt.to_csv(self.fileManager.localNewLabeledVideosFile, sep = ',')

			annotatedClips += 1

			if annotatedClips >= self.number:
				return

