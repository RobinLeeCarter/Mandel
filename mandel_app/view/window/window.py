from typing import Callable, Tuple

from PyQt5 import QtWidgets, QtGui, QtCore

from mandel_app import tuples
from mandel_app.view.window import actions, menu, toolbars, status_bar, central


class Window:
    def __init__(self, application_name: str, window_settings: dict):
        self._application_name = application_name
        self.q_main_window = XMainWindow()
        self.q_settings = QtCore.QSettings()
        self._build(window_settings)

        self.actions = actions.Actions(self.q_main_window)
        self.menu = menu.Menu(self.q_main_window, self.actions.action_dict)
        self.toolbars = toolbars.Toolbars(self.q_main_window, self.actions.action_dict)

        self.central = central.Central(self.q_main_window)
        self.status_bar = status_bar.StatusBar(self.q_main_window)

        # modes
        self.is_full_screen = False
        self.is_active = True

        self.q_main_window.show()
        self.central.set_image_space()

    def _build(self, window_settings: dict):
        # Set some main window's properties
        self.q_main_window.setWindowTitle(self._application_name)
        self.q_main_window.resize(window_settings["size"])
        self.q_main_window.move(window_settings["pos"])
        self.q_main_window.setMinimumSize(200, 200)
        # self.q_main_window.setFocusPolicy(QtCore.Qt.ClickFocus)

        stylesheet = self._get_stylesheet()
        self.q_main_window.setStyleSheet(stylesheet)

    def _get_stylesheet(self):
        stylesheet = """
            background-color: darkGray
        """
        return stylesheet

    def set_full_screen(self, full_screen: bool):
        self.is_full_screen = full_screen
        if full_screen:
            self.q_main_window.showFullScreen()
            self.toolbars.full_screen_hide()
            self.menu.full_screen_hide()
            self.status_bar.q_status_bar.hide()
        else:
            self.q_main_window.showNormal()
            self.toolbars.full_screen_show()
            self.menu.full_screen_show()
            self.status_bar.q_status_bar.show()

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

    def set_on_resize(self, on_resize: Callable[[], None]):
        @QtCore.pyqtSlot()
        def slot():
            on_resize()

        # noinspection PyUnresolvedReferences
        self.q_main_window.resizeSignal.connect(slot)

    def set_on_close(self, on_close: Callable[[], None]):
        @QtCore.pyqtSlot()
        def slot():
            on_close()

        # noinspection PyUnresolvedReferences
        self.q_main_window.closeSignal.connect(slot)

    # endregion


class XMainWindow(QtWidgets.QMainWindow):
    RESIZE_TIMEOUT_MS: int = 100

    keyPressSignal = QtCore.pyqtSignal(QtGui.QKeyEvent)
    activationChangeSignal = QtCore.pyqtSignal()
    resizeSignal = QtCore.pyqtSignal()
    closeSignal = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

    # region delayed resize event handler
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

    def closeEvent(self, close_event: QtGui.QCloseEvent) -> None:
        self.closeSignal.emit()
        super().closeEvent(close_event)
    # endregion
