import math

import thread


class MandelProgressEstimator(thread.ProgressEstimator):
    def __init__(self):
        super().__init__()

        self._mode: str = "NORMAL"
        self._progress_from: float = 0.0
        self._progress_to: float = 1.0
        self._expected_work: float = 0.0
        self.cumulative_work: float = 0.0

    def set_expected_work(self, expected_work: float = 0.0):
        self._expected_work: float = expected_work

    def _calculate_progress(self, yielded: float):
        # print(f"{self._mode} yielded {yielded}")
        if self._mode in ("RANGE", "WORK"):
            if self._mode == "RANGE":
                proportion = yielded
            else:
                proportion = self._work_proportion_estimate(yielded)
            self.progress = self._progress_from_range(proportion=proportion)
            # print(f"progress: {self.progress:.2f}")
        else:
            super()._calculate_progress(yielded)

    # range mode
    def set_progress_range(self, progress_to: float, mode: str = "RANGE"):
        # print(f"set_progress_range {progress_to}")
        self._mode = mode
        self._progress_from = self.progress
        self._progress_to = progress_to

    def _work_proportion_estimate(self, work_done: float) -> float:
        self.cumulative_work += work_done
        # print(f"cumulative_work = {self.cumulative_work}")
        if self._expected_work == 0.0:
            proportion = 0.0
        else:
            done_vs_expected = self.cumulative_work / self._expected_work
            cutoff: float = 0.8
            if done_vs_expected <= cutoff:
                proportion = done_vs_expected
            else:
                # keeps increasing monotonically and never reaches 1.0 no matter how much unexpected work appears
                proportion = cutoff + (1-cutoff) * math.tanh(done_vs_expected - cutoff)
        return proportion

    def _progress_from_range(self, proportion: float) -> float:
        return self._progress_from + (self._progress_to - self._progress_from) * proportion
