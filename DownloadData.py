import argparse, sys
from Modules.DataPreparers.ProjectPreparer import ProjectPreparer as PP

parser = argparse.ArgumentParser()
parser.add_argument('DataType', type = str, choices=['Prep','Depth','Cluster','ClusterClassification','FishDetection','ManualAnnotation','ManualLabelVideos','Figures','All'], help = 'What type of analysis to perform')
parser.add_argument('ProjectID', type = str, help = 'Manually identify the projects you want to analyze. If All is specified, all non-prepped projects will be analyzed')
parser.add_argument('-v', '--VideoIndex', type = int, help = 'Specify which video should be downloaded if Cluster analysis is to be performed')

args = parser.parse_args()

print('Downloading data for ' + args.ProjectID, file = sys.stderr)

pp_obj = PP(args.ProjectID)
if args.DataType == 'Cluster':
	if args.VideoIndex is None:
		print('Must specify a video index if downloading data for Cluster Analysis')
	pp_obj.downloadData(args.DataType, videoIndex = args.VideoIndex)
else:
	pp_obj.downloadData(args.DataType)

