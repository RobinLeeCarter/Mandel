from typing import List

from PyQt5 import QtWidgets, QtCore

from thread import job, enums


class Worker(QtCore.QObject):
    progressUpdate = QtCore.pyqtSignal(float, int)
    jobComplete = QtCore.pyqtSignal(job.Job)

    activeChange = QtCore.pyqtSignal(bool)
    stopSuccess = QtCore.pyqtSignal()
    debugMessage = QtCore.pyqtSignal(str)

    # region Setup
    def __init__(self):
        super().__init__()
        self._job_queue: List[job.Job] = []
        self._job_count: int = 0
        self._active: bool = False
        self._interrupt_requested: bool = False
    # endregion

    # region Slots for Manager
    def request_job(self,
                    job_: job.Job,
                    queue_as: enums.QueueAs
                    ):
        self._job_count += 1
        job_.job_number = self._job_count
        job_.set_job_checkpoint(self._job_checkpoint)

        if queue_as == enums.QueueAs.ENQUEUE:
            self._job_queue.append(job_)      # join the back of the queue
        elif queue_as == enums.QueueAs.EXPEDITE:
            if self._active:
                self._do_job(job_)      # jump the queue and the job being served, then continue as before
            else:
                self._job_queue.append(job_)  # just add to the front of the work queue
        elif queue_as == enums.QueueAs.SINGULAR:    # eliminate the queue and interrupt the job being served
            self._job_queue.clear()
            self._job_queue.append(job_)
            if self._active:
                self._interrupt_requested = True
            # debug = f"is_running = {self.is_running}\n" + \
            #         f"interrupt_requested = {self.interrupt_requested}"
            # self.debugMessage.emit(debug)

        if not self._active:
            self._do_job_queue()

    def request_stop(self):
        if self._active:
            self._job_queue.clear()
            self._interrupt_requested = True
    # endregion

    # region Job Processing
    def _do_job_queue(self):
        self._set_active(True)
        while self._job_queue:
            job_ = self._job_queue.pop(0)
            self._do_job(job_)
        self._set_active(False)

        if self._interrupt_requested:
            self.stopSuccess.emit()

    def _set_active(self, active: bool):
        if active != self._active:
            self._active = active
            self.activeChange.emit(active)

    def _do_job(self, job_: job.Job):
        self._interrupt_requested = False
        job_.run()
        QtWidgets.QApplication.processEvents()  # lets thread event-queue run so other things can happen
        if not self._interrupt_requested:
            self.jobComplete.emit(job_)
        # job_.follow_on_actions()

    def _job_checkpoint(self, job_: job.Job, progress: float = 0.0):
        if job_.progress_estimator:
            self.progressUpdate.emit(progress, job_.job_number)
        QtWidgets.QApplication.processEvents()  # lets thread event-queue run so other things can happen
        if self._interrupt_requested:
            job_.interrupt_requested = True
    # endregion
