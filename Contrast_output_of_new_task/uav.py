# -*- coding: utf-8 -*-
"""
@Time ： 2024-06
@Auth ： peng tian
@File ：uav.py
@IDE ：PyCharm
"""
import numpy as np
class UAV:
    def __init__(self, id, position, remaining_energy, working, speed, fuel_consumption):
        self.id = id
        self.position = position
        self.remaining_energy = remaining_energy
        self.working = working
        self.speed = speed
        self.fuel_consumption = fuel_consumption
        self.task_sequence = []
        self.flight_path = []
        self.completed_tasks = []
        self.task_completion_times = {}

    def calculate_total_energy_cost(self):
        total_cost = 0
        for i in range(len(self.flight_path) - 1):
            distance = np.linalg.norm(np.array(self.flight_path[i+1]) - np.array(self.flight_path[i]))
            total_cost += distance * self.fuel_consumption
        for task_id in self.completed_tasks:
            task = self.tasks[task_id]
            total_cost += task.required_energy
        return total_cost
