from typing import Optional

import numpy as np
import cupy as cp

import thread
import utils
from mandel_app import tuples
from mandel_app.view.portal import transform


class Frame:
    def __init__(self):
        self._timer: utils.Timer = utils.Timer()
        self._calc_thread_state: Optional[thread.State] = None

        self._source_np: Optional[np.ndarray] = None
        self._source_cp: Optional[cp.ndarray] = None
        self.offset: tuples.PixelPoint = tuples.PixelPoint(0, 0)

        # portal arrays that only change when window is resized
        self.frame_shape: Optional[tuples.ImageShape] = None
        self._pan: tuples.PixelPoint = tuples.PixelPoint(0, 0)
        self._rotation_degrees: float = 0.0
        self._scale: float = 1.0
        self._scale_point: tuples.PixelPoint = tuples.PixelPoint(0, 0)

        self._use_gpu: bool = True

        # numpy transformations
        self._matrix: Optional[np.ndarray] = None
        self._vector: Optional[np.ndarray] = None
        self._source_frame_matrix: Optional[np.ndarray] = None
        self._source_frame_vector: Optional[np.ndarray] = None

        # numpy and cupy frame array (both prepared in advance)
        self._frame_pixels_np: Optional[np.ndarray] = None
        self._frame_pixels_cp: Optional[cp.ndarray] = None

        # result (GPU or CPU)
        self._frame_rgba: Optional[np.ndarray] = None

    @property
    def rgba(self) -> np.ndarray:
        return self._frame_rgba

    def set_calc_thread_state(self, calc_thread_state: thread.State):
        self._calc_thread_state = calc_thread_state

    def set_frame_shape(self, frame_shape: tuples.ImageShape):
        """call when resize window"""
        # print("set_frame_shape", image_shape)
        self.frame_shape = frame_shape
        frame_y = self.frame_shape.y
        frame_x = self.frame_shape.x

        self._frame_pixels_np = np.zeros(shape=(frame_y, frame_x, 2), dtype=np.float32)

        y_range = np.arange(start=0, stop=frame_y, dtype=np.float32)
        x_range = np.arange(start=0, stop=frame_x, dtype=np.float32)

        # for 3D array: 0 is x, 1 is y
        # noinspection PyTypeChecker
        self._frame_pixels_np[:, :, 1], self._frame_pixels_np[:, :, 0] = np.meshgrid(y_range, x_range, indexing='ij')
        self._frame_pixels_cp = cp.asarray(self._frame_pixels_np)

    def set_source(self, source: np.ndarray):
        """call when change the source"""
        self._source_np = source
        self._source_cp = cp.asarray(self._source_np)
        self._reset_transform()

    def set_offset(self, offset: Optional[tuples.PixelPoint]):
        """call when change the source"""
        self.offset = offset
        # self._reset_transform()

    def plain(self):
        self._get_frame_from_transform()

    def pan(self, pan: tuples.PixelPoint):
        self._pan = pan
        # print("Pan")
        # if not cp.cuda.get_current_stream().done:
        #     print("Stream.done: False")
        # if self._calc_thread_state.worker_active:
        #     print(f"Worker active: {self._calc_thread_state.worker_active}")
        self._get_frame_from_pan_slice()
        # self._get_frame_from_transform()

    def rotate(self, rotation_degrees: float):
        self._rotation_degrees = rotation_degrees
        # print("Rotate")
        # if not cp.cuda.get_current_stream().done:
        #     print("Stream.done: False")
        # if self._calc_thread_state.worker_active:
        #     print(f"Worker active: {self._calc_thread_state.worker_active}")
        self._get_frame_from_transform()

    def scale(self, scale: float, scale_point: tuples.PixelPoint):
        self._scale = scale
        self._scale_point = scale_point
        self._get_frame_from_transform()

    def _get_frame_from_transform(self):
        # print("_get_frame_from_transform")
        # print(f"_get_frame_from_transform frame.frame_shape:\t{self.frame_shape}")
        # self._timer.start()
        self._calculate_transform()
        # self._timer.lap("calc")

        stream_done = cp.cuda.get_current_stream().done
        worker_ready = not self._calc_thread_state.worker_active
        either_ready = stream_done or worker_ready

        # if worker_ready and not stream_done:
        #     print("worker_ready and not stream_done")
        # if stream_done and not worker_ready:
        #     print("stream_done and not worker_ready")

        # print(f"Stream.done: {stream_done}")
        # print(f"worker_ready: {worker_ready}")

        # if not stream_done:
        #     print(f"stream_done: {stream_done}")
        # if not worker_ready:
        #     print(f"worker_ready: {worker_ready}")

        # self._apply_transform_cp()

        # self._get_frame_from_pan_slice()
        # self._apply_transform_np()

        # self._timer.lap("apply")
        # self._timer.stop()

        # self._timer.start()

        if either_ready:
            # GPU ready so use that
            self._apply_transform_cp()
        else:
            # GPU not ready so fall back to CPU
            self._apply_transform_np()

        # self._timer.stop(show=False)
        # either_fps = 1.0/self._timer.total

        # if not (stream_done and worker_ready):
        #     print(f"stream_done: {stream_done}\t worker_ready: {worker_ready}\t either_fps FPS: {either_fps:.1f}")

        # self._timer.start()
        #
        # if worker_ready:
        #     # GPU ready so use that
        #     self._apply_transform_cp()
        # else:
        #     # GPU not ready so fall back to CPU
        #     self._apply_transform_np()
        #
        # self._timer.stop(show=False)
        # inactive_fps = 1.0/self._timer.total
        #
        # self._timer.start()
        #
        # if stream_done:
        #     # GPU ready so use that
        #     self._apply_transform_cp()
        # else:
        #     # GPU not ready so fall back to CPU
        #     self._apply_transform_np()
        #
        # self._timer.stop(show=False)
        # done_fps = 1.0 / self._timer.total

        # if done_fps < 100.0 or inactive_fps < 100.0:
        #     print(f"Inactive FPS: {inactive_fps:.1f}\t Done FPS: {done_fps:.1f}")

    # noinspection PyPep8Naming,PyPep8
    def _calculate_transform(self):
        """takes 0.0001s"""
        # purely numpy

        # functions
        identity = transform.Transform.identity
        flip_y = transform.Transform.flip_y
        translate = transform.Transform.translate
        scale = transform.Transform.scale
        rotate_degrees = transform.Transform.rotate_degrees

        # values
        # source_x = float(self._source.shape[1])
        source_y = float(self._source_np.shape[0])
        frame_x = float(self.frame_shape.x)
        frame_y = float(self.frame_shape.y)
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

        # final transform for frame_image to source_image
        self._matrix = frame_image_to_source_image[0:2, 0:2]
        self._vector = frame_image_to_source_image[0:2, 2]

        # source_point to frame_point transform
        source_cartesian_to_frame_cartesian = translate(-offset_x, -offset_y)
        inv_frame_transform = np.linalg.inv(frame_transform)
        # combine matrices using multiplication, so in reserve order:
        source_cartesian_to_frame_point = inv_frame_transform @ \
            source_cartesian_to_frame_cartesian
        self._source_frame_matrix = source_cartesian_to_frame_point[0:2, 0:2]
        self._source_frame_vector = source_cartesian_to_frame_point[0:2, 2]

    def source_to_transformed_frame(self, source_point: tuples.PixelPoint):
        # always uses numpy as just one point
        source_np = np.array([source_point.x, source_point.y], dtype=float)
        frame_np = np.matmul(self._source_frame_matrix, source_np) + self._source_frame_vector
        frame_point = tuples.PixelPoint(x=frame_np[0], y=frame_np[1])
        return frame_point

    def _reset_transform(self):
        self._pan = tuples.PixelPoint(0, 0)
        self._rotation_degrees = 0
        self._scale = 1.0
        self._scale_point = tuples.PixelPoint(0, 0)

    def _apply_transform_cp(self):
        source_shape_y: cp.int32 = cp.int32(self._source_cp.shape[0])
        source_shape_x: cp.int32 = cp.int32(self._source_cp.shape[1])
        frame_shape_y: cp.int32 = cp.int32(self.frame_shape.y)
        frame_shape_x: cp.int32 = cp.int32(self.frame_shape.x)

        matrix = cp.asarray(self._matrix, dtype=cp.float32)
        vector = cp.asarray(self._vector, dtype=cp.float32)
        frame_to_source_fp32 = cp.matmul(self._frame_pixels_cp, matrix.T) + vector
        frame_to_source_int32 = cp.rint(frame_to_source_fp32).astype(cp.int32)

        # for 3D array: 0 is x, 1 is y
        source_x = frame_to_source_int32[:, :, 0]  # 2D array of x pixel in source
        source_y = frame_to_source_int32[:, :, 1]  # 2D array of y pixel in source

        # boolean 2-D array of portal pixels that map to a pixel on the source
        # will be false if the pixel on source would fall outside of source
        mapped = (source_y >= 0) & (source_y < source_shape_y) & \
                 (source_x >= 0) & (source_x < source_shape_x)

        frame_rgba = cp.zeros(shape=(frame_shape_y, frame_shape_x, 4), dtype=cp.uint8)
        # if cp.all(mapped):
        #     frame_rgba[:, :] = self._source_cp[source_y, source_x, :]
        # else:
        #     frame_rgba[mapped, :] = self._source_cp[source_y[mapped], source_x[mapped], :]
        frame_rgba[mapped, :] = self._source_cp[source_y[mapped], source_x[mapped], :]
        # self.image_rgba[~mapped, :] = self._zero_uint     probably slower than just zeroing everything first

        self._frame_rgba = cp.asnumpy(frame_rgba)

    def _apply_transform_np(self):
        # takes about 0.025s
        # print("_apply_transform_np")
        # self._timer.start()

        source_shape_y: np.int32 = np.int32(self._source_np.shape[0])
        source_shape_x: np.int32 = np.int32(self._source_np.shape[1])
        frame_shape_y: np.int32 = np.int32(self.frame_shape.y)
        frame_shape_x: np.int32 = np.int32(self.frame_shape.x)

        frame_to_source_fp32 = np.matmul(self._frame_pixels_np, self._matrix.T) + self._vector
        frame_to_source_int32 = np.rint(frame_to_source_fp32).astype(np.int32)

        # for 3D array: 0 is x, 1 is y
        source_x = frame_to_source_int32[:, :, 0]  # 2D array of x pixel in source
        source_y = frame_to_source_int32[:, :, 1]  # 2D array of y pixel in source

        # self._timer.lap("mapping")

        # boolean 2-D array of portal pixels that map to a pixel on the source
        # will be false if the pixel on source would fall outside of source
        mapped = (source_y >= 0) & (source_y < source_shape_y) & \
                 (source_x >= 0) & (source_x < source_shape_x)

        # self._timer.lap("mapped")

        frame_rgba = np.zeros(shape=(frame_shape_y, frame_shape_x, 4), dtype=np.uint8)
        if np.all(mapped):
            # twice as fast and np.all is almost instant
            frame_rgba[:, :] = self._source_np[source_y, source_x, :]
        else:
            frame_rgba[mapped, :] = self._source_np[source_y[mapped], source_x[mapped], :]
        # frame_rgba[mapped, :] = self._source_np[source_y[mapped], source_x[mapped], :]
        # self._timer.lap("assignment")
        # self._timer.stop()
        # self.image_rgba[~mapped, :] = self._zero_uint     probably slower than just zeroing everything first

        self._frame_rgba = frame_rgba

    def _get_frame_from_pan_slice(self):
        # self._timer.start()

        # inputs
        source: tuples.VectorInt = tuples.VectorInt(
            y=self._source_np.shape[0],
            x=self._source_np.shape[1]
        )
        frame: tuples.VectorInt = tuples.VectorInt(
            x=int(self.frame_shape.x),
            y=int(self.frame_shape.y)
        )
        # cartesian total_offset
        pan: tuples.VectorInt = tuples.VectorInt(
            x=self.offset.x+self._pan.x,
            y=self.offset.y+self._pan.y
        )
        # print(f"source : {source}")
        # print(f"frame  : {frame}")
        # print(f"pan    : {pan}")
        # print()

        # default output (fully transparent because alpha = 0)
        frame_rgba = np.zeros(shape=(frame.y, frame.x, 4), dtype=np.uint8)

        # overlap
        overlap: bool = True
        if pan.x > source.x or pan.y > source.y:
            overlap = False
        if -pan.x > frame.x or -pan.y > frame.y:
            overlap = False

        # assumption: frame < source for x and y
        if overlap:
            frame_min: tuples.VectorInt = tuples.VectorInt(0, 0)
            frame_max: tuples.VectorInt = tuples.VectorInt(frame.x, frame.y)

            # x co-ordinates for cases with an overlap that diverge for default min and max
            if pan.x >= 0:
                frame_right = pan.x + frame.x
                if source.x < frame_right:
                    frame_max.x = frame.x - (frame_right - source.x)
            else:
                frame_min.x = -pan.x

            # y co-ordinates for cases with an overlap that diverge for default min and max
            if pan.y >= 0:
                frame_top = pan.y + frame.y
                if source.y < frame_top:
                    frame_max.y = frame.y - (frame_top - source.y)
            else:
                frame_min.y = -pan.y

            source_min: tuples.VectorInt = pan + frame_min
            source_max: tuples.VectorInt = pan + frame_max

            # print(f"frame_min : {frame_min}")
            # print(f"frame_max : {frame_max}")
            # print(f"source_min: {source_min}")
            # print(f"source_max: {source_max}")

            # flip from cartesian to image co-ordinates
            frame_min.y = frame.y - frame_min.y
            frame_max.y = frame.y - frame_max.y
            source_min.y = source.y - source_min.y
            source_max.y = source.y - source_max.y

            # self._timer.lap("init")

            frame_rgba[frame_max.y:frame_min.y, frame_min.x:frame_max.x, :] = \
                self._source_np[source_max.y:source_min.y, source_min.x:source_max.x, :]

            # self._timer.lap("slice")

        # self._timer.stop()

        self._frame_rgba = frame_rgba
