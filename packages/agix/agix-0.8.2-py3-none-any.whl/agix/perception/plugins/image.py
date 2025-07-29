from .base import SensorPlugin
import numpy as np


class ImagePlugin(SensorPlugin):
    """Convierte listas de píxeles en arrays NumPy."""

    def process(self, raw_input):
        return np.asarray(raw_input)
