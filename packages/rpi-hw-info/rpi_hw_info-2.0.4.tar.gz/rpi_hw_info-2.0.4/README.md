# Raspberry Pi Hardware Info Detector

A Python tool to detect Raspberry Pi hardware information, including model name, CPU and FPU targets.

## Installation

### From PyPI

```bash
pipx install rpi-hw-info
```

### From Source

```bash
git clone https://github.com/username/rpi-hw-info.git
cd rpi-hw-info
pip install .
```

## Usage

### As a Command-Line Tool

```bash
# Run directly
rpi-hw-info

# Show version
rpi-hw-info --version

# Use in shell scripts
CPU_TARGET=$(rpi-hw-info | awk -F ':' '{print $3}')
gcc -mtune=${CPU_TARGET} ...
```

### As a Python Package

```python
from rpi_hw_info import detect_rpi_model

# Get RPi model information
rpi_model = detect_rpi_model()

# Access model properties
print(f"Model: {rpi_model.model_name}")
print(f"CPU Target: {rpi_model.cpu_target}")
print(f"FPU Target: {rpi_model.fpu_target}")

# Get package version
from rpi_hw_info import __version__
print(f"Package version: {__version__}")
```

## Output Format

The command-line tool outputs a colon (`:`)-separated list of data to stdout:

Example:

```
3B+:0xd:cortex-a53:neon-fp-armv8
```

| Column # | Contents                   | Example       |
| -------- | -------------------------- | ------------- |
| 1        | Short human-readable model | 3B+           |
| 2        | Hexadecimal model ID       | 0xd           |
| 3        | CPU target                 | cortex-a53    |
| 4        | FPU target                 | neon-fp-armv8 |

## Error Handling

If the hardware info cannot be detected, an error message will be printed to stderr and the process will exit with a non-zero status code.


## Technical Details

Detection is based on decoding the hardware "revision" per the [Raspberry Pi Documentation](https://www.raspberrypi.org/documentation/hardware/raspberrypi/revision-codes/README.md).

## Developer Guide

### Versioning

This project uses Semantic Versioning with automatic version calculation based on [Conventional Commits](https://www.conventionalcommits.org/).

Version numbers are automatically calculated based on commit messages:
- `fix:` commits increment the patch version (0.0.X)
- `feat:` commits increment the minor version (0.X.0)
- Commits with `BREAKING CHANGE:` in the description increment the major version (X.0.0)

### Release Process

Commits pushed to the master branch are automatically analyzed, and if there are unreleased changes:
1. The version is automatically incremented according to Conventional Commits
2. A new GitHub release is created
3. The package is automatically published to PyPI

No manual version management is needed - just write proper commit messages!

## Publishing to PyPI

This project uses GitHub Actions to automatically publish releases to PyPI using [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/).
