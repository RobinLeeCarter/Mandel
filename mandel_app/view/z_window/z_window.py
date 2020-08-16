from typing import Callable, Optional

from PyQt5 import QtWidgets, QtGui, QtCore

from mandel_app import tuples
from mandel_app.view.z_window import actions, central


class ZWindow:
    def __init__(self, parent: QtWidgets.QMainWindow, image_shape: tuples.ImageShape):
        self.q_main_window = XMainWindow(parent=parent)
        self.is_active = False
        self.actions = actions.Actions(self.q_main_window)
        self.central = central.Central(self.q_main_window, image_shape)

        self.build(image_shape)

    def build(self, image_shape: tuples.ImageShape):
        self.q_main_window.setWindowTitle('Z Tracing')
        self.q_main_window.setGeometry(200, 200, image_shape.x, image_shape.y)
        self.q_main_window.setMinimumSize(200, 200)
        stylesheet = self.get_stylesheet()
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

    def get_stylesheet(self):
        stylesheet = """
            background-color: darkGray
        """
        return stylesheet

    def hide(self):
        self.q_main_window.setVisible(False)

    def show(self):
        self.q_main_window.setVisible(False)
        self.q_main_window.setVisible(True)

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

    def set_on_resize(self, on_resize: Callable[[QtGui.QResizeEvent], None]):
        @QtCore.pyqtSlot()
        def slot(resize_event: QtGui.QResizeEvent):
            on_resize(resize_event)

        # noinspection PyUnresolvedReferences
        self.q_main_window.resizeEventSignal.connect(slot)


class XMainWindow(QtWidgets.QMainWindow):
    RESIZE_TIMEOUT_MS: int = 100
    resizeEventSignal = QtCore.pyqtSignal(QtGui.QResizeEvent)
    keyPressSignal = QtCore.pyqtSignal(QtGui.QKeyEvent)
    activationChangeSignal = QtCore.pyqtSignal()
    closeSignal = QtCore.pyqtSignal()

    def __init__(self, parent=Optional[QtWidgets.QWidget]):
        super().__init__(parent=parent)
        self.resize_q_timer = QtCore.QTimer(parent=self)
        self.resize_q_timer.setSingleShot(True)
        self.resize_current_event: Optional[QtGui.QResizeEvent] = None
        self.resize_enabled: bool = False   # start (has funny results regarding alpha)
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

    # region delayed resize event handler
    def resizeEvent(self, resize_event: QtGui.QResizeEvent) -> None:
        # if resize_event.oldSize() != QtCore.QSize(-1, -1):  # start (has funny results regarding alpha)
        if self.resize_enabled:
            self.resize_current_event = resize_event
            self.resize_q_timer.start(XMainWindow.RESIZE_TIMEOUT_MS)
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
