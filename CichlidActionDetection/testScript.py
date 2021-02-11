import subprocess, os

# subprocess.run(['rclone', 'copy', 'cichlidVideo:McGrath/Apps/CichlidPiData/__TestData/15_minute_clip.mp4', os.getenv('HOME') + '/Temp/'])
subprocess.run(['rclone', 'copy', 'cichlidVideo:BioSci-McGrath/Apps/CichlidPiData/__TestData/15_minute_clip.mp4', os.getenv('HOME') + '/Temp/'])

args = ['python3', 'VideoFocus.py']
args.extend(['--Movie_file', os.getenv('HOME') + '/Temp/15_minute_clip.mp4'])
args.extend(['--Num_workers', '24'])
args.extend(['--Log', os.getenv('HOME') + '/Temp/TestHMM/FocusingLog.txt'])
args.extend(['--HMM_temp_directory', os.getenv('HOME') + '/Temp/TestHMM/TempHMMFiles/'])
args.extend(['--HMM_filename', os.getenv('HOME') + '/Temp/TestHMM/Test.hmm'])
args.extend(['--HMM_transition_filename', os.getenv('HOME') + '/Temp/TestHMM/TestCoords.npy'])
args.extend(['--Cl_labeled_transition_filename', os.getenv('HOME') + '/Temp/TestHMM/TestLabeledCoords.npy'])
args.extend(['--Cl_labeled_cluster_filename', os.getenv('HOME') + '/Temp/TestHMM/TestClusters.csv'])
args.extend(['--Cl_videos_directory', os.getenv('HOME') + '/Temp/TestHMM/AllClips'])
args.extend(['--ML_frames_directory', os.getenv('HOME') + '/Temp/TestHMM/MLFrames'])
args.extend(['--ML_videos_directory', os.getenv('HOME') + '/Temp/TestHMM/MLClips'])
args.extend(['--Video_start_time', '2018-05-12 08:03:20.913025'])
args.extend(['--VideoID', '15_minute_clip'])

subprocess.run(args)

#subprocess.run(['rclone', 'copy', 'cichlidVideo:McGrath/Apps/CichlidPiData/MC6_5/Videos/0002_vid.mp4', os.getenv('HOME') + '/Temp/'])
#subprocess.run(['rclone', 'copy', 'cichlidVideo:BioSci-McGrath/Apps/CichlidPiData/MC6_5/Videos/0002_vid.mp4', os.getenv('HOME') + '/Temp/'])

args = ['python3', 'VideoFocus.py']
args.extend(['--Movie_file', os.getenv('HOME') + '/Temp/0002_vid.mp4'])
args.extend(['--Num_workers', '24'])
args.extend(['--Log', os.getenv('HOME') + '/Temp/FullVideoHMM/FocusingLog.txt'])
args.extend(['--HMM_temp_directory', os.getenv('HOME') + '/Temp/FullVideoHMM/TempHMMFiles/'])
args.extend(['--HMM_filename', os.getenv('HOME') + '/Temp/FullVideoHMM/Test.hmm'])
args.extend(['--HMM_transition_filename', os.getenv('HOME') + '/Temp/FullVideoHMM/TestCoords.npy'])
args.extend(['--Cl_labeled_transition_filename', os.getenv('HOME') + '/Temp/FullVideoHMM/TestLabeledCoords.npy'])
args.extend(['--Cl_labeled_cluster_filename', os.getenv('HOME') + '/Temp/FullVideoHMM/TestClusters.csv'])
args.extend(['--Cl_videos_directory', os.getenv('HOME') + '/Temp/FullVideoHMM/AllClips'])
args.extend(['--ML_frames_directory', os.getenv('HOME') + '/Temp/FullVideoHMM/MLFrames'])
args.extend(['--ML_videos_directory', os.getenv('HOME') + '/Temp/FullVideoHMM/MLClips'])
args.extend(['--Video_start_time', '2018-05-12 08:03:20.913025'])
args.extend(['--Filter_start_time', '2018-05-12 08:00:00'])
args.extend(['--Filter_end_time', '2018-05-12 18:00:00'])
args.extend(['--VideoID', 'MC6_5-0002_vid'])

# subprocess.run(args)
