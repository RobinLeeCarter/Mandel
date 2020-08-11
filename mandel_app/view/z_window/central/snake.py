from typing import List, Optional

import math

import numpy as np
from matplotlib import animation, figure, lines, collections, colors, text

from mandel_app.model.z_model import trace


class Snake:
    def __init__(self, fig: figure.Figure, ax: figure.Axes):
        # external
        self._fig = fig
        self._ax = ax

        # constant for a given snake
        self._snake_length: int = 50
        self._trace: Optional[trace.Trace] = None
        self._point_count: int = 0
        self._frames: int = 0
        self._snake_point_numbering: np.ndarray = np.arange(self._snake_length)
        self._norm = colors.Normalize(-self._snake_length, self._snake_length)
        self._ani: Optional[animation.FuncAnimation] = None

        # varying for each frame
        self._frame_x: List[float] = []
        self._frame_y: List[float] = []
        self._collection: Optional[collections.LineCollection] = None
        self._head_point: int = 0
        self._tail_point: int = 0
        self._head: lines.Line2D
        self._head, = self._ax.plot([], [], marker='o', markersize=5, color="blue")
        self._counter: Optional[text.Text] = None

    def draw_snake(self, trace_: trace.Trace, counter: text.Text):
        self._trace = trace_
        self._point_count = len(self._trace.z_values)
        self._frames = self._point_count + (self._snake_length - 1)
        self._counter = counter

        # These functions have to be nested because FuncAnimation does not allow their allow signatures to include self
        def _init():
            """initialize animation"""
            return self._draw_frame(0)

        def _draw_frame(frame: int):
            """perform animation frame"""
            return self._draw_frame(frame)

        if self._point_count < 2000:
            ideal_ani_length_ms = 1000 * math.log(self._point_count, 2)
            interval_ms = ideal_ani_length_ms / self._frames
        else:
            interval_ms = 0

        self._ani = animation.FuncAnimation(fig=self._fig,
                                            func=_draw_frame,
                                            frames=self._frames,
                                            init_func=_init,
                                            interval=interval_ms,
                                            repeat_delay=1000,
                                            repeat=True,
                                            blit=True
                                            )

    def _draw_frame(self, frame: int):
        self._get_frame_points(frame)

        # from: https://matplotlib.org/3.1.1/gallery/lines_bars_and_markers/multicolored_line.html
        # Create a set of line segments so that we can color them individually
        # This creates the points as a N x 1 x 2 array so that we can stack points
        # together easily to get the segments. The segments array for line collection
        # needs to be (numlines) x (points per line) x 2 (for x and y)
        points = np.array([self._frame_x, self._frame_y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        line_collection = collections.LineCollection(segments, cmap='Blues', norm=self._norm)
        line_collection.set_array(self._snake_point_numbering)
        self._collection = self._ax.add_collection(line_collection)

        # head_point
        head_z = self._trace.z_values[self._head_point]
        self._head.set_data([head_z.real], [head_z.imag])

        self._counter.set_text(f"n = {self._head_point}")

        return self._collection, self._head, self._counter

    def _get_frame_points(self, frame: int):
        self._frame_x.clear()
        self._frame_y.clear()

        self._head_point = min(frame, self._point_count-1)
        self._tail_point = max(0, frame-(self._snake_length-1))

        for i in range(self._tail_point, self._head_point+1):
            self._frame_x.append(self._trace.x_values[i])
            self._frame_y.append(self._trace.y_values[i])

    def stop_snake(self):
        if self._ani is not None:
            # from: https://stackoverflow.com/questions/48564181/how-to-stop-funcanimation-by-func-in-matplotlib
            # https://matplotlib.org/3.3.0/api/_as_gen/matplotlib.animation.Animation.html
            # https://gist.github.com/Seanny123/2c7efd90bebbe9c7bea6a1bd30a2133c
            self._ani.event_source.stop()
            self._ani = None
