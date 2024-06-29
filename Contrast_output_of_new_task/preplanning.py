from task_allocation_kmeans import kmeans_task_clustering
from hungarian_algorithm import hungarian_algorithm
from genetic_algorithm import genetic_algorithm
import numpy as np
# -*- coding: utf-8 -*-
"""
@Time ： 2024-06
@Auth ： peng tian
@File ：preplanning.py
@IDE ：PyCharm
"""
def plan_tasks_and_uavs(tasks, uavs):
    # 过滤出工作的无人机
    working_uavs = [uav for uav in uavs if uav.working]

    # 使用 k-means 算法将任务划分为若干子任务
    k = len(working_uavs)
    task_positions = [task.position for task in tasks]
    cluster_centers, task_clusters = kmeans_task_clustering(task_positions, k)

    # 使用匈牙利算法将子任务中心点分配给无人机
    assigned_uavs = hungarian_algorithm(working_uavs, cluster_centers)

    results = []

    # 输出每个无人机分配的任务簇并使用遗传算法优化任务序列
    for uav, cluster_id in assigned_uavs.items():
        uav_result = {
            'uav_id': uav.id,
            'cluster_id': cluster_id,
            'assigned_tasks': [],
            'uav_position': uav.position  # 将起始位置添加到结果中
        }

        assigned_tasks = [tasks[task_id - 1] for task_id in task_clusters[cluster_id]]
        for task in assigned_tasks:
            uav_result['assigned_tasks'].append({
                'task_id': task.id,
                'position': task.position,
                'required_energy': task.required_energy
            })

        # 使用遗传算法优化无人机的任务序列
        best_tasks, best_energy_cost = genetic_algorithm(uav, assigned_tasks)
        if best_tasks == "超出剩余能量，无输出解":
            uav_result['best_sequence'] = "超出剩余能量，无输出解"
            uav_result['best_energy_cost'] = "超出剩余能量，无输出解"
            uav_result['best_task_value'] = "超出剩余能量，无输出解"
            uav_result['task_completion_times'] = []  # 添加空的任务完成时刻列表
        else:
            # 计算最佳任务序列的能量消耗和总价值
            best_energy_cost = 0
            best_task_value = 0
            current_position = uav.position
            task_completion_times = []
            for task in best_tasks:
                task_position = task.position  # 获取任务位置
                task_energy_cost = np.linalg.norm(
                    np.array(current_position) - np.array(task_position)) * uav.fuel_consumption + task.required_energy
                best_energy_cost += task_energy_cost
                best_task_value += task.value  # 假设任务对象有一个名为 value 的属性，表示任务价值

                # 计算任务完成时间并添加到列表中
                distance = np.linalg.norm(np.array(current_position) - np.array(task_position))
                travel_time = distance / uav.speed
                task_completion_times.append(travel_time)

                current_position = task_position

            uav_result['best_sequence'] = []
            for task, completion_time in zip(best_tasks, task_completion_times):
                uav_result['best_sequence'].append({
                    'task_id': task.id,
                    'position': task.position,
                    'required_energy': task.required_energy,
                    'completion_time': completion_time  # 将完成时间加入任务序列
                })
            uav_result['best_energy_cost'] = best_energy_cost
            uav_result['best_task_value'] = best_task_value
            uav_result['task_completion_times'] = task_completion_times

        results.append(uav_result)

    return results
