import argparse, sys
from cichlid_bower_tracking.helper_modules.cichlid_tracker import CichlidTracker as CT
sys.path.append('/home/pi/CichlidBowerTracking')

parser = argparse.ArgumentParser(usage='This command starts a script on a Raspberry Pis to collect depth and RGB data. Allows control through a Google Spreadsheet.')

args = parser.parse_args()
	
CT()
