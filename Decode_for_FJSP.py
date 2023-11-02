import matplotlib.pyplot as plt
from Jobs import Job
from Machines import Machine_Time_window
from Instance import put_time, pick_time, switch_time, INVALID
import numpy as np

from memory_profiler import profile

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
            plt.barh(i, width=End_time[i_1] - Start_time[i_1], height=0.8, left=Start_time[i_1], color='white', edgecolor='black')
            plt.text(x=Start_time[i_1] + 0.1, y=i, s=Machine.assigned_task[i_1])
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
            plt.barh(i, width=End_time[j] - Start_time[j], height=0.8, left=Start_time[j], color='white', edgecolor='black')
            plt.text(x=Start_time[j] + 0.1, y=i, s=job.J_machine[j]+1)
    plt.yticks(np.arange(i + 1), np.arange(1, i + 2))
    plt.title('Scheduling Gantt chart')
    plt.ylabel('Jobs')
    plt.xlabel('Time(s)')
    plt.show()


class Decode:
    def __init__(self, J, Processing_time, M_num, M_status):
        self.Processing_time = Processing_time
        # self.Scheduled = []  # 已经排产过的工序
        self.M_num = M_num  # 机器数
        self.Machines = []  # 存储机器类
        self.fitness = 0    # 计算适应度
        self.J = J          # 表示各个工件对应的工序数。用键值对来表示
        for j in range(M_num):
            self.Machines.append(Machine_Time_window(j))    # 为每个机器分配一个机器类，并对其进行编号
        self.Machine_time = np.zeros(self.M_num, dtype=float)  # 机器时间初始化，使用当前机器运行情况初始化
        self.Machine_State = [x for x in M_status]          # 当前机器还有多少时间达到空闲
        self.Jobs = []  # 存储工件类
        for k, v in J.items():
            self.Jobs.append(Job(k, v))

    # 时间顺序矩阵和机器顺序矩阵
    # @profile(precision=4, stream=open('memory_profiler.log', 'w+'))
    def Order_Matrix(self, MS):  # MS为机器选择部分
        JM = []
        T = []
        Ms_decompose = []
        Site = 0
        for S_i in self.J.values():
            Ms_decompose.append(MS[Site:Site + S_i])
            Site += S_i
        # print(Ms_decompose)
        for i in range(len(Ms_decompose)):
            JM_i = []
            T_i = []
            for j in range(len(Ms_decompose[i])):
                O_j = self.Processing_time[i][j]
                M_ij = []
                T_ij = []
                for Mac_num in range(len(O_j)):  # 寻找MS对应部分的机器时间和机器顺序
                    if O_j[Mac_num] != INVALID:
                        M_ij.append(Mac_num)
                        T_ij.append(O_j[Mac_num])
                    else:
                        continue
                # Ms_decompose二维数组代表工件在每个工序上所选择的机器，第一维代表工件数，第二维代表每个工件的工序数，
                JM_i.append(M_ij[Ms_decompose[i][j]])
                T_i.append(T_ij[Ms_decompose[i][j]])
            JM.append(JM_i)
            T.append(T_i)
        return JM, T

    # @profile(precision=4, stream=open('memory_profiler.log', 'w+'))
    def Earliest_Start(self, job, O_num, Machine):
        P_t = self.Processing_time[job][O_num][Machine]
        last_O_end = self.Jobs[job].Last_Processing_end_time  # 上道工序结束时间
        Selected_Machine = Machine  # 选中的机器即为当前的机器编号
        M_window = self.Machines[Selected_Machine].Empty_time_window()
        M_Tstart = M_window[0]
        M_Tend = M_window[1]
        M_Tlen = M_window[2]
        Machine_end_time = self.Machines[Selected_Machine].End_time  # 当前选中的机器在哪个时刻达到空闲状态
        ealiest_start = max(last_O_end, Machine_end_time)  # 当前工序的最早开始时间为上一道工序完成时间与机器到达空闲状态时间取最大值
        if M_Tlen is not None:  # 此处为全插入时窗
            for le_i in range(len(M_Tlen)):
                if M_Tlen[le_i] >= P_t:
                    if M_Tstart[le_i] >= last_O_end:
                        ealiest_start = M_Tstart[le_i]
                        break
                    if M_Tstart[le_i] < last_O_end and M_Tend[le_i] - last_O_end >= P_t:
                        ealiest_start = last_O_end
                        break
        M_Ealiest = ealiest_start
        End_work_time = M_Ealiest + P_t
        return M_Ealiest, Selected_Machine, P_t, O_num, last_O_end, End_work_time  # 返回

    # 解码
    # @profile(precision=4, stream=open('memory_profiler.log', 'w+'))
    def Decode_1(self, CHS, Len_Chromo):
        MS = list(CHS[0:Len_Chromo])
        OS = list(CHS[Len_Chromo:2 * Len_Chromo])
        Needed_Matrix = self.Order_Matrix(MS)
        JM = Needed_Matrix[0]
        for i in OS:
            Job = i
            O_num = self.Jobs[Job].Current_Processed()
            Machine = JM[Job][O_num]
            Para = self.Earliest_Start(Job, O_num, Machine)
            self.Jobs[Job]._Input(Para[0], Para[5], Para[1])
            if Para[5] > self.fitness:
                self.fitness = Para[5]
            self.Machines[Machine]._Input(Job, Para[0], Para[2], Para[3])
        return self.fitness
