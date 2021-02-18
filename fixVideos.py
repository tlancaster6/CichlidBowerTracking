from Modules.FileManager import FileManager as FM
import pandas as pd
import pdb, os

fm = FM(projectID = None, modelID = 'Temp')

#fm.downloadProjectData('Train3DModel')

dt = pd.read_csv(fm.localLabeledClipsFile)
dt['ProjectID'] = dt.ClipName.str.split('__').str[0]
dt['ClipName'] = dt.ClipName + '.mp4'

downloaded_projects = set()
for i,mp4file in enumerate([x for x in dt.ClipName if '.mp4' in x]):
    if not os.path.exists(fm.localLabeledClipsDir + mp4file):
    	projectID = mp4file.split('__')[0]
    	if projectID not in downloaded_projects:
    		fm = FM(projectID = projectID, modelID = 'Temp')
	    	fm.downloadProjectData('ClusterClassification')
    		downloaded_projects.add(projectID)
    	pdb.set_trace()