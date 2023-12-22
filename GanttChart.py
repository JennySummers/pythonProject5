import matplotlib.pyplot as plt
import numpy as np


# @profile(precision=4, stream=open('memory_profiler.log', 'w+'))
def Gantt_Machine(Machines):
    M = ['red', 'blue', 'yellow', 'orange', 'green', 'palegoldenrod', 'purple', 'pink', 'Thistle', 'Magenta',
         'SlateBlue', 'RoyalBlue', 'Cyan', 'Aqua', 'floralwhite', 'ghostwhite', 'goldenrod', 'mediumslateblue',
         'navajowhite',
         'navy', 'sandybrown', 'moccasin']
    plt.rcParams['figure.figsize'] = (38, 60)
    for i in range(len(Machines)):
        Machine = Machines[i]
        Start_time = Machine.O_start
        End_time = Machine.O_end
        for i_1 in range(len(End_time)):
            # plt.barh(i, width=End_time[i_1] - Start_time[i_1], height=0.8, left=Start_time[i_1], color=M[Machine.assigned_task[i_1][0]], edgecolor='black')
            # plt.text(x=Start_time[i_1] + 0.1, y=i, s=Machine.assigned_task[i_1])
            plt.barh(i, width=End_time[i_1] - Start_time[i_1], height=0.8, left=Start_time[i_1], color='white',
                     edgecolor='black')
            # plt.text(x=Start_time[i_1] + 0.1, y=i, s=Machine.assigned_task[i_1])
    plt.yticks(np.arange(i + 1), np.arange(1, i + 2))
    plt.title('Scheduling Gantt chart')
    plt.ylabel('Machines')
    plt.xlabel('Time(s)')
    plt.show()


# @profile(precision=4, stream=open('memory_profiler.log', 'w+'))
def Gantt_Job(Jobs):
    M = ['red', 'blue', 'yellow', 'orange', 'green', 'palegoldenrod', 'purple', 'pink', 'Thistle', 'Magenta',
         'SlateBlue', 'RoyalBlue', 'Cyan', 'Aqua', 'floralwhite', 'ghostwhite', 'goldenrod', 'mediumslateblue',
         'navajowhite',
         'navy', 'sandybrown', 'moccasin']
    plt.rcParams['figure.figsize'] = (80, 6)
    for i in range(len(Jobs)):
        job = Jobs[i]
        # print(job.J_machine)
        Start_time = job.J_start
        End_time = job.J_end
        for j in range(len(End_time)):
            # plt.barh(i, width=End_time[j] - Start_time[j], height=0.8, left=Start_time[j], color=M[job.J_machine[j]], edgecolor='black')
            # plt.text(x=Start_time[j] + 0.1, y=i, s=job.J_machine[j]+1)
            plt.barh(i, width=End_time[j] - Start_time[j], height=0.8, left=Start_time[j], color='white',
                     edgecolor='black')
            # plt.text(x=Start_time[j] + 0.1, y=i, s=job.J_machine[j] + 1)
    plt.yticks(np.arange(i + 1), np.arange(1, i + 2))
    plt.title('Scheduling Gantt chart')
    plt.ylabel('Jobs')
    plt.xlabel('Time(s)')
    plt.show()
