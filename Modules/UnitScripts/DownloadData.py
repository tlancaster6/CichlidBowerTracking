import argparse, sys
from Modules.DataPreparers.ProjectPreparer import ProjectPreparer as PP

parser = argparse.ArgumentParser()
parser.add_argument('DataType', type = str, choices=['Prep','Depth','Cluster','ClusterClassification','Train3DModel', 'FishDetection','ManualAnnotation','ManualLabelVideos','Figures','All'], help = 'What type of analysis to perform')
parser.add_argument('--ProjectID', type = str, help = 'Manually identify the projects you want to analyze. If All is specified, all non-prepped projects will be analyzed')
parser.add_argument('--VideoIndex', type = int, help = 'Specify which video should be downloaded if Cluster analysis is to be performed')
parser.add_argument('--NewModelID', type = str, help = 'Specify which video should be downloaded if Cluster analysis is to be performed')

args = parser.parse_args()

print('Downloading data for ' + args.ProjectID, file = sys.stderr)

pp_obj = PP(args.ProjectID, args.NewModelID)
pp_obj.downloadData(args.DataType, videoIndex = args.VideoIndex)

