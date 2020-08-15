#include <cupy/complex.cuh>
extern "C" __global__
void mandel_pixel(const complex<double>* c,
                  complex<double>* z,
                  int* iterations,
                  const int start_iter,
                  const int end_iter
                 )
{
    int tid = blockDim.x * blockIdx.x + threadIdx.x;
    int k = start_iter;
    const double cx = c[tid].real();
    const double cy = c[tid].imag();
    double x;
    double y;
    double xx;
    double yy;
    /* double xy; */
    double x2;
    bool cont = true;
    if (start_iter == 0)
    {
        x = cx;
        y = cy;
    }
    else
    {
        x = z[tid].real();
        y = z[tid].imag();
    }

    if (k == end_iter)
    {
        cont = false;
    }
    else
    {
        xx = x * x;
        yy = y * y;
        /* xy = x * y; */
        cont = (xx + yy < 4.0);
    }

    while (cont)
    {
        /* x2 = x + x; */
        x2 = x * 2.0;
        x = xx - yy + cx;
        /* y = 2*x*y + cy; */
        y = __fma_rn(x2, y, cy);

        k++;
        
        if (k == end_iter)
        {
            cont = false;
            z[tid] = complex<double>(x, y);
        }
        else
        {
            xx = x * x;
            yy = y * y;
            /* xy = x * y; */
            cont = (xx + yy < 4.0);
        }
    }
    iterations[tid] = k;
}
