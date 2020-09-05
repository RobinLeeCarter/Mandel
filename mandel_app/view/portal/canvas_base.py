from __future__ import annotations
from typing import Optional
from abc import ABC, abstractmethod

import numpy as np

from matplotlib import figure
from matplotlib.backends import backend_qt5agg

# import utils
from mandel_app import tuples
from mandel_app.view.portal import drawable


class CanvasBase(ABC):
    """
    Renders a single axes to an rgba array.
    Does not need to be physically displayed on the screen but canvas.draw() still required.
    0.1s slower than direct input array to rgba array (using cmap) but thought to be worth it for consistency.
    """
    def __init__(self):
        self._fig: figure.Figure = figure.Figure(frameon=False, dpi=100.0)
        self._figure_canvas: backend_qt5agg.FigureCanvasQTAgg = backend_qt5agg.FigureCanvasQTAgg(self._fig)
        # Space around axes. Documentation not helpful. Taken from stack-overflow.
        self._fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        self._ax: figure.Axes = self._fig.subplots()
        self._drawable: Optional[drawable.Drawable] = None
        self._buf: Optional[memoryview] = None
        self._rgba_output: Optional[np.ndarray] = None
        self._current_shape: Optional[tuples.ImageShape] = None

        # self._timer = utils.Timer()

    @property
    def shape(self) -> tuples.ImageShape:
        return self._drawable.shape

    @property
    def rgba_output(self) -> np.ndarray:
        assert self._rgba_output is not None, "Canvas: _rgba is None"
        return self._rgba_output

    def set_drawable(self, drawable_: drawable.Drawable):
        self._drawable = drawable_
        self._drawable.set_ax(self._ax)

    @abstractmethod
    def draw(self):
        pass

    def _fig_size(self):
        new_shape = self.shape
        if self._current_shape is None or self._current_shape != new_shape:
            self._on_resize()
            self._current_shape = new_shape

    def _on_resize(self):
        width, height = self.shape
        width_inches: float = float(width) / 100.0
        height_inches: float = float(height) / 100.0
        self._fig.set_size_inches(width_inches, height_inches)
        # self._figure_canvas.resize(self._width, self._height)
