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
    double x_p_y;
    double x_m_y;
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
        cont = (x*x + y*y < 4.0);
        x_p_y = x + y;
        x_m_y = x - y;
    }

    while (cont)
    {
        /* x2 = x + x; */

        /* x = x*x - y*y + cx; */
        /* y = 2*x*y + cy; */
        x2 = x * 2.0;
        x = __fma_rn(x_m_y, x_p_y, cx);
        y = __fma_rn(x2, y, cy);

        k++;
        
        if (k == end_iter)
        {
            cont = false;
            z[tid] = complex<double>(x, y);
        }
        else
        {
            x_p_y = x + y;
            x_m_y = x - y;
            if (x_p_y > 2 || x_p_y < -2 || x_m_y > 2 || x_m_y < -2)
            {
                /* large and rare, outside diamond, potentially outside circle, do full test */
                cont = (x*x + y*y < 4.0);
            }
        }
    }
    iterations[tid] = k;
}
