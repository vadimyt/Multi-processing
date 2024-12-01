#include <iostream>
#include <functional>
#include <math.h>
#include <omp.h>
#include <chrono>
#include <fstream>

struct res
{
    double area;
    long int n;
    res(double _area, long int _n)
    {
        area = _area;
        n = _n;
    }
};

res DefiniteIntegral(std::function<double(double)> function, double a, double b, double precision)
{
    double result = 0, result0;
    long int n = 2;
    do
    {
        result0 = result;
        result = 0;
        double d = (b - a) / n;
        for (long int i = 0; i < n; i += 1)
        {
            const double x1 = a + i * d;
            const double x2 = a + (i + 1) * d;
            result += 0.5 * (x2 - x1) * (function(x1) + function(x2));
        }
        n *= 2;
    } while (std::abs(result - result0) > precision);
    return res(result, n);
}

res ParallelDefiniteIntegral(std::function<double(double)> function, double a, double b, double precision, int p)
{
    double result = 0;
    long int n = 0;
    double d = (b - a) / p;
#pragma omp parallel for
    for (long int i = 0; i < p; i += 1)
    {
        const double x1 = a + i * d;
        const double x2 = a + (i + 1) * d;
        res tmpRes = DefiniteIntegral(function, x1, x2, precision);
        result += tmpRes.area;
        n += tmpRes.n;
    }
    return res(result, n + p);
}

int main()
{
    std::ofstream file("file5.txt");
    char buffer[100];

    double a = 8.0, b = 12.0; // Отрезок
    file << "Отрезок: " << a << " - " << b << '\n';

    // auto f = [](double x)
    // { return (pow((1-3*log10(x)), 1/3)/x); };

    // auto f = [](double x)
    // { return (x*atan(2*x)); };

    // auto f = [](double x)
    // { return (1/(3*cos(x)+4*sin(x))); };

    // auto f = [](double x)
    // { return (pow(x,3)/(1+pow((pow(x,4)+1),1/3))); };

    auto f = [](double x)
    { return (((pow(x,3)+2*pow(x,2)-4*x+3)/(pow(x,3)-2*pow(x,2)+x))); };

    file << "First: \n";

    for (int i = 0; i < 10; i++)
    {
        float precision = pow(10, -(i+1));
        auto start{std::chrono::steady_clock::now()};

        res defRes = DefiniteIntegral(f, a, b, precision);
        printf("\n Result: %.10f, N: %i", defRes.area, defRes.n);

        auto end{std::chrono::steady_clock::now()};
        std::chrono::duration<double> elapsed_seconds{end - start};
        printf("The time: %f ms\n", elapsed_seconds * 1000);

        std::snprintf(buffer, 100, "%.10f %i %f \n", defRes.area, defRes.n, elapsed_seconds * 1000);
        file << buffer;
    }

    file << "Second: \n";

    for (int i = 0; i < 10; i++)
    {
        float precision = pow(10, -(i+1));
        auto start = std::chrono::steady_clock::now();

        res parRes = ParallelDefiniteIntegral(f, a, b, precision, 1000);
        printf("\n Result: %.10f, N: %i ", parRes.area, parRes.n);

        auto end = std::chrono::steady_clock::now();
        std::chrono::duration<double> elapsed_seconds = end - start;
        printf("The time: %f ms\n", elapsed_seconds * 1000);

        std::snprintf(buffer, 100, "%.10f %i %f \n", parRes.area, parRes.n, elapsed_seconds * 1000);
        file << buffer;
    }

    file.close();
    return 0;
}