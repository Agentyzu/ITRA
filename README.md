# ITRA
This is the code for the paper "Incremental Task Replanning Algorithm for Multi-UAV Based on Centralized-Distributed Negotiation".For the simulation of UAv damage and new tasks in the context of ITRA, there are dynamic output and comparative outputs.
`initiality.py`

# File Description
* The entire simulation can be divided into dynamic motion trajectories and comparisons at different times.Among them, the Contrast_output_of_new_task file and the Contrast_output_of_UAV_damage file represent the contrast of output at different times for the new task and the UAV damage situation, respectively.The Dynamic_output_of UAV_damage and Dynamic_output_of_new_task represent the dynamic trajectory charts at different times under the scenarios of increased task and damaged UAV.
*Here is description to the .py file
* The `task_allocation_kmeans.py` file is used to cluster and assign tasks. Vehicles (UAVs) and tasks, iteration count, and hyperparameters among others.
* The `genetic_algorithm.py` file is used for optimizing the drone's task sequence.
* The hungarian_algorithm.py` file is used to distribute the task group to the drones.
* The `preplanning.py` combines `task_allocation_kmeans.py`, `hungarian_algorithm.py`, and `hungarian_algorithm.py` together as a task reassignment algorithm, taking in the drones and tasks involved in the reassignment and outputting the final path solution.
* The `task.py` and `uav.py` contain definitions of the task and drone class attributes.
* The `visual.py` includes drone motion simulation, image interface visualization, and drone incremental.
* In the `main.py` file, you can define the parameters of the drone and the mission, which can be randomly generated or specified manually. You can also define in the main function when and what attributes the drone will be destroyed or when a new task will be added.


# Usage
When installing Python, which can be directly downloaded from the official Python website, it is advisable to add Python to the environment variables during the installation process to avoid separate configurations later. 


**Tips**:`PyCharm` is a comprehensive integrated development environment (IDE) tailored for Python programming. It offers robust features for code completion, debugging, testing, and version control. Regardless of whether you use PyCharm or any other IDE, you can simply double-click `Main.py` to open and execute it directly.


