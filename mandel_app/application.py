import sys

from PyQt5 import QtWidgets

from mandel_app import model, view, controller


class Application:
    def __init__(self):
        application_name: str = "Mandlebrot Explorer"
        organization_name: str = "Robin Carter Industries"

        self._application: QtWidgets.QApplication = QtWidgets.QApplication(sys.argv)
        self._application.setOrganizationName(organization_name)
        self._application.setApplicationName(application_name)

        self._model: model.Model = model.Model()
        self._view: view.View = view.View(self._application, application_name)
        self._controller: controller.Controller = controller.Controller(self._model, self._view)

        # enable model and view to send messages to controller
        self._model.set_controller(self._controller)
        self._view.set_controller(self._controller)

        self._controller.build()

        sys.exit(self._application.exec_())


def launch_application():
    Application()
