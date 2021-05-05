import argparse, pdb, sys
from Modules.DataPreparers.ProjectPreparer import ProjectPreparer as PP

parser = argparse.ArgumentParser(usage = 'This script will use a previously trained 3D Resnet model to classify videos')
parser.add_argument('ProjectID', type = str, help = 'Which projectID you want to identify')
args = parser.parse_args()

print('Analyzing depth data for ' + args.ProjectID, file = sys.stderr)

pp_obj = PP(args.ProjectID)
pp_obj.runDepthAnalysis()

