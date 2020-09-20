import math

import numpy as np


class Transform:
    # def __init__(self):
    #     pass

    @staticmethod
    def identity():
        return np.array(
            [[1,  0, 0],
             [0,  1, 0],
             [0,  0, 1]],
            dtype=float
        )

    @staticmethod
    def flip_y(size_y):
        return np.array(
            [[1,  0, 0],
             [0, -1, size_y],
             [0,  0, 1]],
            dtype=float
        )

    @staticmethod
    def translate(x, y):
        return np.array(
            [[1, 0, x],
             [0, 1, y],
             [0, 0, 1]],
            dtype=float
        )

    @staticmethod
    def scale(s):
        return np.array(
            [[s, 0, 0],
             [0, s, 0],
             [0, 0, 1]],
            dtype=float
        )

    @staticmethod
    def rotate_degrees(theta_degrees: float):
        """clockwise"""
        theta_radians = math.radians(theta_degrees)
        return Transform.rotate_radians(theta_radians)

    @staticmethod
    def rotate_radians(theta_radians: float):
        """clockwise"""
        cos = math.cos(theta_radians)
        sin = math.sin(theta_radians)
        return np.array(
            [[cos,  sin, 0],
             [-sin, cos, 0],
             [0,      0, 1]],
            dtype=float
        )
