from copy import *

import GeneticA
import GeneticA_re
from Instance import Processing_time, J, M_num, J_num, O_num, Machine_status
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
        for i in range(len(self.pres_jobs)):
            for j in range(self.pres_jobs[i].Operation_num):
                self.pre_machines.append(self.pres_jobs[i].J_machine[j])
                self.pre_jobs.append(i)
                self.pre_ops.append(j)
                self.pre_st.append(self.pres_jobs[i].J_start[j])
                self.pre_ed.append(self.pres_jobs[i].J_end[j])

    def Join(self, processing_time, j, m_num, j_num, o_num, TM_num):
        self.get_W_State()
        cnt = 0
        self.New_Processing_time = processing_time
        self.New_M_num = m_num
        self.New_TM_num = TM_num
        self.New_J_num = j_num
        self.New_O_num = o_num
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
        re.Pre_Job = self.pres_jobs
        # re.Best_Job = Best_Job
        re.main(new_Processing_time, new_J, new_M_num, new_J_num, new_O_num, new_TM_num, group_name_index,
                type_index, cmd_message_path)


if __name__ == '__main__':
    Layout_path, layout_raw_path, Wafer_path, Wafer_noBM_path, Cmd_message_path, read_from_cpp_path = set_Wafer()
    r = get_Recipe(Layout_path, layout_raw_path, Wafer_path, Wafer_noBM_path, read_from_cpp_path)
    g = GeneticA.GA(r.Machine_status)
    g.main(r.Processing_time, r.J, r.M_num, r.J_num, r.O_num, r.TM_num, r.group_name_index,
           r.type_index, Cmd_message_path)
    n = new_join(150)
    n.main(g.Best_Machine, g.Best_Job, r.Machine_status, r.Processing_time, r.J, r.M_num, r.J_num, r.O_num, r.TM_num,
           r.group_name_index, r.type_index, Cmd_message_path)
    print("1")
    # 取放 3.6ms
