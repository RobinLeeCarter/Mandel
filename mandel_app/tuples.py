import math
from collections import namedtuple
from dataclasses import dataclass

from PyQt5 import QtCore

ImageShape = namedtuple('ImageShape', ['x', 'y'])
PixelPoint = namedtuple('PixelPoint', ['x', 'y'])


def pixel_distance(pixel_point: PixelPoint) -> float:
    return math.sqrt(pixel_point.x**2 + pixel_point.y**2)


def image_shape_from_q_size(q_size: QtCore.QSize) -> ImageShape:
    return ImageShape(x=q_size.width(), y=q_size.height())


@dataclass
class VectorInt:
    x: int = 0
    y: int = 0

    # def __repr__(self):
    #     return '%s(%s, %s)' % (type(self).__name__, self.x, self.y)

    # def __hash__(self):
    #     return hash(self._d)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return self.x != other.x or self.y != other.y

    def __add__(self, other):
        return type(self)(self.x+other.x, self.y+other.y)

    def __sub__(self, other):
        return type(self)(self.x-other.x, self.y-other.y)

    def __mul__(self, scalar):
        return VectorInt(int(self.x*scalar), int(self.y*scalar))

    def __rmul__(self, scalar):
        return VectorInt(int(self.x*scalar), int(self.y*scalar))

    def __abs__(self):
        return math.hypot(self.x, self.y)

    @property
    def size(self) -> float:
        return math.hypot(self.x, self.y)

    @staticmethod
    def from_pixel_point(pixel_point: PixelPoint):
        return VectorInt(pixel_point.x, pixel_point.y)
