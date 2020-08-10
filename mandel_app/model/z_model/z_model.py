from typing import List, Optional
import cmath

from mandel_app.model.z_model import trace, field


class ZModel:
    def __init__(self, z0: Optional[complex] = None):
        self.z0: Optional[complex] = None
        self.solutions: List[complex] = []
        self.trace = trace.Trace()
        self.field = field.Field()
        if z0 is not None:
            self.build(z0)

    def build(self, z0: complex):
        self.z0 = z0

        principle_root: complex = cmath.sqrt(0.25 - self.z0)
        self.solutions: List[complex] = [
            0.5 + principle_root,
            0.5 - principle_root
        ]

        self.trace.build(self.z0)
        self.field.build(self.z0, self.solutions)
