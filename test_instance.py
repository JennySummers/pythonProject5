import csv

Processing_time = []
J = {}  # 每个recipe需要的工序数
J_num = 0   # recipe(job)的个数
M_num = 0   # PM(machine)的个数
O_Max_len = 0
O_num = 0

if __name__ == '__main__':
    J_num = int(input("please input the num of recipe:"))
    print(J_num)
    # M_num = input("请输入机器数:")
    # J = {}
    # print("请输入各job需要的工序数")
    # 读取多个recipe
    for i in range(J_num):
        # print(i)
        path = "./recipe/recipe" + str(i) + ".csv"
        recipe_time = []
        with open(path, 'r', encoding='utf-8') as file:
            data = csv.reader(file)
            next(data)  # 跳过csv表头
            # step_time = []
            row_count = 0
            # 一次读一行
            for row in data:
                # step_time.append(row)
                recipe_time.append(row)
                row_count = row_count + 1   # 计算行数
                M_num = len(row)
            print("row_count=" + str(row_count))
            J[i+1] = row_count
            O_num = O_num + row_count
            if row_count > O_Max_len:
                O_Max_len = row_count
        # recipe_time.append(step_time)
        Processing_time.append(recipe_time)
    print(Processing_time)
    # for line in file.readlines():
    #     line = line.strip() #strip() 方法用于移除字符串头尾指定的字符（默认为空格或换行符）或字符序列
    print(J)
    print("M_num=" + str(M_num))
    print("O_Max_len=" + str(O_Max_len))
    print("O_num=" + str(O_num))
