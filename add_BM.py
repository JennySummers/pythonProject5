# 两层遍历判断wafer中相邻的两个processModule是否在同一个TM下
# 如果不在，则需要找中转的BM
# 将找到的BM插入recipe中
import json

group_elements_num = {'CM1': 4, 'PG1': 10, 'PG2': 2, 'PG3': 8, 'PG4': 2, 'PG5': 2, 'PG6': 8, 'PG7': 2, 'PG8': 8,
                      'PG9': 6, 'PG10': 3, 'PG11': 2, 'PG12': 8, 'PG13': 2, 'PG14': 8, 'PG15': 2, 'BM2-1': 2,
                      'BM2-2': 2, 'BM6-3': 2, 'BM6-1': 2, 'BM6-2': 2, 'BM8-1': 1, 'BM8-2': 1, 'BM6-11': 2, 'BM6-12': 2}
group_elements_index = {'CM1': 0, 'PG1': 4, 'PG2': 14, 'PG3': 16, 'PG4': 24, 'PG5': 26, 'PG6': 28, 'PG7': 36,
                        'PG8': 38, 'PG9': 46, 'PG10': 52, 'PG11': 55, 'PG12': 57, 'PG13': 65, 'PG14': 67, 'PG15': 75,
                        'BM2-1': 77, 'BM2-2': 79, 'BM6-3': 81, 'BM6-1': 83, 'BM6-2': 85, 'BM8-1': 87, 'BM8-2': 88,
                        'BM6-11': 89, 'BM6-12': 91}
buffer_module = ['BM2-1', 'BM2-2', 'BM6-3', 'BM6-1', 'BM6-2', 'BM8-1', 'BM8-2', 'BM6-11', 'BM6-12']
all_elements_num = 93
accessibleList = [{0}, {0}, {0}, {0}, {1}, {1}, {1}, {1}, {1}, {1}, {1}, {1}, {1}, {1}, {1, 2}, {1, 2}, {2}, {2}, {2},
                  {2}, {2}, {2}, {2}, {2}, {1, 2}, {1, 2}, {1, 3}, {1, 3}, {3}, {3}, {3}, {3}, {3}, {3}, {3}, {3},
                  {3, 4}, {3, 4}, {4}, {4}, {4}, {4}, {4}, {4}, {4}, {4}, {4}, {4}, {4}, {4}, {4}, {4}, {5}, {5}, {5},
                  {5}, {5}, {6}, {6}, {6}, {6}, {6}, {6}, {6}, {6}, {4, 7}, {4, 7}, {7}, {7}, {7}, {7}, {7}, {7}, {7},
                  {7}, {1, 7}, {1, 7}, {0, 1}, {0, 1}, {0, 1}, {0, 1}, {4}, {4}, {4, 5}, {4, 5}, {4, 5}, {4, 5}, {5},
                  {5}, {4, 6}, {4, 6}, {4, 6}, {4, 6}]
TM = [{'groupName': 'TM1', 'elements': ['TM1'], 'accessibleList': ['CM1', 'BM2-1', 'BM2-2'], 'transferTime': 3},
      {'groupName': 'TM2', 'elements': ['TM2'], 'accessibleList': ['BM2-1', 'BM2-2', 'PG1', 'PG2', 'PG4', 'PG5', 'PG15'], 'transferTime': 3},
      {'groupName': 'TM3', 'elements': ['TM3'], 'accessibleList': ['PG2', 'PG3', 'PG4'], 'transferTime': 3},
      {'groupName': 'TM4', 'elements': ['TM4'], 'accessibleList': ['PG5', 'PG6', 'PG7'], 'transferTime': 3},
      {'groupName': 'TM6', 'elements': ['TM6'], 'accessibleList': ['PG7', 'PG8', 'PG9', 'PG13', 'BM6-3', 'BM6-1', 'BM6-2', 'BM6-11', 'BM6-12'], 'transferTime': 3},
      {'groupName': 'TM8', 'elements': ['TM8'], 'accessibleList': ['BM6-1', 'BM6-2', 'BM8-1', 'BM8-2', 'PG10', 'PG11'], 'transferTime': 3},
      {'groupName': 'TM7', 'elements': ['TM7'], 'accessibleList': ['BM6-11', 'BM6-12', 'PG12'], 'transferTime': 3},
      {'groupName': 'TM5', 'elements': ['TM5'], 'accessibleList': ['PG13', 'PG14', 'PG15'], 'transferTime': 3}]

layout_path = "./config/example1/layout.json"
wafer_path = "./config/example1/wafer.json"
wafer_path_test = "./config/example1/wafer_noBM.json"

new_wafer_json_data = []

with open(wafer_path_test, 'r', encoding='utf-8') as file:
    wafer_json_data = json.load(file)
    for waferGroup in wafer_json_data:
        list_recipe = []  # 第二层[]，代表不同的recipe
        recipe = waferGroup['recipe']
        # 注意！waferGroup['recipe']是list类型，若直接=赋值会导致修改了new_recipe同时修改recipe
        # new_recipe = waferGroup['recipe']  # 插入BM后的新recipe
        new_recipe = list(waferGroup['recipe'])     # 插入BM后的新recipe
        step_num = len(recipe)  # 工序数
        index = 0   # 标记i在new_recipe中的所在位置
        for i in range(step_num-1):
            moduleName1 = recipe[i]['processModule'][0]
            moduleName2 = recipe[i+1]['processModule'][0]
            # print('moduleName1', moduleName1)
            moduleName1_index = group_elements_index[moduleName1]
            moduleName2_index = group_elements_index[moduleName2]
            # 相邻的两个processModule的可达的机械臂(的编号)：
            accessibleTM1 = accessibleList[moduleName1_index]
            accessibleTM2 = accessibleList[moduleName2_index]
            print('i=', i)
            print('index=', index)
            print(moduleName1, accessibleList[moduleName1_index])
            print(moduleName2, accessibleList[moduleName2_index])
            print()
            transfer = accessibleTM1 & accessibleTM2
            if transfer == set():   # 若两个processModule不在同一个TM下(交集为空)，则需要找这两组TM的accessibleList中共同的BM
                print('两个processModule不在同一个TM下(交集为空)')
                # print('moduleName1:', moduleName1)
                # print('i=', i)
                # print('accessibleTM1', accessibleTM1)
                # print('accessibleTM2', accessibleTM2)
                # TODO 有多个可选的BM怎么处理(采用双层循环？)
                flag = False
                for j in accessibleTM1:
                    access_module1 = TM[j]['accessibleList']
                    print('access_module1', access_module1)
                    for k in accessibleTM2:
                        access_module2 = TM[k]['accessibleList']
                        print('access_module2', access_module2)

                        # 找出这两个机械臂可达的BM
                        access_buffer_module1 = [l for l in access_module1 if l in buffer_module]
                        access_buffer_module2 = [l for l in access_module2 if l in buffer_module]
                        bm = [l for l in access_buffer_module1 if l in access_buffer_module2]
                        print('access_buffer_module1', access_buffer_module1)
                        print('access_buffer_module2', access_buffer_module2)
                        print('bm', bm)
                        print()

                        if bm:  # 非空
                            flag = True
                            # 将BM信息插入json文件中，若有多个BM可选则只插入第一个
                            # 需要考虑同时有多个BM的情况，如BM6-1/BM6-2,当前是选第一个，且在recipe中写死
                            bm_info = {
                                "processModule": [bm[0]],
                                "processTime": 0
                            }
                            # new_recipe.insert(i + 1, bm_info)
                            new_recipe.insert(index + 1, bm_info)
                            index = index + 1
                            print(new_recipe)
                            break
                    if flag:
                        break
                if not flag:
                    print('当前路径存在断路,请检查机台结构')
                    exit()
            index = index + 1

        print(new_recipe)
        waferGroup['recipe'] = new_recipe
        new_wafer_json_data.append(waferGroup)
    print(new_wafer_json_data)

with open(wafer_path, 'w+', encoding='utf-8') as file:
    json.dump(new_wafer_json_data, file, indent=4)


# a = {1}
# b = {0}
# c = a & b
# if c == set():
#     print('1')
# print(c)

# accessibleTM1 = {0}
# accessibleTM2 = {1}
# for j in accessibleTM1:
#     access_module1 = TM[j]['accessibleList']
#     print(access_module1)
# for k in accessibleTM2:
#     access_module2 = TM[j]['accessibleList']
#     print(access_module2)
# # 找出这两个机械臂可达的BM
# # access_buffer_module1 = access_module1 & buffer_module
# # access_buffer_module2 = access_module2 & buffer_module
# access_buffer_module1 = [i for i in access_module1 if i in buffer_module]
# access_buffer_module2 = [i for i in access_module2 if i in buffer_module]
# bm = [i for i in access_buffer_module1 if i in access_buffer_module2]
# # bm = access_buffer_module1 & access_buffer_module2
# print('access_buffer_module1', access_buffer_module1)
# print('access_buffer_module2', access_buffer_module2)
# print('bm[0]', bm[0])
# bm_info = {
#     "processModule": [bm[0]],
#     "processTime": 0
# }
# print(bm_info)

# access_buffer_module1 = ['BM2-2']
# access_buffer_module2 = ['BM2-1']
# bm = [l for l in access_buffer_module1 if l in access_buffer_module2]
# print('bm', bm)
# if bm == []:
#     print('1')
#     print('当前路径存在断路,请检查机台结构')
#     exit()

# bm = ['1']
# if bm:
#     print('0')

