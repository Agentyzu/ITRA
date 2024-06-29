# -*- coding: utf-8 -*-
"""
@Time ： 2024-06
@Auth ： peng tian
@File ：visual.py
@IDE ：PyCharm
"""
import random
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from task import Task

def generate_random_position():
    return [random.randint(5, 95), random.randint(5, 95)]
class VisualSimulator:
    def __init__(self, uavs, tasks, results, simulation_steps=1000000, reallocate_time=100):
        self.uavs = {uav.id: uav for uav in uavs}
        self.tasks = {task.id: task for task in tasks}
        self.results = results
        self.simulation_steps = simulation_steps
        self.reallocate_time = reallocate_time  # 重新分配的时间步
        self.time_step = 0
        self.colors = ['r', 'g', 'b', 'm', 'c', 'y']
        self.marker = '>'
        self.no_solution = False  # 添加状态标志
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.plot_state()

    def plot_state(self):
        self.ax.clear()

        for idx, uav in enumerate(self.uavs.values()):
            color = self.colors[idx % len(self.colors)]
            marker = self.marker

            self.ax.plot(uav.position[0], uav.position[1], f'{color}{marker}' if uav.working else 'kx', markersize=10)
            self.ax.text(uav.position[0], uav.position[1], f'U{uav.id}', fontsize=10, ha='right')

            flight_path = np.array(uav.flight_path)
            if len(flight_path) > 1:
                self.ax.plot(flight_path[:, 0], flight_path[:, 1], f'{color}-')

            if hasattr(uav, 'task_sequence') and uav.task_sequence:
                task_positions = [self.tasks[task_id].position for task_id in uav.task_sequence]
                task_positions.insert(0, uav.position)
                task_positions = np.array(task_positions)
                self.ax.plot(task_positions[:, 0], task_positions[:, 1], f'{color}--')

        for task in self.tasks.values():
            status_color = 'go' if not task.completed else 'gx'
            self.ax.plot(task.position[0], task.position[1], status_color)
            self.ax.text(task.position[0], task.position[1], f'$T_{{{task.id}}}$', fontsize=10, ha='left')

        for idx, color in enumerate(self.colors[:len(self.uavs)]):
            self.ax.plot([], [], f'{color}{self.marker}', label=f'$U_{{{idx + 1}}}$ Working')
            self.ax.plot([], [], f'{color}-', label=f'$U_{{{idx + 1}}}$ Completed Path')
            self.ax.plot([], [], f'{color}--', label=f'$U_{{{idx + 1}}}$ Planned Path')

        self.ax.plot([], [], 'go', label='Pending Task')
        self.ax.plot([], [], 'gx', label='Completed Task')

        self.ax.set_title(f"Time Step: {self.time_step}")
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.grid()
        self.ax.legend()
        plt.pause(1)
    def run_simulation(self):
        for result in self.results:
            uav_id = result['uav_id']
            uav = self.uavs[uav_id]
            best_sequence = result['best_sequence']

            if best_sequence != "超出剩余能量，无输出解":
                uav.task_sequence = [task['task_id'] for task in best_sequence]
            else:
                self.no_solution = True  # 设置无解标志
            uav.flight_path = [uav.position]
            uav.completed_tasks = []
            uav.task_completion_times = {}

        self.plot_state()

        for _ in range(self.simulation_steps):
            self.time_step += 1

            if self.time_step == self.reallocate_time:
                self.reallocate_tasks()

            self.update_positions()
            self.plot_state()

            if all(task.completed for task in self.tasks.values()):
                self.save_figure("simulation_result.png")
                break

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
                self.plot_state()
                print(f"m={m}时，参与重分配的无人机有：{[uav.id for uav in selected_uavs]}，完成重分配。")
                for uav in selected_uavs:
                    print(f"UAV {uav.id} 任务序列: {uav.task_sequence}")
                return
            else:
                print(f"m={m}时，无解。")
                m += 1

        print("任务分配存在超出剩余能量的情况，无法完成所有任务。")
        self.no_solution = True
        self.results = results
        self.plot_state()

    def custom_new_tasks(self):
        # 自定义新任务
        new_tasks = [
            Task(id=11, position=[47, 62], required_energy=10, value=100),
            Task(id=12, position=[45, 39], required_energy=20, value=200),
            Task(id=13, position=[46, 74], required_energy=20, value=200)
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
                        current_task.completed = True  # 设置任务完成
                        remaining_time -= time_to_task
                        print(f"UAV {uav.id} 完成任务 T{current_task_id} 在时刻 {self.time_step}")
                    else:
                        direction = (np.array(current_task.position) - np.array(uav.position)) / np.linalg.norm(
                            np.array(current_task.position) - np.array(uav.position))
                        move_distance = remaining_time * uav.speed
                        uav.position = tuple(np.array(uav.position) + move_distance * direction)
                        uav.flight_path.append(uav.position)
                        remaining_time = 0

    def save_figure(self, filename):
        self.fig.savefig(filename)