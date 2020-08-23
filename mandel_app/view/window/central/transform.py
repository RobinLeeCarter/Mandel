from __future__ import annotations
from typing import Optional

import numpy as np

from matplotlib import cm, colors

# import utils
from mandel_app import tuples
from mandel_app.model import mandelbrot


class Transform:
    def __init__(self,):
        # input array and any offset
        self._iteration: Optional[np.ndarray] = None
        self._offset: tuples.PixelPoint = tuples.PixelPoint(0, 0)
        # normalised and color-ready input array
        self._source: Optional[np.ndarray] = None

        # self._norm = colors.Normalize(vmin=0, vmax=1)
        self._cmap: colors.Colormap = cm.get_cmap("hot")

        # frame arrays that only change when window is resized
        self._frame_shape: Optional[tuples.ImageShape] = None
        self._frame_pixels: Optional[np.ndarray] = None
        self._frame_to_source_fp32: Optional[np.ndarray] = None
        self._frame_to_source_int32: Optional[np.ndarray] = None

        self._zero_uint: np.ndarray = np.zeros(shape=(4,), dtype=np.uint8)
        self.image_rgba: Optional[np.ndarray] = None

        self._identity_matrix: np.ndarray = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
        self._null_vector: np.ndarray = np.array([0.0, 0.0], dtype=np.float32)

        self._transform_matrix: np.ndarray = np.copy(self._identity_matrix)
        self._transform_vector: np.ndarray = np.copy(self._null_vector)
        self._do_matrix: bool = False
        self._do_vector: bool = False

        # whether image_rgba is fully updated or not
        self.updated: bool = False

    def set_cmap(self, cmap: colors.Colormap):
        self._cmap = cmap
        self.updated = False

    def set_mandel(self, mandel: mandelbrot.Mandel):
        self._offset = mandel.offset
        self._iteration = mandel.iteration
        self._source = np.mod(np.log10(1 + self._iteration), 1)
        # self._norm.autoscale(mod_log_iterations)
        # self._source = self._norm(mod_log_iteration)
        self._source[self._iteration == mandel.max_iteration] = 0
        self.updated = False

    def set_frame_shape(self, frame_shape: tuples.ImageShape):
        self._frame_shape = frame_shape

        _x_pixels = self._frame_shape.x
        _y_pixels = self._frame_shape.y

        self._frame_pixels = np.zeros(shape=(_y_pixels, _x_pixels, 2), dtype=np.float32)

        x_range = np.arange(start=0, stop=_x_pixels, dtype=np.float32)
        y_range = np.arange(start=0, stop=_y_pixels, dtype=np.float32)

        self._frame_pixels[:, :, 1], self._frame_pixels[:, :, 0] = np.meshgrid(y_range, x_range, indexing='ij')

        self._frame_to_source_fp32 = np.zeros(shape=(_y_pixels, _x_pixels), dtype=np.float32)
        self._frame_to_source_int32 = np.zeros(shape=(_y_pixels, _x_pixels), dtype=np.int32)
        self.image_rgba = np.zeros(shape=(_y_pixels, _x_pixels, 4), dtype=np.uint8)
        self.updated = False

    def pan(self, pan: tuples.PixelPoint) -> np.ndarray:
        self._transform_vector = [-self._offset.x - pan.x,
                                  -self._offset.y - pan.y]
        self._do_matrix = False
        self._do_vector = True
        self.updated = False
        return self.apply_transform()

    def apply_transform(self) -> np.ndarray:
        # create self._frame_to_source_int32
        if self._do_matrix:
            if self._do_vector:
                self._frame_to_source_fp32 = np.matmul(self._frame_pixels, self._transform_matrix.T)\
                                             + self._transform_vector
            else:
                self._frame_to_source_fp32 = np.matmul(self._frame_pixels, self._transform_matrix.T)
        else:
            self._frame_to_source_fp32 = self._frame_pixels + self._transform_vector
        self._frame_to_source_int32 = np.rint(self._frame_to_source_fp32).astype(np.int32)
        frame_x = self._frame_to_source_int32[:, :, 0]
        frame_y = self._frame_to_source_int32[:, :, 1]

        source_y_shape: int = self._source.shape[0]
        source_x_shape: int = self._source.shape[1]

        _x_pixels: int = self._frame_shape.x
        _y_pixels: int = self._frame_shape.y

        # boolean 2-D array
        mapped = (frame_x >= 0.0) & (frame_x < source_x_shape) & (frame_y >= 0.0) & (frame_y < source_y_shape)

        self.image_rgba = np.zeros(shape=(_y_pixels, _x_pixels, 4), dtype=np.uint8)
        self.image_rgba[mapped, :] = self._source[frame_y[mapped], frame_x[mapped], :]
        # self.image_rgba[~mapped, :] = self._zero_uint     probably slower than just zeroing everything

        self.updated = True
        return self.image_rgba
