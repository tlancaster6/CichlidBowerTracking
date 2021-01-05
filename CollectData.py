import argparse
from Modules.Tracking.CichlidTracker import CichlidTracker as CT

parser = argparse.ArgumentParser(help='This command starts a script on a Raspberry Pis to collect depth and RGB data. Allows control through a Google Spreadsheet.')

args = parser.parse_args()
	
CT()
