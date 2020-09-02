from typing import Optional

import numpy as np
import cupy as cp

from mandel_app import tuples
from mandel_app.view.portal import transform


class Frame:
    def __init__(self):
        # arrays are all cupy arrays unless prefixed np_

        self._source: Optional[cp.ndarray] = None
        self.offset: tuples.PixelPoint = tuples.PixelPoint(0, 0)

        # portal arrays that only change when window is resized
        self.shape: Optional[tuples.ImageShape] = None
        self._frame_pixels: Optional[cp.ndarray] = None
        self._frame_to_source_fp32: Optional[cp.ndarray] = None
        self._frame_to_source_int32: Optional[cp.ndarray] = None
        self._frame_rgba: Optional[cp.ndarray] = None
        self._np_frame_rgba: Optional[np.ndarray] = None

        self._pan: tuples.PixelPoint = tuples.PixelPoint(0, 0)
        self._rotation_degrees: float = 0.0
        self._scale: float = 1.0
        self._scale_point: tuples.PixelPoint = tuples.PixelPoint(0, 0)

        self._transform_matrix: Optional[cp.ndarray] = None
        self._transform_vector: Optional[cp.ndarray] = None

    @property
    def result_rgba(self) -> np.ndarray:
        return self._np_frame_rgba

    def set_frame_shape(self, image_shape: tuples.ImageShape):
        """call when resize window"""
        self.shape = image_shape
        # self.shape = tuples.ImageShape(800, 800)
        frame_y = self.shape.y
        frame_x = self.shape.x

        self._frame_pixels = cp.zeros(shape=(frame_y, frame_x, 2), dtype=cp.float32)

        y_range = cp.arange(start=0, stop=frame_y, dtype=cp.float32)
        x_range = cp.arange(start=0, stop=frame_x, dtype=cp.float32)

        # for 3D array: 0 is x, 1 is y
        # noinspection PyTypeChecker
        self._frame_pixels[:, :, 1], self._frame_pixels[:, :, 0] = cp.meshgrid(y_range, x_range, indexing='ij')
        # print(f"self._frame_pixels.shape: {self._frame_pixels.shape}")
        # print(self._frame_pixels)

        self._frame_to_source_fp32 = cp.zeros(shape=(frame_y, frame_x), dtype=cp.float32)
        self._frame_to_source_int32 = cp.zeros(shape=(frame_y, frame_x), dtype=cp.int32)
        self._frame_rgba = cp.zeros(shape=(frame_y, frame_x, 4), dtype=cp.uint8)

    # def set_source(self, source: np.ndarray, offset: Optional[tuples.PixelPoint] = None):
    #     """call when change the source"""
    #     self._source = cp.asarray(source)
    #     if offset is not None:
    #         self.offset = offset
    #     self._reset_transform()

    def set_source(self, source: np.ndarray):
        """call when change the source"""
        self._source = cp.asarray(source)
        self._reset_transform()

    def set_offset(self, offset: Optional[tuples.PixelPoint]):
        """call when change the source"""
        self.offset = offset
        # self._reset_transform()

    def plain(self):
        self.get_frame()

    def pan(self, pan: tuples.PixelPoint):
        self._pan = pan
        self.get_frame()

    def rotate(self, rotation_degrees: float):
        self._rotation_degrees = rotation_degrees
        self.get_frame()

    # TODO: scale a point for actual zooming, possibly pan (from center) + scale
    def scale(self, scale: float, scale_point: Optional[tuples.PixelPoint] = None):
        self._scale = scale
        self._scale_point = scale_point
        self.get_frame()

    def get_frame(self):
        # print("get_frame")
        self._calculate_transform()
        self._apply_transform()
        # TODO: double conversion?
        self._frame_to_source_int32 = cp.rint(self._frame_to_source_fp32).astype(cp.int32)
        # if self.offset.x < 0:
        #     print(f"self._frame_to_source_int32.shape: {self._frame_to_source_int32.shape}")
        #     print(self._frame_to_source_int32)

        # for 3D array: 0 is x, 1 is y
        frame_x = self._frame_to_source_int32[:, :, 0]  # 2D array of x pixel in source
        frame_y = self._frame_to_source_int32[:, :, 1]  # 2D array of y pixel in source

        source_y_shape: int = self._source.shape[0]
        source_x_shape: int = self._source.shape[1]
        # boolean 2-D array of portal pixels that map to a pixel on the source
        # will be false if the pixel on source would fall outside of source
        mapped = (frame_y >= 0) & (frame_y < source_y_shape) & \
                 (frame_x >= 0) & (frame_x < source_x_shape)
        # if self.offset.x < 0:
        #     print(f"mapped.shape: {mapped.shape}")
        #     print(mapped)
        # print(f"mapped count_nonzero: {cp.count_nonzero(mapped)}")

        frame_y_size: int = self.shape.y
        frame_x_size: int = self.shape.x
        self._frame_rgba = cp.zeros(shape=(frame_y_size, frame_x_size, 4), dtype=cp.uint8)
        self._frame_rgba[mapped, :] = self._source[frame_y[mapped], frame_x[mapped], :]
        # self.image_rgba[~mapped, :] = self._zero_uint     probably slower than just zeroing everything first

        self._np_frame_rgba = cp.asnumpy(self._frame_rgba)

        # print(f"self._frame_rgba.shape: {self.frame_rgba.shape}")
        # print(f"frame_rgba count_nonzero: {cp.count_nonzero(self.frame_rgba)}")
        # print(self.frame_rgba)

        # return self.np_frame_rgba

    # noinspection PyPep8Naming,PyPep8
    def _calculate_transform(self):
        """takes 0.0001s"""
        # for readability
        # functions
        identity = transform.Transform.identity
        flip_y = transform.Transform.flip_y
        translate = transform.Transform.translate
        scale = transform.Transform.scale
        rotate_degrees = transform.Transform.rotate_degrees

        # values
        # source_x = float(self._source.shape[1])
        source_y = float(self._source.shape[0])
        frame_x = float(self.shape.x)
        frame_y = float(self.shape.y)
        # cartesian offset when source and portal were first generated, x and y are both positive
        offset_x = float(self.offset.x)
        offset_y = float(self.offset.y)

        # goal is to get from frame_image co-ordinates to transformed source_image co-ordinates
        # want to do all the transforms in portal cartesian co-ordinates
        # path portal-image -> portal-cartesian -> portal-cartesian-transformed -> source-cartesian -> source-image

        # can't directly chain transforms.Affine2D so just deal in matrices

        # x unchanged, flip y (inverse of itself)

        frame_image_to_frame_cartesian = flip_y(frame_y)

        if self._rotation_degrees != 0.0:
            center_x, centre_y = frame_x * 0.5, frame_y * 0.5
            # 1) move center to origin
            # 2) rotate
            # 3) move origin back to center
            # so in reserve order:
            frame_transform = translate(center_x, centre_y) @ \
                rotate_degrees(self._rotation_degrees) @ \
                translate(-center_x, -centre_y)

        elif self._scale != 1.0:
            center_x, centre_y = frame_x * 0.5, frame_y * 0.5
            # 1) move scale_point to origin
            # 2) scale
            # 3) move origin back to center
            # so in reserve order:
            frame_transform = translate(self._scale_point.x, self._scale_point.y) @ \
                scale(self._scale) @ \
                translate(-center_x, -centre_y)

        elif self._pan != tuples.PixelPoint(0, 0):
            frame_transform = translate(self._pan.x, self._pan.y)

        else:
            frame_transform = identity()

        frame_cartesian_to_source_cartesian = translate(offset_x, offset_y)

        # x unchanged, flip y (inverse of itself)
        source_cartesian_to_source_image = flip_y(source_y)

        # combine matrices using multiplication, so in reserve order:
        frame_image_to_source_image = source_cartesian_to_source_image @ \
            frame_cartesian_to_source_cartesian @ \
            frame_transform @ \
            frame_image_to_frame_cartesian

        # if offset_x < 0:
        #     self.print_transform("frame_image_to_frame_cartesian", frame_image_to_frame_cartesian)
        #     self.print_transform("frame_transform", frame_transform)
        #     self.print_transform("frame_cartesian_to_source_cartesian", frame_cartesian_to_source_cartesian)
        #     self.print_transform("source_cartesian_to_source_image", source_cartesian_to_source_image)
        #     self.print_transform("frame_image_to_source_image", frame_image_to_source_image)

        np_matrix = frame_image_to_source_image[0:2, 0:2]
        np_vector = frame_image_to_source_image[0:2, 2]

        # print(t)

        self._transform_matrix = cp.asarray(np_matrix, dtype=cp.float32)
        self._transform_vector = cp.asarray(np_vector, dtype=cp.float32)

        # self._transform_matrix = cp.asarray(I, dtype=cp.float32)
        # self._transform_vector = cp.asarray(Frame.zero_vector, dtype=cp.float32)

    def print_transform(self, desc: str, array: np.ndarray):
        print(desc + "\n", np.rint(array).astype(cp.int32))

    def _reset_transform(self):
        self._pan = tuples.PixelPoint(0, 0)
        self._rotation_degrees = 0
        self._scale = 1.0
        self._scale_point = tuples.PixelPoint(0, 0)

    def _apply_transform(self):
        # print(f"self._frame_pixels.shape: {self._frame_pixels.shape}")
        # print(f"self._transform_vector: {self._transform_vector}")
        self._frame_to_source_fp32 = cp.matmul(self._frame_pixels, self._transform_matrix.T) \
                                     + self._transform_vector
