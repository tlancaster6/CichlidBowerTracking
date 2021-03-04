import argparse, subprocess, pdb
import pandas as pd

parser = argparse.ArgumentParser(description='This script is used to manually prepared projects for downstream analysis')
parser.add_argument('--ProjectIDs', type = str, nargs = '+', help = 'Name of projectIDs to run analysis on')
parser.add_argument('--SummaryFile', type = str, help = 'Name of summary file to use identify projects')
parser.add_argument('--Workers', type = str, help = 'Number of workers. If not included all available cpus are used')

args = parser.parse_args()

if args.Workers is None:
	import multiprocessing
	workers = multiprocessing.cpu_count()
else:
	workers = args.Workers

if args.ProjectIDs is not None:
	for projectID in args.ProjectIDs:
		subprocess.run(['python3', '-m', 'Modules.UnitScripts.DownloadData','Cluster', '--ProjectID', projectID])
		subprocess.run(['python3', '-m', 'Modules.UnitScripts.AnalyzeClusters', projectID, '--Workers', workers])
		subprocess.run(['python3', '-m', 'Modules.UnitScripts.UploadData','Cluster', projectID])
		#subprocess.run(['python3', '-m', 'Modules.UnitScripts.DeleteData', projectID])

elif args.SummaryFile is not None:
	dt = pd.read_csv(args.SummaryFile, index_col = 0)
	for projectID in dt[dt.ClusterFiles == False].projectID:
		subprocess.run(['python3', '-m', 'Modules.UnitScripts.DownloadData','Cluster', '--ProjectID', projectID])
		subprocess.run(['python3', '-m', 'Modules.UnitScripts.AnalyzeCluster', projectID, '--Workers', workers])
		subprocess.run(['python3', '-m', 'Modules.UnitScripts.UploadData','Cluster', projectID])
		#subprocess.run(['python3', '-m', 'Modules.UnitScripts.DeleteData', projectID])

		dt.loc[dt.projectID == projectID,'ClusterFiles'] = True
		dt.to_csv(args.SummaryFile)

else:
	print('Must use one of two options')