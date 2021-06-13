cmake_minimum_required(VERSION 3.13)
project(diff_eq_solution)

set(CMAKE_CXX_STANDARD 14)

add_executable(diff_eq_solution main.cpp DiffSystem.cpp DiffSolution.cpp)

#find_package(Python3 COMPONENTS Development)
#target_include_directories(diff_eq_solution PRIVATE ${Python3_INCLUDE_DIRS})
#target_link_libraries(diff_eq_solution Python3::Python)

find_package(Python3 COMPONENTS Development NumPy)
target_include_directories(diff_eq_solution PRIVATE ${Python3_INCLUDE_DIRS} ${Python3_NumPy_INCLUDE_DIRS})
target_link_libraries(diff_eq_solution Python3::Python Python3::NumPy)