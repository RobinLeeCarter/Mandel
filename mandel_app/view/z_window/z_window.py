import copy
from typing import Callable, Optional, Tuple

from PyQt5 import QtWidgets, QtGui, QtCore

from mandel_app import tuples
from mandel_app.view.z_window import actions, central


class ZWindow:
    def __init__(self, parent: QtWidgets.QMainWindow, z_window_settings: dict):
        self.q_main_window = XMainWindow(parent=parent)
        self.is_active = False
        self.actions = actions.Actions(self.q_main_window)
        image_shape = tuples.image_shape_from_q_size(z_window_settings["size"])
        self.central = central.Central(self.q_main_window, image_shape)

        self._build(z_window_settings)

    def _build(self, z_window_settings: dict):
        self.q_main_window.setWindowTitle('Z Tracing')
        self.q_main_window.resize(z_window_settings["size"])
        self.q_main_window.move(z_window_settings["pos"])
        self.q_main_window.setMinimumSize(200, 200)
        stylesheet = self._get_stylesheet()
        self.q_main_window.setStyleSheet(stylesheet)
        self.q_main_window.show()
        self.central.set_image_space()
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
        @QtCore.pyqtSlot()
        def slot(key_event: QtGui.QKeyEvent):
            on_key_pressed(key_event)

        # noinspection PyUnresolvedReferences
        self.q_main_window.keyPressSignal.connect(slot)

    def set_on_active(self, on_active: Callable[[], None]):
        @QtCore.pyqtSlot()
        def slot():
            if not self.is_active:
                on_active()

        # noinspection PyUnresolvedReferences
        self.q_main_window.activationChangeSignal.connect(slot)

    def set_on_close(self, on_close: Callable[[], None]):
        @QtCore.pyqtSlot()
        def slot():
            on_close()

        # noinspection PyUnresolvedReferences
        self.q_main_window.closeSignal.connect(slot)

    def set_on_resize(self, on_resize: Callable[[], None]):
        @QtCore.pyqtSlot()
        def slot():
            on_resize()

        # noinspection PyUnresolvedReferences
        self.q_main_window.resizeSignal.connect(slot)
    # endregion


class XMainWindow(QtWidgets.QMainWindow):
    # on my machine in Ubuntu 19.10 a shorter timeout results in artifacts as the window redraws
    RESIZE_TIMEOUT_MS: int = 100

    keyPressSignal = QtCore.pyqtSignal(QtGui.QKeyEvent)
    activationChangeSignal = QtCore.pyqtSignal()
    closeSignal = QtCore.pyqtSignal()
    resizeSignal = QtCore.pyqtSignal()

    def __init__(self, parent=Optional[QtWidgets.QWidget]):
        super().__init__(parent=parent)
        self.resize_q_timer = QtCore.QTimer(parent=self)
        self.resize_q_timer.setSingleShot(True)
        self.resize_enabled: bool = False   # disable for the first time through as alpha on plot images gets set to 1
        self.resize_connect_timer()

    def keyPressEvent(self, key_event: QtGui.QKeyEvent) -> None:
        # noinspection PyUnresolvedReferences
        self.keyPressSignal.emit(key_event)
        super().keyPressEvent(key_event)

    def changeEvent(self, event: QtCore.QEvent) -> None:
        if event.type() == QtCore.QEvent.ActivationChange and self.isActiveWindow():
            self.activationChangeSignal.emit()
        super().changeEvent(event)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if event.spontaneous():
            self.closeSignal.emit()
        super().closeEvent(event)

    # region delayed resize resize_event handler
    def resizeEvent(self, resize_event: QtGui.QResizeEvent) -> None:
        if self.resize_enabled:
            # NOTE: resize_event will be messed up by the resize delay code so we don't take a copy
            self.resize_q_timer.start(XMainWindow.RESIZE_TIMEOUT_MS)
        self.resize_enabled = True
        super().resizeEvent(resize_event)

    def resize_connect_timer(self):
        @QtCore.pyqtSlot()
        def slot():
            # noinspection PyUnresolvedReferences
            self.resizeSignal.emit()

        self.resize_q_timer.timeout.connect(slot)
    # endregion
