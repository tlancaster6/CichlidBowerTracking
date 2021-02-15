import argparse, os, cv2, math, datetime, subprocess, pdb, sys
import numpy as np
from HMMAnalyzer import HMMAnalyzer as HA


class HMM_calculator:
    def __init__(self, args):
        self.args = args
        self.workers = args.Num_workers  # Rename to make more readable
        self.output_directory = self.args.HMM_temp_directory  # Rename to make more readable
        if self.output_directory[-1] != '/':
            self.output_directory = self.output_directory + '/'

        self.row_command_arguments = []
        for key, value in vars(args).items():
            if 'HMM' in key:
                if 'filename' not in key and 'directory' not in key and 'time' not in key and 'blocksize' not in key:
                    self.row_command_arguments.extend(['--' + key, str(value)])

    def calculateHMM(self):
        self._validateVideo()
        self._decompressVideo()
        self._calculateHMM()
        self._createCoordinateFile()

    def _validateVideo(self):
        cap = cv2.VideoCapture(self.args.Movie_file)
        self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.framerate = int(cap.get(cv2.CAP_PROP_FPS))
        self.frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if self.args.Filter_start_time is not None and self.args.Filter_start_time > self.args.Video_start_time:
            self.start_time = int((self.args.Filter_start_time - self.args.Video_start_time).total_seconds())
        else:
            self.start_time = 0
        if self.args.Filter_end_time is not None:
            self.stop_time = int((self.args.Filter_end_time - self.args.Video_start_time).total_seconds())
        else:
            self.stop_time = int(self.frames / self.framerate) - 1

        self.HMMsecs = int(self.stop_time - self.start_time + 1)
        cap.release()

    def _decompressVideo(self):

        blocksize = self.args.HMM_blocksize * 60  # Rename to make code easier to read.

        totalBlocks = math.ceil(
            self.HMMsecs / (blocksize))  # Number of blocks that need to be analyzed for the full video
        print('  HMM_Maker:Decompressing video into 1 second chunks,,Time: ' + str(datetime.datetime.now()))
        print('    ' + str(totalBlocks) + ' total blocks. On block ', end='', flush=True)

        # First decompress mp4 file into managable chunks. One frame per second. blocksize is length of chunks in minutes
        for i in range(0, totalBlocks, self.workers):
            print(str(i) + '-' + str(min(i + self.workers, totalBlocks - 1)) + ',', end='', flush=True)
            processes = []
            for j in range(self.workers):
                if i + j >= totalBlocks:
                    break
                min_time = self.start_time + int((i + j) * blocksize)
                max_time = self.start_time + int(min((i + j + 1) * blocksize, self.HMMsecs))

                if max_time < min_time:
                    pdb.set_trace()
                command_stub = ['bash -c \"source activate CichlidBowerTracking; python']
                cmnd = command_stub + ['Utils/Decompress_block.py', self.args.Movie_file, str(self.framerate),
                                       str(min_time), str(max_time),
                                       self.output_directory + 'Decompressed_' + str(i + j) + '.npy']

                processes.append(subprocess.Popen(' '.join(cmnd) + '\"', shell=True))

            for p in processes:
                p.communicate()

        print()

        # Now combine the chunks together into separate row file. Separating by row keeps filesizes managable
        print('  Combining data into rowfiles,,Time: ' + str(datetime.datetime.now()))
        print('    ' + str(totalBlocks) + ' total blocks. On block: ', end='', flush=True)
        for i in range(0, totalBlocks, self.workers):
            print(str(i) + '-' + str(min(i + self.workers, totalBlocks - 1)) + ',', end='', flush=True)
            data = []
            for j in range(self.workers):
                block = i + j
                if block >= totalBlocks:
                    break

                data.append(np.load(self.output_directory + 'Decompressed_' + str(block) + '.npy'))

            alldata = np.concatenate(data, axis=2)

            for row in range(self.height):
                row_file = self.output_directory + str(row) + '.npy'
                out_data = alldata[row]
                if os.path.isfile(row_file):
                    out_data = np.concatenate([np.load(row_file), out_data], axis=1)
                np.save(row_file, out_data)
                # Verify size is right
                if block + 1 == totalBlocks:
                    try:
                        assert out_data.shape == (self.width, self.HMMsecs)
                    except AssertionError:
                        pdb.set_trace()

            for j in range(self.workers):
                block = i + j
                subprocess.run(['rm', '-f', self.output_directory + 'Decompressed_' + str(block) + '.npy'])
        print()

    def _calculateHMM(self):
        print('  Calculating HMMs for each row,,Time: ' + str(datetime.datetime.now()))
        # Calculate HMM on each block

        print('    ' + str(self.height) + ' total rows. On rows ', end='', flush=True)

        for i in range(0, self.height, self.workers):
            start_row = i
            stop_row = min((i + self.workers, self.height))
            print(str(start_row) + '-' + str(stop_row - 1) + ',', end='', flush=True)
            processes = []
            for row in range(start_row, stop_row):
                command_stub = ['bash -c \"source activate CichlidBowerTracking; python']
                cmnd = command_stub + ['Utils/HMM_row.py', '--Rowfile', self.output_directory + str(row) + '.npy'] + \
                       self.row_command_arguments
                cmnd = ' '.join(cmnd) + '\"'
                processes.append(subprocess.Popen(cmnd, shell=True))
            for p in processes:
                p.communicate()
        print()
        all_data = []
        # Concatenate all data together
        for row in range(self.height):
            all_data.append(np.load(self.output_directory + str(row) + '.hmm.npy'))
            subprocess.run(['rm', '-f', self.output_directory + str(row) + '.hmm.npy'])
        out_data = np.concatenate(all_data, axis=0)

        # Correct start time and end time
        out_data[:, 0] += self.start_time
        out_data[:, 1] += self.start_time

        # Save npy and txt files for future use
        np.save(self.args.HMM_filename + '.npy', out_data)
        with open(self.args.HMM_filename + '.txt', 'w') as f:
            print('Width: ' + str(self.width), file=f)
            print('Height: ' + str(self.height), file=f)
            print('Frames: ' + str(int(self.HMMsecs * self.framerate)), file=f)
            print('FrameRate: ' + str(int(self.framerate)), file=f)
            print('StartTime: ' + str(self.args.Video_start_time), file=f)
            for key, value in vars(self.args).items():
                if value is not None:
                    print(key + ': ' + str(value), file=f)
            print('PythonVersion: ' + sys.version.replace('\n', ' '), file=f)
            print('NumpyVersion: ' + np.__version__, file=f)
            import hmmlearn
            print('HMMLearnVersion: ' + hmmlearn.__version__, file=f)
            import scipy
            print('ScipyVersion: ' + scipy.__version__, file=f)
            print('OpenCVVersion: ' + cv2.__version__, file=f)

    def _createCoordinateFile(self):
        print('  Creating coordinate file from HMM transitions,,Time: ' + str(datetime.datetime.now()))

        # Load in HMM data
        hmmObj = HA(self.args.HMM_filename)

        # Convert into coords object and save it
        coords = hmmObj.retDBScanMatrix()
        np.save(self.args.HMM_transition_filename, coords)


parser = argparse.ArgumentParser(description='This script calculates an HMM for a single video')

parser.add_argument('--Movie_file', type=str, required=True, help='Name of movie file to analyze. Must be .mp4 video')
parser.add_argument('--Num_workers', type=int, default=1,
                    help='Transition magnitude to be included in cluster analysis')

# Temp directories that wlil be deleted at the end of the analysis
parser.add_argument('--HMM_temp_directory', type=str, required=True,
                    help='Location for temp files to be stored. Should not be in a location that is automatically synced (e.g. Dropbox folder)')

# Output data
parser.add_argument('--HMM_filename', type=str, required=True,
                    help='Basename of output HMM files. ".txt" and ".npy" will be added to basename')
parser.add_argument('--HMM_transition_filename', type=str, required=True,
                    help='Name of npy file containing all transitions with associated magnitude')

# Parameters to filter when HMM is run on
parser.add_argument('--VideoID', type=str, required=True, help='Required argument that gives a short ID for the video')
parser.add_argument('--Video_start_time', type=datetime.datetime.fromisoformat, required=True,
                    help='Required argument that indicates the start time of the video')
parser.add_argument('--Filter_start_time', type=datetime.datetime.fromisoformat,
                    help='Optional argument that indicates the start time when the Clusters should be run')
parser.add_argument('--Filter_end_time', type=datetime.datetime.fromisoformat,
                    help='Optional argument that indicates the start time when the Clusters should be run')

# Parameters for calculating HMM 
parser.add_argument('--HMM_blocksize', type=int, default=5,
                    help='Blocksize (in minutes) to decompress video for hmm analysis')
parser.add_argument('--HMM_mean_window', type=int, default=120,
                    help='Number of seconds to calculate mean over for filtering out large pixel changes for hmm analysis')
parser.add_argument('--HMM_mean_filter', type=float, default=7.5,
                    help='Grayscale change in pixel value for filtering out large pixel changes for hmm analysis')
parser.add_argument('--HMM_window', type=int, default=10, help='Used to reduce the number of states for hmm analysis')
parser.add_argument('--HMM_seconds_to_change', type=float, default=1800,
                    help='Used to determine probablility of state transition in hmm analysis')
parser.add_argument('--HMM_non_transition_bins', type=float, default=2,
                    help='Used to prevent small state transitions in hmm analysis')
parser.add_argument('--HMM_std', type=float, default=100, help='Standard deviation of pixel data in hmm analysis')

args = parser.parse_args()

hmm_obj = HMM_calculator(args)
hmm_obj.calculateHMM()
