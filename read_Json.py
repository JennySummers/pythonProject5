import json

layout_path = "./config/example1/layout.json"
wafer_path = "./config/example1/wafer.json"

Processing_time = []

wafer_num = []

group_elements_num = {}     # 各group含有的elements数量
group_elements_index={}     # 各group在list中的起始索引位；例CM1=0,PG1=4,则list中0-3位的数字表示CM1的时间
all_elements_num = 0    # CM/PM含有的elements总个数，即每个step的list中的元素个数

with open(layout_path, 'r', encoding='utf-8') as file:
    layout_json_data = json.load(file)
    # print(json.dumps(json_data, indent=4))
    # print(json.dumps(layout_json_data['PM'], indent=4))
    # 将CM/PM的各个group含有的element个数添加到字典
    index = 0   #各group在list中的起始索引位
    CM = layout_json_data['CM']
    for CG in CM:
        groupName = CG['groupName']
        # print(groupName)
        # print(PG['groupName'])
        len_group = len(CG['elements'])
        # CM/PM含有的elements总个数
        all_elements_num += len_group
        # 各group在list中的起始索引位
        group_elements_index[groupName] = index
        index += len_group
        # print(len_group)
        # print(PG['elements'])
        # group_elements_num.update(groupName:len_group)
        group_elements_num[groupName] = len_group
    PM = layout_json_data['PM']
    for PG in PM:
        groupName = PG['groupName']
        # print(groupName)
        # print(PG['groupName'])
        len_group = len(PG['elements'])
        all_elements_num += len_group
        group_elements_index[groupName] = index
        index += len_group
        # print(len_group)
        # print(PG['elements'])
        # group_elements_num.update(groupName:len_group)
        group_elements_num[groupName] = len_group


print(group_elements_num)
print(group_elements_index)
print(all_elements_num)

with open(wafer_path, 'r', encoding='utf-8') as file:
    wafer_json_data = json.load(file)
    # print(json.dumps(wafer_json_data, indent=4))
    for waferGroup in wafer_json_data:
        list_recipe = []    # 第二层[]，代表不同的recipe
        # print(waferGroup['waferGroupName'])
        # print(waferGroup['waferNum'])
        wafer_num.append(waferGroup['waferNum'])
        # print(json.dumps(waferGroup['recipe'], indent=4))
        recipe = waferGroup['recipe']
        # 工序数
        step_num = len(waferGroup['recipe'])
        print(step_num)
        for step in recipe:
            list_step = [9999]*all_elements_num  # 第三层[]，代表各个step需要的时间
            processModule = step['processModule']
            processTime = step['processTime']
            for name in processModule:
                index = group_elements_index[name]
                num = group_elements_num[name]
                # 修改这几个值为正确值
                for i in range(num):
                    list_step[index+i] = processTime
            # print(list_step)
            list_recipe.append(list_step)
        Processing_time.append(list_recipe)


print(Processing_time)  # 最后结果
# print(wafer_num)
# print(len(wafer_num))
