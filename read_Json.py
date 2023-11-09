import json
import numpy as np
import copy

INVALID = 99999999


class Read_json:
    def __init__(self, layout_path, wafer_path, wafer_noBM_path):
        # layout_path = "./config/example1/layout.json"
        # wafer_path = "./config/example1/wafer.json"
        self.layout_path = layout_path
        self.wafer_path = wafer_path
        self.wafer_noBM_path = wafer_noBM_path
        self.Processing_time = []
        self.process_list = []  # 工序列表
        self.wafer_num = []  # wafer的数量
        self.group_elements_num = {}  # 各group含有的处理单元(elements)数量
        self.group_elements_index = {}  # 各group在list中的起始索引位；例CM1=0,PG1=4,则一个list中0-3位的数字表示CM1的时间
        self.all_elements_num = 0  # CM/PM含有的处理单元(elements)总个数，即每个step的list中的元素个数
        self.buffer_module = []  # 存放所有的BM，以供判断

        # 机械臂相关
        self.transfer_time = []  # 每个机械臂的取放时间
        self.accessibleList = []  # 每个PM/CM的可交互机械臂列表在transfer_time中的索引

    # 自动添加buffer到wafer.json
    def add_BM(self):
        new_wafer_json_data = []
        TM = self.layout_json_data['TM']
        with open(self.wafer_noBM_path, 'r', encoding='utf-8') as file:
            wafer_json_data = json.load(file)
            for waferGroup in wafer_json_data:
                list_recipe = []  # 第二层[]，代表不同的recipe
                recipe = waferGroup['recipe']
                # 注意！waferGroup['recipe']是list类型，若直接=赋值会导致修改了new_recipe同时修改recipe
                # new_recipe = waferGroup['recipe']  # 插入BM后的新recipe
                new_recipe = list(waferGroup['recipe'])  # 插入BM后的新recipe
                step_num = len(recipe)  # 工序数
                index = 0  # 标记recipe的索引i在new_recipe中的对应位置
                for i in range(step_num - 1):
                    moduleName1 = recipe[i]['processModule'][0]
                    moduleName2 = recipe[i + 1]['processModule'][0]
                    # print('moduleName1', moduleName1)
                    moduleName1_index = self.group_elements_index[moduleName1]
                    moduleName2_index = self.group_elements_index[moduleName2]
                    # 相邻的两个processModule的可达的机械臂(的编号)：
                    accessibleTM1 = self.accessibleList[moduleName1_index]
                    accessibleTM2 = self.accessibleList[moduleName2_index]
                    # print('i=', i)
                    # print('index=', index)
                    # print(moduleName1, self.accessibleList[moduleName1_index])
                    # print(moduleName2, self.accessibleList[moduleName2_index])
                    # print()
                    transfer = accessibleTM1 & accessibleTM2
                    if transfer == set():  # 若两个processModule不在同一个TM下(交集为空)，则需要找这两组TM的accessibleList中共同的BM
                        # print('moduleName1:', moduleName1)
                        # print('i=', i)
                        # print('accessibleTM1', accessibleTM1)
                        # print('accessibleTM2', accessibleTM2)
                        # TODO 有多个可选的BM怎么处理(采用双层循环？)
                        flag = False
                        for j in accessibleTM1:
                            access_module1 = TM[j]['accessibleList']
                            # print('access_module1', access_module1)
                            for k in accessibleTM2:
                                access_module2 = TM[k]['accessibleList']
                                # print('access_module2', access_module2)

                                # 找出这两个机械臂可达的BM
                                access_buffer_module1 = [l for l in access_module1 if l in self.buffer_module]
                                access_buffer_module2 = [l for l in access_module2 if l in self.buffer_module]
                                bm = [l for l in access_buffer_module1 if l in access_buffer_module2]

                                if bm:  # 非空
                                    flag = True
                                    # 将BM信息插入json文件中，若有多个BM可选则只插入第一个
                                    # 需要考虑同时有多个BM的情况，如BM6-1/BM6-2,当前是选第一个，且在recipe中写死
                                    bm_info = {
                                        "processModule": bm,
                                        "processTime": 0
                                    }
                                    # bm_info = {
                                    #     "processModule": [bm[0]],
                                    #     "processTime": 0
                                    # }
                                    print(bm_info)
                                    new_recipe.insert(index + 1, bm_info)
                                    index = index + 1
                                    break
                            if flag:
                                break
                        if not flag:
                            print('当前路径存在断路,请检查机台结构')
                            exit()
                    index = index + 1

                # print(new_recipe)
                waferGroup['recipe'] = new_recipe
                new_wafer_json_data.append(waferGroup)
            print(new_wafer_json_data)

        with open(self.wafer_path, 'w+', encoding='utf-8') as file:
            json.dump(new_wafer_json_data, file, indent=4)

    # 根据晶圆的顺序实现按序取片
    def Ordered_wafer(self, arm_time=1):
        wafer_nums = [x for x in self.wafer_num]

    def get_Layout_Info(self):
        with open(self.layout_path, 'r', encoding='utf-8') as file:
            self.layout_json_data = json.load(file)
            # 将CM的各个group含有的处理单元(elements)个数、数组中的索引位添加到字典
            index = 0  # 各group在list中的起始索引位
            CM = self.layout_json_data['CM']
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
            PM = self.layout_json_data['PM']
            for PG in PM:
                groupName = PG['groupName']
                len_group = len(PG['elements'])
                self.all_elements_num += len_group
                self.group_elements_index[groupName] = index
                index += len_group
                self.group_elements_num[groupName] = len_group

            BM = self.layout_json_data['BM']
            for BG in BM:
                groupName = BG['groupName']
                self.buffer_module.append(groupName)
                len_group = len(BG['elements'])
                self.all_elements_num += len_group
                self.group_elements_index[groupName] = index
                index += len_group
                self.group_elements_num[groupName] = len_group
            # print(self.buffer_module)

            self.accessibleList = [set() for i in range(self.all_elements_num)]
            TM = self.layout_json_data['TM']
            for TG in TM:  # 遍历顺序是TM1,TM2,TM3,TM4,TM6,TM8,TM7,TM5
                count = len(TG['elements'])  # 该机械臂组所包含的元素数
                base = len(self.transfer_time)  # 该组之前已有的机械臂元素总数
                temp_accessible_set = {x for x in range(base, base + count)}  # 可访问集合列表

                # 存储每个机械臂的运动时间
                for i in range(count):
                    self.transfer_time.append(TG['transferTime'])

                # 构建从PM/CM至TM的索引
                for accessibleModule in TG['accessibleList']:
                    if self.group_elements_index.__contains__(
                            accessibleModule):  # 由于暂未将BM添加进group_elements_index中，故添加此判断条件来跳过BM
                        index = self.group_elements_index[accessibleModule]
                        num = self.group_elements_num[accessibleModule]
                        for i in range(num):
                            self.accessibleList[i + index] |= temp_accessible_set

        print('group_elements_num', self.group_elements_num)
        print('group_elements_index', self.group_elements_index)
        print('all_elements_num', self.all_elements_num)

    # TODO 当前此函数生成的路径存在断路（如Processing_time[0][1]中所有时间均是9999），因为没有考虑BM，有些转移不能依靠单个机械臂完成，需要在此种情况下自动插入BM step
    def get_Wafer_Info(self):
        with open(self.wafer_path, 'r', encoding='utf-8') as file:
            wafer_json_data = json.load(file)
            for waferGroup in wafer_json_data:
                list_recipe = []  # 第二层[]，代表不同的recipe
                wafer_num = waferGroup['waferNum']
                self.wafer_num.append(wafer_num)
                recipe = waferGroup['recipe']
                # 工序数
                step_num = len(recipe)
                # self.process_list.append(step_num)
                # print('number of gongxu : ', step_num)
                last_transfer = None
                for step in recipe:
                    now_transfer = set()
                    list_step = [INVALID] * (
                            self.all_elements_num + len(self.transfer_time))  # 第三层[]，表示一个step中不同的处理单元的用时
                    transfer_step_time = [INVALID] * (self.all_elements_num + len(self.transfer_time))
                    processModule = step['processModule']
                    processTime = step['processTime']
                    for name in processModule:
                        # 找到该group对应的位置
                        index = self.group_elements_index[name]
                        num = self.group_elements_num[name]
                        # 修改该gruop中的各处理单元对应的处理时间
                        for i in range(num):
                            list_step[index + i] = copy.deepcopy(processTime)
                            now_transfer |= self.accessibleList[index + i]  # 记录与当前工序相关联的机械臂
                    # 在工序列表中添加机械臂行
                    if last_transfer:  # 第一个工序不需要添加前置机械臂
                        transfer = last_transfer & now_transfer  # 选取前一道工序和当前工序关联机械臂的交集
                        for transfer_index in transfer:  # TODO 假如该工序与多个机械臂有关联，怎么处理？
                            transfer_step_time[self.all_elements_num + transfer_index] = self.transfer_time[
                                transfer_index]
                        list_recipe.append(transfer_step_time)
                    last_transfer = now_transfer
                    list_recipe.append(list_step)
                self.process_list.append(len(list_recipe))  # 算上机械臂后的工序数
                for i in range(wafer_num):
                    self.Processing_time.append(copy.deepcopy(list_recipe))
        # print(self.Processing_time)  # 最后结果

        # print('wafer_num:', self.wafer_num)
        # print('wafer_num:', len(self.wafer_num))


'''
J 表示各个工件对应的工序数。用键值对来表示。
Machine_status 表示当前状态下各个机器还需要Machine_status[i]个单位时间达到空闲状态。
M_num 表示机器数目。
O_Max_len 表示最大的工序数目
J_num 表示工件数目
O_num 表示所有工件的所有工序总数
'''


class get_Recipe:
    def __init__(self, layout_path, wafer_path, wafer_noBM_path):
        j = Read_json(layout_path, wafer_path, wafer_noBM_path)
        j.get_Layout_Info()
        j.add_BM()
        j.get_Wafer_Info()
        # self.M_num = j.all_elements_num  # 配方的可用机器数
        self.M_num = j.all_elements_num + len(j.transfer_time)  # 配方的可用机器数,要考虑TM
        self.O_Max_len = 0  # 表示最大的工序数目
        # self.J_num = len(j.process_list)  # 表示工件数目
        self.J_num = len(j.Processing_time)  # 表示工件数目
        self.O_num = 0  # 表示所有工件的所有工序总数
        self.J = {}  # 表示各个工件对应的工序数，用键值对来表示
        # for i in range(len(j.process_list)):
        for i in range(len(j.Processing_time)):
            # self.J[i] = j.process_list[i]
            self.J[i + 1] = len(j.Processing_time[i])
            # self.O_num = self.O_num + j.process_list[i]
            self.O_num = self.O_num + len(j.Processing_time[i])
            # self.O_Max_len = max(self.O_Max_len, j.process_list[i])
            self.O_Max_len = max(self.O_Max_len, len(j.Processing_time[i]))
        self.Processing_time = self.modify_processing(j.Processing_time)
        self.Machine_status = np.zeros(self.M_num, dtype=float)
        print(self.M_num)
        print(self.O_Max_len)
        print(self.J_num)
        print(self.O_num)
        print(self.J)

    def modify_processing(self, processing_time):
        tmp = copy.deepcopy(processing_time)
        for i in range(self.J_num):
            for j in range(self.J_num):
                tmp[i][0][j] = INVALID
        for i in range(self.J_num):
            tmp[i][0][i] = i * 3
        return tmp