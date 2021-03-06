import enum


class ImageAction(enum.IntEnum):
    NONE = enum.auto()      # no current action being performed, free to start one or switch image
    PANNING = enum.auto()   # part-way through panning
    PANNED = enum.auto()    # panned and waiting for result, can pan again but may not rotate
    ROTATING = enum.auto()  # part-way through rotating
    ROTATED = enum.auto()   # rotated and waiting for result, can rotate again but may not pan
    RESIZED = enum.auto()   # part-way through resizing, cannot rotate, pan or zoom
    ZOOMED = enum.auto()    # part-way through zooming, cannot rotate or pan
    DRAWING = enum.auto()   # in the process of drawing, used to purge events so they will not fire immediately after
