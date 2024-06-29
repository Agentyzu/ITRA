# -*- coding: utf-8 -*-
"""
@Time ： 2024-06
@Auth ： peng tian
@File ：visual.py
@IDE ：PyCharm
"""
import random
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from task import Task

def generate_random_position():
    return [random.randint(5, 95), random.randint(5, 95)]

class VisualSimulator:
    def __init__(self, uavs, tasks, results, simulation_steps=1000, reallocate_time=100):
        self.uavs = {uav.id: uav for uav in uavs}
        self.tasks = {task.id: task for task in tasks}
        self.results = results
        self.simulation_steps = simulation_steps
        self.reallocate_time = reallocate_time
        self.time_step = 0
        self.colors = ['r', 'g', 'b', 'm', 'c', 'y']
        self.marker = '>'
        self.no_solution = False
        # 初始化子图，创建1x4的网格
        self.fig, self.axes = plt.subplots(1, 4, figsize=(20, 5))
        plt.rcParams['font.family'] = 'Arial'
        plt.rcParams['font.size'] = 15

    def plot_state(self, ax):
        ax.clear()

        # 绘制每个UAV的位置、路径及任务
        for idx, uav in enumerate(self.uavs.values()):
            color = self.colors[idx % len(self.colors)]
            marker = self.marker

            # 绘制UAV当前的位置
            ax.plot(uav.position[0], uav.position[1], f'{color}{marker}' if uav.working else 'kx', markersize=10)
            ax.text(uav.position[0], uav.position[1], f'$U_{{{uav.id}}}$', fontsize=10, ha='right')

            # 绘制已完成的飞行路径
            flight_path = np.array(uav.flight_path)
            if len(flight_path) > 1:
                ax.plot(flight_path[:, 0], flight_path[:, 1], f'{color}-')

            # 绘制计划的任务路径
            if hasattr(uav, 'task_sequence') and uav.task_sequence:
                task_positions = [self.tasks[task_id].position for task_id in uav.task_sequence]
                task_positions.insert(0, uav.position)
                task_positions = np.array(task_positions)
                ax.plot(task_positions[:, 0], task_positions[:, 1], f'{color}--')

        # 绘制任务的位置及状态
        for task in self.tasks.values():
            status_color = 'go' if not task.completed else 'gx'
            ax.plot(task.position[0], task.position[1], status_color)
            ax.text(task.position[0], task.position[1], f'$T_{{{task.id}}}$', fontsize=10, ha='left')

        # 为图例创建虚拟对象
        for idx, color in enumerate(self.colors[:len(self.uavs)]):
            ax.plot([], [], f'{color}{self.marker}', label=f'$U_{{{idx + 1}}}$ Working')
            ax.plot([], [], f'{color}-', label=f'$U_{{{idx + 1}}}$ Completed Path')
            ax.plot([], [], f'{color}--', label=f'$U_{{{idx + 1}}}$ Planned Path')

        ax.plot([], [], 'go', label='Pending Task')
        ax.plot([], [], 'gx', label='Completed Task')

        # 设置标题、坐标轴范围及网格
        ax.set_title(f"Time Step: {self.time_step}")
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.grid()

        # 添加箭头坐标轴
        ax.spines['left'].set_position('zero')
        ax.spines['bottom'].set_position('zero')

        # 移除顶部和右侧的边框
        ax.spines['right'].set_color('none')
        ax.spines['top'].set_color('none')

        # 设置x轴和y轴刻度在底部和左侧
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')

        # 添加箭头
        ax.plot(1, 0, '>k', transform=ax.get_yaxis_transform(), clip_on=False)
        ax.plot(0, 1, '^k', transform=ax.get_xaxis_transform(), clip_on=False)

    def run_simulation(self):
        for result in self.results:
            uav_id = result['uav_id']
            uav = self.uavs[uav_id]
            best_sequence = result['best_sequence']

            if best_sequence != "超出剩余能量，无输出解":
                uav.task_sequence = [task['task_id'] for task in best_sequence]
            else:
                self.no_solution = True
            uav.flight_path = [uav.position]
            uav.completed_tasks = []
            uav.task_completion_times = {}

        # 绘制初始状态
        self.plot_state(self.axes[0])

        for _ in range(self.simulation_steps):
            self.time_step += 1

            if self.time_step == self.reallocate_time:
                self.reallocate_tasks()

            self.update_positions()

            # 在指定时间步绘制状态
            if self.time_step == 5:
                self.plot_state(self.axes[1])
            if self.time_step == 8:
                self.plot_state(self.axes[2])
            if self.time_step == 11:
                self.plot_state(self.axes[3])

            if all(task.completed for task in self.tasks.values()):
                break

        # 汇总所有子图的图例句柄和标签
        handles, labels = [], []
        for ax in self.axes:
            for handle, label in zip(*ax.get_legend_handles_labels()):
                if label not in labels:
                    labels.append(label)
                    handles.append(handle)

        # 创建图例并放置在所有子图下方
        # plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        self.fig.legend(handles, labels, loc='upper right', bbox_to_anchor=(1.001, 0.93),ncol=1,fontsize=10)
        plt.show()

# 模拟UAV、任务以及结果数据的代码
    def reallocate_tasks(self):
        print(f"发现新增任务们开始重规划 {self.time_step}...")

        tasks = [task for task in self.tasks.values() if not task.completed]
        new_tasks = self.custom_new_tasks()
        for task in new_tasks:
            self.tasks[task.id] = task
            tasks.append(task)

        new_task_positions = [task.position for task in new_tasks]
        kmeans = KMeans(n_clusters=1)
        kmeans.fit(new_task_positions)
        cluster_center = kmeans.cluster_centers_[0]
        new_cluster_tasks = [new_tasks[i] for i in range(len(new_tasks))]

        uav_distances = [(uav.id, np.linalg.norm(np.array(uav.position) - cluster_center)) for uav in
                         self.uavs.values()]
        uav_distances.sort(key=lambda x: x[1])

        m = 1
        max_m = len(uav_distances)

        while m <= max_m:
            selected_uavs = [self.uavs[uav_distances[i][0]] for i in range(min(m, max_m))]
            tasks_for_reallocation = new_cluster_tasks[:]
            for uav in selected_uavs:
                if hasattr(uav, 'task_sequence'):
                    incomplete_tasks = [self.tasks[task_id] for task_id in uav.task_sequence if
                                        not self.tasks[task_id].completed]
                    tasks_for_reallocation.extend(incomplete_tasks)

            print(f"m={m}时，参与重分配的无人机有：{[uav.id for uav in selected_uavs]}")

            from preplanning import plan_tasks_and_uavs
            results = plan_tasks_and_uavs(tasks_for_reallocation, selected_uavs)

            no_solution = any(result['best_sequence'] == "超出剩余能量，无输出解" for result in results)

            if not no_solution:
                for result in results:
                    uav_id = result['uav_id']
                    uav = self.uavs[uav_id]
                    best_sequence = result['best_sequence']

                    if best_sequence != "超出剩余能量，无输出解":
                        uav.task_sequence = [task['task_id'] for task in best_sequence]

                self.results = results
                # 输出重分配后的任务序列和飞行过程信息
                for uav in selected_uavs:
                    print(f"UAV {uav.id} 重分配后的任务序列为: {uav.task_sequence}")
                return
            else:
                print(f"m={m}时，无解。")
                m += 1

        print("任务分配存在超出剩余能量的情况，无法完成所有任务。")
        self.no_solution = True
        self.results = results

    def custom_new_tasks(self):
        new_tasks = [
            Task(id=29, position=[47, 82], required_energy=10, value=100),
            Task(id=30, position=[45, 89], required_energy=20, value=200),
            Task(id=31, position=[46, 94], required_energy=20, value=200)
        ]
        return new_tasks

    def update_positions(self):
        for uav in self.uavs.values():
            if uav.working and hasattr(uav, 'task_sequence') and uav.task_sequence:
                remaining_time = 1
                while remaining_time > 0 and uav.task_sequence:
                    current_task_id = uav.task_sequence[0]
                    current_task = self.tasks[current_task_id]
                    distance = np.linalg.norm(np.array(current_task.position) - np.array(uav.position))
                    time_to_task = distance / uav.speed

                    if remaining_time >= time_to_task:
                        uav.position = current_task.position
                        uav.flight_path.append(uav.position)
                        uav.task_sequence.pop(0)
                        uav.completed_tasks.append(current_task_id)
                        uav.task_completion_times[current_task_id] = self.time_step
                        current_task.completed = True
                        remaining_time -= time_to_task
                        print(f"UAV {uav.id} 完成任务 T{current_task_id} 在时刻 {self.time_step}")
                    else:
                        direction = (np.array(current_task.position) - np.array(uav.position)) / np.linalg.norm(
                            np.array(current_task.position) - np.array(uav.position))
                        move_distance = remaining_time * uav.speed
                        uav.position = tuple(np.array(uav.position) + move_distance * direction)
                        uav.flight_path.append(uav.position)
                        remaining_time = 0

