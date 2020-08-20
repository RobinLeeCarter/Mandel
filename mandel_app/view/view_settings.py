from typing import Optional

from PyQt5 import QtCore, QtWidgets


class ViewSettings:
    def __init__(self, reset: bool = False):
        self._q_settings: QtCore.QSettings = QtCore.QSettings()
        self._group: Optional[str] = None
        self._default: dict = {}
        self.initial_settings: dict = {}

        self._set_defaults()
        self._read_settings(reset)

        # filtered settings
        self.window_settings: dict = self._filtered_settings('window')
        self.z_window_settings: dict = self._filtered_settings('z_window')

    def _set_defaults(self):
        self._begin_group("window")
        self._add_default("pos", QtCore.QPoint(100, 100))
        self._add_default("size", QtCore.QSize(1600, 1000))
        self._end_group()

        self._begin_group("z_window")
        self._add_default("pos", QtCore.QPoint(120, 600))
        self._add_default("size", QtCore.QSize(400, 400))
        self._end_group()

    def _read_settings(self, reset: bool = False):
        for setting, default in self._default.items():
            if reset:
                self.initial_settings[setting] = default
            else:
                self.initial_settings[setting] = self._q_settings.value(setting, default)

    def _filtered_settings(self, filter_str: str) -> dict:
        full_filter_str = filter_str + '/'
        filtered = {}
        for setting, value in self.initial_settings.items():
            if setting.startswith(full_filter_str):
                new_setting = setting.lstrip(full_filter_str)
                filtered[new_setting] = value
        return filtered

    def write_window_settings(self, q_main_window: QtWidgets.QMainWindow):
        self._q_settings.beginGroup("window")
        self._q_settings.setValue("pos", q_main_window.pos())
        self._q_settings.setValue("size", q_main_window.size())
        self._q_settings.endGroup()

    def write_z_window_settings(self, q_main_window: QtWidgets.QMainWindow):
        self._q_settings.beginGroup("z_window")
        self._q_settings.setValue("pos", q_main_window.pos())
        self._q_settings.setValue("size", q_main_window.size())
        self._q_settings.endGroup()

    # region default grouping
    def _begin_group(self, group: str):
        self._group = group

    def _end_group(self):
        self._group = None

    def _add_default(self, setting: str, obj: object):
        if self._group is None:
            prefix = ""
        else:
            prefix = self._group + "/"
        self._default[prefix + setting] = obj
    # endregion

# if type casting becomes necessary
# obj = self._q_settings.value(setting, _default)
# desired_type = type(self._default[setting])
# if desired_type == QtCore.QPoint:
#     window_settings[setting] = obj.toPoint()
# elif desired_type == QtCore.QSize:
#     window_settings[setting] = obj.toSize()
# else:
#     window_settings[setting] = obj
