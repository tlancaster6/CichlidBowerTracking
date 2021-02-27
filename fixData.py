import argparse, subprocess, pdb, shutil, os
import pandas as pd
from Modules.FileManager import FileManager as FM
from Modules.LogParser import LogParser as LP


parser = argparse.ArgumentParser(description='This script is used to manually prepared projects for downstream analysis')
parser.add_argument('--ProjectIDs', type = str, nargs = '+', help = 'Name of projectIDs to run analysis on')
parser.add_argument('--SummaryFile', type = str, help = 'Name of summary file to use identify projects')

args = parser.parse_args()

if args.ProjectIDs is not None:
	for projectID in args.ProjectIDs:
		subprocess.run(['python3', 'Modules/UnitScripts/DownloadData.py','Prep', '--ProjectID', projectID])
		subprocess.run(['python3', 'Modules/UnitScripts/PrepData.py', projectID])
		subprocess.run(['python3', 'Modules/UnitScripts/UploadData.py','Prep', projectID])

else:
	dt = pd.read_csv(args.SummaryFile, index_col = 0)
	for projectID in dt[dt.StartingFiles == False].projectID:
		fm_obj = FM(projectID = projectID)
		print(projectID)
		# Download and read log file
		fm_obj.downloadData(fm_obj.localLogfile)
		lp = LP(fm_obj.localLogfile)

		fm_obj.createDirectory(fm_obj.localPrepDir)

		data_dirs = subprocess.run(['rclone', 'lsf', 'cichlidVideo:McGrath/Apps/CichlidPiData/' + projectID], capture_output = True, encoding = 'utf-8').stdout.split('\n')

		if 'Frames.tar' in data_dirs:
			fm_obj.downloadData(fm_obj.localFrameDir, tarred = True)
			fix_Frames = False
		elif 'Frames/' in data_dirs:
			fm_obj.downloadData(fm_obj.localFrameDir, tarred = False)
			fix_Frames = True
		else:
			pdb.set_trace()

		for movie in lp.movies:
			if movie.startTime.hour > 8 and movie.startTime.hour < 18:
				depthObj = [x for x in lp.frames if x.time > movie.startTime][0]
				break
		
		shutil.copy2(fm_obj.localProjectDir + depthObj.npy_file, fm_obj.localPrepDir + 'FirstDepth.npy')
		shutil.copy2(fm_obj.localProjectDir + depthObj.pic_file, fm_obj.localPrepDir + 'DepthRGB.jpg')

		fm_obj.downloadData(fm_obj.localProjectDir + movie.pic_file)
		shutil.copy2(fm_obj.localProjectDir + movie.pic_file, fm_obj.localPrepDir + 'PiCameraRGB.jpg')

		i = -1
		while not os.path.exists(fm_obj.localProjectDir + lp.frames[i].npy_file):
			i -= 1

		shutil.copy2(fm_obj.localProjectDir + lp.frames[i].npy_file, fm_obj.localPrepDir + 'FirstDepth.npy')
	
		fm_obj.uploadData(fm_obj.localPrepDir)


		if fix_Frames:
			fm_obj.uploadData(fm_obj.localFrameDir, tarred = True)

