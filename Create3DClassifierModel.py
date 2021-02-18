import argparse, pdb, sys
from Modules.DataPreparers.ProjectPreparer import ProjectPreparer as PP

parser = argparse.ArgumentParser(usage = 'This script will create or finetune a 3D Resnet model for classifying sand manipulation videos')
parser.add_argument('Purpose', type = str, choices = ['New', 'Finetune'], help = 'Create new model or finetune the master model')
parser.add_argument('NewModelID', type = str, help = 'Name of the model created')
parser.add_argument('ProjectIDs', nargs = '+', type = str, help = 'ProjectIDs to include. (Use all to include all)')
parser.add_argument('--GPU', type = str, help = 'Specify the GPU card to use')

args = parser.parse_args()

pp_obj = PP('PatrickControl2', args.NewModelID)
pp_obj.createModel(args.Purpose, args.ProjectIDs, args.OldModelID, args.GPU)