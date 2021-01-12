import argparse, os, pdb, sys
from Modules.DataPreparers.ProjectPreparer import ProjectPreparer as PP

parser = argparse.ArgumentParser()

parser.add_argument('ProjectIDs',  nargs = '+', type = str, help = 'Which projectID you want to identify')

args = parser.parse_args()

for projectID in args.ProjectIDs:
	print('Processing depth data for ' + projectID, file = sys.stderr)

	pp_obj = PP(projectID)
	pp_obj.runDepthAnalysis()

