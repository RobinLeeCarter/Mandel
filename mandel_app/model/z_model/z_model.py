from __future__ import annotations
from typing import List, Optional
import cmath

from mandel_app import tuples
from mandel_app.model.z_model import trace, field


class ZModel:
    def __init__(self,
                 z0: Optional[complex] = None,
                 image_shape: Optional[tuples.ImageShape] = None):
        self.z0: Optional[complex] = z0
        self.image_shape: Optional[tuples.ImageShape] = image_shape
        self.solutions: List[complex] = []
        self.trace = trace.Trace()
        self.field = field.Field()
        if self._build_requirements_met:
            self.build(self.z0, self.image_shape)

    @property
    def _build_requirements_met(self) -> bool:
        return self.z0 is not None and self.image_shape is not None

    def build(self,
              z0: Optional[complex] = None,
              image_shape: Optional[tuples.ImageShape] = None):
        if z0 is not None:
            self.z0 = z0
            self.solutions = self._calc_solutions(self.z0)
        if image_shape is not None:
            self.image_shape = image_shape

        if not self._build_requirements_met:
            raise Exception("model.z_model.z_model.ZModel build requirements not met")

        if z0 is not None:
            self.trace.build(self.z0)
        self.field.build(self.z0, self.solutions, self.image_shape)

    @staticmethod
    def _calc_solutions(z0: complex) -> List[complex]:
        principle_root: complex = cmath.sqrt(0.25 - z0)
        solutions: List[complex] = [
            0.5 + principle_root,
            0.5 - principle_root
        ]
        return solutions
