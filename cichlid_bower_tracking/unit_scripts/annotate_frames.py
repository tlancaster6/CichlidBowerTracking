import argparse, pdb, sys
from cichlid_bower_tracking.data_preparers.project_preparer import ProjectPreparer as PP

parser = argparse.ArgumentParser(usage = 'This script will perform inital analysis of depth data to create a smoothed, interpolated, 3D npy array')
parser.add_argument('ProjectID', type = str, help = 'Which projectID you want to identify')
parser.add_argument('Number', type = int, help = 'Total number of videos to label for this project')
parser.add_argument('Initials', type = str, help = 'Initials of annotator')

args = parser.parse_args()

if len(args.Initials) != 3:
	print('Initials must be three letters long')
	sys.exit()

pp_obj = PP(args.ProjectID)
pp_obj.manuallyLabelFrames(args.Initials.upper(), args.Number)