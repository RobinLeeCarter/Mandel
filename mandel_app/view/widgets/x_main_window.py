from typing import Callable

from PyQt5 import QtWidgets, QtGui, QtCore


class XMainWindow(QtWidgets.QMainWindow):
    # on my machine in Ubuntu 19.10 a shorter timeout results in artifacts as the window redraws
    RESIZE_TIMEOUT_MS: int = 100

    keyPressSignal = QtCore.pyqtSignal(QtGui.QKeyEvent)
    activationChangeSignal = QtCore.pyqtSignal()
    closeSignal = QtCore.pyqtSignal(QtGui.QCloseEvent)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._resize_q_timer = QtCore.QTimer(parent=self)
        self._resize_q_timer.setSingleShot(True)
        self._resize_enabled: bool = False   # disable for the first time through as alpha on plot images gets set to 1

    def keyPressEvent(self, key_event: QtGui.QKeyEvent) -> None:
        self.keyPressSignal.emit(key_event)
        super().keyPressEvent(key_event)

    def changeEvent(self, event: QtCore.QEvent) -> None:
        if event.type() == QtCore.QEvent.ActivationChange and self.isActiveWindow():
            self.activationChangeSignal.emit()
        super().changeEvent(event)

    def resizeEvent(self, resize_event: QtGui.QResizeEvent) -> None:
        if self._resize_enabled:
            # NOTE: resize_event will be messed up by the resize delay code so we don't take a copy
            self._resize_q_timer.start(XMainWindow.RESIZE_TIMEOUT_MS)
        self._resize_enabled = True
        super().resizeEvent(resize_event)

    def closeEvent(self, close_event: QtGui.QCloseEvent) -> None:
        self.closeSignal.emit(close_event)
        super().closeEvent(close_event)

    # region Connect Events
    def set_on_key_pressed(self, on_key_pressed: Callable[[QtGui.QKeyEvent], None]):
        self.keyPressSignal.connect(on_key_pressed)

    def set_on_active(self, on_active: Callable[[], None]):
        self.activationChangeSignal.connect(on_active)

    def set_on_resize(self, on_resize: Callable[[], None]):
        self._resize_q_timer.timeout.connect(on_resize)

    def set_on_close(self, on_close: Callable[[], None]):
        self.closeSignal.connect(on_close)
    # endregion
