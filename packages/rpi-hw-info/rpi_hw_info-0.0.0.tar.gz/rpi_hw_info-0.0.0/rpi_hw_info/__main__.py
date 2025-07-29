import sys
import argparse
from . import __version__
from .detector import detect_and_print

def main():
	"""
	Main entry point for the CLI
	"""
	parser = argparse.ArgumentParser(description="Raspberry Pi Hardware Info Detector")
	parser.add_argument("--version", action="version", version=f"rpi-hw-info {__version__}")
	args = parser.parse_args()
	
	return detect_and_print()

if __name__ == '__main__':
	sys.exit(main())
