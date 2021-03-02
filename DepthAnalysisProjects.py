import argparse, subprocess, pdb, sys
import pandas as pd

parser = argparse.ArgumentParser(description='This script is used to manually prepared projects for downstream analysis')
parser.add_argument('--ProjectIDs', type = str, nargs = '+', help = 'Name of projectIDs to run analysis on')
parser.add_argument('--SummaryFile', type = str, help = 'Name of summary file to use identify projects')

args = parser.parse_args()

if args.ProjectIDs is not None:
	projectIDs = args.ProjectIDs
elif args.SummaryFile is not None:
	dt = pd.read_csv(args.SummaryFile, index_col = 0)
	projectIDs = list(dt[dt.DepthFiles == False].projectID)
else:
	print('Must use one of two options')
	sys.exit()

uploadProcess = []
subprocess.run(['python3', '-m', 'Modules.UnitScripts.DownloadData','Depth', '--ProjectID', projectIDs[0]])
for i, projectID in enumerate(projectIDs):
	p1 = subprocess.Popen(['python3', '-m', 'Modules.UnitScripts.AnalyzeDepth', projectID])
	if i+1 < len(projectIDs):
		# Download next project 
		p2 = subprocess.Popen(['python3', '-m', 'Modules.UnitScripts.AnalyzeDepth', projectIDs[i+1]])
	p1.communicate()
	p2.communicate()
	if args.SummaryFile:
		dt.loc[dt.projectID == projectID,'DepthFiles'] = True
		dt.to_csv(args.SummaryFile)

	uploadProcesses.append(subprocess.Popen(['python3', '-m', 'Modules.UnitScripts.UploadData','Depth', '--Delete', projectID]))

for p in uploadProcesses():
	p.communicate()
