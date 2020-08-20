from typing import Optional, Union, Callable

from PyQt5 import QtWidgets, QtGui, QtCore

from mandel_app.view import icon

ShortcutType = Union[QtGui.QKeySequence, QtGui.QKeySequence.StandardKey, str, int]


class Action:
    def __init__(self,
                 q_main_window: QtWidgets.QMainWindow,
                 name: str,
                 icon_filename: Optional[str] = None,
                 text: str = "",
                 status_tip: Optional[str] = None,
                 checkable: bool = False,
                 shortcut: Optional[ShortcutType] = None,
                 on_triggered: Optional[Callable[[bool], None]] = None
                 ):
        self._q_main_window: QtWidgets.QMainWindow = q_main_window
        self.name: str = name
        if icon_filename is None:
            self.q_action = QtWidgets.QAction(text, self._q_main_window)
        else:
            self.icon_: icon.Icon = icon.Icon(icon_filename)
            self.q_action: QtWidgets.QAction = QtWidgets.QAction(self.icon_.q_icon, text, self._q_main_window)

        if shortcut is not None:
            self.q_action.setShortcut(shortcut)
        if status_tip is not None:
            self.q_action.setStatusTip(status_tip)
        if checkable:
            self.q_action.setCheckable(checkable)
        if on_triggered is not None:
            self.set_on_triggered(on_triggered)

        self._q_main_window.addAction(self.q_action)

    def set_on_triggered(self, on_triggered: Callable[[bool], None]):
        # noinspection PyUnresolvedReferences
        self.q_action.triggered.connect(on_triggered)
