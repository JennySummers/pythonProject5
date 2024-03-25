import json

src_path = './config/XWX_test/recipe_array.json'
src_path_new = './config/example3/Sch_output_new.json'
wafer_noBM_path = "./config/example3/wafer_noBM.json"
src_path_indentation = './config/XWX_test/recipe_array_indentation.json'

# 将json读入后输出缩进格式
with open(src_path, 'r', encoding='utf-8') as file:
    data = json.load(file)
with open(src_path_indentation, 'w+', encoding='utf-8') as file:
    json.dump(data, file, indent=4)

# new_data = []
#
#
# # 判断该recipe是否已经存在.若存在则waferNum+1，否则将新的recipe添加进来
# def is_same_recipe(new_data, wafer):
#     recipe = list(wafer['recipe'])
#     for waferGroup in new_data:
#         if all(i in waferGroup['recipe'] for i in recipe):
#             print('该recipe已经存在')
#             waferGroup['waferNum'] = waferGroup['waferNum'] + wafer['waferNum']
#             print('waferNum=' + str(waferGroup['waferNum']))
#             return new_data
#     print('该recipe不存在')
#     new_data.append(wafer)
#     return new_data
#
#
# # 将processModule放进[]中
# def invert_processModule_in_list(data):
#     for waferGroup in data:
#         recipe = waferGroup['recipe']
#         for step in recipe:
#             processModule = [step['processModule']]
#             step['processModule'] = processModule
#     return data
#
#
# # 好像不需要？
# # recipe去重；将processModule放进[]中
# with open(src_path_new, 'r', encoding='utf-8') as file:
#     data = json.load(file)
#     for waferGroup in data:
#         recipe = list(waferGroup['recipe'])
#         new_data = is_same_recipe(new_data, waferGroup)
#     print(new_data)
#     new_data = invert_processModule_in_list(new_data)
#     print(new_data)
#
# with open(wafer_noBM_path, 'w+', encoding='utf-8') as file:
#     json.dump(new_data, file, indent=4)


