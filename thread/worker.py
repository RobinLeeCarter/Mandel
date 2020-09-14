from typing import List

# import cupy as cp
from PyQt5 import QtWidgets, QtCore

from thread import job, enums


class Worker(QtCore.QObject):
    progressUpdate = QtCore.pyqtSignal(job.Job, float)
    jobComplete = QtCore.pyqtSignal(job.Job)

    activeChange = QtCore.pyqtSignal(bool)
    stopSuccess = QtCore.pyqtSignal()
    debugMessage = QtCore.pyqtSignal(str)

    # region Setup
    def __init__(self):
        super().__init__()
        # 0 is the front of the queue, the current job is the only at the front of the queue
        # a job must always be on the queue before calling do_job

        # Kanban job queues
        self._to_do_queue: List[job.Job] = []
        self._doing_queue: List[job.Job] = []
        self._job_number: int = 0
        self._job_loop_active: bool = False
        self._worker_active: bool = False
        self._stopping: bool = False
    # endregion

    # region Slots for Manager
    def request_job(self,
                    job_: job.Job,
                    queue_as: enums.QueueAs
                    ):
        self._job_number += 1
        job_.job_number = self._job_number
        job_.set_job_checkpoint(self._job_checkpoint)
        self._stopping = False

        if queue_as == enums.QueueAs.ENQUEUE:
            # join the back of the queue and waits it's turn
            self._to_do_queue.append(job_)
        elif queue_as == enums.QueueAs.SINGULAR:
            # Command to just run this job and get rid of all the others as quickly as possible
            # request all other jobs to stop
            # add this job to be next in the queue
            self._request_all_existing_jobs_stop()
            self._to_do_queue.append(job_)
        elif queue_as == enums.QueueAs.EXPEDITE:
            # should always have the job loop active if running a job
            if self._job_loop_active:
                # don't need to worry about ensuring an active job loop
                # do this job leaving the previous current job partially completed
                self._do_job(job_)
                # so can then continue with previous job that was in progress or the next in the queue

                # Clean up:
                # If job queue already active it will do nothing. Cleanup will happen when another one stops.
                # If it is inactive but there is nothing to_do then it is the last job in progress then will clean up.

                # if not self._job_loop_active and not self._to_do_queue:
                #     self._final_cleanup()
            else:
                # use the job loop to run the job
                self._to_do_queue.append(job_)

        # Always call the job loop and let it sort out running of other jobs and ultimate cleanup.
        self._job_loop()

        # if not self._job_loop_active and len(self._todo_queue) > 0:
        #     self._job_loop()

    # def _print_status(self, calling_point: str):
    #     print(calling_point)
    #     print(f"to_do       : {len(self._to_do_queue)}")
    #     print(f"doing       : {len(self._doing_queue)}")
    #     print(f"loop active : {self._job_loop_active}")
    #     print(f"stopping    : {self._stopping}")

    def request_stop(self):
        # cancel all jobs in the to_do queue
        # self._print_status("request_stop start")
        self._stopping = True
        self._request_all_existing_jobs_stop()
        if not self._doing_queue:
            self._set_active(False)
            self.stopSuccess.emit()
            self._stopping = False
        # self._print_status("request_stop end")

    def _request_all_existing_jobs_stop(self):
        self._to_do_queue.clear()
        for job_ in self._doing_queue:
            job_.stop_requested = True
    # endregion

    # region Job Processing
    def _job_loop(self):
        if not self._job_loop_active:
            self._job_loop_active = True
            while self._to_do_queue:
                current_job = self._to_do_queue.pop(0)
                self._do_job(current_job)
            self._job_loop_active = False

            if not self._doing_queue:   # otherwise it will clean up here once the doing queue is empty
                self._final_cleanup()

    def _final_cleanup(self):
        # execution about to end, do clean-up
        self._set_active(False)
        # if the final job in the queue was requested to stop then that it was a stop request so emit stopSuccess
        if self._stopping:
            self.stopSuccess.emit()
            self._to_do_queue.clear()
            self._stopping = False
        # self._print_status("_final_cleanup")

    def _do_job(self, job_: job.Job):
        # self._print_status("_do_job")
        self._set_active(True)
        # add to (front) of doing queue
        self._doing_queue.insert(0, job_)
        job_.run()
        # let the thread event-queue run so this job can be requested to be stopped
        QtWidgets.QApplication.processEvents()
        # if the job was requested to be stopped then we don't want the actions associated with the job completing
        if not job_.stop_requested:
            self.jobComplete.emit(job_)
        # remove from doing queue
        self._doing_queue.remove(job_)

    def _set_active(self, active: bool):
        if active != self._worker_active:
            self._worker_active = active
            self.activeChange.emit(active)

    def _job_checkpoint(self, job_: job.Job, progress: float = 0.0):
        if job_.progress_estimator:
            self.progressUpdate.emit(job_, progress)
        # let the thread event-queue run so this job can be requested to be stopped
        QtWidgets.QApplication.processEvents()
        # if it does stop execution will re-emerge in _do_job after job_.run()
    # endregion
