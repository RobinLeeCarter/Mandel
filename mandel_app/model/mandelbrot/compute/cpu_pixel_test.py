import multiprocessing
import itertools
import numpy as np

from mandel_app.model.mandelbrot.compute import cpu_pixel
import utils


class CpuPixelTest:
    def __init__(self):
        self.calls = 2000
        self.end_iter = 10000
        self.timer = utils.Timer()

        self.c = np.zeros(shape=(self.calls,), dtype=complex)
        for x in range(self.calls):
            self.c[x] = 0.1j * (float(x) / float(self.calls))
        self.z = np.copy(self.c)
        self.iterations = np.zeros(shape=(self.calls,), dtype=int)

    def do_pixels(self):
        self.timer.start()
        zipped = list(zip(self.c,
                          self.z,
                          self.iterations,
                          itertools.repeat(self.end_iter)
                          ))
        self.timer.lap("zip to list")

        with multiprocessing.Pool() as pool:
            results = pool.starmap(cpu_pixel.do_pixel,
                                   zipped
                                   )
            # results = pool.starmap(cpu_pixel.do_pixel,
            #                        zip(self.c,
            #                            self.z,
            #                            self.iterations,
            #                            itertools.repeat(self.end_iter)
            #                            )
            #                        )
        self.timer.lap("calc")
        # z_list, i_list = zip(*results)
        # self.z = np.array(z_list)
        # self.iterations = np.array(i_list)
        self.z = np.array([z for z, i in results])
        self.iterations = np.array([i for z, i in results])
        self.timer.lap("results")
        self.timer.stop()
        print(self.iterations)


if __name__ == "__main__":
    cpu_pixel_test_ = CpuPixelTest()
    cpu_pixel_test_.do_pixels()
    print(cpu_pixel_test_.z.dtype)
    print(cpu_pixel_test_.iterations.dtype)
