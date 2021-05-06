import argparse, pdb
from cichlid_bower_tracking.data_preparers.project_preparer import ProjectPreparer as PP

parser = argparse.ArgumentParser(usage = 'This script will perform inital analysis of depth data to create a smoothed, interpolated, 3D npy array')
parser.add_argument('ProjectID', type = str, help = 'Which projectID you want to identify')
parser.add_argument('--VideoIndex', type = int, help = 'Index of video that should be analyzed')
parser.add_argument('--Workers', type = int, default = 1, help = 'Number of threads to run this analysis in parallel')
args = parser.parse_args()

pp_obj = PP(args.ProjectID, workers = args.Workers)

pp_obj.runClusterAnalysis(args.VideoIndex)

