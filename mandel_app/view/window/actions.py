from PyQt5 import QtWidgets, QtCore

from mandel_app.view import action, actions


class Actions(actions.Actions):
    def __init__(self, q_main_window: QtWidgets.QMainWindow):
        super().__init__(q_main_window)

        self.full_screen = action.Action(
            q_main_window=self._q_main_window,
            name="full_screen",
            icon_filename="application-resize.png",
            text="Full-screen",
            status_tip="Enter or leave full-screen mode",
            checkable=True,
            shortcut=QtCore.Qt.Key_F11
        )
        self._add_action(self.full_screen)

        self.z_mode = action.Action(
            q_main_window=self._q_main_window,
            name="z_mode",
            icon_filename="cross-white.png",
            text="Z Trace",
            status_tip="Trace the z values for a point",
            checkable=True
        )
        self._add_action(self.z_mode)

        self.max_iterations = action.Action(
            q_main_window=self._q_main_window,
            name="max_iterations",
            icon_filename="plus.png",
            text="Fix maximum iterations",
            status_tip="Fix the maximum number of iterations as a power of 2",
            checkable=True,
        )
        self._add_action(self.max_iterations)

        self.escape = action.Action(
            q_main_window=self._q_main_window,
            name="escape",
            text="Escape",
            shortcut=QtCore.Qt.Key_Escape
        )
        self._add_action(self.escape)
