from typing import List


def do_pixel(c: complex,
             z: complex,
             iterations: int,
             end_iter: int):
    prev_x: List[float] = []
    prev_y: List[float] = []
    store_from: int = end_iter - 50

    k: int = iterations
    cx: float = c.real
    cy: float = c.imag
    x: float = z.real
    y: float = z.imag
    xx: float = x * x
    yy: float = y * y
    # x2: float # x * 2.0
    # cont: bool = k < end_iter and xx + yy < 4.0
    cont: bool = \
        k != -1 and \
        k < end_iter and \
        xx + yy < 4.0

    while cont:
        # slot = (k - iterations) % 10
        # # print(slot)
        # if k >= store_from:
        prev_x.append(x)
        prev_y.append(y)

        y = 2*x*y + cy
        # x2 = x * 2.0
        # y = __fma_rn(x2, y, cy)
        x = xx - yy + cx
        k += 1

        if k == end_iter:
            cont = False
        # if cont and x in prev_x:
        #     if (x, y) in zip(prev_x, prev_y):
        #         k = -1
        #         cont = False
        if cont:
            xx = x * x
            yy = y * y
            cont = xx + yy < 4.0

    if x in prev_x:
        if (x, y) in zip(prev_x, prev_y):
            k = -1

    z = complex(x, y)
    iterations = k
    return z, iterations
