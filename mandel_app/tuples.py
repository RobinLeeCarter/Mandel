import math
from collections import namedtuple

ImageShape = namedtuple('ImageShape', ['x', 'y'])
PixelPoint = namedtuple('PixelPoint', ['x', 'y'])
Geometry = namedtuple('Geometry', ['left', 'top', 'width', 'height'])


def pixel_distance(pixel_point: PixelPoint) -> float:
    return math.sqrt(pixel_point.x**2 + pixel_point.y**2)


def image_shape_from_geometry(geometry: Geometry) -> ImageShape:
    return ImageShape(x=geometry.width, y=geometry.height)
