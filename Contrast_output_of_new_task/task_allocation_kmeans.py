# -*- coding: utf-8 -*-
"""
@Time ： 2024-06
@Auth ： peng tian
@File ：task.py
@IDE ：PyCharm
"""
import numpy as np
from sklearn.cluster import KMeans

def kmeans_task_clustering(task_positions, k):
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(task_positions)

    cluster_centers = kmeans.cluster_centers_
    labels = kmeans.labels_

    task_clusters = {i+1: [] for i in range(k)}
    for task_id, label in enumerate(labels):
        task_clusters[label + 1].append(task_id + 1)  # 任务ID从1开始，簇ID也从1开始

    return cluster_centers, task_clusters


