from typing import Optional, Callable

from PyQt5 import QtWidgets, QtCore, QtGui

from mandel_app import tuples
from mandel_app.model import z_model
from mandel_app.view.z_window.central import canvas


class Central:
    def __init__(self, q_main_window: QtWidgets.QMainWindow, image_shape: tuples.ImageShape):
        # components of central area
        self.q_scroll_area = XScrollArea(q_main_window)
        self.q_main = QtWidgets.QWidget()
        self.q_main_layout = QtWidgets.QVBoxLayout(self.q_main)
        self.canvas = canvas.Canvas(image_shape)
        self.image_space: Optional[tuples.ImageShape] = image_shape
        self.build(q_main_window)

    def build(self, q_main_window: QtWidgets.QMainWindow):
        # make connections between components
        q_main_window.setCentralWidget(self.q_scroll_area)
        self.q_scroll_area.setWidget(self.q_main)
        self.q_main.setLayout(self.q_main_layout)
        self.q_main_layout.addWidget(self.canvas.figure_canvas, 1)

        # set properties of components
        self.q_scroll_area.setAlignment(QtCore.Qt.AlignCenter)
        self.q_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.q_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.q_scroll_area.setStyleSheet("border: 0")
        # self.q_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        # self.q_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        # self.q_main_layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.BottomToTop, self.q_main)
        self.q_main_layout.setSpacing(0)
        self.q_main_layout.setContentsMargins(0, 0, 0, 0)

        # self.q_main_layout.setAlignment(Qt.AlignBottom)
        # self.q_layout.setAlignment(self.canvas.mandel_canvas, QtCore.Qt.AlignCenter)
        # self.q_scroll_area.setAlignment(Qt.AlignBottom)
        # self.q_scroll_area.setWidget(self.canvas.mandel_canvas)
        # q_main_window.setCentralWidget(self.q_main)
        # self.q_main.setVisible(False) #  changed

        # getting _get_image_space at this point in code gives a false reading as no image yet

    def show_graph(self, z_model_: z_model.ZModel):
        self.canvas.draw_graph(z_model_)
        self.q_main.setVisible(True)
        self.q_main.resize(self.image_space.x, self.image_space.y)  # changed
        self.q_main_layout.update()

    def hide_graph(self):
        self.canvas.clear_graph()

    def set_image_space(self):
        self.image_space = self._get_image_space()

    def _get_image_space(self) -> tuples.ImageShape:
        # self.q_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # self.q_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        x = self.q_scroll_area.viewport().width()
        y = self.q_scroll_area.viewport().height()

        # self.q_scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        # self.q_scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        return tuples.ImageShape(x, y)

    def set_on_resize(self, on_resize: Callable[[QtGui.QResizeEvent], None]):
        @QtCore.pyqtSlot()
        def slot(resize_event: QtGui.QResizeEvent):
            on_resize(resize_event)

        # noinspection PyUnresolvedReferences
        self.q_scroll_area.resizeEventSignal.connect(slot)


# This disables the scroll-wheel since we are using it for zooming
# plus the scrollbars are disabled
# removing the QScrollArea altogether messed up the image rendering and it was so hard to get right the first time
class XScrollArea(QtWidgets.QScrollArea):
    RESIZE_TIMEOUT_MS: int = 100
    resizeEventSignal = QtCore.pyqtSignal(QtGui.QResizeEvent)

    def __init__(self, parent=Optional[QtWidgets.QWidget]):
        super().__init__(parent=parent)
        self.resize_q_timer = QtCore.QTimer(parent=self)
        self.resize_q_timer.setSingleShot(True)
        self.resize_current_event: Optional[QtGui.QResizeEvent] = None
        self.resize_enabled: bool = False   # start (has funny results regarding alpha)
        self.resize_connect_timer()

    # region delayed resize event handler
    def resizeEvent(self, resize_event: QtGui.QResizeEvent) -> None:
        # if resize_event.oldSize() != QtCore.QSize(-1, -1):  # start (has funny results regarding alpha)
        if self.resize_enabled:
            self.resize_current_event = resize_event
            self.resize_q_timer.start(XScrollArea.RESIZE_TIMEOUT_MS)
        self.resize_enabled = True
        super().resizeEvent(resize_event)

    def resize_connect_timer(self):
        @QtCore.pyqtSlot()
        def slot():
            # self.resize_enabled = False
            # new_size = self.resize_current_event.size()
            # new_length = min(new_size.height(), new_size.width())

            # noinspection PyUnresolvedReferences
            self.resizeEventSignal.emit(self.resize_current_event)

        self.resize_q_timer.timeout.connect(slot)
    # endregion

    def wheelEvent(self, wheel_event: QtGui.QWheelEvent) -> None:
        wheel_event.ignore()
