import argparse, sys
from Modules.DataPreparers.ProjectPreparer import ProjectPreparer as PP

parser = argparse.ArgumentParser()
parser.add_argument('DataType', type = str, choices=['Prep','Depth','Cluster','ClusterClassification','FishDetection','ManualAnnotation','Figures','All'], help = 'What type of analysis to perform')
parser.add_argument('ProjectIDs', nargs = '+', type = str, help = 'Manually identify the projects you want to analyze. If All is specified, all non-prepped projects will be analyzed')

args = parser.parse_args()

for projectID in args.ProjectIDs:
	print('Downloading data for ' + projectID, file = sys.stderr)

	pp_obj = PP(projectID)
	pp_obj.downloadData(args.DataType)
