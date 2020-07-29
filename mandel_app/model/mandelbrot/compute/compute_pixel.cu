#include <cupy/complex.cuh>
extern "C" __global__
void mandel_pixel(const complex<double>* c,
                  complex<double>* z,
                  int* iterations,
                  const int start_iter,
                  const int max_iter
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
    double xy;
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

    if (k == max_iter)
    {
        cont = false;
    }
    else
    {
        xx = x * x;
        yy = y * y;
        xy = x * y;
        cont = (xx + yy < 4.0);
    }

    while (cont)
    {
        x = xx - yy + cx;
        y = 2*xy + cy;
        k++;
        
        if (k == max_iter)
        {
            cont = false;
            z[tid] = complex<double>(x, y);
        }
        else
        {
            xx = x * x;
            yy = y * y;
            xy = x * y;
            cont = (xx + yy < 4.0);
        }
    }
    iterations[tid] = k;
}
