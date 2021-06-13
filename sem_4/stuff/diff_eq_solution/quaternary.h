#ifndef DIFF_EQ_SOLUTION_QUATERNARY_H
#define DIFF_EQ_SOLUTION_QUATERNARY_H

template<class T>
struct quaternary {
    quaternary() = default;

    quaternary(const T &i_1, const T &i_2, const T &i_3, const T &i_4) : i_1(i_1), i_2(i_2), i_3(i_3), i_4(i_4) {}

    T i_1;
    T i_2;
    T i_3;
    T i_4;
};


#endif //DIFF_EQ_SOLUTION_QUATERNARY_H
