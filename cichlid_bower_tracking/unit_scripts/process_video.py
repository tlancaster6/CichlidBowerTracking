from cichlid_bower_tracking.helper_modules.file_manager import FileManager as FM
import argparse, subprocess, os

parser = argparse.ArgumentParser()
parser.add_argument('VideoFile', type = str, help = 'Name of h264 file to be processed')
parser.add_argument('Framerate', type = float, help = 'Video framerate')
parser.add_argument('ProjectID', type = str, help = 'Video framerate')

args = parser.parse_args()

fileManager = FM(projectID = args.ProjectID)

if '.h264' not in args.VideoFile:
	raise Exception(args.VideoFile + ' not an h264 file')

# Convert h264 to mp4
ffmpeg_output = subprocess.run(['ffmpeg', '-r', str(args.Framerate), '-i', args.VideoFile, '-threads', '1', '-c:v', 'copy', '-r', str(args.Framerate), args.VideoFile.replace('.h264', '.mp4')], capture_output = True)
assert os.path.isfile(args.VideoFile.replace('.h264', '.mp4'))
assert os.path.getsize(args.VideoFile.replace('.h264','.mp4')) > os.path.getsize(args.VideoFile)

# Sync with cloud (will return error if something goes wrong)
fileManager.uploadData(args.VideoFile.replace('.h264', '.mp4'))

# Delete videos
try:
	subprocess.run(['mv', args.VideoFile, fileManager.localBackupDir])
except:
	continue

