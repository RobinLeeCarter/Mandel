from typing import Callable

from PyQt5 import QtWidgets, QtGui

from mandel_app import tuples
from mandel_app.view.custom_widgets import x_main_window
from mandel_app.view.z_window import actions, central


class ZWindow:
    def __init__(self, parent: QtWidgets.QMainWindow, z_window_settings: dict):
        self.q_main_window: x_main_window.XMainWindow = x_main_window.XMainWindow(parent=parent)
        self.is_active: bool = False
        self.actions: actions.Actions = actions.Actions(self.q_main_window)
        image_shape: tuples.ImageShape = tuples.image_shape_from_q_size(z_window_settings["size"])
        self.central: central.Central = central.Central(self.q_main_window, image_shape)

        self._build(z_window_settings)

    def _build(self, z_window_settings: dict):
        self.q_main_window.setWindowTitle('Z Tracing')
        self.q_main_window.resize(z_window_settings["size"])
        self.q_main_window.move(z_window_settings["pos"])
        self.q_main_window.setMinimumSize(200, 200)
        stylesheet = self._get_stylesheet()
        self.q_main_window.setStyleSheet(stylesheet)
        self.q_main_window.show()
        self.central.refresh_image_space()
        self.q_main_window.setVisible(False)

        # self.menu = menu.Menu(self.q_main_window, self.actions.action_dict)
        # self.toolbars = toolbars.Toolbars(self.q_main_window, self.actions.action_dict)

        # self.toolbar = toolbar.Toolbar("My main toolbar", self.q_main_window)
        # self.central = central.Central(self.q_main_window)
        # self.status_bar = status_bar.StatusBar(self.q_main_window)

        # self.q_main_window.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

    def _get_stylesheet(self):
        stylesheet = """
            background-color: darkGray
        """
        return stylesheet

    def hide(self):
        self.q_main_window.setVisible(False)

    def show(self):
        self.q_main_window.setVisible(False)
        self.q_main_window.setVisible(True)

    # region Connect Events
    def set_on_key_pressed(self, on_key_pressed: Callable[[QtGui.QKeyEvent], None]):
        self.q_main_window.keyPressSignal.connect(on_key_pressed)

    def set_on_active(self, on_active: Callable[[], None]):
        self.q_main_window.activationChangeSignal.connect(on_active)

    def set_on_close(self, on_close: Callable[[], None]):
        self.q_main_window.closeSignal.connect(on_close)

    def set_on_resize(self, on_resize: Callable[[], None]):
        self.q_main_window.resize_q_timer.timeout.connect(on_resize)
    # endregion
