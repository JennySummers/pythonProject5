import json
import numpy as np
import copy

INVALID = 99999999
pick_time = 1
put_time = 1
unit_time = 1  # 单位时间设定，单位为毫秒


class Read_json:
    def __init__(self, layout_path, layout_raw_path, wafer_path, wafer_noBM_path):
        # layout_path = "./config/example1/layout.json"
        # wafer_path = "./config/example1/wafer.json"
        self.layout_path = layout_path
        self.layout_raw_path = layout_raw_path
        self.wafer_path = wafer_path
        self.wafer_noBM_path = wafer_noBM_path
        self.Processing_time = []
        self.process_list = []  # 工序列表
        self.wafer_num = []  # wafer的数量
        self.group_elements_num = {}  # 各group含有的处理单元(elements)数量
        self.group_elements_index = {}  # 各group在list中的起始索引位；例CM1=0,PG1=4,则一个list中0-3位的数字表示CM1的时间
        self.all_elements_index = {}  # 所有elements在list中的索引位
        self.type_index = {}  # 按CM/PM/TM/BM分类的index
        self.all_elements_num = 0  # CM/PM含有的处理单元(elements)总个数，即每个step的list中的元素个数
        self.buffer_module = []  # 存放所有的BM，以供判断
        self.graph = {}  # 邻接矩阵
        self.circle = []  # 存放找到的环路
        self.TM_num = 0  # 记录TM（机械臂）的总数量
        self.CM_num = 0  # 记录CM的槽位数量
        self.wafer_sum = 0  # 记录wafer_sum的总数量
        self.CM_name_list = []
        self.elements_name_list = []

        # 机械臂相关
        self.transfer_time = []  # 每个机械臂的取放时间
        self.accessibleList = []  # 每个PM/CM的可交互机械臂列表在transfer_time中的索引
        self.TM_element_to_group = {}   # 将element的序号与TM group的序号对应

    # 判断输入的CM的槽位是否小于wafer数量，若是，则报错退出
    def check_waferNum(self):
        CM_num = 0
        wafer_sum = 0
        with open(self.layout_path, 'r', encoding='utf-8') as layout_file:
            layout_json_data = json.load(layout_file)
            CM = layout_json_data['CM']
            for CG in CM:
                num = len(CG['elements'])
                CM_num = CM_num + num
                self.CM_name_list.append(CG['groupName'])
        with open(self.wafer_noBM_path, 'r', encoding='utf-8') as file:
            wafer_json_data = json.load(file)
            for waferGroup in wafer_json_data:
                num = waferGroup['waferNum']
                wafer_sum = wafer_sum + num

        self.CM_num = CM_num
        self.wafer_sum = wafer_sum
        print('CM_num:' + str(CM_num))
        print('wafer_sum:' + str(wafer_sum))
        # print(self.CM_name_list)
        if CM_num < wafer_sum:
            print('CM的槽位数小于输入的wafer数量，请重新检查')
            exit()

    # 给layout.json的所有element添加groupName前缀
    def layout_add_element_groupName(self):
        with open(self.layout_raw_path, 'r', encoding='utf-8') as file:
            layout_raw_data = json.load(file)
            for CG in layout_raw_data['CM']:
                new_element = []
                for element in CG['elements']:
                    element = CG['groupName'] + '-' + element
                    new_element.append(element)
                CG['elements'] = new_element

            for PG in layout_raw_data['PM']:
                new_element = []
                for element in PG['elements']:
                    element = PG['groupName'] + '-' + element
                    new_element.append(element)
                PG['elements'] = new_element

            for BG in layout_raw_data['BM']:
                new_element = []
                for element in BG['elements']:
                    element = BG['groupName'] + '-' + element
                    new_element.append(element)
                BG['elements'] = new_element

            for TG in layout_raw_data['TM']:
                new_element = []
                for element in TG['elements']:
                    element = TG['groupName'] + '-' + element
                    new_element.append(element)
                TG['elements'] = new_element

            with open(self.layout_path, 'w+', encoding='utf-8') as file2:
            # with open("./config/example3/layout_TEST.json", 'w+', encoding='utf-8') as file2:
                json.dump(layout_raw_data, file2, indent=4)

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

                    moduleName1_index = self.group_elements_index[moduleName1]
                    moduleName2_index = self.group_elements_index[moduleName2]
                    # 相邻的两个processModule的可达的机械臂(的编号)：
                    accessibleTM1 = self.accessibleList[moduleName1_index]
                    accessibleTM2 = self.accessibleList[moduleName2_index]

                    transfer = accessibleTM1 & accessibleTM2
                    if transfer == set():  # 若两个processModule不在同一个TM下(交集为空)，则需要找这两组TM的accessibleList中共同的BM
                        # 有多个可选的BM怎么处理(采用双层循环？)
                        flag = False
                        for j in accessibleTM1:
                            access_module1 = TM[self.TM_element_to_group[j]]['accessibleList']
                            # 当前逻辑是找到一组能用的BM就不再进行遍历
                            for k in accessibleTM2:
                                access_module2 = TM[self.TM_element_to_group[k]]['accessibleList']

                                # 找出这两个机械臂可达的BM
                                access_buffer_module1 = [l for l in access_module1 if l in self.buffer_module]
                                access_buffer_module2 = [l for l in access_module2 if l in self.buffer_module]
                                bm = [l for l in access_buffer_module1 if l in access_buffer_module2]

                                if bm:  # 非空
                                    flag = True
                                    # 将BM信息插入json文件中，若有多个BM可选则只插入第一个
                                    # 需要考虑同时有多个BM的情况，如BM6-1/BM6-2
                                    bm_info = {
                                        "processModule": bm,
                                        "processTime": 0
                                    }
                                    new_recipe.insert(index + 1, bm_info)
                                    index = index + 1
                                    # print('添加BM', bm)
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
            # print(new_wafer_json_data)

        with open(self.wafer_path, 'w+', encoding='utf-8') as file:
            json.dump(new_wafer_json_data, file, indent=4)

    # 根据晶圆的顺序实现按序取片
    def Ordered_wafer(self, arm_time=1):
        wafer_nums = [x for x in self.wafer_num]

    def get_Layout_Info(self):
        with open(self.layout_path, 'r', encoding='utf-8') as file:
            self.layout_json_data = json.load(file)
            index = 0  # 各group在list中的起始索引位
            element_index = 0

            # 将CM的各个group含有的处理单元(elements)个数、数组中的索引位添加到字典
            CM = self.layout_json_data['CM']
            self.type_index['CM'] = index
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
                # 记录每个元素的名称
                self.append_elements_name(CG)
                # 各单元在数组(list)中的索引位
                for element in CG['elements']:
                    self.all_elements_index[element] = element_index
                    element_index = element_index + 1
            self.type_index['CM_end'] = index - 1

            # 将PM的各个group含有的处理单元(elements)个数、数组中的索引位添加到字典
            PM = self.layout_json_data['PM']
            self.type_index['PM'] = index
            for PG in PM:
                groupName = PG['groupName']
                len_group = len(PG['elements'])
                self.all_elements_num += len_group
                self.group_elements_index[groupName] = index
                index += len_group
                self.group_elements_num[groupName] = len_group
                # 记录每个元素的名称
                self.append_elements_name(PG)
                # 各单元在数组(list)中的索引位
                for element in PG['elements']:
                    self.all_elements_index[element] = element_index
                    element_index = element_index + 1
            self.type_index['PM_end'] = index - 1

            BM = self.layout_json_data['BM']
            self.type_index['BM'] = index
            for BG in BM:
                groupName = BG['groupName']
                self.buffer_module.append(groupName)
                len_group = len(BG['elements'])
                self.all_elements_num += len_group
                self.group_elements_index[groupName] = index
                index += len_group
                self.group_elements_num[groupName] = len_group
                # 记录每个元素的名称
                self.append_elements_name(BG)
                # 各单元在数组(list)中的索引位
                for element in BG['elements']:
                    self.all_elements_index[element] = element_index
                    element_index = element_index + 1
            self.type_index['BM_end'] = index - 1

            self.accessibleList = [set() for i in range(self.all_elements_num)]
            TM = self.layout_json_data['TM']
            self.type_index['TM'] = index
            TM_elements_num = 0     # 具体的element从0开始编号
            TM_group_num = 0        # TM group从0开始编号
            # TM_num = 0  # 记录TM（机械臂）的总数量
            for TG in TM:  # 遍历顺序是TM1,TM2,TM3,TM4,TM6,TM8,TM7,TM5(当前不是此顺序)
                # self.TM_num = self.TM_num + 1
                groupName = TG['groupName']
                len_group = len(TG['elements'])
                self.TM_num = self.TM_num + len_group   # 记录TM（机械臂）的总数量
                # self.all_elements_num += len_group    # 不清楚TM这部分代码的具体情况，暂不修改所有元素的数量
                self.group_elements_index[groupName] = index
                index += len_group
                self.group_elements_num[groupName] = len_group
                count = len(TG['elements'])  # 该机械臂组所包含的元素数
                base = len(self.transfer_time)  # 该组之前已有的机械臂元素总数
                temp_accessible_set = {x for x in range(base, base + count)}  # 可访问集合列表
                # 记录每个元素的名称
                self.append_elements_name(TG)
                # 各单元在数组(list)中的索引位
                for element in TG['elements']:
                    self.all_elements_index[element] = element_index
                    element_index = element_index + 1

                # TM中各element在self.accessibleList中的索引
                # key是element在self.accessibleList中的索引，value是self.layout_json_data['TM']按序下来的编号
                # 用于add_BM函数
                for element in TG['elements']:
                    self.TM_element_to_group[TM_elements_num] = TM_group_num
                    TM_elements_num = TM_elements_num + 1
                TM_group_num = TM_group_num + 1

                # 存储每个机械臂的运动时间
                for i in range(count):
                    self.transfer_time.append(TG['transferTime'])

                # 构建从PM/CM至TM的索引
                for accessibleModule in TG['accessibleList']:
                    if self.group_elements_index.__contains__(
                            accessibleModule):  # 由于暂未将BM添加进group_elements_index中，故添加此判断条件来跳过BM
                        index0 = self.group_elements_index[accessibleModule]
                        num = self.group_elements_num[accessibleModule]
                        for i in range(num):
                            self.accessibleList[i + index0] |= temp_accessible_set
            self.type_index['TM_end'] = index - 1

        print('group_elements_num', self.group_elements_num)
        print('group_elements_index', self.group_elements_index)
        print('all_elements_index', self.all_elements_index)
        print('type_index', self.type_index)
        print('all_elements_num', self.all_elements_num)
        print('TM_element_to_group', self.TM_element_to_group)

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
                        # 令空出来的槽位=INVALID
                        if name in self.CM_name_list:
                            for i in range(self.CM_num - self.wafer_sum):
                                list_step[index + self.wafer_sum + i] = INVALID
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

    def DFS(self, v, vis, trace):
        if v in vis:
            if v in trace:
                v_index = trace.index(v)
                print("There are loops in the path:")
                road = []
                for i in range(v_index, len(trace)):
                    print(trace[i] + ' ', end='')
                    road.append(trace[i])
                print(v)
                road.append(v)
                self.circle.append(road)
                print("\n")
                return
            return

        vis.append(v)
        trace.append(v)
        for vs in self.graph[v]:
            self.DFS(vs, vis, trace)
        trace.pop()

    def findCircle(self):
        vis = []
        trace = []
        with open(self.wafer_path, 'r', encoding='utf-8') as file:
            wafer_json_data = json.load(file)
            # 有多个recipe时
            for waferGroup in wafer_json_data:
                recipe = list(waferGroup['recipe'])
                for i in range(len(recipe) - 1):
                    processModule1 = recipe[i]['processModule']
                    processModule2 = recipe[i + 1]['processModule']
                    for module in processModule1:
                        self.graph[module] = processModule2
                for module in recipe[len(recipe)-1]['processModule']:
                    # 遍历到最后，有向图有点只有入边
                    if module not in self.graph:
                        self.graph[module] = []

        with open(self.layout_path, 'r', encoding='utf-8') as file:
            layout_json_data = json.load(file)
            TM = list(layout_json_data['TM'])
            for TG in TM:
                # 加入TM->module的数据
                groupName = TG['groupName']
                self.graph[groupName] = TG['accessibleList']

                # # TODO 加入module->TM的数据，存疑
                # for module in TG['accessibleList']:
                #     # print(graph[module])
                #     if module in self.graph:
                #         self.graph[module].append(groupName)
                #     else:
                #         list_module = [module]
                #         self.graph[module] = list_module
                #     # print(self.graph[module])

        self.DFS(list(self.graph.keys())[0], vis, trace)

    def append_elements_name(self, module_group):
        for element in module_group['elements']:
            self.elements_name_list.append(element)


'''
J 表示各个工件对应的工序数。用键值对来表示。
Machine_status 表示当前状态下各个机器还需要Machine_status[i]个单位时间达到空闲状态。
M_num 表示机器数目。
O_Max_len 表示最大的工序数目
J_num 表示工件数目
O_num 表示所有工件的所有工序总数
'''


class get_Recipe:
    def __init__(self, layout_path, layout_raw_path, wafer_path, wafer_noBM_path):
        j = Read_json(layout_path, layout_raw_path, wafer_path, wafer_noBM_path)
        j.check_waferNum()  # 判断输入的CM的槽位是否小于wafer数量，若是,则报错退出
        j.layout_add_element_groupName()
        j.get_Layout_Info()
        j.add_BM()
        j.get_Wafer_Info()
        j.findCircle()
        # self.M_num = j.all_elements_num  # 配方的可用机器数
        self.M_num = j.all_elements_num + len(j.transfer_time)  # 配方的可用机器数,要考虑TM
        self.O_Max_len = 0  # 表示最大的工序数目
        # self.J_num = len(j.process_list)  # 表示工件数目
        self.J_num = len(j.Processing_time)  # 表示工件数目
        self.O_num = 0  # 表示所有工件的所有工序总数
        self.J = {}  # 表示各个工件对应的工序数，用键值对来表示
        self.elements_name = j.elements_name_list
        # for i in range(len(j.process_list)):
        for i in range(len(j.Processing_time)):
            # self.J[i] = j.process_list[i]
            self.J[i + 1] = len(j.Processing_time[i])
            # self.O_num = self.O_num + j.process_list[i]
            self.O_num = self.O_num + len(j.Processing_time[i])
            # self.O_Max_len = max(self.O_Max_len, j.process_list[i])
            self.O_Max_len = max(self.O_Max_len, len(j.Processing_time[i]))

        self.Processing_time = self.modify_processing(j.Processing_time)  # 修改晶圆在CM中的时间
        # self.Processing_time = j.Processing_time
        self.Machine_status = np.zeros(self.M_num, dtype=float)
        self.TM_num = j.TM_num  # 记录TM（机械臂）的总数量
        # 将字典的key，value调换(此字典value为编号，唯一）
        self.group_name_index = {v: k for k, v in j.all_elements_index.items()}  # 编号与对应名称的映射
        self.type_index = j.type_index
        print(self.M_num)
        print(self.O_Max_len)
        print(self.J_num)
        print(self.O_num)
        print(self.J)
        print(self.TM_num)
        print(self.group_name_index)

    def modify_processing(self, processing_time):
        tmp = copy.deepcopy(processing_time)
        for i in range(self.J_num):
            for j in range(self.J_num):
                tmp[i][0][j] = INVALID
        for i in range(self.J_num):
            # tmp[i][0][i] = i * 3
            tmp[i][0][i] = 0
        return tmp
