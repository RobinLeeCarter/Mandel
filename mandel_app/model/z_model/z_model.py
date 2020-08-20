from __future__ import annotations
from typing import List, Optional
import cmath

from mandel_app import tuples
from mandel_app.model.z_model import trace, field


class ZModel:
    def __init__(self):
        self._z0: Optional[complex] = None
        self.solutions: List[complex] = []
        self.image_shape: Optional[tuples.ImageShape] = None
        self.trace: trace.Trace = trace.Trace()
        self.field: field.Field = field.Field()

    # self.solutions must always be recalculated when z0 is changed so make z0 a property
    @property
    def z0(self) -> complex:
        return self._z0

    def build(self,
              z0: Optional[complex] = None,
              image_shape: Optional[tuples.ImageShape] = None):
        if z0 is not None:
            self._z0 = z0
            self.solutions = self._calc_solutions(self._z0)
        if image_shape is not None:
            self.image_shape = image_shape

        if self._z0 is None or self.image_shape is None:
            raise Exception("model.z_model.z_model.ZModel build requirements not met")

        if z0 is not None:
            self.trace.build(self._z0)
        self.field.build(self._z0, self.solutions, self.image_shape)

    @staticmethod
    def _calc_solutions(z0: complex) -> List[complex]:
        principle_root: complex = cmath.sqrt(0.25 - z0)
        solutions: List[complex] = [
            0.5 + principle_root,
            0.5 - principle_root
        ]
        return solutions
