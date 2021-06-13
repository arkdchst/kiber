#include <iostream>
#include <fstream>
#include <functional>
#include <vector>
#include <cmath>


#include "DiffSystem.h"
#include "spider_constants.h"

/// \tparam TValue - value type
/// \tparam Func - function type
/// \param x - point, where the derivative calculated
/// \param dx - step-size
/// \param function - differentiable function
/// \return
/// f'(x) = 3/2 m1 - 3/5 m2 + 1/10 m3 + O(dx^6)
/// m1 = (f(x+dx) - f(x-dx)) / 2 dx
/// m2 = (f(x+2dx)-f(x-2dx)) / 4 dx
/// m3 = (f(x+3dx)-f(x-3dx)) / 6 dx
template<class TValue>
TValue derivative(const TValue x, const TValue dx, std::function<TValue(TValue)> function) {
    const TValue dx1 = dx;
    const TValue dx2 = 2 * dx;
    const TValue dx3 = 3 * dx;

    const TValue m1 = (function(x + dx1) - function(x - dx1)) / 2;
    const TValue m2 = (function(x + dx2) - function(x - dx2)) / 4;
    const TValue m3 = (function(x + dx3) - function(x - dx3)) / 6;

    return (m1 * 15 - m2 * 6 + m3) / (10 * dx);
}

// a = X[0]
// b = X[1]
// f = X[2]
// a' = X[3]
// b' = X[4]
// f' = X[5]
double f1(double t, std::vector<double> X) {
    return X[3];
}

double f2(double t, std::vector<double> X) {
    return X[4];
}

double f3(double t, std::vector<double> X) {
    return X[5];
}

double f4(double t, std::vector<double> X) {
    double expr1 = -2 * X[3] * J_A3 * (X[5] - X[4]) * sin(2 * X[1] - 2 * X[2]);
    double expr2 = -4 * p_3 * l_1 * X[3] * m_3 * (X[5] - X[4]) * sin(X[1] - X[2]);
    double expr3 = 2 * J_A2 * X[3] * X[4] * sin(2 * X[1]);
    double expr4 =
            (4 * l_1 * sin(X[1]) * (l_2 * m_3 + m_2 * p_2) * X[4] + 4 * p_3 * sin(X[2]) * X[5] * l_2 * m_3) * X[3] +
            2 * R_1;

    double sum_exp1 = expr1 + expr2 + expr3 + expr4;

    double expr5 = J_A3 * cos(2 * X[1] - 2 * X[2]) + 4 * cos(-X[2] + X[1]) * l_1 * m_3 * p_3;
    double expr6 = cos(2 * X[1]) * J_A2 + 4 * l_1 * (l_2 * m_3 + m_2 * p_2) * cos(X[1]);
    double expr7 = 4 * cos(X[2]) * l_2 * m_3 * p_3 + (2 * l_1 * l_1 + 2 * l_2 * l_2 + 2 * p_3 * p_3) * m_3;
    double expr8 = 2 * p_1 * p_1 * m_1 + 2 * m_2 * p_2 * p_2 + 2 * l_1 * l_1 * m_2 + J_A3 + 2 * J_g1 + 2 * J_A1 + J_A2;

    double sum_exp2 = expr5 + expr6 + expr7 + expr8;

    return sum_exp1 / sum_exp2;
}

double f5(double t, std::vector<double> X) {
    double expr1 = -2 * J_A3 * X[3] * X[3] * (2 * m_3 * p_3 * p_3 + J_g3) * sin(2 * X[1] - 2 * X[2]) -
                   J_A3 * X[3] * X[3] * l_2 * m_3 * p_3 * sin(-3 * X[2] + 2 * X[1]);
    double expr2 = -J_A3 * X[3] * X[3] * l_2 * m_3 * p_3 * sin(-X[2] + 2 * X[1]);
    double expr3 = -4 * g * p_3 * m_3 * (2 * m_3 * p_3 * p_3 + J_g3) * cos(-X[2] + X[1]);
    double expr4 = -4 * p_3 * X[3] * X[3] * l_1 * m_3 * (2 * m_3 * p_3 * p_3 + J_g3) * sin(-X[2] + X[1]);
    double expr5 = -2 * g * l_2 * m_3 * m_3 * p_3 * p_3 * cos(X[1] - 2 * X[2]);
    double expr6 = -2 * X[3] * X[3] * l_1 * l_2 * m_3 * m_3 * p_3 * p_3 * sin(X[1] - 2 * X[2]);
    double expr7 = -2 * X[3] * X[3] * J_A2 * (m_3 * p_3 * p_3 + J_A3 + J_g3) * sin(2 * X[1]);
    double expr8 = 2 * l_2 * l_2 * m_3 * m_3 * p_3 * p_3 * (X[4] * X[4] + X[3] * X[3]) * sin(2 * X[2]);

    double sum_expr1_part1 = expr1 + expr2 + expr3 + expr4 + expr5 + expr6 + expr7 + expr8;

    expr1 = -4 * p_3 * l_2 * m_3 * (J_A3 - m_3 * p_3 * p_3) * sin(X[2]);
    expr2 = 3 * p_3 * p_3 * l_2 * m_3 * m_3 / 2;
    expr3 = (p_2 * p_3 * p_3 * m_2 + l_2 * (J_A3 + J_g3)) * m_3;
    expr4 = p_2 * m_2 * (J_A3 + J_g3);
    expr5 = -4 * (expr2 + expr3 + expr4) * sin(X[1]) * l_1;

    double sum_expr1_part2 = (expr1 + expr5) * X[3] * X[3];

    expr1 = -4 * p_3 * l_2 * m_3 * (-m_3 * p_3 * p_3 + J_A3) * sin(X[2]) * X[4] * X[4];
    expr2 = 8 * p_3 * sin(X[2]) * X[5] * l_2 * m_3 * (m_3 * p_3 * p_3 + J_A3 + J_g3) * X[4];
    expr3 = 4 * p_3 * sin(X[2]) * l_2 * m_3 * (m_3 * p_3 * p_3 + J_A3 + J_g3) * X[5] * X[5];

    double sum_expr1_part3 = expr1 + expr2 + expr3;

    expr1 = 3 * p_3 * p_3 * l_2 * m_3 * m_3 / 2 + m_3 * ((l_2 * m_g3 + m_2 * p_2) * p_3 * p_3 + l_2 * (J_A3 + J_g3));
    expr2 = (l_2 * m_g3 + m_2 * p_2) * (J_A3 + J_g3);

    double sum_expr1_part4 = -4 * g * cos(X[1]) * (expr1 + expr2);

    expr1 = -4 * cos(X[2]) * R_3 * l_2 * m_3 * p_3 + 4 * p_3 * p_3 * (R_2 - R_3) * m_3;
    expr2 = (4 * R_2 + 4 * R_3) * J_A3 + 4 * J_g3 * R_2;

    double sum_expr1_part5 = expr1 + expr2;

    double sum_expr1 = sum_expr1_part1 + sum_expr1_part2 + sum_expr1_part3 + sum_expr1_part4 + sum_expr1_part5;

    expr1 = -2 * l_2 * l_2 * m_3 * m_3 * p_3 * p_3 * cos(2 * X[2]);
    expr2 = 16 * (J_A3 + J_g3 / 2) * p_3 * m_3 * l_2 * cos(X[2]) + 2 * l_2 * l_2 * m_3 * m_3 * p_3 * p_3;

    double sum_expr2_part1 = expr1 + expr2;

    expr1 = (4 * m_2 * p_2 * p_2 + 4 * J_A2 + 16 * J_A3 + 4 * J_g2 + 4 * J_g3) * p_3 * p_3;
    expr2 = 4 * l_2 * l_2 * (J_A3 + J_g3);

    double sum_expr2_part2 = (expr1 + expr2) * m_3;

    expr1 = (4 * m_2 * p_2 * p_2 + 4 * J_A2 + 4 * J_g2 + 4 * J_g3) * J_A3;
    expr2 = 4 * J_g3 * (m_2 * p_2 * p_2 + J_A2 + J_g2);

    double sum_expr2_part3 = expr1 + expr2;

    double sum_expr2 = sum_expr2_part1 + sum_expr2_part2 + sum_expr2_part3;

    return sum_expr1 / sum_expr2;
}

double f6(double t, std::vector<double> X) {
    double expr1 = (l_2 * l_2 + 2 * p_3 * p_3) * m_3 + m_2 * p_2 * p_2 + J_g2 + J_A2;
    double expr2 = 2 * X[3] * X[3] * J_A3 * sin(2 * X[1] - 2 * X[2]) * expr1;
    double expr3 = 3 * (J_A3 + J_A2 / 3) * p_3 * m_3 * X[3] * X[3] * l_2 * sin(-X[2] + 2 * X[1]);
    double expr4 = 3 * J_A3 * X[3] * X[3] * l_2 * m_3 * p_3 * sin(-3 * X[2] + 2 * X[1]);

    double sum_expr1_part1 = expr1 + expr2 + expr3 + expr4;

    expr1 = (2 * p_3 * p_3 + 3 * l_2 * l_2 / 2) * m_3 + m_g3 * l_2 * l_2 / 2;
    expr2 = m_2 * p_2 * p_2 + p_2 * l_2 * m_2 / 2 + J_g2 + J_A2;
    expr3 = 4 * (expr1 + expr2) * p_3 * m_3 * g * cos(-X[2] + X[1]);

    double sum_expr1_part2 = expr3;

    expr1 = 4 * p_3 * m_3 * X[3] * X[3] * l_1;
    expr2 = (2 * p_3 * p_3 + 3 * l_2 * l_2 / 2) * m_3 + m_2 * p_2 * p_2 + p_2 * l_2 * m_2 / 2 + J_g2 + J_A2;

    double sum_expr1_part3 = expr1 * expr2 * sin(-X[2] + X[1]);

    expr1 = 6 * g * l_2 * m_3 * m_3 * p_3 * p_3 * cos(X[1] - 2 * X[2]);
    expr2 = 6 * X[3] * X[3] * l_1 * l_2 * m_3 * m_3 * p_3 * p_3 * sin(X[1] - 2 * X[2]);
    expr3 = J_A2 * X[3] * X[3] * l_2 * m_3 * p_3 * sin(2 * X[1] + X[2]);

    double sum_expr1_part4 = expr1 + expr2 + expr3;

    expr1 = 2 * g * p_3 * l_2 * m_3 * (l_2 * m_3 + l_2 * m_g3 + m_2 * p_2) * cos(X[1] + X[2]);
    expr2 = 2 * p_3 * X[3] * X[3] * l_1 * l_2 * m_3 * (l_2 * m_3 + m_2 * p_2) * sin(X[1] + X[2]);
    expr3 = -2 * l_2 * l_2 * m_3 * m_3 * p_3 * p_3 *
            (X[5] * X[5] + 2 * X[5] * X[4] + 2 * X[4] * X[4] + 2 * X[3] * X[3]) * sin(2 * X[2]);
    expr4 = -2 * X[3] * X[3] * J_A2 * (-m_3 * p_3 * p_3 + J_A3) * sin(2 * X[1]);

    double sum_expr1_part5 = expr1 + expr2 + expr3 + expr4;

    expr1 = (l_2 * l_2 + p_3 * p_3) * m_3 + m_2 * p_2 * p_2 + J_A3 + J_g2 + J_A2;
    expr2 = -4 * p_3 * m_3 * l_2 * sin(X[2]) * expr1;
    expr3 = (-5 * p_3 * p_3 * l_2 * m_3 * m_3 / 2 + (-p_2 * p_3 * p_3 * m_2 + J_A3 * l_2) * m_3 + J_A3 * p_2 * m_2) *
            (-4 * sin(X[1]) * l_1);
    expr4 = (expr2 + expr3) * X[3] * X[3];

    double sum_expr1_part6 = expr4;

    expr1 = -4 * p_3 * m_3 * l_2 * ((l_2 * l_2 + p_3 * p_3) * m_3 + m_2 * p_2 * p_2 + J_A3 + J_g2 + J_A2) * sin(X[2]) *
            X[4] * X[4];
    expr2 = 8 * p_3 * sin(X[2]) * X[5] * l_2 * m_3 * (-m_3 * p_3 * p_3 + J_A3) * X[4];
    expr3 = 4 * p_3 * l_2 * m_3 * (-m_3 * p_3 * p_3 + J_A3) * sin(X[2]) * X[5] * X[5];

    double sum_expr1_part7 = expr1 + expr2 + expr3;

    expr1 = -5 * p_3 * p_3 * l_2 * m_3 * m_3 / 2 + ((-l_2 * m_g3 - m_2 * p_2) * p_3 * p_3 + J_A3 * l_2) * m_3 +
            J_A3 * (l_2 * m_g3 + m_2 * p_2);
    expr2 = -4 * g * cos(X[1]) * expr1;

    double sum_expr1_part8 = expr2;

    expr1 = -4 * p_3 * l_2 * m_3 * (R_2 - 2 * R_3) * cos(X[2]);
    expr2 = ((-4 * R_2 + 4 * R_3) * p_3 * p_3 + 4 * R_3 * l_2 * l_2) * m_3;
    expr3 = (4 * R_2 + 4 * R_3) * J_A3 + 4 * R_3 * (m_2 * p_2 * p_2 + J_A2 + J_g2);

    double sum_expr1_part9 = expr1 + expr2 + expr3;

    double sum_expr1 =
            sum_expr1_part1 + sum_expr1_part2 + sum_expr1_part3 + sum_expr1_part4 + sum_expr1_part5 + sum_expr1_part6 +
            sum_expr1_part7 + sum_expr1_part8 + sum_expr1_part9;

    expr1 = -2 * l_2 * l_2 * m_3 * m_3 * p_3 * p_3 * cos(2 * X[2]);
    expr2 = 16 * (J_A3 + J_g3 / 2) * p_3 * m_3 * l_2 * cos(X[2]) + 2 * l_2 * l_2 * m_3 * m_3 * p_3 * p_3;

    double sum_expr2_part1 = expr1 + expr2;

    expr1 = ((4 * m_2 * p_2 * p_2 + 4 * J_A2 + 16 * J_A3 + 4 * J_g2 + 4 * J_g3) * p_3 * p_3 +
             4 * l_2 * l_2 * (J_A3 + J_g3)) * m_3;
    expr2 = (4 * m_2 * p_2 * p_2 + 4 * J_A2 + 4 * J_g2 + 4 * J_g3) * J_A3 + 4 * J_g3 * (m_2 * p_2 * p_2 + J_A2 + J_g2);

    double sum_expr2_part2 = expr1 + expr2;

    double sum_expr2 = sum_expr2_part1 + sum_expr2_part2;

    return sum_expr1 / sum_expr2;
}

int main(int argc, const char **argv) {
//    std::vector<double> ics = {195.34, 287.78,152.8 , 2.15, -3.34, 9.07};
    std::vector<double> ics = {0.5, 1, -2.3, 0.2, 0, 0};
    std::vector<std::function<double(double, std::vector<double>)>> functions;
    std::function<double(double, std::vector<double>)> fu1 = f1;
    std::function<double(double, std::vector<double>)> fu2 = f2;
    std::function<double(double, std::vector<double>)> fu3 = f3;
    std::function<double(double, std::vector<double>)> fu4 = f4;
    std::function<double(double, std::vector<double>)> fu5 = f5;
    std::function<double(double, std::vector<double>)> fu6 = f6;

    functions.push_back(fu1);
    functions.push_back(fu2);
    functions.push_back(fu3);
    functions.push_back(fu4);
    functions.push_back(fu5);
    functions.push_back(fu6);


    DiffSystem De_sys = DiffSystem(functions, ics, 0, 0.8);
    DiffSolution solution = De_sys.solve(10000);

    solution.print();
    solution.plot_2d({0, 1});

//    solution.plot_3d({1, 2, 3});
    //  solution.plot_3d({0,1,2});
    //
    return 0;
}
