import argparse, os, pdb, sys
from Modules.DataPreparers.ProjectPreparer import ProjectPreparer as PP

parser = argparse.ArgumentParser(usage = 'This script will perform inital analysis of depth data to create a smoothed, interpolated, 3D npy array')

parser.add_argument('ProjectIDs', type = str, help = 'Which projectID you want to identify')

args = parser.parse_args()

pp_obj = PP(args.ProjectID)
pp_obj.runDepthAnalysis()

