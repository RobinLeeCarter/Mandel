from abc import ABC, abstractmethod
from typing import Optional

import numpy as np
from matplotlib import figure


class Drawable(ABC):
    def __init__(self):
        self.width: int = 0
        self.height: int = 0
        self._ax: Optional[figure.Axes] = None

    def set_ax(self, ax: figure.Axes):
        self._ax = ax

    @abstractmethod
    def draw(self):
        pass

    def _adopt_shape(self, data: np.ndarray):
        self.height, self.width = data.shape
