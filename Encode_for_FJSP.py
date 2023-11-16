import numpy as np
import random
from Instance import put_time, pick_time, switch_time, INVALID

from memory_profiler import profile


class Encode:
    def __init__(self, Matrix, Pop_size, J, J_num, M_num, M_status):
        self.Matrix = Matrix  # 工件各工序对应各机器加工时间矩阵
        self.GS_num = int(0.6 * Pop_size)  # 全局选择初始化的种群数目
        self.LS_num = int(0.2 * Pop_size)  # 局部选择初始化的种群数目
        self.RS_num = int(0.2 * Pop_size)  # 随机选择初始化的种群数目
        self.J = J  # 各工件对应的工序数
        self.J_num = J_num  # 工件数
        self.M_num = M_num  # 机器数
        self.Machine_status = [x for x in M_status]  # 当前机器还需要Machine_status[i]个单位时间达到空闲状态。
        self.CHS = []
        self.Len_Chromo = 0  # 染色体长度，长度等于所有工序数的总和
        for i in J.values():
            self.Len_Chromo += i

    # 生成工序准备的部分
    # @profile(precision=4, stream=open('memory_profiler.log', 'w+'))
    def OS_List(self):
        OS_list = []
        for k, v in self.J.items():
            OS_add = [k - 1 for j in range(v)]
            OS_list.extend(OS_add)
        return OS_list

    # 生成初始化矩阵
    # @profile(precision=4, stream=open('memory_profiler.log', 'w+'))
    def CHS_Matrix(self, C_num):  # C_num:所需列数
        return np.zeros([C_num, self.Len_Chromo], dtype=int)

    # @profile(precision=4, stream=open('memory_profiler.log', 'w+'))
    def Site(self, Job, Operation):  # 第job个工件的第operation道工序在染色体中机器选择部分的位置。机器选择部分的下标对应一道确定的工序。
        O_num = 0
        # for k, v in self.J.items():
        for i in range(len(self.J)):
            # if k-1 == Job:
            if i == Job:
                return O_num + Operation
            else:
                O_num = O_num + self.J[i + 1]
                # O_num = O_num + v
        return O_num

    # 全局选择初始化
    # @profile(precision=4, stream=open('memory_profiler.log', 'w+'))
    def Global_initial(self):
        MS = self.CHS_Matrix(self.GS_num)
        OS_list = self.OS_List()
        OS = self.CHS_Matrix(self.GS_num)
        for i in range(self.GS_num):
            # Machine_time = np.zeros(self.M_num, dtype=float)  # 机器时间初始化，使用当前机器运行情况初始化
            Machine_time = [x for x in self.Machine_status]  # 机器时间初始化，使用当前机器运行情况初始化
            # random.shuffle(OS_list)  # 生成工序排序部分
            OS[i] = np.array(OS_list)
            GJ_list = [i for i in range(self.J_num)]  # GJ_list表示
            # random.shuffle(GJ_list)
            for g in GJ_list:  # 随机选择工件集的第一个工件,从工件集中剔除这个工件
                h = self.Matrix[g]  # 第一个工件含有的工序，self.Matrix[g]表示第g个工件的工序集合和可处理的机器及其对应的处理时间
                for j in range(len(h)):  # 从工件的第一个工序开始选择机器
                    D = h[j]  # h[j]表示第g个工件的第j道工序可用的机器集合及其对应的处理时间
                    List_Machine_position = []
                    for k in range(len(D)):  # 每道工序可使用的机器以及机器的加工时间
                        Using_Machine = D[k]
                        if Using_Machine != INVALID:  # 确定可加工该工序的机器
                            List_Machine_position.append(k)
                    Machine_Select = []
                    for Machine_add in List_Machine_position:  # 将这道工序的可用机器时间和以前积累的机器时间相加
                        #  比较可用机器的时间加上以前累计的机器时间的时间值，并选出时间最小
                        Machine_Select.append(Machine_time[Machine_add] + D[Machine_add])
                    # print(Machine_Select)
                    Min_time = min(Machine_Select)
                    K = Machine_Select.index(Min_time)  # K表示可选机器集中的第几台机器
                    I = List_Machine_position[K]  # I表示这台机器实际的编号
                    Machine_time[I] += D[I]  # 使用当前工件在这台机器加工的时间来更新机器时间
                    # Machine_time[I] += Min_time
                    site = self.Site(g, j)
                    MS[i][site] = K
        '''
        MS[i][j]表示第i个染色体的j对应的工件的工序选择的机器在当前工序可选机器集中的位置
        OS[i][j]表示第i个染色体的工序处理顺序排序
        CHS1[i] = MS[i] + OS[i]
        '''
        CHS1 = np.hstack((MS, OS))
        return CHS1

    # 局部选择初始化
    # @profile(precision=4, stream=open('memory_profiler.log', 'w+'))
    def Local_initial(self):
        MS = self.CHS_Matrix(self.LS_num)
        OS_list = self.OS_List()
        OS = self.CHS_Matrix(self.LS_num)
        for i in range(self.LS_num):
            random.shuffle(OS_list)  # 生成工序排序部分
            OS_gongxu = OS_list
            OS[i] = np.array(OS_gongxu)
            GJ_list = [i_1 for i_1 in range(self.J_num)]
            for g in GJ_list:
                Machine_time = np.zeros(self.M_num)  # 机器时间初始化
                h = self.Matrix[g]  # 第一个工件及其对应工序的加工时间
                for j in range(len(h)):  # 从工件的第一个工序开始选择机器
                    D = h[j]
                    List_Machine_weizhi = []
                    for k in range(len(D)):  # 每道工序可使用的机器以及机器的加工时间
                        Useing_Machine = D[k]
                        if Useing_Machine == INVALID:  # 确定可加工该工序的机器
                            continue
                        else:
                            List_Machine_weizhi.append(k)
                    Machine_Select = []
                    for Machine_add in List_Machine_weizhi:  # 将这道工序的可用机器时间和以前积累的机器时间相加
                        Machine_time[Machine_add] = Machine_time[Machine_add] + D[
                            Machine_add]  # 比较可用机器的时间加上以前累计的机器时间的时间值，并选出时间最小
                        Machine_Select.append(Machine_time[Machine_add])
                    Machine_Index_add = Machine_Select.index(min(Machine_Select))
                    site = self.Site(g, j)
                    MS[i][site] = MS[i][site] + Machine_Index_add
        CHS1 = np.hstack((MS, OS))
        return CHS1

    # @profile(precision=4, stream=open('memory_profiler.log', 'w+'))
    def Random_initial(self):
        MS = self.CHS_Matrix(self.RS_num)
        OS_list = self.OS_List()
        OS = self.CHS_Matrix(self.RS_num)
        for i in range(self.RS_num):
            random.shuffle(OS_list)  # 生成工序排序部分
            OS_gongxu = OS_list
            OS[i] = np.array(OS_gongxu)
            GJ_list = [i_1 for i_1 in range(self.J_num)]
            A = 0
            for gon in GJ_list:
                Machine_time = np.zeros(self.M_num)  # 机器时间初始化
                g = gon  # 随机选择工件集的第一个工件   #从工件集中剔除这个工件
                h = np.array(self.Matrix[g])  # 第一个工件及其对应工序的加工时间
                for j in range(len(h)):  # 从工件的第一个工序开始选择机器
                    D = np.array(h[j])
                    List_Machine_weizhi = []
                    Site = 0
                    for k in range(len(D)):  # 每道工序可使用的机器以及机器的加工时间
                        if D[k] == INVALID:  # 确定可加工该工序的机器
                            continue
                        else:
                            List_Machine_weizhi.append(Site)
                            Site += 1
                    Machine_Index_add = random.choice(List_Machine_weizhi)
                    MS[i][A] = MS[i][A] + Machine_Index_add
                    A += 1
        CHS1 = np.hstack((MS, OS))
        return CHS1
