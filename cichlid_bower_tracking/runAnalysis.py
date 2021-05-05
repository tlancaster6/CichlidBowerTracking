# To do
# 1. Make summary file on Dropbox
# 2. Handle Sigint to make sure uploads complete

import argparse, subprocess, pdb
import pandas as pd

parser = argparse.ArgumentParser(description='This script is used to manually prepared projects for downstream analysis')
parser.add_argument('AnalysisType', type = str, choices=['Prep','Depth','Cluster','ClusterClassification','Summary'], help = 'Type of analysis to run')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--ProjectIDs', type = str, nargs = '+', help = 'Name of projectIDs to run analysis on')
group.add_argument('--SummaryFile', type = str, help = 'Name of csv file that specifies projects to analyze')
parser.add_argument('--Workers', type = int, default = 1, help = 'Number of workers')
parser.add_argument('--ModelID', type = int, default = 1, help = 'ModelID to use to classify clusters with')

args = parser.parse_args()

# Identify projects to run analysis on
if args.ProjectIDs is not None:
	projectIDs = args.ProjectIDs # Specified at the command line
else:
	dt = pd.read_csv(args.SummaryFile, index_col = 0) # Specified in the csv file
	projectIDs = list(dt[dt[args.AnalysisType] == False].projectID) # Only run analysis on projects that need it


# To run analysis efficiently, we download and upload data in the background while the main script runs
uploadProcesses = [] # Keep track of all of the processes still uploading so we don't quit before they finish
subprocess.run(['python3', '-m', 'cichlid_bower_tracking.unit_scripts.download_data',args.AnalysisType, '--ProjectID', projectIDs[0]])
for i, projectID in enumerate(projectIDs):

	# Run appropriate analysis script
	if args.AnalysisType == 'Prep':
		p1 = subprocess.Popen(['python3', '-m', 'cichlid_bower_tracking.unit_scripts.prep_data', projectID])
	elif args.AnalysisType == 'Depth':
		p1 = subprocess.Popen(['python3', '-m', 'cichlid_bower_tracking.unit_scripts.analyze_depth', projectID])
	elif args.AnalysisType == 'Cluster':
		p1 = subprocess.Popen(['python3', '-m', 'cichlid_bower_tracking.unit_scripts.analyze_clusters', projectID,'--Workers',str(args.Workers)])
	elif args.AnalysisType == 'ClusterClassification':
		p1 = subprocess.Popen(['python3', '-m', 'cichlid_bower_tracking.unit_scripts.classify_clusters', projectID,args.ModelID])

	# In the meantime, download data for next project in the background
	if i+1 < len(projectIDs):
		p2 = subprocess.Popen(['python3', '-m', 'cichlid_bower_tracking.unit_scripts.download_data', args.AnalysisType, '--ProjectID', projectIDs[i+1]])
	
	# Pause script until current analysis is complete and data for next project is downloaded
	p1.communicate()
	try:
		p2.communicate() # Need to catch an exception if only one project is analyzed
	except NameError:
		pass
	#Modify summary file if necessary
	if args.SummaryFile:
		dt.loc[dt.projectID == projectID,args.AnalysisType] = True
		dt.to_csv(args.SummaryFile)

	#Upload data and keep track of it
	uploadProcesses.append(subprocess.Popen(['python3', '-m', 'cichlid_bower_tracking.unit_scripts.upload_data', args.AnalysisType, '--Delete', projectID]))

for p in uploadProcesses:
	p.communicate()
