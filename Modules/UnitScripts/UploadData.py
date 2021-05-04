# Things to add
# 1. Delete model data if it is generated/downloaded
# 2. Upload model data if it is created

import argparse,sys
from Modules.DataPreparers.ProjectPreparer import ProjectPreparer as PP

parser = argparse.ArgumentParser()
parser.add_argument('DataType', type = str, choices=['Prep','Depth','Video', 'Cluster','ClusterClassification','FishDetection','ManualAnnotation','Summary','All'], help = 'What type of analysis to perform')
parser.add_argument('ProjectID', type = str, help = 'Manually identify the projects you want to analyze. If All is specified, all non-prepped projects will be analyzed')
parser.add_argument('-v', '--VideoIndex', type = int, help = 'Specify which video should be downloaded if Cluster analysis is to be performed')
parser.add_argument('-d', '--Delete', action = 'store_true', help = 'Delete data once it is uploaded')

args = parser.parse_args()

print('Uploading data for ' + args.ProjectID, file = sys.stderr)

pp_obj = PP(args.ProjectID)
if args.DataType in ['Cluster','Video']:
	if args.VideoIndex is None:
		print('Must specify a video index if downloading data for Cluster Analysis')
	pp_obj.uploadData(args.DataType, videoIndex = args.VideoIndex)
else:
	pp_obj.uploadData(args.DataType)
if args.Delete:
	pp_obj.localDelete()