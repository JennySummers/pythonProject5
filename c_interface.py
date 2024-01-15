import json
import sys


# 记录一个晶圆的配方信息
class one_wafer_recipe:
    def __init__(self,one_wafer_json):
        self.recipe_array=one_wafer_json["recipe_array"] #二维数组，存储该晶圆的配方
        processing_unit=one_wafer_json.get("processing_unit")
        if processing_unit is None:
            self.has_processing=False # 该晶圆是否已开始加工
        else :
            self.has_processing=True # 该晶圆是否已开始加工
            self.time_proceed=0 # 该晶圆在当前步骤中已进行加工的时间
            self.processing_step=processing_unit["processing_step"] # 该晶圆所处的加工步骤编号
            self.processing_unit_num=processing_unit["processing_unit"] # 该晶圆所处的机器编号
            self.begin_time=processing_unit["begin_time"] # 开始当前步骤加工的时间,用于统一计算time_proceed

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
        if one_wafer.begin_time>max_begin_time:
            max_begin_time=one_wafer.begin_time
    # 已加工时间计算
    for wafer in wafers:
        wafer.time_proceed=max_begin_time-wafer.begin_time

    # TODO 调用遗传算法

    # 在输出格式上，进行了简化，现在只需输出动作类型+目标机器号+机械臂机器号 三元组即可，参照GA::simple_output_Message_to_Json和config/example3/cmd_message_bak.json

