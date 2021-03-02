import argparse,sys
from Modules.DataPreparers.ProjectPreparer import ProjectPreparer as PP

parser = argparse.ArgumentParser()
parser.add_argument('ProjectID', type = str, help = 'Manually identify the projects you want to analyze. If All is specified, all non-prepped projects will be analyzed')

args = parser.parse_args()

print('Deleting data for ' + args.ProjectID, file = sys.stderr)

pp_obj = PP(args.ProjectID)
pp_obj.localDelete()
