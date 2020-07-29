import utils


class ProgressEstimator:
    def __init__(self):
        self.progress: float = 0.0
        self.timer = utils.Timer()

    # region Requests
    def start(self):
        self.progress = 0.0
        self.timer.start()

    def stop(self):
        self.progress = 1.0
        self.timer.stop(show=False)

    def estimate_progress(self, yielded: float):
        self._calculate_progress(yielded)
        self._record_progress()
    # endregion

    # region Internals
    # override generally
    def _calculate_progress(self, yielded: float):
        self.progress = yielded

    def _record_progress(self):
        self.timer.lap(f"progress: {100 * self.progress:.0f}%")
    # endregion
