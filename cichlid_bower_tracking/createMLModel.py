import argparse, subprocess
from cichlid_bower_tracking.data_preparers.project_preparer import ProjectPreparer as PP

parser = argparse.ArgumentParser(usage = 'This script will train a new ML model')
parser.add_argument('MLType', type = str, choices = ['3DResnet', 'RCNN'], help = 'Choose between a 3D Resnet for classifying videos or an RCNN to identify fish')
parser.add_argument('ModelID', type = str, help = 'Name of the model created')
parser.add_argument('--ProjectIDs', nargs = '+', type = str, help = 'Restrict training data to the following ProjectIDs')
parser.add_argument('--GPU', type = str, default = '0', help = 'Specify the GPU card to use')

args = parser.parse_args()

subprocess.run(['python3', '-m', 'cichlid_bower_tracking.unit_scripts.download_data', 'Train' + args.MLType, '--ModelID', args.ModelID])

pp_obj = PP(projectID = None, modelID = args.ModelID)
pp_obj.createModel(args.type, args.ProjectIDs, args.GPU)

subprocess.run(['python3', '-m', 'cichlid_bower_tracking.unit_scripts.upload_data', 'Train' + args.MLType, '--ModelID', args.ModelID])
