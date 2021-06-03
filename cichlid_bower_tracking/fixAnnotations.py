import argparse, subprocess
from cichlid_bower_tracking.helper_modules.object_labeler import AnnotationDisagreements as AD
from cichlid_bower_tracking.helper_modules.file_manager import FileManager as FM

parser = argparse.ArgumentParser()
parser.add_argument('User1', type = str, help = 'Initials of user annotations to compare')
parser.add_argument('User2', type = str, help = 'Initials user annotations to compare')
parser.add_argument('ProjectID', type = str, help = 'Project to analyze')
parser.add_argument('-p', '--Practice', action = 'store_true', help = 'Use if you dont want to save annotations')

args = parser.parse_args()

fm_obj = FM(projectID = args.ProjectID)
fm_obj.downloadData(fm_obj.localLabeledClipsProjectDir, tarred = True)
fm_obj.downloadData(fm_obj.localBoxedFishFile)


obj = AD(self.fileManager.localLabeledFramesProjectDir, self.fileManager.localBoxedFishFile, args.ProjectID, args.User1, args.User2)

ad_obj = AD(fm_obj.localBoxedFishDir + args.ProjectID + '/', temp_dt, args.ProjectID, args.User1, args.User2, args.All)

# Redownload csv in case new annotations have been added
fm_obj.downloadData(fm_obj.localBoxedFishFile)

old_dt = pd.read_csv(fm_obj.localBoxedFishFile, index_col = 0)
new_dt = pd.read_csv(temp_dt)

old_dt = old_dt.append(new_dt, sort = 'False').drop_duplicates(subset = ['ProjectID', 'Framefile', 'User', 'Sex', 'Box'], keep = 'last').sort_values(by = ['ProjectID', 'Framefile'])
old_dt.to_csv(fm_obj.localBoxedFishFile, sep = ',', columns = ['ProjectID', 'Framefile', 'Nfish', 'Sex', 'Box', 'CorrectAnnotation','User', 'DateTime'])

if not args.Practice:
	fm_obj.uploadData(fm_obj.localBoxedFishFile)

subprocess.run(['rm', '-rf', fm_obj.localProjectDir])
subprocess.run(['rm', '-rf', fm_obj.localAnnotationDir])

			self.downloadData(self.localLabeledClipsProjectDir, tarred = True)
