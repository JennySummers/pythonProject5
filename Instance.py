import numpy as np

'''
pick_time表示取片花费的时间
put_time表示放片花费的时间
switch_time表示切换机器人的时间
'''
pick_time = 1
put_time = 1
switch_time = 1
'''
Processing_time代表不同的工件的不同工序可选的机器编号和对应的处理时间。
Processing_time[i][j][k]表示工件i的第j道工序可以在机器k上加工，加工时间为Processing_time[i][j][k]
'''
Processing_time = [[[5, 3, 5, 3, 3, 9999, 10, 9],
                    [10, 9999, 5, 8, 3, 9, 9, 6],
                    [9999, 10, 9999, 5, 6, 2, 4, 5]],

                   [[5, 7, 3, 9, 8, 9999, 9, 9999],
                    [9999, 8, 5, 2, 6, 7, 10, 9],
                    [9999, 10, 9999, 5, 6, 4, 1, 7],
                    [10, 8, 9, 6, 4, 7, 9999, 9999]],

                   [[10, 9999, 9999, 7, 6, 5, 2, 4],
                    [9999, 10, 6, 4, 8, 9, 10, 9999],
                    [1, 4, 5, 6, 9999, 10, 9999, 7]],

                   [[3, 1, 6, 5, 9, 7, 8, 4],
                    [12, 11, 7, 8, 10, 5, 6, 9],
                    [4, 6, 2, 10, 3, 9, 5, 7]],

                   [[3, 6, 7, 8, 9, 9999, 10, 9999],
                    [10, 9999, 7, 4, 9, 8, 6, 9999],
                    [9999, 9, 8, 7, 4, 2, 7, 9999],
                    [11, 9, 9999, 6, 7, 5, 3, 6]],

                   [[6, 7, 1, 4, 6, 9, 9999, 10],
                    [11, 9999, 9, 9, 9, 7, 8, 4],
                    [10, 5, 9, 10, 11, 9999, 10, 9999]],

                   [[5, 4, 2, 6, 7, 9999, 10, 9999],
                    [9999, 9, 9999, 9, 11, 9, 10, 5],
                    [9999, 8, 9, 3, 8, 6, 9999, 10]],

                   [[2, 8, 5, 9, 9999, 4, 9999, 10],
                    [7, 4, 7, 8, 9, 9999, 10, 9999],
                    [9, 9, 9999, 8, 5, 6, 7, 1],
                    [9, 9999, 3, 7, 1, 5, 8, 9999]]]
'''
J 表示各个工件对应的工序数。用键值对来表示。
Machine_status 表示当前状态下各个机器还需要Machine_status[i]个单位时间达到空闲状态。
M_num 表示机器数目。
O_Max_len 表示最大的工序数目
J_num 表示工件数目
O_num 表示所有工件的所有工序总数
'''
J = {1: 3, 2: 4, 3: 3, 4: 3, 5: 4, 6: 3, 7: 3, 8: 4}
Machine_status = [1, 2, 3, 4, 1, 2, 3, 0]
M_num = 8
O_Max_len = 4
J_num = 8
O_num = 27
