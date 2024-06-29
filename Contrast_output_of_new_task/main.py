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
    return (random.randint(5, 95), random.randint(5, 95))

def main():

    # tasks = []
    # for i in range(1, 10):
    #     position = generate_random_position()
    #     energy_required = random.randint(5, 20)
    #     value = random.randint(50, 500)
    #     tasks.append(Task(id=i, position=position, required_energy=energy_required, value=value))
    # uavs = []
    # for i in range(1, 6):
    #     position = (50, 0)
    #     uavs.append(UAV(id=i, position=position, remaining_energy=800, working=True, speed=3, fuel_consumption=2))
    tasks = [
        Task(id=1, position=[94, 57], required_energy=12, completed=False, value=61),
        Task(id=2, position=[8, 21], required_energy=9, completed=False, value=270),
        Task(id=3, position=[88, 25], required_energy=17, completed=False, value=123),
        Task(id=4, position=[84, 44], required_energy=12, completed=False, value=411),
        Task(id=5, position=[60, 6], required_energy=17, completed=False, value=405),
        Task(id=6, position=[9, 11], required_energy=10, completed=False, value=162),
        Task(id=7, position=[56, 56], required_energy=5, completed=False, value=496),
        Task(id=8, position=[93, 18], required_energy=9, completed=False, value=106),
        Task(id=9, position=[64, 81], required_energy=6, completed=False, value=137),
        Task(id=10, position=[89, 55], required_energy=15, completed=False, value=177),
        Task(id=11, position=[11, 71], required_energy=5, completed=False, value=477),
        Task(id=12, position=[29, 47], required_energy=17, completed=False, value=391),
        Task(id=13, position=[67, 10], required_energy=34, completed=False, value=278),
        Task(id=14, position=[57, 40], required_energy=11, completed=False, value=238),
        Task(id=15, position=[21, 69], required_energy=11, completed=False, value=212),
        Task(id=16, position=[84, 28], required_energy=16, completed=False, value=174),
        Task(id=17, position=[42, 63], required_energy=11, completed=False, value=315),
        Task(id=18, position=[69, 84], required_energy=18, completed=False, value=349),
        Task(id=19, position=[62, 52], required_energy=15, completed=False, value=417),
        Task(id=20, position=[9, 36], required_energy=7, completed=False, value=417),
        Task(id=21, position=[8, 29], required_energy=20, completed=False, value=423),
        Task(id=22, position=[76, 57], required_energy=16, completed=False, value=494),
        Task(id=23, position=[40, 53], required_energy=11, completed=False, value=211),
        Task(id=24, position=[28, 41], required_energy=6, completed=False, value=465),
        Task(id=25, position=[31, 6], required_energy=10, completed=False, value=257),
        Task(id=26, position=[80, 73], required_energy=15, completed=False, value=390),
        Task(id=27, position=[49, 73], required_energy=18, completed=False, value=151),
        Task(id=28, position=[17, 10], required_energy=16, completed=False, value=90)

     ]

    uavs = [
    UAV(id=1, position=(50, 0), remaining_energy=500, working=True, speed=5, fuel_consumption=1),
    UAV(id=2, position=(50, 0), remaining_energy=500, working=True, speed=5, fuel_consumption=1),
    UAV(id=3, position=(50, 0), remaining_energy=500, working=True, speed=5, fuel_consumption=1),
    UAV(id=4, position=(50, 0), remaining_energy=500, working=True, speed=5, fuel_consumption=1),
    UAV(id=5, position=(50, 0), remaining_energy=500, working=True, speed=5, fuel_consumption=1)
    ]

    results = plan_tasks_and_uavs(tasks, uavs)

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
        else:
            print("  最佳任务序列:", best_tasks)

        print("  消耗的能量:", best_energy_cost)

    tasks_dict = {task.id: task for task in tasks}

    simulator = VisualSimulator(uavs, tasks, results, simulation_steps=1000, reallocate_time=8)
    simulator.run_simulation()

    if simulator.no_solution:
        print("任务分配存在超出剩余能量的情况，无法完成所有任务。")
        return

    for uav in uavs:
        print(f"UAV {uav.id} 整个任务过程中完成:", uav.completed_tasks)
        # total_energy_cost = uav.calculate_total_energy_cost()
        # total_value = sum(tasks_dict[task_id].value for task_id in uav.completed_tasks)
        # print(f"UAV {uav.id} 总消耗能量: {total_energy_cost}，总获得价值: {total_value}")

if __name__ == "__main__":
    main()