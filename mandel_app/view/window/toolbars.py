from typing import List, Dict

from PyQt5 import QtWidgets, QtCore

from mandel_app.view.window import actions, dial, slider


class Toolbars:
    def __init__(self,
                 q_main_window: QtWidgets.QMainWindow,
                 action_dict: Dict[str, QtWidgets.QAction]):
        self._q_main_window = q_main_window
        self._action_dict = action_dict
        # self.tool_bars = List[QtWidgets.QToolBar]
        self.tool_bars = []
        # self.previously_visible_tool_bars = List[QtWidgets.QToolBar]
        self.previously_visible_tool_bars = []

        # self.file_tool_bar: QtWidgets.QToolBar = self._q_main_window.addToolBar("File")
        # self._add_actions(self.file_tool_bar, ["load", "save", "close"])

        self.view_tool_bar = self._q_main_window.addToolBar("View")
        self._add_actions(self.view_tool_bar, ["full_screen", "z_mode"])

        self.dial = dial.Dial(self._q_main_window, size=40)
        self.view_tool_bar.addWidget(self.dial.q_dial)

        self.view_tool_bar.addSeparator()

        self._add_actions(self.view_tool_bar, ["max_iterations"])

        self.power_label = QtWidgets.QLabel(" 2 to the power")
        self.power_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self._power_label_action = self.view_tool_bar.addWidget(self.power_label)

        self.iteration_slider = slider.Slider(self._q_main_window)
        self._iteration_slider_action = self.view_tool_bar.addWidget(self.iteration_slider._labelled_slider)

        self.iterations_label = QtWidgets.QLabel("")
        self.iterations_label.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self._iterations_label_action = self.view_tool_bar.addWidget(self.iterations_label)

        initial_power = 20
        self.iteration_slider.q_slider.setValue(initial_power)
        self.set_iterations_label(2**initial_power)
        self.slider_visibility(visible=False)

        self.view_tool_bar.setFixedHeight(50)

        # self.view_tool_bar.hide()
        # print(self.view_tool_bar.height())

    def _add_actions(self, tool_bar: QtWidgets.QToolBar, action_names: List[str]):
        for action_name in action_names:
            tool_bar.addAction(self._action_dict[action_name])
        self.tool_bars.append(tool_bar)

    def full_screen_hide(self):
        self.previously_visible_tool_bars = []
        toolbar: QtWidgets.QToolBar
        for toolbar in self.tool_bars:
            if toolbar.isVisible():
                self.previously_visible_tool_bars.append(toolbar)
                toolbar.hide()

    def full_screen_show(self):
        toolbar: QtWidgets.QToolBar
        for toolbar in self.previously_visible_tool_bars:
            toolbar.show()

    def set_iterations_label(self, iterations: int):
        self.iterations_label.setText(f"= {iterations:,} max iterations")

    def slider_visibility(self, visible: bool):
        self._power_label_action.setVisible(visible)
        self._iteration_slider_action.setVisible(visible)
        self._iterations_label_action.setVisible(visible)


# test script
if __name__ == "__main__":
    q_application = QtWidgets.QApplication([])
    main_window = QtWidgets.QMainWindow()
    actions = actions.Actions(main_window)
    toolbars = Toolbars(main_window, actions.action_dict)
    print("done")
