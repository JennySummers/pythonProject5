import json
import GeneticA
import GeneticA_re
from read_Json import INVALID, get_Recipe
import sys

def set_Wafer(layout_path="./config/example3/layout.json",
              layout_raw_path="./config/example3/layout_raw.json",
              wafer_path="./config/example3/wafer.json",
              wafer_noBM_path="./config/example3/wafer_noBM.json",
              cmd_message_path="./config/example3/cmd_message.json",
              read_from_cpp_path='./config/example3/Sch_output.json'):
    return layout_path, layout_raw_path, wafer_path, wafer_noBM_path, cmd_message_path, read_from_cpp_path

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
    def __init__(self):
        self.New_Processing_time = []  # 故障发生后新产生的各个晶圆处理时间矩阵
        self.New_Machine_status = []  # 故障发生后机器状态
        self.New_J = {}
        self.New_M_num = 0
        self.New_TM_num = 0
        self.New_J_num = 0
        self.New_O_num = 0

    def Join(self, pre_wafers, new_wafers):
        no = int(1)
        for Wafer in pre_wafers:
            if Wafer.has_processing:
                new_array = []
                tmp = []
                for i in range(len(Wafer.recipe_array[Wafer.processing_step])):
                    tmp.append(INVALID)
                tmp[Wafer.processing_unit_num] = Wafer.recipe_array[Wafer.processing_step][Wafer.processing_unit_num] - Wafer.time_proceed
                new_array.append(tmp)
                for i in range(Wafer.processing_step + 1, len(Wafer.recipe_array)):
                    new_array.append(Wafer.recipe_array[i])
                self.New_Processing_time.append(new_array)
                self.New_J[no] = len(Wafer.recipe_array) - Wafer.processing_step
                self.New_O_num = self.New_O_num + self.New_J[no]
                self.New_J_num = self.New_J_num + 1
            else:
                self.New_Processing_time.append(Wafer.recipe_array)
                self.New_J[no] = len(Wafer.recipe_array)
                self.New_O_num = self.New_O_num + self.New_J[no]
                self.New_J_num = self.New_J_num + 1
            no = no + 1
        for k, v in new_wafers.J.items():
            self.New_J[no] = v
            no = no + 1
        for pro_t in new_wafers.Processing_time:
            self.New_Processing_time.append(pro_t)
        self.New_O_num = self.New_O_num + new_wafers.O_num
        self.New_J_num = self.New_J_num + new_wafers.J_num
        self.New_M_num = new_wafers.M_num
        self.New_TM_num = new_wafers.TM_num
        self.New_Machine_status = new_wafers.Machine_status
        print('done')

    # processing_time, J_O, m_num, j_num, o_num, TM_num, group_name_index, elements_name, type_index, cmd_message_path
    def main(self, pre_wafers):
        Layout_path, layout_raw_path, Wafer_path, Wafer_noBM_path, Cmd_message_path, read_from_cpp_path = set_Wafer()
        r = get_Recipe(Layout_path, layout_raw_path, Wafer_path, Wafer_noBM_path, read_from_cpp_path)
        self.Join(pre_wafers, r)
        g = GeneticA.GA(r.Machine_status)
        g.main(self.New_Processing_time, self.New_J, self.New_M_num, self.New_J_num, self.New_O_num, self.New_TM_num, r.group_name_index,
               r.type_index, Cmd_message_path)

# 用于被c语言调用
if __name__ == '__main__':
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
        tmIndexs = json.load(f)

    print(wafers)

    # TODO 调用遗传算法
    # 在输出格式上，进行了简化，现在只需输出动作类型+目标机器号+机械臂机器号 三元组即可，参照GA::simple_output_Message_to_Json和config/example3/cmd_message_bak.json
    new_join = New_join()
    new_join.main(wafers)
