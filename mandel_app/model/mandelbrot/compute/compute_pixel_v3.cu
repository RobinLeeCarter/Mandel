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
    double xy;
    /* double x2; */
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
        cont = (xx + yy < 4.0);
    }

    while (cont)
    {
        xy = x * y;
        /* x2 = x + x; */
        /* x2 = 2 * x; */
        x = xx - yy + cx;
        /*y = 2.0*xy + cy;*/
        y = __fma_rn(xy, 2.0, cy);

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
            /*if (xx > 2.0 || yy > 2.0)    possible further speed up
            {*/
            cont = (xx + yy < 4.0);
            /*}*/
        }
    }
    iterations[tid] = k;
}
