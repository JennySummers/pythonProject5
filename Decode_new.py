import matplotlib.pyplot as plt
from Jobs import Job
from Machines import Machine_Time_window
from Instance import put_time, pick_time, switch_time, INVALID
import numpy as np

bias = 1


class Decode:
    def __init__(self, J, Processing_time, M_num, TM_num, M_status):
        self.Processing_time = Processing_time
        # self.Scheduled = []  # 已经排产过的工序
        self.M_num = M_num  # 机器数
        self.Machines = []  # 存储机器类
        self.fitness = 0  # 计算适应度
        self.J = J  # 表示各个工件对应的工序数。用键值对来表示
        # self.Machine_time = np.zeros(self.M_num, dtype=float)  # 机器时间初始化，使用当前机器运行情况初始化
        self.Machine_time = [x for x in M_status]  # 机器时间初始化，使用当前机器运行情况初始化
        self.Jobs = []  # 存储工件类
        self.JM = []  # 机器顺序矩阵，JM[i][j]表示工件i的第j道工序在机器JM[i][j]上加工
        self.T = []  # 时间顺序矩阵，T[i][j]表示工件i的第j道工序在机器JM[i][j]上加工的加工时间为T[i][j]
        self.TM_List = M_num - TM_num  # 机械臂列表
        for j in range(M_num):
            self.Machines.append(Machine_Time_window(j, self.Machine_time[j]))  # 为每个机器分配一个机器类，并对其进行编号
        for k, v in J.items():
            self.Jobs.append(Job(k, v))

    def reset(self):
        self.Machines.clear()
        self.fitness = 0
        self.Jobs.clear()
        for j in range(self.M_num):
            self.Machines.append(Machine_Time_window(j, self.Machine_time[j]))  # 为每个机器分配一个机器类，并对其进行编号
        for k, v in self.J.items():
            self.Jobs.append(Job(k, v))

    # 时间顺序矩阵和机器顺序矩阵
    def Order_Matrix(self, MS):  # MS为机器选择部分，对机器选择部分进行解码,从左到右依次读取并转换成机器顺序矩阵JM和时间顺序矩阵T。
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
            self.JM.append(JM_i)
            self.T.append(T_i)
        # 删除临时变量
        del Ms_decompose
        del Site

    def Earliest_Start(self, job, O_num, Selected_Machine, early_start, late_start):  # 选中的机器即为当前的机器编号
        P_t = self.Processing_time[job][O_num][Selected_Machine]
        M_Tstart, M_Tend, M_Tlen = self.Machines[Selected_Machine].Empty_time_window()
        earliest_start = int(max(early_start,self.Machines[Selected_Machine].End_time))  # 当前工序的最早开始时间为上一道工序完成时间与机器到达空闲状态时间取最大值
        nxt_early = earliest_start + P_t
        nxt_late = int(-1)
        if M_Tlen is not None:  # 此处为全插入时窗
            for le_i in range(len(M_Tlen)):
                if M_Tlen[le_i] >= P_t:
                    if M_Tstart[le_i] >= early_start and (late_start < 0 or M_Tstart[le_i] < late_start):
                        earliest_start = M_Tstart[le_i]
                        nxt_early = earliest_start + P_t
                        nxt_late = M_Tend[le_i]
                        break
                    if M_Tstart[le_i] < early_start and (late_start < 0 or M_Tstart[le_i] < late_start) and M_Tend[le_i] - early_start >= P_t:
                        earliest_start = early_start
                        nxt_early = earliest_start + P_t
                        nxt_late = M_Tend[le_i]
                        break
        # M_Earliest = earliest_start
        # End_work_time = earliest_start + P_t
        # 删除临时变量
        del M_Tstart
        del M_Tend
        del M_Tlen

        return int(earliest_start), int(nxt_early), int(nxt_late)  # 返回0.工件的工序最早开始时间，1.下一道工序最早可以开始的时间，2.下一道工序最晚可以开始的时间

    # 解码
    def Decode_1(self, CHS, Len_Chromo):
        MS = list(CHS[0:Len_Chromo])
        OS = list(CHS[Len_Chromo:2 * Len_Chromo])
        self.Order_Matrix(MS)
        for k, v in self.J.items():
            LT = self.DFS_for_jobs(k - 1, 0, v, [], [], [])  # early 和 late 为空表示第一道工序开始时间和结束时间无限制
            st = int(0)
            et = int(0)
            for ti in range(len(LT)):
                machine = self.JM[k-1][ti]
                P_t = self.T[k-1][ti]
                st = LT[ti]
                if ti + 1 < len(LT):
                    et = LT[ti + 1]
                else:
                    et = st + P_t
                if machine >= self.TM_List:  # 机械臂的处理
                    et = LT[ti+1]
                    st = LT[ti+1] - P_t
                else:  #处理单元的处理
                    if ti + 2 < v:
                        st = LT[ti]
                        et = LT[ti+2] - self.T[k-1][ti+1]
                self.Jobs[k-1]._Input(st, et, machine)  # 参数含义:工件的工序最早开始时间，当前工序结束时间，选择的机器号
                if et > self.fitness:
                    self.fitness = et
                self.Machines[machine]._Input(k-1, st, et - st, ti)  # 参数含义:工件编号，工件的工序最早开始时间，处理时间，工序编号

        return self.fitness

    def DFS_for_jobs(self, job, op, sop, LT, early_s, late_s):  # 参数：工件号，工序号，工序总数， 当前开始时间序列，当前工序的最早开始时间，最晚开始时间
        if not early_s:
            early = int(0)
        else:
            early = early_s[-1]
        if not late_s:
            late = int(-1)
        else:
            late = late_s[-1]
        if op == sop:
            return LT
        machine = self.JM[job][op]  # JM[i][j]表示工件i的第j道工序在机器JM[i][j]上加工
        P_t = self.T[job][op]  # T[i][j]表示工件i的第j道工序的加工时间为T[i][j]
        while 1:
            earliest_start, nxt_early, nxt_late = self.Earliest_Start(job, op, machine, early, late)
            '''
            if machine >= self.TM_List:
                nxt_early = earliest_start + P_t
                nxt_late = late + P_t
                if late == -1:
                    nxt_late = -1
            '''
            # 得到下一道工序的最早开始时间，和最晚开始时间
            if late == -1 or early <= earliest_start <= late:
                LT.append(earliest_start)
                early_s.append(nxt_early)
                late_s.append(nxt_late)
                return self.DFS_for_jobs(job, op + 1, sop, LT, early_s, late_s)
            else:  # 不满足条件则探索下一个时间窗
            # if early >= late:  # 当结束时间无限制或最早时间大于最晚开始时间时说明无解，回溯
                break
        early_s.pop()
        late_s.pop()
        LT.pop()
        if early_s:
            early_s[-1] = late + 1
        return self.DFS_for_jobs(job, op-1, sop, LT, early_s, late_s)
        # 返回当前工件的所有工序的开始时间序列
