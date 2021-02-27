import subprocess, argparse, pdb
import pandas as pd

from Modules.FileManager import FileManager as FM

parser = argparse.ArgumentParser(description='This script is used to determine project states.')
parser.add_argument('--ProjectIDs', type = str, nargs = '+', help = 'Restrict analysis to specified projectIDs ')
parser.add_argument('--SummaryFile', type = str, help = 'Restrict analysis to projectIDs specified in file, which will be rewritten')

args = parser.parse_args()

if args.ProjectIDs is not None:
	projectIDs = args.ProjectIDs
elif args.SummaryFile is not None:
	dt = pd.read_csv(args.SummaryFile, index_col = 0)
	projectIDs = list(dt.projectID)
else:
	projectIDs = FM().getAllProjectIDs()

if args.SummaryFile:
	dt = pd.read_csv(args.SummaryFile, index_col = 0)
else:
	dt = pd.DataFrame(columns = ['projectID', 'tankID', 'StartingFiles', 'PrepFiles', 'DepthFiles', 'ClusterFiles', '3DClassifyFiles'])

for projectID in projectIDs:
	fm_obj = FM(projectID = projectID)
	out_data = fm_obj.getProjectStates()

	if projectID in list(dt.projectID):
		print('Editing row')
		dt.loc[dt.projectID == projectID, out_data.keys()] = out_data.values()
	else:
		print('Adding row')
		dt = dt.append(out_data, ignore_index=True)
	subprocess.run(['rm', '-rf', fm_obj.localProjectDir])
if args.SummaryFile:
	dt.to_csv(args.SummaryFile)
else:
	dt.to_csv('SummaryFile.csv')
