# -*- coding: utf-8 -*-
"""
@Time ： 2024-06
@Auth ： peng tian
@File ：hungarian_algorithm.py
@IDE ：PyCharm
"""
import numpy as np
from scipy.optimize import linear_sum_assignment

def hungarian_algorithm(uavs, cluster_centers):
    k = len(uavs)
    cost_matrix = np.zeros((k, k))

    for i, uav in enumerate(uavs):
        for j, center in enumerate(cluster_centers):
            cost_matrix[i, j] = np.linalg.norm(np.array(uav.position) - np.array(center))

    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    assignments = {uavs[i]: col_ind[i] + 1 for i in range(len(uavs))}
    return assignments
