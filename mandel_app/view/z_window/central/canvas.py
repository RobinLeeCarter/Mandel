from typing import Optional

import numpy as np
import matplotlib
from matplotlib import figure, patches, lines, text
from matplotlib.backends import backend_qt5agg

from PyQt5 import QtWidgets, QtGui
# import utils
from mandel_app import tuples
from mandel_app.model import z_model
from mandel_app.view.z_window.central import snake


class Canvas:
    def __init__(self, image_shape: tuples.ImageShape):
        # was in learnpyqt tutorial and probably no harm but doesn't seem to do anything
        matplotlib.use('Qt5Agg')

        self._dpi: int = self._get_dpi()
        self._fig = figure.Figure(frameon=False, dpi=self._dpi)
        self._ax: figure.Axes = self._fig.subplots()
        self._figure_canvas = backend_qt5agg.FigureCanvasQTAgg(self._fig)
        self._snake = snake.Snake(fig=self._fig, ax=self._ax)
        self._z_model: Optional[z_model.ZModel] = None
        self._image_shape = image_shape
        self.build()

    def build(self):
        self._set_margins()
        # self._ax.set_aspect(aspect='equal')
        # self._ax.autoscale(enable=False)
        self._set_limits()
        # self._ax.set_facecolor('white')

    def _set_margins(self):
        width_px, height_px = self._image_shape
        left_px, right_px = 40, 10
        bottom_px, top_px = 32, 10
        left_pc = left_px / width_px
        right_pc = 1.0 - (right_px / width_px)
        bottom_pc = bottom_px / height_px
        top_pc = 1.0 - (top_px / height_px)
        # matplotlib then helpfully readjusts this. Presumably it knows best?
        # https://matplotlib.org/api/_as_gen/matplotlib.pyplot.subplots_adjust.html
        self._fig.subplots_adjust(left=left_pc, right=right_pc, bottom=bottom_pc, top=top_pc, hspace=0.0, wspace=0.0)

        # to lose axes altogether
        # self._ax.set_axis_off()
        # self._fig.subplots_adjust(left=0.0, right=1.0, bottom=0.0, top=1.0)

    def _set_limits(self):
        self._ax.set_xlim(left=-2, right=2)
        self._ax.set_xlabel("real", labelpad=-3.0)
        self._ax.set_ylim(bottom=-2, top=2)
        self._ax.set_ylabel("imaginary", labelpad=-9.0)

    @property
    def figure_canvas(self) -> backend_qt5agg.FigureCanvasQTAgg:
        return self._figure_canvas

    def _get_dpi(self):
        q_application = QtWidgets.QApplication.instance()   # get singleton
        screen: QtGui.QScreen = q_application.screens()[0]
        dpi = round(screen.physicalDotsPerInch())
        # print(f"dpi = {dpi}")
        return dpi

    def draw_graph(self, z_model_: z_model.ZModel):
        self._z_model = z_model_

        self._set_margins()
        # self._ax.set_aspect(aspect='equal')
        # self._ax.autoscale(enable=False)
        self._set_limits()  # reset limits because sometimes matplotlib gets confused
        self._draw_background()
        self._draw_legend()
        counter = self._draw_counter()
        self._snake.draw_snake(trace_=z_model_.trace, counter=counter)
        self._figure_canvas.draw()

    def clear_graph(self):
        self._snake.stop_snake()
        self._figure_canvas.resize(self._image_shape.x, self._image_shape.y)
        self._ax.clear()

    def _draw_background(self):
        field = self._z_model.field

        # create and show RGB array for regions of attraction
        attraction_shape = (field.x.shape[0], field.x.shape[1], 3)
        attraction = np.zeros(shape=attraction_shape, dtype=float)

        red_channel = attraction[:, :, 0]
        green_channel = attraction[:, :, 1]
        red_channel[field.s1_closer] = field.s1_attraction_intensity[field.s1_closer]
        green_channel[field.s2_closer] = field.s2_attraction_intensity[field.s2_closer]

        self._ax.imshow(attraction, interpolation='none', origin='lower', extent=(-2.0, 2.0, -2.0, 2.0),
                        alpha=0.3, zorder=0)

        # max_value = np.max(field.repulsion2)
        # norm = colors.Normalize(-max_value, max_value)
        # self._ax.quiver(field.x, field.y, field.vx, field.vy,
        #                 scale=10, color='darkgreen', alpha=1.0, headwidth=10, headlength=10)
        self._ax.streamplot(field.x, field.y, field.vx, field.vy,
                            color='grey', zorder=1)
        # self._ax.streamplot(field.x, field.y, field.vx, field.vy, density=1.0, zorder=10,
        #                     color=-field.repulsion2, cmap="Reds", norm=norm)

        outer_circle = patches.Circle(xy=(0, 0), color="grey", radius=2, lw=2, fill=False, zorder=1)
        self._ax.add_patch(outer_circle)

        z0 = self._z_model.z0
        self._ax.plot([z0.real], [z0.imag], marker='x', markersize=30, color="blue", zorder=2)

        s1, s2 = self._z_model.solutions
        # self._ax.plot([s1.real], [s1.imag], marker='x', markersize=20, color="red", zorder=5)
        # self._ax.plot([s2.real], [s2.imag], marker='x', markersize=20, color="green", zorder=5)

        solution1 = patches.Circle(xy=(s1.real, s1.imag), radius=0.05, fill=True,
                                   alpha=0.5, color="red", linewidth=0, zorder=2)
        solution2 = patches.Circle(xy=(s2.real, s2.imag), radius=0.05, fill=True,
                                   alpha=0.5, color="green", linewidth=0, zorder=2)
        self._ax.add_patch(solution1)
        self._ax.add_patch(solution2)

    def _draw_legend(self):
        z0 = lines.Line2D([0], [0], marker='x', color='blue', label='z$_0$', markersize=7, linestyle='')
        z_trace = lines.Line2D([0], [0], color='blue', marker='o', lw=1, markersize=4, label='z$_n$')
        s1 = lines.Line2D([0], [0], marker='o', color='red', label='solution 1', markersize=7, linestyle='', alpha=0.5)
        s2 = lines.Line2D([0], [0], marker='o', color='green', label='solution 2', markersize=7, linestyle='', alpha=0.5)
        p1 = patches.Patch(facecolor=(1.0, 0.3, 0.3, 0.3), label='s1 attract')
        p2 = patches.Patch(facecolor=(0.3, 1.0, 0.3, 0.3), label='s2 attract')
        direction = lines.Line2D([0], [0], marker='>', color='grey', label='direction', markersize=5, linestyle='-')

        legend_elements = [z0, z_trace, s1, p1, s2, p2, direction]
        self._ax.legend(handles=legend_elements, loc='upper right', labelspacing=0.1,
                        facecolor=(0.7, 0.7, 0.7, 1.0), frameon=True, edgecolor='grey')

    def _draw_counter(self) -> text.Text:
        text_str = "n = 0"
        # these are matplotlib.patch.Patch properties
        patch_properties = dict(boxstyle='round', facecolor='grey', alpha=0.8)

        # place a text box in upper left in axes co-ordinates
        counter: text.Text = self._ax.text(x=0.02, y=0.98, transform=self._ax.transAxes,
                                           s=text_str, fontsize=10, verticalalignment='top',
                                           bbox=patch_properties)
        return counter

    def on_resized(self, new_image_shape: tuples.ImageShape) -> tuples.ImageShape:
        self.clear_graph()
        min_length = min(new_image_shape.x, new_image_shape.y)
        self._image_shape = tuples.PixelPoint(x=min_length, y=min_length)
        return self._image_shape
