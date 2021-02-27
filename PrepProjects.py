import argparse, subprocess, pdb
import pandas as pd

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
	for projectID in dt[dt.PrepFiles == False].projectID:
		subprocess.run(['python3', 'Modules/UnitScripts/DownloadData.py','Prep', '--ProjectID', projectID])
		subprocess.run(['python3', 'Modules/UnitScripts/PrepData.py', projectID])
		subprocess.run(['python3', 'Modules/UnitScripts/UploadData.py','Prep', projectID])
		dt.loc[dt.projectID == projectID,'PrepFiles'] = True
		dt.to_csv(args.SummaryFile)
