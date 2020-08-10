from __future__ import annotations
from typing import List, Optional

MAX_ITERATIONS = 10000


class Trace:
    def __init__(self):
        self.z0: Optional[complex] = None
        self.x_values: List[float] = []
        self.y_values: List[float] = []
        self.z_values: List[complex] = []

    def build(self, z0: complex) -> Trace:
        self.z0 = z0
        self._generate_z_values()
        self._convert_to_x_y_arrays()
        return self

    def _generate_z_values(self):
        i: int = 0
        z: complex = self.z0
        self.z_values.clear()
        self.z_values.append(z)
        z_squared_norm: float = self._squared_norm(z)
        cont: bool = (z_squared_norm < 4)

        while cont:
            z = z**2 + self.z0
            self.z_values.append(z)
            z_squared_norm = self._squared_norm(z)
            if i >= MAX_ITERATIONS or z_squared_norm > 4:
                cont = False
            i = i + 1

    def _squared_norm(self, z: complex) -> float:
        return (z * z.conjugate()).real

    def _convert_to_x_y_arrays(self):
        self.x_values = [z.real for z in self.z_values]
        self.y_values = [z.imag for z in self.z_values]
