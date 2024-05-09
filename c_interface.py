import json
import os

import numpy as np

import GeneticA
# import GeneticA_re
INVALID = 9999
pick_time = 0.1
put_time = 0.1
unit_time = 1.0  # 单位时间设定，单位为毫秒
import sys

# 记录一个晶圆的配方信息
class one_wafer_recipe:
    # recipe_array 二维数组，存储该晶圆的配方
    # processing_unit 正处于的单元
    # time_proceed 该晶圆在当前步骤中已进行加工的时间
    def __init__(self,one_wafer_json):
        self.recipe_array=one_wafer_json["recipe_array"]  # 二维数组，存储该晶圆的配方
        processing_unit=one_wafer_json.get("processing_unit")
        if processing_unit is None:
            self.has_processing=False  # 该晶圆是否已开始加工
        else :
            self.has_processing=True  # 该晶圆是否已开始加工
            self.time_proceed=0  # 该晶圆在当前步骤中已进行加工的时间
            self.processing_step=processing_unit["processing_step"]  # 该晶圆所处的加工步骤编号
            self.processing_unit_num=processing_unit["processing_unit"]  # 该晶圆所处的机器编号
            self.begin_time=processing_unit["begin_time"]  # 开始当前步骤加工的时间,用于统一计算time_proceed


class New_join:
    def __init__(self, m_num, tm_index, t_limit, tm_cool_time):
        self.New_Processing_time = []  # 故障发生后新产生的各个晶圆处理时间矩阵
        self.New_Machine_status = []  # 故障发生后机器状态
        self.New_J = {}
        self.New_M_num = m_num
        self.New_TM_list = tm_index
        self.New_J_num = 0
        self.New_O_num = 0
        self.time_limit = t_limit
        self.tm_cooling_time = tm_cool_time
        self.pre_list = []

    def Join(self, pre_wafers):
        no = int(1)
        for Wafer in pre_wafers:
            if Wafer.has_processing:
                new_array = []
                tmp = []
                for i in range(len(Wafer.recipe_array[Wafer.processing_step])):
                    tmp.append(INVALID)
                tmp[Wafer.processing_unit_num] = max(0, Wafer.recipe_array[Wafer.processing_step][Wafer.processing_unit_num] - Wafer.time_proceed)
                new_array.append(tmp)
                for i in range(Wafer.processing_step + 1, len(Wafer.recipe_array)):
                    new_array.append(Wafer.recipe_array[i])
                self.New_Processing_time.append(new_array)
                self.New_J[no] = len(Wafer.recipe_array) - Wafer.processing_step
                self.New_O_num = self.New_O_num + self.New_J[no]
                self.New_J_num = self.New_J_num + 1
                self.pre_list.append(no - 1)
                self.pre_list.append(Wafer.processing_unit_num)
            else:
                self.New_Processing_time.append(Wafer.recipe_array)
                self.New_J[no] = len(Wafer.recipe_array)
                self.New_O_num = self.New_O_num + self.New_J[no]
                self.New_J_num = self.New_J_num + 1
            no = no + 1
        # for k, v in new_wafers.J.items():
        #     self.New_J[no] = v
        #     no = no + 1
        # for pro_t in new_wafers.Processing_time:
        #     self.New_Processing_time.append(pro_t)
        # self.New_O_num = self.New_O_num + new_wafers.O_num
        # self.New_J_num = self.New_J_num + new_wafers.J_num
        self.New_Machine_status = np.zeros(self.New_M_num, dtype=float)
        print('done')

    # processing_time, J_O, m_num, j_num, o_num, TM_num, group_name_index, elements_name, type_index, cmd_message_path
    def main(self, Wafers):
        self.Join(Wafers)
        Cmd_message_path = './config/example3/cmd_message.json'
        g = GeneticA.GA(self.time_limit, self.tm_cooling_time, self.New_Machine_status, self.pre_list)
        g.main(self.New_Processing_time, self.New_J, self.New_M_num, self.New_J_num, self.New_O_num, self.New_TM_list, Cmd_message_path)

# 用于被c语言调用
if __name__ == '__main__':
    os.chdir(os.path.dirname(__file__)) # 修改工作目录为当前文件的绝对路径
    with open('config/example3/recipe_array.json') as f:
        json_data=json.load(f)
    # 存储至对象数组
    # wafers中每一个元素都存储了一片晶圆的调度需求
    wafers=[]
    max_begin_time=0
    for one_wafer_json in json_data:
        one_wafer=one_wafer_recipe(one_wafer_json)
        wafers.append(one_wafer)
        if one_wafer.has_processing and one_wafer.begin_time>max_begin_time:
            max_begin_time=one_wafer.begin_time
    # 已加工时间计算
    for wafer in wafers:
        if wafer.has_processing:
            wafer.time_proceed=max_begin_time-wafer.begin_time

    with open('config/example3/layout.json') as f:
        layout=json.load(f)
        tmIndex = layout['tmNumList']
        time_limit=layout['timeLimit']  # 每个机器上的最长等待时间
        tm_cooling_time=layout['tmTime']  # 机械臂的单次交互时间

    M_num = 0
    if wafers:
        M_num = len(wafers[0].recipe_array[0])

    print(wafers)

    # 在输出格式上，进行了简化，现在只需输出动作类型+目标机器号+机械臂机器号 三元组即可，参照GA::simple_output_Message_to_Json和config/example3/cmd_message_bak.json
    new_join = New_join(M_num, tmIndex, time_limit, tm_cooling_time)
    new_join.main(wafers)
