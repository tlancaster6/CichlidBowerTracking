import argparse, subprocess
from Modules.DataPreparers.ProjectPreparer import ProjectPreparer as PP

parser = argparse.ArgumentParser()
parser.add_argument('ProjectIDs', nargs = '+', type = str, help = 'Manually identify the projects you want to analyze. If All is specified, all non-prepped projects will be analyzed')

args = parser.parse_args()

print(['python3', 'DownloadData.py', 'Prep'] + args.ProjectIDs)
subprocess.run(['python3', 'DownloadData.py', 'Prep'] + args.ProjectIDs)

for projectID in args.ProjectIDs:
	pp_obj = PP(projectID)
	pp_obj.runPrepAnalysis()
		
	#pp_obj.backupAnalysis()
	#ap_obj.updateAnalysisFile(newProjects = False, projectSummary = False)
