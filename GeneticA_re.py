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
from Processing_list import processing_list
import itertools
from Messages import Arm_Message
import datetime
import math
import json


def Timestep2Time(cur_time, time_step, time_decay=0):  # 将单位时间转换为实际的时间
    return cur_time + datetime.timedelta(milliseconds=(time_step + time_decay) * unit_time)


def Time2Timestep(start_time, cur_time):  # 将实际的时间转换为单位时间
    return math.ceil(((cur_time - start_time)/datetime.timedelta(milliseconds=1)) / unit_time)


def set_Processing_list(Best_jobs):  # 将最终的调度结果存入json文件
    path = 'config/example3/processing_list.json'
    process = processing_list()
    process.Job2Info(Best_jobs)
    process.write_info(path)


def get_Processing_list():  # 将json文件中的信息读取到job和machine中
    path = 'config/example3/processing_list.json'
    process = processing_list()
    process.read_info(path)
    pre_jobs = process.Info2Job()
    pre_machine = process.Info2Machine()
    return pre_jobs, pre_machine


class GA:
    def __init__(self, join_time, M_status, pop_size=2):
        self.join_time = join_time
        self.Pre_Job = None  # 之前的晶圆加工调度结果
        self.Best_Job = None  # 最优的晶圆加工调度结果
        self.Best_Machine = None  # 最优的加工单元调度结果
        self.Pop_size = pop_size  # 种群数量
        self.d = None  # 解码对象
        self.Machine_status = [x for x in M_status]
        self.Best_fit = []
        self.TM_msg = []  # 机械臂指令集合
        self.TM_List = []  # 机械臂编号集合

    '''
    def set_Jobs(self, jobs):
        self.Best_Job = jobs

    def set_Machines(self, machines):
        self.Best_Machine = machines
    '''

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
                # TODO 解决先前序列输出问题
                pre = self.Best_Job[j].J_machine[o - 1]
                nxt = self.Best_Job[j].J_machine[o + 1]
                time_1 = Start_time[i_1]  # 设置时间格式为单位时间格式
                time_2 = Start_time[i_1] + pick_time  # 设置时间格式为单位时间格式
                time_3 = End_time[i_1] - put_time  # 设置时间格式为单位时间格式
                # time_1 = Timestep2Time(cur_time, Start_time[i_1])  # 设置时间格式为具体时间格式
                # time_2 = Timestep2Time(cur_time, Start_time[i_1] + pick_time)  # 设置时间格式为具体时间格式
                # time_3 = Timestep2Time(cur_time, End_time[i_1] - put_time)  # 设置时间格式为具体时间格式
                if time_1 > self.join_time:
                    self.TM_msg.append(Arm_Message(i, j+1, o+1, time_1, 0, pre, nxt))  # 机械臂取片指令
                if time_1 > self.join_time:
                    self.TM_msg.append(Arm_Message(i, j+1, o+1, time_2, 2, pre, nxt))  # 机械臂移动指令
                if time_1 > self.join_time:
                    self.TM_msg.append(Arm_Message(i, j+1, o+1, time_3, 1, pre, nxt))  # 机械臂放片指令
            self.TM_msg.sort(key=lambda TM_msg: TM_msg.cmd_time)  # 根据机械臂指令的时间，对指令进行排序

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



    # 以精简形式将cmd命令所需的信息输出到json文件中
    def simple_output_Message_to_Json(self, cmd_message_path):
        Message_data = []
        self.TM_msg.sort(key=lambda y: y.cmd_time)  # 按时间进行排序
        msg_size = len(self.TM_msg)
        i = 0
        while i < msg_size:
            msg_group = []
            time = self.TM_msg[i].cmd_time

            while i < msg_size and self.TM_msg[i].cmd_time == time:
                msg = []
                type=self.TM_msg[i].move_type
                msg.append(self.TM_msg[i].move_type)
                msg.append(self.TM_msg[i].move_from if type==0 else self.TM_msg[i].move_to)
                msg.append(self.TM_msg[i].machine_no)

                msg_group.append(msg)
                i += 1
            Message_data.append(msg_group)

        with open(cmd_message_path, 'w+', encoding='utf-8') as file:
            json.dump(Message_data, file, indent=4)
        # print(Message_data)

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
                msg['slot'] = slot_num
                msg['TM'] = elements_name[x.machine_no]
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
                msg['slot'] = slot_num
                msg['TM'] = elements_name[x.machine_no]
                last_msg = msg
                Message_data.append(msg)
        last_msg['relative_time'] = 0   # 最后一个因为没有再下一个来减了，所以相对时间设置为0
        with open(cmd_message_path, 'w+', encoding='utf-8') as file:
            json.dump(Message_data, file, indent=4)
        # print(Message_data)

    def set_Machine_status(self, machines, jobs, sts, eds, ops, J_O, processing_time, m_num, TM_num):
        self.d = Decode(J_O, processing_time, m_num, TM_num, self.Machine_status, self.join_time)
        for i in range(len(machines)):
            self.d.set_Machines(machines[i], jobs[i], sts[i], eds[i] - sts[i], ops[i])

    def set_pre_jobs(self, pre_J, machines, jobs, sts, eds, ops):
        Jobs = []
        for k, v in pre_J.items():
            Jobs.append(Job(k, v))
        for i in range(len(machines)):
            Jobs[jobs[i]]._Input(sts[i], eds[i], machines[i])  # 参数含义:工件的工序最早开始时间，当前工序结束时间，选择的机器号
        self.Pre_Job = Jobs
    
    # 适应度
    def fitness(self, CHS, J_f, Processing_t, M_number, Len):
        Fit = [self.d.Decode_1(CHS[0], Len)]
        '''
        for i in range(len(CHS)):
            self.d.reset()
            # d = Decode(J_f, Processing_t, M_number, self.Machine_status)
            Fit.append(self.d.Decode_1(CHS[i], Len))
        '''
        return Fit

    def main(self, processing_time, J_O, m_num, j_num, o_num, TM_num, group_name_index, type_index, cmd_message_path):
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
        # self.d = Decode(J_O, processing_time, m_num, TM_num, self.Machine_status)
        Fit = self.fitness(C, J_O, processing_time, m_num, Len_Chromo)
        Best = C[Fit.index(min(Fit))]
        best_fitness = min(Fit)
        stop_time = datetime.datetime.now()
        r_time = stop_time - start_time
        print("Running time : ", r_time.total_seconds(), 'seconds')
        if best_fitness < Optimal_fit:
            Optimal_fit = best_fitness
            self.Best_fit.append(Optimal_fit)
            print('best_fitness', best_fitness)
            # d = Decode(J_O, processing_time, m_num, self.Machine_status)
            self.Best_Machine = deepcopy(self.d.Machines)
            # self.Best_Job = self.Pre_Job + self.d.Jobs
            self.Best_Job = []
            for job in self.Pre_Job:
                if job.Last_Processing_end_time > self.join_time:
                    self.Best_Job.append(job)
            for job in self.d.Jobs:
                if job.Last_Processing_end_time > self.join_time:
                    self.Best_Job.append(job)
            # Gantt_Machine(d.Machines)  # 根据机器调度结果，绘制调度结果的甘特图
            # Gantt_Job(d.Jobs)  # 根据工件调度结果，绘制调度结果的甘特图
        stop_time = datetime.datetime.now()
        set_Processing_list(self.Best_Job)
        pre_job, pre_machine = get_Processing_list()
        self.set_TM_Message(m_num, TM_num, group_name_index, stop_time)
        # self.print_TM_cmd(elements_name)
        # self.print_Message_Flow(elements_name, type_index)
        self.simple_output_Message_to_Json(cmd_message_path)  # 将cmd命令所需的信息输出到json文件中
        Gantt_Machine(self.Best_Machine)  # 根据机器调度结果，绘制调度结果的甘特图
        Gantt_Job(self.Best_Job)  # 根据工件调度结果，绘制调度结果的甘特图
        r_time = stop_time - start_time
        print("Running time : ", r_time.total_seconds(), 'seconds')
        print("Time steps = ", Time2Timestep(start_time, stop_time))

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
