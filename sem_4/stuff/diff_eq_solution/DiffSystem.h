#ifndef DIFF_EQ_SOLUTION_DIFFSYSTEM_H
#define DIFF_EQ_SOLUTION_DIFFSYSTEM_H

#include <functional>
#include <vector>
#include <unordered_map>

#include "quaternary.h"
#include "DiffSolution.h"

///Normal DE system class
class DiffSystem {
public:
    DiffSystem(const std::vector<std::function<double(double, std::vector<double>)>> &functions,
               const std::vector<double> ics, double t_start, double t_end) : functions_(functions),
                                                                              order_(functions.size()),
                                                                              ics_(ics), t_start_(t_start),
                                                                              t_end_(t_end){}

    std::vector<std::function<double(double, std::vector<double>)>> functions() const { return functions_; }

    int order() const { return order_; }

    std::vector<double> ics() const { return ics_; }

    double t_start() const { return t_start_; }

    double t_end() const { return t_end_; }

    DiffSolution solve(int iter_count) const;

    ~DiffSystem() = default;

private:
    void calculate_K(const std::vector<double> &x_i, quaternary<std::vector<double>> &K, double t_i,
                     double h) const;


private:
    std::vector<std::function<double(double, std::vector<double>)>> functions_;
    int order_;
    std::vector<double> ics_;
    double t_start_;
    double t_end_;
};

#endif //DIFF_EQ_SOLUTION_DIFFSYSTEM_H
