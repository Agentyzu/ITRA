# -*- coding: utf-8 -*-
"""
@Time ： 2024-06
@Auth ： peng tian
@File ：main.py
@IDE ：PyCharm
"""
import random
from task import Task
from uav import UAV
from preplanning import plan_tasks_and_uavs
from visual import VisualSimulator  # 导入VisualSimulator类


def generate_random_position():
    return [random.randint(5, 95), random.randint(5, 95)]


def main():
    # 示例任务数据
    tasks = []
    for i in range(1, 31):
        position = generate_random_position()
        energy_required = random.randint(5, 20)
        value = random.randint(50, 500)
        tasks.append(Task(id=i, position=position, required_energy=energy_required, value=value))
    # tasks = [
    #     Task(id=1, position=[94, 57], required_energy=12, completed=False, value=61),
    #          Task(id=2, position=[8, 21], required_energy=9, completed=False, value=270),
    #          Task(id=3, position=[88, 25], required_energy=17, completed=False, value=123),
    #          Task(id=4, position=[84, 44], required_energy=12, completed=False, value=411),
    #          Task(id=5, position=[67, 6], required_energy=17, completed=False, value=405),
    #          Task(id=6, position=[9, 11], required_energy=10, completed=False, value=162),
    #          Task(id=7, position=[56, 56], required_energy=5, completed=False, value=496),
    #          Task(id=8, position=[89, 18], required_energy=9, completed=False, value=106),
    #          Task(id=9, position=[64, 81], required_energy=6, completed=False, value=137),
    #          Task(id=10, position=[89, 55], required_energy=15, completed=False, value=177),
    #          Task(id=11, position=[11, 71], required_energy=5, completed=False, value=477),
    #          Task(id=12, position=[29, 47], required_energy=17, completed=False, value=391),
    #          Task(id=13, position=[86, 16], required_energy=34, completed=False, value=278),
    #          Task(id=14, position=[57, 50], required_energy=11, completed=False, value=238),
    #          Task(id=15, position=[21, 69], required_energy=11, completed=False, value=212),
    #          Task(id=16, position=[84, 28], required_energy=16, completed=False, value=174),
    #          Task(id=17, position=[34, 32], required_energy=9, completed=False, value=446),
    #          Task(id=18, position=[42, 63], required_energy=11, completed=False, value=315),
    #          Task(id=19, position=[69, 84], required_energy=18, completed=False, value=349),
    #          Task(id=20, position=[62, 52], required_energy=15, completed=False, value=417),
    #          Task(id=21, position=[31, 41], required_energy=11, completed=False, value=459),
    #          Task(id=22, position=[9, 36], required_energy=7, completed=False, value=417),
    #          Task(id=23, position=[8, 29], required_energy=20, completed=False, value=423),
    #          Task(id=24, position=[76, 57], required_energy=16, completed=False, value=494),
    #          Task(id=25, position=[40, 53], required_energy=11, completed=False, value=211),
    #          Task(id=26, position=[28, 41], required_energy=6, completed=False, value=465),
    #          Task(id=27, position=[31, 6], required_energy=10, completed=False, value=257),
    #          Task(id=28, position=[80, 73], required_energy=15, completed=False, value=390),
    #          Task(id=29, position=[49, 73], required_energy=18, completed=False, value=151),
    #          Task(id=30, position=[17, 10], required_energy=16, completed=False, value=90)
    #
    #  ]
    # 示例无人机数据
    uavs = []
    for i in range(1, 5):
        position = (50, 0)
        uavs.append(UAV(id=i, position=position, remaining_energy=700, working=True, speed=5, fuel_consumption=2))
    # uavs = [
    # UAV(id=1, position=(50, 0), remaining_energy=600, working=True, speed=5, fuel_consumption=2),
    # UAV(id=2, position=(50, 0), remaining_energy=600, working=True, speed=5, fuel_consumption=2),
    # UAV(id=3, position=(50, 0), remaining_energy=600, working=True, speed=5, fuel_consumption=2),
    # UAV(id=4, position=(50, 0), remaining_energy=600, working=True, speed=5, fuel_consumption=2),
    # UAV(id=5, position=(50, 0), remaining_energy=900, working=True, speed=5, fuel_consumption=2)
    # ]

    # 输出生成的无人机信息
    # 输出生成的无人机信息
    # for task in tasks:
    #     print(task)
    # for uav in uavs:
    #     print(uav)
    # 进行任务预规划和无人机分配
    results = plan_tasks_and_uavs(tasks, uavs)


    # 输出每个无人机分配的任务簇和最佳任务序列
    for result in results:
        uav_id = result['uav_id']
        cluster_id = result['cluster_id']
        assigned_tasks = result['assigned_tasks']
        best_tasks = result['best_sequence']
        best_energy_cost = result['best_energy_cost']
        best_task_value = result['best_task_value']

        print(f"UAV {uav_id} 分配的任务群ID {cluster_id}:")
        print("  分配的任务:", [task['task_id'] for task in assigned_tasks])

        if isinstance(best_tasks, list):
            print("  最佳任务序列:", [task['task_id'] for task in best_tasks])
            print(f"  最佳任务序列消耗能量: {best_energy_cost}")
        else:
            print("  最佳任务序列:", best_tasks)

    # 设置重分配的时间步长
    reallocate_time = 50

    # 创建仿真器并运行仿真
    destroyed_uav_schedule = {
        8: 1,  # 在时间步长8时损毁无人机1
        # 20: 2,  # 在时间步长20时损毁无人机2
        # 可以添加更多时间步长和无人机ID
    }

    visual_simulator = VisualSimulator(uavs, tasks, results, simulation_steps=100, reallocate_time=reallocate_time,
                                       destroyed_uav_schedule=destroyed_uav_schedule)

    visual_simulator.run_simulation()

    # 输出每个无人机完成的任务列表
    for uav in uavs:
        print(f"无人机 {uav.id} 整个过程中完成的任务: {uav.completed_tasks}")


if __name__ == "__main__":
    main()
