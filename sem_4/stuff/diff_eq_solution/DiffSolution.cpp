#include "DiffSolution.h"
#include "matplotlibcpp.h"
#include "spider_constants.h"

#include <fstream>
#include <cmath>
#include <vector>

void DiffSolution::print() const {
    if (is_empty()) {
        std::cout << "Uninitialized solution\n";
        return;
    }

    for (const auto &elem: *values) {
        std::cout.precision(6);
        std::cout << std::scientific << elem.first << " ";
        for (const auto &val : elem.second) {
            std::cout << val << " ";
        }
        std::cout << std::endl;
    }
}

void DiffSolution::write_to_file(const std::string file_name) const {
    if (is_empty()) {
        std::cout << "Uninitialized solution\n";
        return;
    }

    std::ofstream fout;
    fout.open(file_name);

    if (fout.is_open()) {
        for (const auto &elem: *values) {
            if (fout.is_open())
                fout.precision(4);
            fout << std::scientific << elem.first << " ";
            for (const auto &val : elem.second) {
                fout << val << " ";
            }
            fout << std::endl;
        }
    } else {
        throw std::runtime_error("error while opening file");
    }
    fout.close();
}

void DiffSolution::plot_2d(std::pair<int, int> scene) const {
    namespace plt = matplotlibcpp;

    std::vector<double> abscissas;
    std::vector<double> ordinates;

    int i1 = scene.first;
    int i2 = scene.second;

    if (i1 == 0) {
        for (const auto &elem: *values) {
            abscissas.push_back(elem.first);
            ordinates.push_back(elem.second[i2 - 1]);
        }
    } else if (i2 == 0) {
        for (const auto &elem: *values) {
            abscissas.push_back(elem.second[i1 - 1]);
            ordinates.push_back(elem.first);
        }
    } else {
        for (const auto &elem: *values) {
            abscissas.push_back(elem.second[i1 - 1]);
            ordinates.push_back(elem.second[i2 - 1]);
        }
    }

    plt::figure();
    plt::plot(abscissas, ordinates);
    plt::show();
}

void DiffSolution::plot_3d(std::vector<int> scene) const {
    namespace plt = matplotlibcpp;

    std::vector<double> abscissas;
    std::vector<double> ordinates;
    std::vector<double> applicates;

    int i1 = scene[0];
    int i2 = scene[1];
    int i3 = scene[3];

    if (i1 == 0) {
        for (const auto &elem:*values) {
            abscissas.push_back(elem.first);
            ordinates.push_back(elem.second[i2 - 1]);
            applicates.push_back(elem.second[i3 - 1]);
        }
    } else if (i2 == 0) {
        for (const auto &elem:*values) {
            abscissas.push_back(elem.second[i1 - 1]);
            ordinates.push_back(elem.first);
            applicates.push_back(elem.second[i3 - 1]);
        }
    } else if (i3 == 0) {
        for (const auto &elem:*values) {
            abscissas.push_back(elem.second[i1 - 1]);
            ordinates.push_back(elem.second[i2 - 1]);
            applicates.push_back(elem.first);
        }
    } else {
        for (const auto &elem:*values) {
            abscissas.push_back(elem.second[i1 - 1]);
            ordinates.push_back(elem.second[i2 - 1]);
            applicates.push_back(elem.second[i3 - 1]);
        }
    }

    std::vector<std::vector<double>> x, y, z;
    x.push_back(abscissas);
    y.push_back(ordinates);
    z.push_back(applicates);
    plt::plot3(abscissas, ordinates, applicates);
    plt::show();
}

//void DiffSolution::animate() const {
//    namespace plt = matplotlibcpp;
//    std::vector<double> x;
//    std::vector<double> y;
//    std::vector<double> z;
//
//    int i = 0;
//
//    for (const auto &elem: *values) {
//        x.push_back(i);
//        y.push_back(0);
//        double k = tan(elem.second[0]);
//        z.push_back(k*i);
//        if (i % 10 == 0) {
//            plt::clf();
//
//            plt::plot(x, z);
//
//         //   plt::xlim(0,int( l_1*cos(elem.second[0])));
//
//            plt::pause(0.01);
//        }
//        ++i;
//    }
//}