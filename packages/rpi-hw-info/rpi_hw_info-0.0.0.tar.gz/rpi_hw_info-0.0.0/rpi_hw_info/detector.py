import subprocess
import sys

from .models import RPIModel, RPI_MODELS

def detect_rpi_model():
	"""
	Detect the Raspberry Pi model by reading /proc/cpuinfo
	
	Returns:
		RPIModel: The detected Raspberry Pi model or None if not detected
	
	Raises:
		SystemExit: If the revision format is not supported or model is not recognized
	"""
	cpuinfo = subprocess.Popen(["cat", "/proc/cpuinfo"], stdout=subprocess.PIPE)

	if not cpuinfo or not cpuinfo.stdout:
		sys.exit("Could not read /proc/cpuinfo")
	
	# see https://www.raspberrypi.org/documentation/hardware/raspberrypi/revision-codes/README.md
	revision_format_bitmask = int("0x800000", 16)
	model_id_bitmask = int("0xFF0", 16)
	
	for line in cpuinfo.stdout:
		fields = line.strip().split()
		if fields and fields[0] == b"Revision":
			revision = fields[2]
			revision_hex = int(b"0x" + revision, 16)
			
			revision_format = (revision_hex & revision_format_bitmask) >> 23
			if revision_format == 0:
				sys.exit(revision.decode() + ": older revision format `" + str(revision_format) + "' is not supported.")
			
			model_id = (revision_hex & model_id_bitmask) >> 4
			for rpi in RPI_MODELS:
				if rpi.model_id == model_id:
					return rpi
	
	if 'revision' in locals():
		sys.exit(revision.decode() + ": unrecognized revision.")
	else:
		sys.exit("Could not find Revision in /proc/cpuinfo")

def detect_and_print():
	"""
	Detect the Raspberry Pi model and print the information
	"""
	rpi_model = detect_rpi_model()
	if rpi_model:
		print(str(rpi_model))
		return 0
	return 1
