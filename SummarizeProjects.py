import argparse, subprocess, pdb, os
import pandas as pd
from Modules.FileManager import FileManager as FM
from PyPDF2 import PDFFileMerger

parser = argparse.ArgumentParser(description='This script is used to manually prepared projects for downstream analysis')
parser.add_argument('--ProjectIDs', type = str, nargs = '+', help = 'Name of projectIDs to run analysis on')
parser.add_argument('--SummaryFile', type = str, help = 'Name of summary file to use identify projects')

args = parser.parse_args()

if args.ProjectIDs is not None:
	for projectID in args.ProjectIDs:
		subprocess.run(['python3', '-m', 'Modules.UnitScripts.DownloadData','Cluster', '--ProjectID', projectID])
		subprocess.run(['python3', '-m', 'Modules.UnitScripts.AnalyzeClusters', projectID, '--Workers', str(workers)])
		subprocess.run(['python3', '-m', 'Modules.UnitScripts.UploadData','Cluster', projectID])
		#subprocess.run(['python3', '-m', 'Modules.UnitScripts.DeleteData', projectID])

elif args.SummaryFile is not None:
	s_dt = pd.read_csv(args.SummaryFile, index_col = 0)
	s_pdfs = PdfFileMerger()
	for projectID in s_dt.projectID:
		if 'F' not in projectID:
			continue
		fm_obj = FM(projectID = projectID)
		try:
			fm_obj.downloadData(fm_obj.localDepthSummaryFile)
			dt = pd.read_excel(fm_obj.localDepthSummaryFile, index_col = 0)
			fm_obj.downloadData(fm_obj.localDepthSummaryFigure)
			s_pdfs.append(fm_obj.localDepthSummaryFigure)

		except FileNotFoundError:
			print('Cant find ' + projectID)
			continue
		try:
			all_dt = all_dt.append(dt)
		except NameError:
			all_dt = dt
		os.remove(fm_obj.localDepthSummaryFile)
	merger.write("F2s_Depth.pdf")
	merger.close()
	pdb.set_trace()	

else:
	print('Must use one of two options')