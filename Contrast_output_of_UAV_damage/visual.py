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

            if uav.working:
                ax.plot(uav.position[0], uav.position[1], f'{color}{marker}', markersize=10)
                ax.text(uav.position[0], uav.position[1], f'$U_{{{uav.id}}}$', fontsize=12, ha='right')

                flight_path = np.array(uav.flight_path)
                if len(flight_path) > 1:
                    ax.plot(flight_path[:, 0], flight_path[:, 1], f'{color}-')

                if hasattr(uav, 'task_sequence') and uav.task_sequence:
                    task_positions = [self.tasks[task_id].position for task_id in uav.task_sequence]
                    task_positions.insert(0, uav.position)
                    task_positions = np.array(task_positions)
                    ax.plot(task_positions[:, 0], task_positions[:, 1], f'{color}--')
            else:
                ax.plot(uav.position[0], uav.position[1], 'kx', markersize=10)
                ax.text(uav.position[0], uav.position[1], f'$U_{{{uav.id}}}$', fontsize=12, ha='right')

                flight_path = np.array(uav.flight_path)
                if len(flight_path) > 1:
                    ax.plot(flight_path[:, 0], flight_path[:, 1], 'k-')  # 使用黑色实线绘制已飞行路径

        for task in self.tasks.values():
            status_color = 'go' if not task.completed else 'gx'
            ax.plot(task.position[0], task.position[1], status_color)
            ax.text(task.position[0], task.position[1], f'$T_{{{task.id}}}$', fontsize=12, ha='left')

        for idx, color in enumerate(self.colors[:len(self.uavs)]):
            ax.plot([], [], f'{color}{self.marker}', label=f'$U_{{{idx + 1}}}$ Working')
            ax.plot([], [], f'{color}-', label=f'$U_{{{idx + 1}}}$ Completed Path')
            ax.plot([], [], f'{color}--', label=f'$U_{{{idx + 1}}}$ Planned Path')
        ax.plot([], [], 'kx', label='Destroyed UAV')  # 添加损毁无人机的图例
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

            if self.time_step in self.destroyed_uav_schedule:
                uav_to_destroy_id = self.destroyed_uav_schedule[self.time_step]
                if uav_to_destroy_id in self.uavs:
                    self.uavs[uav_to_destroy_id].working = False
                    print(f"UAV {uav_to_destroy_id} 损毁发生在时刻 {self.time_step}")
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
        self.fig.legend(handles, labels, loc='upper right', bbox_to_anchor=(1.001, 0.95),ncol=1,fontsize=10)
        plt.show()


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
