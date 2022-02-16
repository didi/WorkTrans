# -*- coding: utf-8 -*-
import numpy as np


# 返回为0的个数
def get_zero_num(input_num_array):
    return len(input_num_array) - len(np.nonzero(input_num_array)[0])


# 返回中位数
def get_median(input_num_array):
    return np.median(input_num_array)


# 返回算数平均数(加权平均数使用np.average方法)
def get_average(input_num_array):
    return np.mean(input_num_array)


# 返回方差
def get_variance(input_num_array):
    return np.var(input_num_array)


# 获取分位数(3个四分位数即Q1:q=25,Q2:q=50,Q3:q=75)
def percentile(input_num_array, q):
    result = np.percentile(input_num_array, q)
    return result


# 获取小于分位数的数据量
def percentile_less_count(input_num_array, q):
    np_array = np.array(input_num_array)
    percentile_val = percentile(input_num_array, q)
    filter_np_array = np.where(np_array < percentile_val)
    return len(filter_np_array[0])


# 获取大于分位数的数据量
def percentile_more_count(input_num_array, q):
    np_array = np.array(input_num_array)
    percentile_val = percentile(input_num_array, q)
    filter_np_array = np.where(np_array > percentile_val)
    return len(filter_np_array[0])


if __name__ == '__main__':
    npa = np.array([1, 1, 2, 3, 4, 5, 6, 7], dtype=np.dtype(np.float64))
    print(percentile_more_count(npa, 35))
