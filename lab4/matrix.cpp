#include <iostream>
#include <vector>
#include <functional>
#include <math.h>
#include <omp.h>
#include <chrono>
#include <fstream>

std::vector<std::vector<int>> generateMatrix(size_t m, size_t n, int range = 100)
{
    std::vector<std::vector<int>> matrix(m, std::vector<int>(n));

    for (size_t i = 0; i != m; ++i)
    {
        for (size_t j = 0; j != n; ++j)
        {
            matrix[i][j] = rand() % 100;
        }
    }
    return matrix;
}

void printMatrix(std::vector<std::vector<int>> matrix)
{
    for (size_t i = 0; i != matrix.size(); ++i)
    {
        for (size_t j = 0; j != matrix[i].size(); ++j)
        {
            std::cout << matrix[i][j] << "\t";
        }
        std::cout << "\n";
    }
}

void printVector(std::vector<int> vector)
{
    for (size_t i = 0; i != vector.size(); ++i)
    {
        std::cout << vector[i] << "\t";
    }
    std::cout << "\n";
}

std::vector<int> maxMatrixColVal(std::vector<std::vector<int>> matrix)
{
    std::vector<int> maxVal;
    int m = matrix[0].size();
    int n = matrix.size();
    for (size_t i = 0; i != m; ++i)
    {
        int max = matrix[0][i];
        for (size_t j = 0; j != n; ++j)
        {
            if (max < matrix[j][i])
            {
                max = matrix[j][i];
            }
        }
        maxVal.push_back(max);
    }
    return maxVal;
}

std::vector<int> maxMatrixColValPar(std::vector<std::vector<int>> matrix)
{
    std::vector<int> maxVal;
    int m = matrix[0].size();
    int n = matrix.size();
#pragma omp parallel for
    for (size_t i = 0; i != m; ++i)
    {
        int max = matrix[0][i];
        for (size_t j = 0; j != n; ++j)
        {
            if (max < matrix[j][i])
            {
                max = matrix[j][i];
            }
        }
#pragma omp critical
        maxVal.push_back(max);
    }
    return maxVal;
}

int main()
{
    int n = 50;
    int m = 50;
    int iterations = 4;
    // std::cout << "matrix: \n";
    // printMatrix(matrix);
    std::ofstream file("res.txt");
    char buffer[100];
    file << "n\tm\ttime\n";
    file << "First: \n";

    for (int i = 0; i < iterations; i++)
    {
        std::vector<std::vector<int>> matrix = generateMatrix(n*(pow(10,i)), m*(pow(10,i)), 50000);

        auto start{std::chrono::steady_clock::now()};

        std::vector<int> res = maxMatrixColVal(matrix);
        // std::cout << "max in col: \n";
        // printVector(res);

        auto end{std::chrono::steady_clock::now()};
        std::chrono::duration<double> elapsed_seconds{end - start};
        // printf("Lin time: %f ms\n", elapsed_seconds * 1000);

        std::snprintf(buffer, 100, "%i\t%i\t%f\t\n", int(n*(pow(10,i))), int(m*(pow(10,i))), elapsed_seconds * 1000);
        file << buffer;
    }

    
    file << "Second: \n";

    for (int i = 0; i < iterations; i++)
    {
        std::vector<std::vector<int>> matrix = generateMatrix(n*(pow(10,i)), m*(pow(10,i)), 50000);

        auto start2{std::chrono::steady_clock::now()};

        std::vector<int> respar = maxMatrixColValPar(matrix);
        // std::cout << "max in col: \n";
        // printVector(respar);

        auto end2{std::chrono::steady_clock::now()};
        std::chrono::duration<double> elapsed_seconds2{end2 - start2};
        // printf("Par time: %f ms\n", elapsed_seconds2 * 1000);

        std::snprintf(buffer, 100, "%i\t%i\t%f\t\n", int(n*(pow(10,i))), int(m*(pow(10,i))), elapsed_seconds2 * 1000);
        file << buffer;
    }
}