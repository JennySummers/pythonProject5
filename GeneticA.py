import gc
import numpy as np
import random
# from Decode_for_FJSP import Decode
from Decode_new import Decode
from GanttChart import Gantt_Machine, Gantt_Job
from Encode_for_FJSP import Encode
from read_Json import INVALID, pick_time, put_time, unit_time
from Jobs import Job
from copy import *
import itertools
from Messages import Arm_Message
import matplotlib.pyplot as plt
import datetime
import math
import json


def Timestep2Time(cur_time, time_step, time_decay=0):  # 将单位时间转换为实际的时间
    return cur_time + datetime.timedelta(milliseconds=(time_step + time_decay) * unit_time)


def Time2Timestep(start_time, cur_time):  # 将实际的时间转换为单位时间
    return math.ceil(((cur_time - start_time)/datetime.timedelta(milliseconds=1)) / unit_time)


# 机器部分交叉
# @profile(precision=4, stream=open('memory_profiler.log', 'w+'))
def Crossover_Machine(CHS1, CHS2, T0):
    T_r = [j for j in range(T0)]
    r = random.randint(1, 10)  # 在区间[1,T0]内产生一个整数r
    random.shuffle(T_r)
    R = T_r[0:r]  # 按照随机数r产生r个互不相等的整数
    # 将父代的染色体复制到子代中去，保持他们的顺序和位置
    OS_1 = CHS1[T0:2 * T0]
    OS_2 = CHS2[T0:2 * T0]
    C_1 = CHS2[0:T0]
    C_2 = CHS1[0:T0]
    for i in R:
        C_1[i] = C_1[i] + C_2[i]
        C_2[i] = C_1[i] - C_2[i]
        C_1[i] = C_1[i] - C_2[i]
        # K, K_2 = C_1[i], C_2[i]
        # C_1[i], C_2[i] = K_2, K
    CHS1 = np.hstack((C_1, OS_1))
    CHS2 = np.hstack((C_2, OS_2))
    # 删除临时变量
    del T_r
    del r
    del R
    del OS_1
    del OS_2
    del C_1
    del C_2
    return CHS1, CHS2


# 工序交叉部分
def Crossover_Operation(CHS1, CHS2, T0, J_number):
    OS_1 = CHS1[T0:2 * T0]
    OS_2 = CHS2[T0:2 * T0]
    MS_1 = CHS1[0:T0]
    MS_2 = CHS2[0:T0]
    Job_list = [i for i in range(J_number)]
    random.shuffle(Job_list)
    r = random.randint(1, J_number - 1)
    Set1 = Job_list[0:r]
    # Set2 = Job_list[r:J_number]
    new_os = list(np.zeros(T0, dtype=int))
    for k, v in enumerate(OS_1):
        if v in Set1:
            new_os[k] = v + 1
    for i in OS_2:
        if i not in Set1:
            Site = new_os.index(0)
            new_os[Site] = i + 1
    new_os = np.array([j - 1 for j in new_os])
    CHS1 = np.hstack((MS_1, new_os))
    CHS2 = np.hstack((MS_2, new_os))
    # 删除临时变量
    del OS_1
    del OS_2
    del MS_1
    del MS_2
    del Job_list
    del r
    del Set1
    del new_os
    # 删除代码结束
    return CHS1, CHS2


def reduction(num, J_r, T0):
    T0 = [j for j in range(T0)]
    K = []
    Site = 0
    for k, v in J_r.items():
        K.append(T0[Site:Site + v])
        Site += v
    for i in range(len(K)):
        if num in K[i]:
            job = i
            O_number = K[i].index(num)
            break
    # 删除临时变量
    del T0
    del K
    del Site
    return job, O_number


def Select(Fit_value):
    Fit = []
    for i in range(len(Fit_value)):
        fit = 1 / Fit_value[i]
        Fit.append(fit)
    Fit = np.array(Fit)
    idx = np.random.choice(np.arange(len(Fit_value)), size=len(Fit_value), replace=True,
                           p=Fit / (Fit.sum()))
    # 删除临时变量
    del Fit
    return idx


class GA:
    def __init__(self, M_status, pop_size=2, p_c=0.8, p_m=0.3, p_v=0.5, p_w=0.95, max_iteration=1):
        self.Best_Job = None  # 最优的晶圆加工调度结果
        self.Best_Machine = None  # 最优的加工单元调度结果
        self.Pop_size = pop_size  # 种群数量
        self.P_c = p_c  # 交叉概率
        self.P_m = p_m  # 变异概率
        self.P_v = p_v  # 选择何种方式进行交叉
        self.P_w = p_w  # 采用何种方式进行变异
        self.Max_Iterations = max_iteration  # 最大迭代次数
        self.d = None  # 解码对象
        self.Machine_status = [x for x in M_status]
        self.Best_fit = []
        self.TM_msg = []  # 机械臂指令集合
        self.TM_List = []  # 机械臂编号集合

    # 适应度
    def fitness(self, CHS, J_f, Processing_t, M_number, Len):
        Fit = []
        for i in range(len(CHS)):
            self.d.reset()
            # d = Decode(J_f, Processing_t, M_number, self.Machine_status)
            Fit.append(self.d.Decode_1(CHS[i], Len))
        return Fit

    # 机器变异部分
    # @profile(precision=4, stream=open('memory_profiler.log', 'w+'))
    def Variation_Machine(self, CHS, O, T0, J, Machine_stat):  # CHS表示，O表示处理时间矩阵，T0表示，J表示工件对应工序数
        Tr = [i_num for i_num in range(T0)]
        MS = CHS[0:T0]
        OS = CHS[T0:2 * T0]
        # 机器选择部分
        r = random.randint(1, T0 - 1)  # 在变异染色体中选择r个位置
        random.shuffle(Tr)
        T_r = Tr[0:r]
        for i in T_r:
            job = reduction(i, J, T0)
            # O_i = job[0]
            # O_j = job[1]
            Machine_using = O[job[0]][job[1]]
            Machine_time = []
            for j in range(len(Machine_using)):
                if Machine_using[j] != INVALID:
                    Machine_time.append(Machine_using[j] + Machine_stat[j])
            MS[i] = Machine_time.index(min(Machine_time))  # MS[i] = Min_index
            # print(Machine_time)
            # MS[i] = Min_index
            # 删除临时变量
            del job
            del Machine_using
            del Machine_time
        CHS = np.hstack((MS, OS))
        # 删除临时变量
        del Tr
        del MS
        del OS
        del r
        del T_r
        return CHS

    # 工序变异部分
    # @profile(precision=4, stream=open('memory_profiler.log', 'w+'))
    def Variation_Operation(self, CHS, T0, J_number, J_v, Process_time, M_number):
        MS = CHS[0:T0]
        OS = list(CHS[T0:2 * T0])
        r = random.randint(1, J_number - 1)
        Tr = [i for i in range(J_number)]
        random.shuffle(Tr)
        Tr = Tr[0:r]
        # J_os = dict(enumerate(OS))  # 随机选择r个不同的基因
        # J_os = sorted(J_os.items(), key=lambda d: d[1])
        Site = []
        for i in range(r):
            Site.append(OS.index(Tr[i]))
        A = list(itertools.permutations(Tr, r))
        A_CHS = []
        for i in range(len(A)):
            for j in range(len(A[i])):
                OS[Site[j]] = A[i][j]
            C_I = np.hstack((MS, OS))
            A_CHS.append(C_I)
            gc.collect()
        Fit = []
        for i in range(len(A_CHS)):
            # d = Decode(J_v, Process_time, M_number, self.Machine_status)
            self.d.reset()
            Fit.append(self.d.Decode_1(CHS, T0))
        # 删除临时变量
        index = Fit.index(min(Fit))
        del Tr
        del MS
        del OS
        del r
        del Site
        del A
        del Fit
        return A_CHS[index]

    def set_TM_Message(self, M_num, TM_num, group_name_index, cur_time):
        for i in range(M_num - TM_num, M_num):
            self.TM_List.append(i)
        for i in self.TM_List:
            Machine = self.Best_Machine[i]
            Start_time = Machine.O_start
            End_time = Machine.O_end
            for i_1 in range(len(End_time)):
                j = Machine.assigned_task[i_1][0] - 1
                o = Machine.assigned_task[i_1][1] - 1
                pre = self.Best_Job[j].J_machine[o - 1]
                nxt = self.Best_Job[j].J_machine[o + 1]
                time_1 = Start_time[i_1]  # 设置时间格式为单位时间格式
                time_2 = Start_time[i_1] + pick_time  # 设置时间格式为单位时间格式
                time_3 = End_time[i_1] - put_time  # 设置时间格式为单位时间格式
                # time_1 = Timestep2Time(cur_time, Start_time[i_1])  # 设置时间格式为具体时间格式
                # time_2 = Timestep2Time(cur_time, Start_time[i_1] + pick_time)  # 设置时间格式为具体时间格式
                # time_3 = Timestep2Time(cur_time, End_time[i_1] - put_time)  # 设置时间格式为具体时间格式
                self.TM_msg.append(Arm_Message(i, j+1, o+1, time_1, 0, pre, nxt))  # 机械臂取片指令
                self.TM_msg.append(Arm_Message(i, j+1, o+1, time_2, 2, pre, nxt))  # 机械臂移动指令
                self.TM_msg.append(Arm_Message(i, j+1, o+1, time_3, 1, pre, nxt))  # 机械臂放片指令
                # 删除临时变量
                del j
                del o
                del pre
                del nxt
            self.TM_msg.sort(key=lambda TM_msg: TM_msg.cmd_time)  # 根据机械臂指令的时间，对指令进行排序
            # 删除临时变量
            del Machine
            del Start_time
            del End_time

    def get_M_State(self, time):
        cur_state = []
        for m in self.Best_Machine:
            sec = 0
            if len(m.O_end) == 0:
                cur_state.append(0)
                continue
            for i in range(len(m.O_end)):
                if time <= m.O_end[i]:
                    sec = i
                    break
            if m.O_start[sec] < time <= m.O_end[sec]:
                cur_state.append(m.O_end[sec] - time)
            else:
                cur_state.append(0)
        return cur_state

    def print_TM_cmd(self, elements_name):
        for x in self.TM_msg:
            if x.move_type == 0:
                print('Machine:', elements_name[x.machine_no], ' Time:', x.cmd_time, ' pick from:',
                      elements_name[x.move_from])
            if x.move_type == 1:
                print('Machine:', elements_name[x.machine_no], ' Time:', x.cmd_time, ' put to:',
                      elements_name[x.move_to])
            # if x.move_type == 2:
            #     print('Machine:', x.machine_no, ' Time:', x.cmd_time, ' move from:', x.move_from, ' to:', x.move_to)

    # 打印word中的红字指令
    def print_Message_Flow(self, elements_name, type_index):
        self.TM_msg.sort(key=lambda y: y.cmd_time)  # 按时间进行排序
        print('------------------')
        for x in self.TM_msg:
            if x.move_type == 0:    # 机械臂操作为取片，pick
                # 从CM取片
                # if type_index['CM'] <= x.move_from <= type_index['CM_end']:
                #     print(elements_name[x.move_from], ':', 'PREPARE_SEND')
                print('RobotActionCmdType::Pick')
                print('nSlot/ModuleSlot=', elements_name[x.wafer_no], 'index:', x.wafer_no, '  (PREPARE_SEND)')
                print('TargetModule=', elements_name[x.move_from], 'index:', x.move_from)  # 应该存编号？nArm是啥
                print('Time:', x.cmd_time, ' ', elements_name[x.move_from], ':', 'PREPARE_SEND')
                print('Time:', x.cmd_time, ' ', elements_name[x.machine_no], ':', 'PICK_WAFER', 'index:', x.machine_no)
                print('Time:', x.cmd_time, ' ', elements_name[x.move_from], ':', 'POST_SEND')
            if x.move_type == 1:    # 机械臂操作为放片，place
                print('RobotActionCmdType::Place')
                print('nSlot/ModuleSlot=', elements_name[x.wafer_no], 'index:', x.wafer_no, '  (PREPARE_RECV)')
                print('TargetModule=', elements_name[x.move_to], 'index:', x.move_to)  # 应该存编号？nArm是啥
                print('Time:', x.cmd_time, ' ', elements_name[x.move_to], ':', 'PREPARE_RECV')
                print('Time:', x.cmd_time, ' ', elements_name[x.machine_no], ':', 'PLACE_WAFER', 'index:', x.machine_no)
                print('Time:', x.cmd_time, ' ', elements_name[x.move_to], ':', 'POST_RECV')
            # if x.move_type == 2:
            #     print('Machine:', x.machine_no, ' Time:', x.cmd_time, ' move from:', x.move_from, ' to:', x.move_to)

    # 将cmd命令所需的信息输出到json文件中
    def output_Message_to_Json(self, elements_name, cmd_message_path):
        Message_data = []
        self.TM_msg.sort(key=lambda y: y.cmd_time)  # 按时间进行排序
        num = 0
        last_msg = {}
        for x in self.TM_msg:
            msg = {}
            if num > 0:
                last_msg['relative_time'] = x.cmd_time - last_msg['time']
            if x.move_type == 0:    # 机械臂操作为取片，pick
                msg['number'] = num
                num = num + 1
                msg['time'] = x.cmd_time
                msg['type'] = 'pick'

                x_split = elements_name[x.move_from].split("-")
                module_name = x_split[0]
                slot_num = x_split[1]
                msg['target'] = module_name
                msg['target_slot'] = slot_num

                tm_split = elements_name[x.machine_no].split("-")
                tm_name = tm_split[0]
                tm_slot_num = tm_split[1]
                msg['TM'] = tm_name
                msg['TM_slot'] = tm_slot_num

                Message_data.append(msg)
                last_msg = msg
            if x.move_type == 1:    # 机械臂操作为放片，place
                msg['number'] = num
                num = num + 1
                msg['time'] = x.cmd_time
                msg['type'] = 'place'

                x_split = elements_name[x.move_to].split("-")
                module_name = x_split[0]
                slot_num = x_split[1]
                msg['target'] = module_name
                msg['target_slot'] = slot_num

                tm_split = elements_name[x.machine_no].split("-")
                tm_name = tm_split[0]
                tm_slot_num = tm_split[1]
                msg['TM'] = tm_name
                msg['TM_slot'] = tm_slot_num

                last_msg = msg
                Message_data.append(msg)
        last_msg['relative_time'] = -1   # 最后一个因为没有再下一个来减了，所以相对时间设置为0
        with open(cmd_message_path, 'w+', encoding='utf-8') as file:
            json.dump(Message_data, file, indent=4)
        # print(Message_data)

    def main(self, processing_time, J_O, m_num, j_num, o_num, TM_num, group_name_index, elements_name, type_index, cmd_message_path):
        start_time = datetime.datetime.now()
        print("start time is : ", start_time)
        e = Encode(processing_time, self.Pop_size, J_O, j_num, m_num, self.Machine_status)
        # OS_List = e.OS_List()
        Len_Chromo = e.Len_Chromo
        CHS1 = e.Global_initial()
        # CHS2 = e.Random_initial()
        # CHS3 = e.Local_initial()
        # C = np.vstack((CHS1, CHS2, CHS3))
        C = CHS1
        Optimal_fit = INVALID
        # Optimal_CHS = 0
        self.d = Decode(J_O, processing_time, m_num, TM_num, self.Machine_status)
        for i in range(self.Max_Iterations):
            Fit = self.fitness(C, J_O, processing_time, m_num, Len_Chromo)
            Best = C[Fit.index(min(Fit))]
            best_fitness = min(Fit)
            if best_fitness < Optimal_fit:
                Optimal_fit = best_fitness
                Optimal_CHS = Best
                self.Best_fit.append(Optimal_fit)
                print('best_fitness', best_fitness)
                # d = Decode(J_O, processing_time, m_num, self.Machine_status)
                self.d.reset()
                Fit.append(self.d.Decode_1(Optimal_CHS, Len_Chromo))
                self.Best_Machine = deepcopy(self.d.Machines)
                self.Best_Job = deepcopy(self.d.Jobs)
                # Gantt_Machine(d.Machines)  # 根据机器调度结果，绘制调度结果的甘特图
                # Gantt_Job(d.Jobs)  # 根据工件调度结果，绘制调度结果的甘特图
            else:
                self.Best_fit.append(Optimal_fit)
            # Select = self.Select(Fit)
            for j in range(len(C)):
                offspring = []
                if random.random() < self.P_c:
                    N_i = random.choice(np.arange(len(C)))
                    if random.random() < self.P_v:
                        Crossover = Crossover_Machine(C[j], C[N_i], Len_Chromo)
                        # print('Cov1----->>>>>',len(Crossover[0]),len(Crossover[1]))
                    else:
                        Crossover = Crossover_Operation(C[j], C[N_i], Len_Chromo, j_num)
                    offspring.append(Crossover[0])
                    offspring.append(Crossover[1])
                    offspring.append(C[j])
                if random.random() < self.P_m:
                    if random.random() < self.P_w:
                        Mutation = self.Variation_Machine(C[j], processing_time, Len_Chromo, J_O, self.Machine_status)
                    else:
                        Mutation = self.Variation_Operation(C[j], Len_Chromo, j_num, J_O, processing_time, m_num)
                    offspring.append(Mutation)
                if offspring:
                    Fit = []
                    for i in range(len(offspring)):
                        # d = Decode(J_O, processing_time, m_num, self.Machine_status)
                        self.d.reset()
                        flg = True
                        jobs = self.d.Jobs
                        for a in range(len(jobs) - 1):
                            if jobs[a].Last_Processing_end_time > jobs[a + 1].Last_Processing_end_time:
                                flg = False
                        if flg:
                            Fit.append(self.d.Decode_1(offspring[i], Len_Chromo))
                        else:
                            Fit.append(INVALID)
                        del jobs
                    C[j] = offspring[Fit.index(min(Fit))]
            print("current time : ", datetime.datetime.now())
        stop_time = datetime.datetime.now()
        self.set_TM_Message(m_num, TM_num, group_name_index, stop_time)
        # self.print_TM_cmd(elements_name)
        # self.print_Message_Flow(elements_name, type_index)
        self.output_Message_to_Json(elements_name, cmd_message_path)  # 将cmd命令所需的信息输出到json文件中
        # Gantt_Machine(self.Best_Machine)  # 根据机器调度结果，绘制调度结果的甘特图
        # Gantt_Job(self.Best_Job)  # 根据工件调度结果，绘制调度结果的甘特图
        r_time = stop_time - start_time
        print("Running time : ", r_time.total_seconds(), 'seconds')
        print("Time steps = ", Time2Timestep(start_time, stop_time))
        # 删除临时变量
        del start_time
        del e
        del Len_Chromo
        del CHS1
        del C
        del Optimal_fit
        del stop_time
        del r_time

    # 逻辑参考函数：def Gantt_Machine(Machines)
    def get_TM_Move_List(self, M_num, TM_num, group_name_index):
        # for i in range(len(self.Best_Machine)):
        for i in range(M_num - TM_num, M_num):
            print('i:' + str(i))
            print('TM Name:' + group_name_index[i])
            Machine = self.Best_Machine[i]
            Start_time = Machine.O_start
            End_time = Machine.O_end
            for j in range(len(End_time)):
                print('step' + str(j) + ': Start_time:' + str(Start_time[j]) + ' End_time:' + str(End_time[j]))
