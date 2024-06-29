"""
@Time ： 2024-06
@Auth ： peng tian
@File ：genetic_algorithm.py
@IDE ：PyCharm
"""
import numpy as np
import random

def calculate_energy_cost(task_sequence, uav, energy_matrix):
    total_energy_cost = 0
    current_position = tuple(uav.position)

    for task in task_sequence:
        task_position = tuple(task.position)
        task_energy_cost = energy_matrix[(current_position, task_position)] * uav.fuel_consumption
        total_energy_cost += task_energy_cost + task.required_energy
        current_position = task_position

    return total_energy_cost

def genetic_algorithm(uav, tasks, population_size=50, generations=100, mutation_rate=0.1):
    task_ids = [task.id for task in tasks]

    def create_individual():
        return random.sample(task_ids, len(task_ids))

    def crossover(parent1, parent2):
        if len(parent1) == 1:
            return parent1, parent2
        point = random.randint(1, len(parent1) - 1)
        child1 = parent1[:point] + [item for item in parent2 if item not in parent1[:point]]
        child2 = parent2[:point] + [item for item in parent1 if item not in parent2[:point]]
        return child1, child2

    def mutate(individual):
        if len(individual) > 1 and random.random() < mutation_rate:
            point1, point2 = random.sample(range(len(individual)), 2)
            individual[point1], individual[point2] = individual[point2], individual[point1]

    population = [create_individual() for _ in range(population_size)]

    # 包含无人机初始位置到任务位置的能量矩阵
    energy_matrix = {
        (tuple(uav.position), tuple(task.position)): np.linalg.norm(np.array(uav.position) - np.array(task.position))
        for task in tasks
    }

    # 包含任务位置之间的能量矩阵
    for i in range(len(tasks)):
        for j in range(len(tasks)):
            energy_matrix[(tuple(tasks[i].position), tuple(tasks[j].position))] = np.linalg.norm(
                np.array(tasks[i].position) - np.array(tasks[j].position))

    for generation in range(generations):
        population = sorted(population, key=lambda x: calculate_energy_cost([tasks[task_ids.index(t)] for t in x], uav,
                                                                            energy_matrix))
        new_population = population[:10]

        while len(new_population) < population_size:
            parent1, parent2 = random.sample(population[:20], 2)
            child1, child2 = crossover(parent1, parent2)
            mutate(child1)
            mutate(child2)
            new_population.extend([child1, child2])

        population = new_population

    best_individual = population[0]
    best_sequence = [tasks[task_ids.index(t)] for t in best_individual]
    best_energy_cost = calculate_energy_cost(best_sequence, uav, energy_matrix)

    if best_energy_cost > uav.remaining_energy:
        return "超出剩余能量，无输出解", None

    return best_sequence, best_energy_cost
