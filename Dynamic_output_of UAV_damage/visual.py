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
from preplanning import plan_tasks_and_uavs
def generate_random_position():
    return [random.randint(0, 99), random.randint(0, 99)]

class VisualSimulator:
    def __init__(self, uavs, tasks, results, simulation_steps=1000000, reallocate_time=100, destroyed_uav_schedule=None):
        self.uavs = {uav.id: uav for uav in uavs}
        self.tasks = {task.id: task for task in tasks}
        self.results = results
        self.simulation_steps = simulation_steps
        self.reallocate_time = reallocate_time  # 重新分配的时间步
        self.time_step = 0
        self.colors = ['r', 'g', 'b', 'm', 'c', 'y', 'k']
        self.marker = '>'
        self.destroyed_uav_schedule = destroyed_uav_schedule or {}

        self.fig, self.ax = plt.subplots(figsize=(10, 10))

        self.plot_state()

    def plot_state(self):
        self.ax.clear()

        for idx, uav in enumerate(self.uavs.values()):
            color = self.colors[idx % len(self.colors)]
            marker = self.marker

            if uav.working:
                self.ax.plot(uav.position[0], uav.position[1], f'{color}{marker}', markersize=10)
                self.ax.text(uav.position[0], uav.position[1], f'U{uav.id}', fontsize=12, ha='right')

                flight_path = np.array(uav.flight_path)
                if len(flight_path) > 1:
                    self.ax.plot(flight_path[:, 0], flight_path[:, 1], f'{color}-')

                if hasattr(uav, 'task_sequence') and uav.task_sequence:
                    task_positions = [self.tasks[task_id].position for task_id in uav.task_sequence]
                    task_positions.insert(0, uav.position)
                    task_positions = np.array(task_positions)
                    self.ax.plot(task_positions[:, 0], task_positions[:, 1], f'{color}--')
            else:
                self.ax.plot(uav.position[0], uav.position[1], 'kx', markersize=10)
                self.ax.text(uav.position[0], uav.position[1], f'U{uav.id}', fontsize=12, ha='right')

                flight_path = np.array(uav.flight_path)
                if len(flight_path) > 1:
                    self.ax.plot(flight_path[:, 0], flight_path[:, 1], 'k-')  # 使用黑色实线绘制已飞行路径

        for task in self.tasks.values():
            status_color = 'go' if not task.completed else 'gx'
            self.ax.plot(task.position[0], task.position[1], status_color)
            self.ax.text(task.position[0], task.position[1], f'T{task.id}', fontsize=12, ha='left')

        for idx, color in enumerate(self.colors[:len(self.uavs)]):
            self.ax.plot([], [], f'{color}{self.marker}', label=f'UAV {idx + 1} Working')
            self.ax.plot([], [], f'{color}-', label=f'UAV {idx + 1} Completed Path')
            self.ax.plot([], [], f'{color}--', label=f'UAV {idx + 1} Planned Path')
        self.ax.plot([], [], 'kx', label='Destroyed UAV')  # 添加损毁无人机的图例
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
            uav.flight_path = [uav.position]
            uav.completed_tasks = []
            uav.task_completion_times = {}

        self.plot_state()

        for _ in range(self.simulation_steps):
            self.time_step += 1

            # 检查是否在此时间步长发生无人机损毁
            if self.time_step in self.destroyed_uav_schedule:
                uav_to_destroy_id = self.destroyed_uav_schedule[self.time_step]
                if uav_to_destroy_id in self.uavs:
                    self.uavs[uav_to_destroy_id].working = False
                    print(f"UAV {uav_to_destroy_id} 损毁发生在时刻 {self.time_step}")
                self.reallocate_tasks()

            self.update_positions()
            self.plot_state()

            if all(task.completed for task in self.tasks.values()):
                self.save_figure("simulation_result.png")
                break

    def reallocate_tasks(self):
        incomplete_tasks = [task for task in self.tasks.values() if not task.completed]
        if not incomplete_tasks:
            return  # 所有任务都已完成，不需要重新分配

        damaged_uavs = [uav for uav in self.uavs.values() if not uav.working]
        operational_uavs = [uav for uav in self.uavs.values() if uav.working]
        if not damaged_uavs:
            return  # 没有损毁的无人机，不需要重新分配

        damaged_uav = damaged_uavs[0]
        uav_distances = [(uav, np.linalg.norm(np.array(uav.position) - np.array(damaged_uav.position))) for uav in
                         operational_uavs]
        uav_distances.sort(key=lambda x: x[1])

        # 增量式添加参与重分配的无人机数量
        m = 1
        while m <= len(uav_distances):
            selected_uavs = [uav for uav, _ in uav_distances[:m]]
            selected_uav_ids = [uav.id for uav in selected_uavs]

            # 只考虑参与重分配的无人机未完成的任务和损毁无人机的任务
            reallocate_tasks = [task for uav in selected_uavs for task in uav.task_sequence if
                                not self.tasks[task].completed] + \
                               [task for task in damaged_uav.task_sequence if not self.tasks[task].completed]
            reallocate_tasks = list(set(reallocate_tasks))  # 去重

            if not reallocate_tasks:
                return  # 没有需要重分配的任务

            reallocate_task_objs = [self.tasks[task_id] for task_id in reallocate_tasks]

            results = plan_tasks_and_uavs(reallocate_task_objs, selected_uavs)

            if all(result['best_sequence'] != "超出剩余能量，无输出解" for result in results):
                print(f"m={m}, 无人机 {selected_uav_ids} 参与重分配，重分配完成")
                # 找到可行解，更新无人机任务和状态
                for result in results:
                    uav_id = result['uav_id']
                    uav = self.uavs[uav_id]
                    best_sequence = result['best_sequence']

                    if best_sequence != "超出剩余能量，无输出解":
                        uav.task_sequence = [task['task_id'] for task in best_sequence]
                    uav.completed_tasks = []
                    uav.task_completion_times = {}

                self.results = results

                # 输出重分配后的任务序列和飞行过程信息
                for uav in selected_uavs:
                    print(f"UAV {uav.id} 重分配后的任务序列为: {uav.task_sequence}")

                return
            print(f"m={m}, 无人机 {selected_uav_ids} 参与重分配无解")
            m += 1

        print("无法在当前能量限制下重新分配任务。")
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
                        print(f"UAV {uav.id} 完成 T{current_task_id} 在时刻 {self.time_step}")
                    else:
                        direction = (np.array(current_task.position) - np.array(uav.position)) / np.linalg.norm(
                            np.array(current_task.position) - np.array(uav.position))
                        move_distance = remaining_time * uav.speed
                        uav.position = tuple(np.array(uav.position) + move_distance * direction)
                        uav.flight_path.append(uav.position)
                        remaining_time = 0

    def save_figure(self, filename):
        self.fig.savefig(filename)
