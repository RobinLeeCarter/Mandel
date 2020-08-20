from typing import Callable

from PyQt5 import QtGui

import utils
from mandel_app.view import widgets

_ICON_PATH = r"resources/icons/"


class Image:
    def __init__(self, icon_filename: str):
        self.q_pixmap: QtGui.QPixmap = QtGui.QPixmap(utils.full_path(_ICON_PATH + icon_filename))
        self.q_label: widgets.XLabel = widgets.XLabel()
        self.q_label.setPixmap(self.q_pixmap)

    def set_visible(self, visible: bool):
        self.q_label.setVisible(visible)

    def set_on_mouse_press(self, on_mouse_press: Callable[[QtGui.QMouseEvent], None]):
        self.q_label.mousePressSignal.connect(on_mouse_press)
