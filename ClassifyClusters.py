import argparse, pdb
from Modules.DataPreparers.ProjectPreparer import ProjectPreparer as PP

parser = argparse.ArgumentParser(usage = 'This script will use a previously trained 3D Resnet model to classify videos')
parser.add_argument('ProjectID', type = str, help = 'Which projectID you want to identify')
parser.add_argument('ModelID', type = str, help = 'Which previously trained ModelID you want to use to classify the videos')
args = parser.parse_args()

pp_obj = PP(args.ProjectID)
pp_obj.run3DClassification(args.ModelID)

