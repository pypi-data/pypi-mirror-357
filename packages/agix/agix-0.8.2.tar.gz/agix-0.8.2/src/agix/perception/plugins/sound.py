from .base import SensorPlugin
import numpy as np


class SoundPlugin(SensorPlugin):
    """Normaliza muestras de audio en arrays NumPy de flotantes."""

    def process(self, raw_input):
        data = np.asarray(raw_input, dtype=float)
        return data
