from typing import Optional

from matplotlib import lines

from mandel_app import tuples
from mandel_app.view import portal


class DrawMandelFrame(portal.Drawable):
    def __init__(self):
        super().__init__()
        # self._z0: Optional[complex] = None
        self._frame: Optional[portal.Frame] = None
        self._z0_source_point: Optional[tuples.PixelPoint] = None
        # self._complex_to_source: Optional[Callable[[complex], tuples.PixelPoint]] = None

        # self._z0_frame_point: Optional[tuples.PixelPoint] = None
        self._z0_marker = lines.Line2D([], [], marker='x', markersize=30, color="blue",
                                       zorder=1, visible=False)

    @property
    def shape(self) -> Optional[tuples.ImageShape]:
        return self._frame.frame_shape

    def set_frame(self, frame: portal.Frame):
        self._frame = frame

    def set_z0_source_point(self, z0_source_point: tuples.PixelPoint):
        # print("set_z0_source_point")
        # print(f"z0_source_point: {z0_source_point}")
        self._z0_source_point = z0_source_point
        self.show_z0()
        # self._set_z0_frame_point()

    def hide_z0(self):
        self._z0_marker.set_visible(False)

    def show_z0(self):
        self._z0_marker.set_visible(True)

    def draw(self):
        if self._z0_source_point is not None and self._z0_marker.get_visible():
            frame_point = self._frame.source_to_transformed_frame(self._z0_source_point)
            # print(f"z0_frame_point: {frame_point}")
            self._z0_marker.set_data([frame_point.x], [frame_point.y])
            self._ax.draw_artist(self._z0_marker)
