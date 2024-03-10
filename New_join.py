from copy import *

import GeneticA
import GeneticA_re
from read_Json import INVALID
import numpy as np
from read_Json import INVALID, get_Recipe


def set_Wafer(layout_path="./config/example3/layout.json",
              layout_raw_path="./config/example3/layout_raw.json",
              wafer_path="./config/example3/wafer.json",
              wafer_noBM_path="./config/example3/wafer_noBM.json",
              cmd_message_path="./config/example3/cmd_message.json",
              read_from_cpp_path='./config/example3/Sch_output.json'):
    return layout_path, layout_raw_path, wafer_path, wafer_noBM_path, cmd_message_path, read_from_cpp_path


class new_join:
    def __init__(self, join_time):
        self.pres_jobs = None  # 当前正在处理的晶圆的加工工艺序列
        self.pres_machines = None  # 当前调度方案的机器加工状态
        self.New_Processing_time = []  # 故障发生后新产生的各个晶圆处理时间矩阵
        self.New_Machine_status = []  # 故障发生后机器状态
        self.New_J = {}
        self.New_M_num = 0
        self.New_TM_num = 0
        self.New_J_num = 0
        self.New_O_num = 0

        self.pre_J = {}
        self.pre_machines = []
        self.pre_jobs = []
        self.pre_ops = []
        self.pre_st = []
        self.pre_ed = []
        self.pre_time = 0

        self.join_time = join_time

    def set_pres_jobs(self, jobs):
        self.pres_jobs = jobs

    def set_pres_machines(self, machines):
        self.pres_machines = machines

    def set_New_Machine_status(self, M_num, TM_num):
        for i in range(M_num):
            if i >= M_num - TM_num:
                self.New_Machine_status.append(int(0))
            else:
                self.New_Machine_status.append(int(max(0, self.pres_machines[i].End_time - self.join_time)))

    def get_W_State(self):
        jobs = []  # 当前正在处理的工序编号
        cur_m = []  # 当前正在处理的机器，已完成则为-1
        res_t = []  # 剩余处理时间，已完成则为0
        cnt = 0
        for i in range(len(self.pres_jobs)):
            new_s = 0
            while new_s < self.pres_jobs[i].Operation_num and self.pres_jobs[i].J_end[new_s] < self.join_time:
                new_s += 1
            if new_s >= self.pres_jobs[i].Operation_num:  # 当前晶圆的所有工艺都已加工完成
                jobs.append(-1)
                cur_m.append(-1)
                res_t.append(0)
                continue
            self.pre_J[cnt + 1] = self.pres_jobs[i].Operation_num - new_s
            if self.pres_jobs[i].J_start[new_s] <= self.join_time:  # 当前工艺已经开始加工
                jobs.append(new_s)
                cur_m.append(self.pres_jobs[i].J_machine[new_s])
                res_t.append(self.pres_jobs[i].J_end[new_s] - self.join_time)

                self.pre_machines.append(self.pres_jobs[i].J_machine[new_s])
                self.pre_jobs.append(cnt)
                self.pre_ops.append(0)
                self.pre_st.append(0)
                self.pre_ed.append(self.pres_jobs[i].J_end[new_s] - self.join_time)

            else:  # 当前工艺尚未开始加工
                jobs.append(new_s)
                cur_m.append(-1)
                res_t.append(0)

                self.pre_machines.append(self.pres_jobs[i].J_machine[new_s])
                self.pre_jobs.append(cnt)
                self.pre_ops.append(0)
                self.pre_st.append(self.pres_jobs[i].J_start[new_s] - self.join_time)
                self.pre_ed.append(self.pres_jobs[i].J_end[new_s] - self.join_time)

            for j in range(new_s + 1, self.pres_jobs[i].Operation_num):
                self.pre_machines.append(self.pres_jobs[i].J_machine[j])
                self.pre_jobs.append(cnt)
                self.pre_ops.append(j - new_s)
                self.pre_st.append(self.pres_jobs[i].J_start[j] - self.join_time)
                self.pre_ed.append(self.pres_jobs[i].J_end[j] - self.join_time)
            cnt = cnt + 1
        return jobs, cur_m, res_t  # 返回当前正在处理的晶圆的编号(已完成为-1)，当前正在处理的机器编号，剩余处理时间，剩余加工工序数

    def Join(self, processing_time, j, m_num, j_num, o_num, TM_num):
        jobs, cur_m, res_t = self.get_W_State()
        cnt = 0
        for i in range(len(jobs)):
            if jobs[i] != -1:
                self.New_J[cnt + 1] = self.pres_jobs[i].Operation_num - jobs[i]
                self.New_O_num += self.New_J[cnt + 1]
                self.New_J_num += 1
                self.New_Processing_time.append([])
                # o_i = 0
                # o_len = self.pres_jobs[i].Operation_num - jobs[i]
                if cur_m[i] != -1:
                    self.New_Processing_time[cnt].append([INVALID for _ in range(m_num)])
                    self.New_Processing_time[cnt][0][cur_m[i]] = res_t[i]
                    # self.New_Processing_time[cnt][o_i][cur_m[i]] = res_t[i]
                    # o_i += 1
                    if jobs[i] + 1 < self.pres_jobs[i].Operation_num:
                        for x in (processing_time[i][jobs[i] + 1:]):
                            self.New_Processing_time[cnt].append([y for y in x])
                else:
                    for x in (processing_time[i][jobs[i]:]):
                        self.New_Processing_time[cnt].append([y for y in x])
                # for x in range(o_i, o_len):
                #     self.New_Processing_time[cnt].append([INVALID for _ in range(m_num)])
                #     self.New_Processing_time[cnt][o_i][self.pres_jobs[i].J_machine[jobs[i] + x]] = self.pres_jobs[i].J_end[jobs[i] + x] - self.pres_jobs[i].J_start[jobs[i] + x]
                #     o_i += 1
                cnt += 1
        self.New_Processing_time = self.New_Processing_time + processing_time
        self.New_M_num = m_num
        self.New_TM_num = TM_num
        self.New_J_num += j_num
        self.New_O_num += o_num
        for k, v in j.items():
            self.New_J[cnt + 1] = v
            cnt += 1
        print('done')

    # processing_time, J_O, m_num, j_num, o_num, TM_num, group_name_index, elements_name, type_index, cmd_message_path
    def main(self, Best_Machine, Best_Job, new_status, new_Processing_time, new_J, new_M_num, new_J_num,
             new_O_num, new_TM_num, group_name_index, type_index, cmd_message_path):
        self.set_pres_machines(Best_Machine)
        self.set_pres_jobs(Best_Job)
        self.Join(new_Processing_time, new_J, new_M_num, new_J_num, new_O_num, new_TM_num)
        re = GeneticA_re.GA(self.join_time, new_status)
        re.set_Machine_status(self.pre_machines, self.pre_jobs, self.pre_st, self.pre_ed, self.pre_ops, new_J,
                              new_Processing_time, new_M_num, new_TM_num)
        re.set_pre_jobs(self.pre_J, self.pre_machines, self.pre_jobs, self.pre_st, self.pre_ed, self.pre_ops)
        # re.Best_Job = Best_Job
        re.main(new_Processing_time, new_J, new_M_num, new_J_num, new_O_num, new_TM_num, group_name_index,
                type_index, cmd_message_path)


if __name__ == '__main__':
    Layout_path, layout_raw_path, Wafer_path, Wafer_noBM_path, Cmd_message_path, read_from_cpp_path = set_Wafer()
    r = get_Recipe(Layout_path, layout_raw_path, Wafer_path, Wafer_noBM_path, read_from_cpp_path)
    g = GeneticA.GA(r.Machine_status)
    g.main(r.Processing_time, r.J, r.M_num, r.J_num, r.O_num, r.TM_num, r.group_name_index,
           r.type_index, Cmd_message_path)
    n = new_join(200)
    n.main(g.Best_Machine, g.Best_Job, r.Machine_status, r.Processing_time, r.J, r.M_num, r.J_num, r.O_num, r.TM_num,
           r.group_name_index, r.type_index, Cmd_message_path)
    print("1")
    # 取放 3.6ms
