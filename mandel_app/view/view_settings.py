from typing import Dict

from PyQt5 import QtCore, QtWidgets


class ViewSettings:
    def __init__(self):
        self.q_settings = QtCore.QSettings()
        self.default = {}
        self.initial = {}
        self.set_default()
        self.set_initial()

    def set_default(self):
        self.default: Dict[str, object] = {
            "window/left_top": QtCore.QPoint(100, 100),
            "window/size": QtCore.QSize(1200, 800)
        }

    def set_initial(self):
        for setting, default in self.default.items():
            self.initial[setting] = self.q_settings.value(setting, default)

    def write_settings(self, q_main_window: QtWidgets.QMainWindow):
        self.q_settings.setValue("window/left_top", q_main_window.pos())
        self.q_settings.setValue("window/size", q_main_window.size())

# if type casting becomes necessary
# obj = self.q_settings.value(setting, default)
# desired_type = type(self.default[setting])
# if desired_type == QtCore.QPoint:
#     initial[setting] = obj.toPoint()
# elif desired_type == QtCore.QSize:
#     initial[setting] = obj.toSize()
# else:
#     initial[setting] = obj
