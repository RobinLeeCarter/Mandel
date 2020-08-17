import sys

from PyQt5 import QtWidgets

from mandel_app import model, view, controller


class MandelApp:
    def __init__(self):
        self._application = QtWidgets.QApplication(sys.argv)

        self._model = model.Model()
        self._view = view.View(self._application)
        self._controller = controller.Controller(self._model, self._view)

        # enable model and view to send messages to controller
        self._model.set_controller(self._controller)
        self._view.set_controller(self._controller)

        self._controller.build()

        sys.exit(self._application.exec_())
