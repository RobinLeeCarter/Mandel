import math
from collections import namedtuple

ImageShape = namedtuple('ImageShape', ['x', 'y'])
PixelPoint = namedtuple('PixelPoint', ['x', 'y'])
ComplexPoint = namedtuple('ComplexPoint', ['real', 'imag'])


def pixel_distance(pixel_point: PixelPoint) -> float:
    return math.sqrt(pixel_point.x**2 + pixel_point.y**2)
