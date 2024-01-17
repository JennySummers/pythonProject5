import json
import operator
from json import JSONDecodeError

from Jobs import Job
from Machines import Machine_Time_window


class process_unite:  # 处理指令单元类
    def __init__(self, j_no, o_no, m_no, begin_time, end_time):
        self.J_no = j_no  # 晶圆编号
        self.O_no = o_no  # 工序编号
        self.M_no = m_no  # 机器编号
        self.Begin_time = begin_time  # 开始时间
        self.End_time = end_time  # 结束时间


class processing_list:
    def __init__(self):
        self.J_list = []  # 晶圆编号
        self.O_list = []  # 工序编号
        self.M_list = []  # 机器编号
        self.begin_list = []  # 开始时间
        self.end_list = []  # 结束时间
        self.process_list = []  # 处理指令单元列表

    def Job2Info(self, job_list):
        for job in job_list:
            for i in range(job.Operation_num):
                self.J_list.append(job.Job_index)
                self.O_list.append(int(i+1))
                self.M_list.append(job.J_machine[i])
                self.begin_list.append(job.J_start[i])
                self.end_list.append(job.J_end[i])
                self.process_list.append(process_unite(job.Job_index, int(i+1), job.J_machine[i], job.J_start[i], job.J_end[i]))

    def Info2Job(self):  # 用于生成当前已调度晶圆状态的函数
        compares = operator.attrgetter('J_no', 'O_no')
        self.process_list.sort(key=compares)
        j_num = max(self.J_list)
        jobs = []
        for i in range(j_num):
            jobs.append(Job(int(i+1), self.J_list.count(i+1)))
        for pro_u in self.process_list:
            jobs[pro_u.J_no - 1]._Input(pro_u.Begin_time, pro_u.End_time, pro_u.M_no)
        return jobs

    def Info2Machine(self):  # 用于生成当前机台的占用状态的函数
        compares = operator.attrgetter('M_no', 'Begin_time')
        self.process_list.sort(key=compares)
        m_num = max(self.M_list) + 1
        machines = []
        for i in range(m_num):
            machines.append(Machine_Time_window(i, 0))
        for pro_u in self.process_list:
            machines[pro_u.M_no]._Input(pro_u.J_no - 1, pro_u.Begin_time, pro_u.End_time - pro_u.Begin_time, pro_u.O_no - 1)
        return machines

    def read_info(self, path):
        try:
            with open(path, "r", encoding="utf-8") as json_file_handle:
                json_obj = json.load(json_file_handle)
                print(type(json_obj))
                self.J_list = json_obj['J_list']  # 晶圆编号
                self.O_list = json_obj['O_list']  # 工序编号
                self.M_list = json_obj['M_list']  # 机器编号
                self.begin_list = json_obj['begin_list']  # 开始时间
                self.end_list = json_obj['end_list']  # 结束时间
                for i in range(len(self.J_list)):
                    self.process_list.append(process_unite(self.J_list[i], self.O_list[i], self.M_list[i], self.begin_list[i], self.end_list[i]))
        except FileExistsError as e:  # python3的语法
            print("py3文件不存在")
        except JSONDecodeError as e:
            print("JSON文件解码错误(数据格式不正确|没有内容)")

    def write_info(self, path):
        try:
            with open(path, "w+", encoding="utf-8") as json_file_handle:
                json_data = {}
                json.dump(json_data, json_file_handle)
                json_file_handle.seek(0)
                json_file_handle.truncate()
        except FileExistsError as e:
            print("文件不存在")
        try:
            info = dict()
            info['J_list'] = self.J_list
            info['O_list'] = self.O_list
            info['M_list'] = self.M_list
            info['begin_list'] = self.begin_list
            info['end_list'] = self.end_list
            json_str = json.dumps(info, ensure_ascii=False)  # ensure_ascii=False禁用ascii编码
            with open(path, "w+", encoding="utf-8") as json_file_handle:
                json_file_handle.write(json_str)
        except FileExistsError as e:
            print("文件不存在")

