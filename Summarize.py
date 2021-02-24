import argparse
from Modules.DataPreparers.ProjectPreparer import ProjectPreparer as PP

parser = argparse.ArgumentParser(usage = 'This script is run after analysis to create useful figures and summary files')
parser.add_argument('ProjectID', type = str, help = 'Which projectID you want to identify')
args = parser.parse_args()

pp_obj = PP(args.ProjectID)

pp_obj.runSummaryCreation()
