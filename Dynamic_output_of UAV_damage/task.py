# -*- coding: utf-8 -*-
"""
@Time ： 2024-06
@Auth ： peng tian
@File ：task.py
@IDE ：PyCharm
"""
class Task:
    def __init__(self, id, position, required_energy, completed=False, value=20):
        self.id = id  # 任务序号，唯一标识
        self.position = position  # 任务位置，二维坐标 [x, y]
        self.required_energy = required_energy  # 侦察该任务所需能量，整数表示
        self.completed = completed  # 完成状态，False表示未侦察，True表示已侦察完毕
        self.value = value  # 侦察该任务可以获得的价值，整数表示

    def mark_completed(self):
        self.completed = True

    def mark_incomplete(self):
        self.completed = False

    def __repr__(self):
        return f"Task(id={self.id}, position={self.position}, required_energy={self.required_energy}, completed={self.completed}, value={self.value})"