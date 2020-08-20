from PyQt5 import QtWidgets, QtCore

from mandel_app.view import action, actions


class Actions(actions.Actions):
    def __init__(self, q_main_window: QtWidgets.QMainWindow):
        super().__init__(q_main_window)

        self.full_screen: action.Action = action.Action(
            q_main_window=self._q_main_window,
            name="full_screen",
            text="Full-screen",
            shortcut=QtCore.Qt.Key_F11
        )
        self._add_action(self.full_screen)

        self.escape: action.Action = action.Action(
            q_main_window=self._q_main_window,
            name="escape",
            text="Escape",
            shortcut=QtCore.Qt.Key_Escape
        )
        self._add_action(self.escape)
