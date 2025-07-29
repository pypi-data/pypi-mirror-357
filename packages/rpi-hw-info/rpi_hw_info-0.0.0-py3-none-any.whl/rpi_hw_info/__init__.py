__version__ = '2.0.0'

from .models import RPIModel, RPI_MODELS
from .detector import detect_rpi_model, detect_and_print

__all__ = ['RPIModel', 'RPI_MODELS', 'detect_rpi_model', 'detect_and_print']
