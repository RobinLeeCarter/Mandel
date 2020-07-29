from __future__ import annotations

import numpy as np

import utils
from mandel_app import tuples
from mandel_app.model.mandelbrot.server import server

from mandel_app.model.mandelbrot.algorithm.box_algorithm import box


class BoxAlgorithm:

    def __init__(self, server: server.Server, shape: tuples.ImageShape):
        self.server = server
        self.shape = shape

    def run(self) -> np.ndarray:
        # methods
        request_edge_compute = box.Box.request_edge_compute
        check_if_can_fill = box.Box.check_if_can_fill
        spawn_children = box.Box.spawn_children
        request_inside_compute = box.Box.request_inside_compute

        my_timer = utils.Timer()
        # starting box
        box_ = box.Box(x_min=0, y_min=0, x_max=self.shape.x-1, y_max=self.shape.y-1, depth=0, server=self.server)

        # box_.call_method_at_depth(request_edge_compute, depth=0)
        # self.server.serve()
        # box_.call_method_at_depth(check_if_can_fill, depth=0)
        # if self.server.complete:
        #     return self.server.iteration
        #
        # box_.call_method_at_depth(spawn_children, depth=0)
        # box_.call_method_at_depth(request_edge_compute, depth=1)
        # self.server.serve()
        # box_.call_method_at_depth(check_if_can_fill, depth=1)

        max_depth = 5
        complete = False

        # for depth in range(max_depth+1):
        #     box_.call_method_at_depth(request_edge_compute, depth)
        #     self.server.serve()
        #     box_.call_method_at_depth(check_if_can_fill, depth)
        #     complete = self.server.complete
        #     if complete:
        #         break
        #     if depth != max_depth:
        #         box_.call_method_at_depth(spawn_children, depth)
        #     my_timer.lap(f"depth = {depth}")

        for depth in range(max_depth+1):
            if depth <= 3:
                box_.call_method_at_depth(spawn_children, depth)
            else:
                box_.call_method_at_depth(request_edge_compute, depth)
                self.server.serve()
                box_.call_method_at_depth(check_if_can_fill, depth)
                complete = self.server.complete
                if complete:
                    break
                if depth != max_depth:
                    box_.call_method_at_depth(spawn_children, depth)
            # my_timer.lap(f"depth = {depth}")

        if not complete:
            box_.call_method_at_depth(request_inside_compute, max_depth)
            self.server.serve()

        # my_timer.lap("final fill")
        # my_timer.stop()

        # if self.server.complete:
        #     print("complete")

        return self.server.iteration_cpu
