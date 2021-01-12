import argparse, subprocess
from Modules.DataPreparers.ProjectPreparer import ProjectPreparer as PP

parser = argparse.ArgumentParser()
parser.add_argument('ProjectID', type = str, help = 'Manually identify the project you want to analyze')


pp_obj = PP(args.ProjectID)
pp_obj.runPrepAnalysis()
		
