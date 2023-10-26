import json

import numpy as np

from Instance import INVALID


class Read_json:
    def __init__(self, layout_path, wafer_path):
        # layout_path = "./config/example1/layout.json"
        # wafer_path = "./config/example1/wafer.json"
        self.layout_path = layout_path
        self.wafer_path = wafer_path
        self.Processing_time = []
        self.wafer_num = []     # wafer的数量
        self.group_elements_num = {}  # 各group含有的处理单元(elements)数量
        self.group_elements_index = {}  # 各group在list中的起始索引位；例CM1=0,PG1=4,则一个list中0-3位的数字表示CM1的时间
        self.all_elements_num = 0  # CM/PM含有的处理单元(elements)总个数，即每个step的list中的元素个数

    def get_Layout_Info(self):
        with open(self.layout_path, 'r', encoding='utf-8') as file:
            layout_json_data = json.load(file)
            # 将CM的各个group含有的处理单元(elements)个数、数组中的索引位添加到字典
            index = 0  # 各group在list中的起始索引位
            CM = layout_json_data['CM']
            for CG in CM:
                groupName = CG['groupName']
                len_group = len(CG['elements'])
                # CM、PM含有的elements总个数
                self.all_elements_num += len_group
                # 各group在数组(list)中的起始索引位
                self.group_elements_index[groupName] = index
                index += len_group
                # 该group含有的处理单元(elements)数量
                self.group_elements_num[groupName] = len_group
            # 将PM的各个group含有的处理单元(elements)个数、数组中的索引位添加到字典
            PM = layout_json_data['PM']
            for PG in PM:
                groupName = PG['groupName']
                len_group = len(PG['elements'])
                self.all_elements_num += len_group
                self.group_elements_index[groupName] = index
                index += len_group
                self.group_elements_num[groupName] = len_group
        print('group_elements_num', self.group_elements_num)
        print('group_elements_index', self.group_elements_index)
        print('all_elements_num', self.all_elements_num)

    def get_Wafer_Info(self):
        with open(self.wafer_path, 'r', encoding='utf-8') as file:
            wafer_json_data = json.load(file)
            for waferGroup in wafer_json_data:
                list_recipe = []  # 第二层[]，代表不同的recipe
                self.wafer_num.append(waferGroup['waferNum'])
                recipe = waferGroup['recipe']
                # 工序数
                step_num = len(waferGroup['recipe'])
                print('number of gongxu : ', step_num)
                for step in recipe:
                    list_step = [INVALID] * self.all_elements_num  # 第三层[]，表示一个step中不同的处理单元的用时
                    processModule = step['processModule']
                    processTime = step['processTime']
                    for name in processModule:
                        # 找到该group对应的位置
                        index = self.group_elements_index[name]
                        num = self.group_elements_num[name]
                        # 修改该gruop中的各处理单元对应的处理时间
                        for i in range(num):
                            list_step[index + i] = processTime
                    list_recipe.append(list_step)
                self.Processing_time.append(list_recipe)

        print(self.Processing_time)  # 最后结果
        print('wafer_num:', self.wafer_num)
        print('wafer_num:', len(self.wafer_num))


'''
J 表示各个工件对应的工序数。用键值对来表示。
Machine_status 表示当前状态下各个机器还需要Machine_status[i]个单位时间达到空闲状态。
M_num 表示机器数目。
O_Max_len 表示最大的工序数目
J_num 表示工件数目
O_num 表示所有工件的所有工序总数
'''


class get_Recipe:
    def __init__(self, layout_path, wafer_path):
        j = Read_json(layout_path, wafer_path)
        j.get_Layout_Info()
        j.get_Wafer_Info()
        self.M_num = j.all_elements_num
        self.O_Max_len = 4  # 待修改
        self.J_num = 8  # 待修改
        self.O_num = 27  # 待修改
        self.J = {1: 3, 2: 4, 3: 3, 4: 3, 5: 4, 6: 3, 7: 3, 8: 4}  # 待修改
        self.Processing_time = j.Processing_time
        self.Machine_status = np.zeros(self.M_num, dtype=float)
