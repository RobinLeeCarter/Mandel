from __future__ import annotations
from typing import List, Optional
import cmath

from mandel_app import tuples
from mandel_app.model.z_model import trace, field


class ZModel:
    def __init__(self, frame_shape: tuples.ImageShape):
        self._z0: complex = 0
        self._c: complex = 0
        self.solutions: List[complex] = []
        self.frame_shape: tuples.ImageShape = frame_shape
        self.trace: trace.Trace = trace.Trace()
        self.field: field.Field = field.Field()

    # self.solutions must always be recalculated when z0 is changed so make z0 a property
    @property
    def z0(self) -> complex:
        return self._z0

    def build(self,
              c: Optional[complex] = None,
              z0: Optional[complex] = None):
        self._c = c
        self._z0 = z0
        self._calc_solutions()
        self.trace.build(self._c, self._z0)
        self.field.build(self._c, self._z0, self.solutions, self.frame_shape)

    def resize(self, frame_shape: tuples.ImageShape):
        self.frame_shape = frame_shape
        self.field.build(self._c, self._z0, self.solutions, self.frame_shape)

    def _calc_solutions(self):
        principle_root: complex = cmath.sqrt(0.25 - self._c)
        self.solutions: List[complex] = [
            0.5 + principle_root,
            0.5 - principle_root
        ]
