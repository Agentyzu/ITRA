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
    """
    使用KMeans算法将任务划分为若干子任务

    :param task_positions: 任务的坐标列表 [(x1, y1), (x2, y2), ...]
    :param k: 子任务的数量，即无人机的数量
    :return: 子任务中心点的坐标，以及各个子任务里的任务id，格式为
             (cluster_centers, task_clusters)，其中
             cluster_centers 是子任务中心点的坐标列表 [(cx1, cy1), (cx2, cy2), ...]，
             task_clusters 是子任务里的任务id字典 {cluster_id: [task_id1, task_id2, ...], ...}
    """
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(task_positions)

    cluster_centers = kmeans.cluster_centers_
    labels = kmeans.labels_

    task_clusters = {i+1: [] for i in range(k)}
    for task_id, label in enumerate(labels):
        task_clusters[label + 1].append(task_id + 1)  # 任务ID从1开始，簇ID也从1开始

    return cluster_centers, task_clusters


