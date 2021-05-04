import subprocess, argparse, pdb
import pandas as pd

from Modules.FileManager import FileManager as FM

parser = argparse.ArgumentParser(description='This script is used to determine analysis states for each project.')
parser.add_argument('--SummaryFile', type = str, help = 'Restrict analysis to projectIDs specified in csv file, which will be rewritten. ProjectIDs must be found in a column called projectID')

args = parser.parse_args()

fm_obj = FM() 

if args.SummaryFile is not None:
	summary_file = fm_obj.localAnalysisStatesDir + args.SummaryFile
	fm_obj.downloadData(summary_file)
	dt = pd.read_csv(summary_file, index_col = 0)
	projectIDs = list(dt.projectID)
else:
	fm_obj.createDirectory(fm_obj.localAnalysisStatesDir)
	summary_file = fm_obj.localAnalysisStatesDir + 'AllProjects.csv'
	projectIDs = fm_obj.getAllProjectIDs()

dt = pd.DataFrame(columns = ['projectID', 'tankID', 'StartingFiles', 'Prep', 'Depth', 'Cluster', 'ClusterClassification'])

for projectID in projectIDs:
	fm_obj.createProjectData(projectID)
	
	out_data = fm_obj.getProjectStates()

	dt = dt.append(out_data, ignore_index=True)

	subprocess.run(['rm', '-rf', fm_obj.localProjectDir])

dt.to_csv(summary_file)
fm_obj.uploadData(summary_file)


