#include "DiffSystem.h"
#include "stdexcept"

using std::vector;
using std::function;

//vector sum
vector<double> operator+(const vector<double> &v1, const vector<double> &v2) {
    if (v1.size() != v2.size()) throw std::length_error("unequal sizes");

    vector<double> v3(v2.size());
    for (int i = 0; i < v2.size(); ++i) {
        v3[i] = v1[i] + v2[i];
    }
    return v3;
}

//vector scalar right multiply
vector<double> operator*(const vector<double> &v1, const double h) {
    vector<double> v3(v1.size());
    for (int i = 0; i < v1.size(); ++i) {
        v3[i] = v1[i] * h;
    }
    return v3;
}

//vector scalar left multiply
vector<double> operator*(const double h, const vector<double> &v1) {
    return v1 * h;
}

//value of vector-function
vector<double> v_func_value(const vector<function<double(double, vector<double>)>> &v1,
                            const double t, const vector<double> &X) {
    vector<double> res_v(v1.size());
    for (int i = 0; i < res_v.size(); ++i) {
        res_v[i] = v1[i](t, X);
    }
    return res_v;
}

//rk4
DiffSolution DiffSystem::solve(const int iter_count) const {
    int n = iter_count;
    double h = (t_end_ - t_start_) / n; //step-size

    vector<std::pair<double, vector<double>>> solution;
    solution.push_back({t_start_, ics_});

    quaternary<vector<double>> K(vector<double>(this->order_), vector<double>(this->order_),
                                 vector<double>(this->order_),
                                 vector<double>(this->order_));

    const double a1 = 0.166666666666;
    const double a2 = 0.333333333333;
    const double a3 = 0.333333333333;
    const double a4 = 0.166666666666;
    for (int i = 1; i <= n; ++i) {
        double t_i = t_start_ + i * h;

        vector<double> x_i = solution[i - 1].second;
        //Calculate K
        calculate_K(x_i, K, t_i - h, h);


        solution.push_back(
                {t_i, x_i + a1 * K.i_1 + a2 * K.i_2 + a3 * K.i_3 + a4 * K.i_4});
    }

    return DiffSolution(solution);
}

void DiffSystem::calculate_K(const vector<double> &x_i, quaternary<vector<double>> &K, const double t_i,
                             const double h) const {
    K.i_1 = h * v_func_value(functions_, t_i, x_i);
    K.i_2 = h * v_func_value(functions_, t_i + h / 2, x_i + 0.5 * K.i_1);
    K.i_3 = h * v_func_value(functions_, t_i + h / 2, x_i + 0.5 * K.i_2);
    K.i_4 = h * v_func_value(functions_, t_i + h, x_i + K.i_3);
}