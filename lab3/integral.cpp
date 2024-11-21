#include <iostream>
#include <functional>
#include <math.h>
#include <time.h>
#include <omp.h>
#include <chrono>

double DefiniteIntegral(std::function<double(double)> function, double a, double b, double precision)
{
    double result = 0, result0;
    int n = 2;
    do
    {
        result0 = result;
        result = 0;
        double d = (b - a) / n;
        for (int i = 0; i < n; i += 1)
        {
            const double x1 = a + i * d;
            const double x2 = a + (i + 1) * d;
            result += 0.5 * (x2 - x1) * (function(x1) + function(x2));
        }
        n *= 2;
    } while (std::abs(result - result0) > precision);
    return result;
}

double ParallelDefiniteIntegral(std::function<double(double)> function, double a, double b, double precision, int p)
{
    double result = 0;
    double d = (b - a) / p;
#pragma omp parallel for
    for (int i = 0; i < p; i += 1)
    {
        const double x1 = a + i * d;
        const double x2 = a + (i + 1) * d;
        result += DefiniteIntegral(function, x1, x2, precision);
    }
    return result;
}

int main()
{
    double a = -1.0, b = 1.0; // Отрезок
    double precision = 0.001;
    auto f = [](double x)
    { return x * atan(2 * x); };

    auto start{std::chrono::steady_clock::now()};

    std::cout << '\n';
    std::cout << DefiniteIntegral(f, a, b, precision);

    auto end{std::chrono::steady_clock::now()};
    std::chrono::duration<double> elapsed_seconds{end - start};
    printf("The time: %f ms\n", elapsed_seconds*1000);

    start = std::chrono::steady_clock::now();

    std::cout << '\n';
    std::cout << ParallelDefiniteIntegral(f, a, b, precision, 16);

    end = std::chrono::steady_clock::now();
    elapsed_seconds = end - start;
    printf("The time: %f ms\n", elapsed_seconds*1000);
    return 0;
}