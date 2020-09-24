#include <cupy/complex.cuh>
extern "C" __global__
void do_pixel(const complex<double>* c,
                  complex<double>* z,
                  int* iterations,
                  const int end_iter
                 )
{
    int tid = blockDim.x * blockIdx.x + threadIdx.x;
    int k;
    const double cx = c[tid].real();
    const double cy = c[tid].imag();
    double x;
    double y;
    double xx;
    double yy;
    double x2;
    bool cont = true;

    x = z[tid].real();
    y = z[tid].imag();
    k = iterations[tid];

    xx = x * x;
    yy = y * y;
    cont = (k < end_iter && xx + yy < 4.0);

    while (cont)
    {
        // y = 2*x*y + cy;
        x2 = x * 2.0;
        y = __fma_rn(x2, y, cy);
        x = xx - yy + cx;
        k++;

        if (k == end_iter)
        {
            cont = false;
        }
        else
        {
            xx = x * x;
            yy = y * y;
            cont = (xx + yy < 4.0);
        }
    }
    z[tid] = complex<double>(x, y);
    iterations[tid] = k;
}
