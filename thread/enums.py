import enum


class QueueAs(enum.IntEnum):
    ENQUEUE = enum.auto()   # add to the end of the queue and wait it's turn FIFO
    EXPEDITE = enum.auto()  # interrupt current job, run this job, then return to previous job where it left off
    SINGULAR = enum.auto()  # interrupt current job, run this job, clear all other jobs
