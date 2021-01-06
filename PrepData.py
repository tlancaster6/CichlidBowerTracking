import argparse, os, pdb, sys, subprocess

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--ProjectIDs', nargs = '+', required = True, type = str, help = 'Manually identify the projects you want to analyze. If All is specified, all non-prepped projects will be analyzed')

args = parser.parse_args()

args.command == 'ManualPrep':
	
	ap_obj = AP()
	if ap_obj.checkProjects(args.ProjectIDs):
		sys.exit()

	for projectID in args.ProjectIDs:
		pp_obj = PP(projectID, args.Workers)
		pp_obj.runPrepAnalysis()
		
	pp_obj.backupAnalysis()
	ap_obj.updateAnalysisFile(newProjects = False, projectSummary = False)
