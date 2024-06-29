# -*- coding: utf-8 -*-
"""
@Time ： 2024-06
@Auth ： peng tian
@File ：uav.py
@IDE ：PyCharm
"""
class UAV:
    def __init__(self, id, position, remaining_energy, working, speed, fuel_consumption):
        self.id = id
        self.position = position
        self.remaining_energy = remaining_energy
        self.working = working
        self.speed = speed
        self.fuel_consumption = fuel_consumption
        self.flight_path = []  # 记录飞行路径
        self.task_sequence = []  # 无人机的任务序列

    def __repr__(self):
        return f"UAV(id={self.id}, position={self.position}, remaining_energy={self.remaining_energy}, working={self.working}, speed={self.speed}, fuel_consumption={self.fuel_consumption})"
