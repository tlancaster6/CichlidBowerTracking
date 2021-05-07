# Things to add
# 1. Delete model data if it is generated/downloaded
# 2. Upload model data if it is created

import argparse,sys
from cichlid_bower_tracking.data_preparers.project_preparer import ProjectPreparer as PP

parser = argparse.ArgumentParser()
parser.add_argument('DataType', type = str, choices=['Prep','Depth','Cluster','ClusterClassification','FishDetection','ManualAnnotation','Summary','All'], help = 'What type of analysis to perform')
parser.add_argument('ProjectID', type = str, help = 'Manually identify the projects you want to analyze. If All is specified, all non-prepped projects will be analyzed')
parser.add_argument('-v', '--VideoIndex', type = int, help = 'Specify which video should be downloaded if Cluster analysis is to be performed')
parser.add_argument('-d', '--Delete', action = 'store_true', help = 'Delete data once it is uploaded')

args = parser.parse_args()

print('Uploading data for ' + args.ProjectID, file = sys.stderr)

pp_obj = PP(args.ProjectID)

pp_obj.uploadData(args.DataType, args.VideoIndex)

if args.Delete:
	pp_obj.localDelete()