from abc import ABC, abstractmethod
from typing import Optional

import numpy as np
from matplotlib import figure

from mandel_app import tuples


class Drawable(ABC):
    def __init__(self):
        # self.width: int = 0
        # self.height: int = 0
        # self.offset: tuples.PixelPoint = tuples.PixelPoint(0, 0)
        self._ax: Optional[figure.Axes] = None

    @property
    @abstractmethod
    def shape(self) -> Optional[tuples.ImageShape]:
        pass

    # @property
    # @abstractmethod
    # def offset(self) -> Optional[tuples.PixelPoint]:
    #     pass

    def set_ax(self, ax: figure.Axes):
        self._ax = ax

    @abstractmethod
    def draw_source(self):
        pass

    # def update(self):
    #     """Maybe extend to use animation in future"""
    #     self.draw()

    def _get_shape(self, data: np.ndarray):
        height, width = data.shape
        return tuples.ImageShape(x=width, y=height)

    # def _adopt_shape(self, data: np.ndarray):
    #     self.height, self.width = data.shape
