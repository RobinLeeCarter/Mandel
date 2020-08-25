from __future__ import annotations
from typing import Optional

import numpy as np
import cupy as cp

from matplotlib import cm, colors

# import utils
from mandel_app import tuples
from mandel_app.model import mandelbrot


class Transform:
    def __init__(self,):
        # input array and any offset
        self._iteration: Optional[cp.ndarray] = None
        self._offset: tuples.PixelPoint = tuples.PixelPoint(0, 0)

        # self._norm = colors.Normalize(vmin=0, vmax=1)
        self._cmap: colors.Colormap = cm.get_cmap("hot")

        # source data from model converted into an rgba array
        self._source_rgba: Optional[cp.ndarray] = None

        # frame arrays that only change when window is resized
        self._frame_shape: Optional[tuples.ImageShape] = None
        self._frame_pixels: Optional[cp.ndarray] = None
        self._frame_to_source_fp32: Optional[cp.ndarray] = None
        self._frame_to_source_int32: Optional[cp.ndarray] = None

        # self._zero_uint: cp.ndarray = cp.zeros(shape=(4,), dtype=cp.uint8)
        self.frame_rgba: Optional[cp.ndarray] = None

        self._identity_matrix: cp.ndarray = cp.array([[1.0, 0.0], [0.0, 1.0]], dtype=cp.float32)
        self._null_vector: cp.ndarray = cp.array([0.0, 0.0], dtype=cp.float32)

        self._transform_matrix: cp.ndarray = cp.copy(self._identity_matrix)
        self._transform_vector: cp.ndarray = cp.copy(self._null_vector)
        self._do_matrix: bool = False
        self._do_vector: bool = False

        # whether image_rgba is fully updated or not
        self.updated: bool = False

    def set_cmap(self, cmap: colors.Colormap):
        self._cmap = cmap
        self.updated = False

    def set_frame_shape(self, frame_shape: tuples.ImageShape):
        self._frame_shape = frame_shape

        _y_pixels = self._frame_shape.y
        _x_pixels = self._frame_shape.x

        self._frame_pixels = cp.zeros(shape=(_y_pixels, _x_pixels, 2), dtype=cp.float32)

        y_range = cp.arange(start=0, stop=_y_pixels, dtype=cp.float32)
        x_range = cp.arange(start=0, stop=_x_pixels, dtype=cp.float32)

        # for 3D array: 0 is x, 1 is y
        self._frame_pixels[:, :, 1], self._frame_pixels[:, :, 0] = cp.meshgrid(y_range, x_range, indexing='ij')
        # print(f"self._frame_pixels.shape: {self._frame_pixels.shape}")
        # print(self._frame_pixels)

        self._frame_to_source_fp32 = cp.zeros(shape=(_y_pixels, _x_pixels), dtype=cp.float32)
        self._frame_to_source_int32 = cp.zeros(shape=(_y_pixels, _x_pixels), dtype=cp.int32)
        self.frame_rgba = cp.zeros(shape=(_y_pixels, _x_pixels, 4), dtype=cp.uint8)
        self.updated = False

    def set_mandel(self, mandel: mandelbrot.Mandel):
        self._offset = mandel.offset
        self._iteration = cp.asarray(mandel.iteration)
        mod_log_iterations = cp.mod(cp.log10(1 + self._iteration), 1)
        mod_log_iterations[self._iteration == mandel.max_iteration] = 0
        mod_log_iterations_np = cp.asnumpy(mod_log_iterations)
        # self._norm.autoscale(mod_log_iterations)
        # normalised = self._norm(mod_log_iteration)
        source_rgba_np = self._cmap(mod_log_iterations_np, bytes=True)
        self._source_rgba = cp.asarray(source_rgba_np)
        # print(f"self._source_rgba.shape: {self._source_rgba.shape}")
        # print(self._source_rgba)

        self._transform_matrix: cp.ndarray = cp.copy(self._identity_matrix)
        self._transform_vector: cp.ndarray = cp.copy(self._null_vector)
        self._do_matrix: bool = False
        self._do_vector: bool = False

        self.updated = False

    def pan(self, pan: tuples.PixelPoint) -> np.ndarray:
        self._transform_vector = cp.asarray([-self._offset.x + pan.x,
                                            -self._offset.y + pan.y],
                                            dtype=cp.float32)
        self._do_matrix = False
        self._do_vector = True
        self.updated = False
        return self.get_frame()

    def get_frame(self) -> np.ndarray:
        self._apply_transform()
        self._frame_to_source_int32 = cp.rint(self._frame_to_source_fp32).astype(cp.int32)
        # print(f"self._frame_to_source_int32.shape: {self._frame_to_source_int32.shape}")
        # print(self._frame_to_source_int32)

        # for 3D array: 0 is x, 1 is y
        frame_x = self._frame_to_source_int32[:, :, 0]  # x pixel in source
        frame_y = self._frame_to_source_int32[:, :, 1]  # y pixel in source

        source_y_shape: int = self._source_rgba.shape[0]
        source_x_shape: int = self._source_rgba.shape[1]
        # boolean 2-D array of frame pixels that map to a pixel on the source
        # will be false if the pixel on source would fall outside of source
        mapped = (frame_y >= 0) & (frame_y < source_y_shape) & (frame_x >= 0) & (frame_x < source_x_shape)
        # print(f"mapped.shape: {mapped.shape}")
        # print(f"mapped count_nonzero: {cp.count_nonzero(mapped)}")

        _y_pixels: int = self._frame_shape.y
        _x_pixels: int = self._frame_shape.x
        self.frame_rgba = cp.zeros(shape=(_y_pixels, _x_pixels, 4), dtype=cp.uint8)
        self.frame_rgba[mapped, :] = self._source_rgba[frame_y[mapped], frame_x[mapped], :]
        # self.image_rgba[~mapped, :] = self._zero_uint     probably slower than just zeroing everything

        # print(f"self._frame_rgba.shape: {self.frame_rgba.shape}")
        # print(f"frame_rgba count_nonzero: {cp.count_nonzero(self.frame_rgba)}")
        # print(self.frame_rgba)

        self.updated = True
        return cp.asnumpy(self.frame_rgba)

    def _apply_transform(self):
        # create self._frame_to_source_int32
        if self._do_matrix:
            if self._do_vector:
                self._frame_to_source_fp32 = cp.matmul(self._frame_pixels, self._transform_matrix.T)\
                                             + self._transform_vector
            else:
                self._frame_to_source_fp32 = cp.matmul(self._frame_pixels, self._transform_matrix.T)
        else:
            if self._do_vector:
                self._frame_to_source_fp32 = self._frame_pixels + self._transform_vector
            else:
                self._frame_to_source_fp32 = self._frame_pixels
