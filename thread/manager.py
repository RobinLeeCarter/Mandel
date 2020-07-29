from typing import Optional, Callable

from PyQt5 import QtWidgets, QtCore

from thread import worker, job, enums


class Manager(QtCore.QObject):
    _request_work = QtCore.pyqtSignal(job.Job, enums.QueueAs)
    _request_stop = QtCore.pyqtSignal()

    # region Setup
    def __init__(self,
                 on_progress_update: Optional[Callable[[float, int], None]] = None,
                 on_stop_success: Optional[Callable[[], None]] = None,
                 on_job_complete: Optional[Callable[[job.Job], None]] = None
                 ):
        super().__init__()
        self._thread = QtCore.QThread()
        self._worker = worker.Worker()
        self._on_progress_update = on_progress_update
        self._on_stop_success = on_stop_success
        self._on_job_complete = on_job_complete
    # endregion

    # region Requests from main thread
    def start_thread(self):
        # move worker to thread and make sure it is deleted when the thread is finished
        self._worker.moveToThread(self._thread)
        self._thread.finished.connect(self._worker.deleteLater)   # seems to get deleted anyway though

        # make connections across threads (gui <-> worker)
        # gui -> worker
        self._request_work.connect(self._worker.request_job)
        self._request_stop.connect(self._worker.request_stop)
        # worker -> gui
        self._worker.progressUpdate.connect(self.progress_update_slot)
        self._worker.stopSuccess.connect(self.stop_success_slot)
        self._worker.jobComplete.connect(self.job_complete_slot)

        # more reliable than def __del__ in python as may not be called
        QtWidgets.QApplication.instance().aboutToQuit.connect(self.quit_thread)
        self._thread.start()

    def request_work(self, job_: job.Job, queue_as: enums.QueueAs):
        self._request_work.emit(job_, queue_as)

    def request_stop(self):
        self._request_stop.emit()
    # endregion

    # region Slots for Worker
    @QtCore.pyqtSlot(float, int)
    def progress_update_slot(self, progress: float, job_number: int):
        if self._on_progress_update is not None:
            self._on_progress_update(progress, job_number)

    @QtCore.pyqtSlot()
    def stop_success_slot(self):
        if self._on_stop_success is not None:
            self._on_stop_success()

    @QtCore.pyqtSlot(job.Job)
    def job_complete_slot(self, job_: job.Job):
        if self._on_job_complete is not None:
            self._on_job_complete(job_)

    @QtCore.pyqtSlot()
    def quit_thread(self):
        self._thread.quit()
        self._thread.wait()
    # endregion

