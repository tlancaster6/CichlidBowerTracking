import argparse
from Modules.CichlidTracker import CichlidTracker as CT

parser = argparse.ArgumentParser(usage='This command starts a script on a Raspberry Pis to collect depth and RGB data. Allows control through a Google Spreadsheet.')

args = parser.parse_args()
	
CT()
