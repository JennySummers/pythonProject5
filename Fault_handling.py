from copy import *
from GeneticA import GA
from Instance import Processing_time, J, M_num, J_num, O_num, Machine_status
import numpy as np

from read_Json import INVALID
from Messages import Message


class Fault:
    def __init__(self, message):
        self.fault_type = message.fault_type  # 故障类型，0代表机器故障但可以将其中的片取出，1代表机器故障且不可将其中的片取出
        self.fault_pos = message.fault_pos  # 故障机器位置
        self.fault_time = message.fault_time  # 故障时间
        self.fault_wafer = None  # 故障发生时的晶圆编号
        self.fault_op = None  # 故障发生时的工序编号
        self.pres_jobs = None  # 当前正在处理的晶圆的加工工艺序列
        self.pres_machines = None  # 当前调度方案的机器加工状态
        self.New_Processing_time = []  # 故障发生后新产生的各个晶圆处理时间矩阵
        self.New_Machine_status = None  # 故障发生后机器状态
        self.New_J = {}
        self.New_M_num = 0
        self.New_J_num = 0
        self.New_O_num = 0

    def set_pres_jobs(self, jobs):
        self.pres_jobs = deepcopy(jobs)

    def set_pres_machines(self, machines):
        self.pres_machines = deepcopy(machines)

    def get_W_State(self):
        jobs = []  # 当前正在处理的工序编号
        cur_m = []  # 当前正在处理的机器，已完成则为-1
        res_t = []  # 剩余处理时间，已完成则为0
        for i in range(len(self.pres_jobs)):
            new_s = 0
            while self.pres_jobs[i].J_end[new_s] < self.fault_time and new_s < self.pres_jobs[i].Operation_num:
                new_s += 1
            if new_s >= self.pres_jobs[i].Operation_num:  # 当前晶圆的所有工艺都已加工完成
                jobs.append(-1)
                cur_m.append(-1)
                res_t.append(0)
                continue
            if self.pres_jobs[i].J_start[new_s] <= self.fault_time:  # 当前工艺已经开始加工
                if self.pres_jobs[i].J_machine[new_s] == self.fault_pos:
                    jobs.append(-1)
                    self.fault_wafer = i
                    self.fault_op = new_s
                else:
                    jobs.append(new_s)
                cur_m.append(self.pres_jobs[i].J_machine[new_s])
                res_t.append(self.pres_jobs[i].J_end[new_s] - self.fault_time)
            else:  # 当前工艺尚未开始加工
                jobs.append(new_s)
                cur_m.append(-1)
                res_t.append(0)
        return jobs, cur_m, res_t  # 返回当前正在处理的晶圆的编号(已完成为-1)，当前正在处理的机器编号，剩余处理时间，剩余加工工序数

    def get_Machine_status(self):
        return self.New_Processing_time, self.New_M_num

    def get_Job_status(self):
        return self.New_J, self.New_J_num, self.New_O_num

    def Fault_Handle(self, processing_time, m_num):  # 用于对发生故障后的处理单元及晶圆状态获取，以便重新调度
        jobs, cur_m, res_t = self.get_W_State()
        cnt = 0
        for i in range(len(jobs)):
            if jobs[i] != -1:
                self.New_J[i+1] = self.pres_jobs[i].Operation_num - jobs[i]
                self.New_O_num += self.New_J[i+1]
                self.New_J_num += 1
                self.New_Processing_time.append([])
                if cur_m[i] != -1:
                    self.New_Processing_time[cnt].append([INVALID for _ in range(m_num)])
                    self.New_Processing_time[cnt][0][cur_m[i]] = res_t[i]
                    if jobs[i] + 1 < self.pres_jobs[i].Operation_num:
                        for x in (processing_time[i][jobs[i] + 1:]):
                            self.New_Processing_time[cnt].append([y for y in x])
                else:
                    for x in (processing_time[i][jobs[i]:]):
                        self.New_Processing_time[cnt].append([y for y in x])
                cnt += 1
        for x in self.New_Processing_time:
            for y in x:
                y[self.fault_pos] = INVALID
        self.New_M_num = m_num


if __name__ == '__main__':
    g = GA(Machine_status)
    g.main(Processing_time, J, M_num, J_num, O_num)
    mes = Message(1, 4, 10)
    f = Fault(mes)
    f.set_pres_machines(g.Best_Machine)
    f.set_pres_jobs(g.Best_Job)
    f.Fault_Handle(Processing_time, M_num)
    g.main(f.New_Processing_time, f.New_J, f.New_M_num, f.New_J_num, f.New_O_num)
    print("1")

