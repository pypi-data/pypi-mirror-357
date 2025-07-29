class RPIModel:
	def __init__(self, model_name, model_id, cpu_target, fpu_target):
		"""Create a representation of a Raspberry Pi hardware

		Arguments:
		model_name -- the human-readable model name, e.g. "3B"
		model_id   -- Hexadecimal identifier for the RPi model; see https://www.raspberrypi.org/documentation/hardware/raspberrypi/revision-codes/README.md
		cpu_target -- the gcc cpu target to -mtune to
		fpu_target -- the gcc fpu target to -mfpu to
		"""

		self.model_name = model_name
		self.model_id = model_id
		self.cpu_target = cpu_target
		self.fpu_target = fpu_target

	def __repr__(self):
		return self.model_name + ":" + hex(self.model_id) + ":" + self.cpu_target + ":" + self.fpu_target


# List of supported Raspberry Pi models
RPI_MODELS = [
	RPIModel("3B", int("0x8", 16), "cortex-a53", "neon-fp-armv8"),
	RPIModel("3B+", int("0xd", 16), "cortex-a53", "neon-fp-armv8"),
	RPIModel("4B", int("0x11", 16), "cortex-a72", "neon-fp-armv8")
]
