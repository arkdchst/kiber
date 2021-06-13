#ifndef DIFF_EQ_SOLUTION_DIFFSOLUTION_H
#define DIFF_EQ_SOLUTION_DIFFSOLUTION_H

#include <vector>
#include <iostream>
#include <string>


class DiffSolution {
public:
    DiffSolution() : values(nullptr) {}

    DiffSolution(const std::vector<std::pair<double, std::vector<double>>> &solution) {
        values = new std::vector<std::pair<double, std::vector<double>>>(solution);
    }

    bool is_empty() const {
        return values == nullptr;
    }

    std::vector<std::pair<double, std::vector<double>>> get_values() const {
        return *values;
    }

    void print() const;

    // scene determines the axes of the plot
    // 0 - t
    // 1 - x
    // 2 - y
    // 3 - z
    void plot_2d(std::pair<int, int> scene) const;

    void plot_3d(std::vector<int> scene) const;

    void write_to_file(std::string file_name = "data.txt") const;

//    void animate() const;

    ~DiffSolution() {
        delete values;
    }

private:
    std::vector<std::pair<double, std::vector<double>>> *values;
};


#endif //DIFF_EQ_SOLUTION_DIFFSOLUTION_H
