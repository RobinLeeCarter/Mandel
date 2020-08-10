from __future__ import annotations
from typing import List, Optional

import numpy as np


class Field:
    def __init__(self, z0: Optional[complex] = None, solutions: Optional[List[complex]] = None):
        self.z0: Optional[complex] = z0
        if z0 is not None and solutions is not None:
            self.build(z0, solutions)

    # noinspection PyAttributeOutsideInit
    def build(self, z0: complex, solutions: List[complex]) -> Field:
        self.z0 = z0
        min_val = -2.0
        max_val = 2.0
        steps = 700

        y, x = np.ogrid[min_val: max_val: steps * 1j,
                        min_val: max_val: steps * 1j]
        z = x + y*1j
        z_next = z*z + self.z0
        diff = z_next - z

        self.x = np.real(z)
        self.y = np.imag(z)
        self.vx = np.real(diff)
        self.vy = np.imag(diff)
        self.vr = np.abs(diff)

        s1, s2 = solutions  # unpack
        self.d1_before = np.abs(z - s1)
        self.d1_after = np.abs(z_next - s1)
        self.d2_before = np.abs(z - s2)
        self.d2_after = np.abs(z_next - s2)

        self.s1_ratio = self.d1_after / self.d1_before
        self.s2_ratio = self.d2_after / self.d2_before
        self.s1_closer = (self.s1_ratio <= 1)
        self.s2_closer = (self.s2_ratio <= 1)

        self.s1_attraction_intensity = 0.3 + 0.7 * (1.0 - self.s1_ratio)
        self.s2_attraction_intensity = 0.3 + 0.7 * (1.0 - self.s2_ratio)

        return self

        # self.s1_attraction = np.zeros(shape=z.shape, dtype=float)
        # self.s2_attraction = np.zeros(shape=z.shape, dtype=float)
        # self.s1_attraction[self.s1_closer] = 1.0 + (1.0 - self.s1_ratio[self.s1_closer])
        # self.s2_attraction[self.s2_closer] = 1.0 + (1.0 - self.s2_ratio[self.s2_closer])

        # self.s1_attraction: np.ndarray = (self.d1_after <= self.d1_before)
        # self.s2_attraction: np.ndarray = (self.d2_after <= self.d2_before)

        # self.repulsion1 = self.repulsion(solutions[0], z, z_next)
        # self.repulsion2 = self.repulsion(solutions[1], z, z_next)

    # change in distance to solution
    # def repulsion(self, solution: complex, z: np.ndarray, z_next: np.ndarray) -> np.ndarray:
    #     before = np.abs(z - solution)
    #     after = np.abs(z_next - solution)
    #     # TODO: divide by zero error
    #     repulsion = after / before
    #     repulsion[repulsion > 10.0] = 10.0
    #     return repulsion
