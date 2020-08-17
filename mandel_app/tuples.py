import math
from collections import namedtuple

from PyQt5 import QtCore

ImageShape = namedtuple('ImageShape', ['x', 'y'])
PixelPoint = namedtuple('PixelPoint', ['x', 'y'])


def pixel_distance(pixel_point: PixelPoint) -> float:
    return math.sqrt(pixel_point.x**2 + pixel_point.y**2)


def image_shape_from_q_size(q_size: QtCore.QSize) -> ImageShape:
    return ImageShape(x=q_size.width(), y=q_size.height())
