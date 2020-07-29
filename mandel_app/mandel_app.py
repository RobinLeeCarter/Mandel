from mandel_app import model, view, controller


class MandelApp:
    def __init__(self):
        self._model = model.Model()
        self._view = view.View()
        self._controller = controller.Controller()

        # resolve chicken and the egg
        self._model.set_controller(self._controller)
        self._view.set_controller(self._controller)
        self._controller.set_model(self._model)
        self._controller.set_view(self._view)

        self._controller.build_and_run()
