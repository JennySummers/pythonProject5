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
# Processing_time = read_Json.Processing_time

Processing_time = [[[5, 5, 99999999, 99999999, 99999999, 99999999, 99999999, 99999999],
                    [99999999, 99999999, 8, 8, 99999999, 99999999, 99999999, 99999999],
                    [99999999, 99999999, 99999999, 99999999, 6, 6, 99999999, 99999999],
                    [99999999, 99999999, 99999999, 99999999, 99999999, 99999999, 9, 9]],

                   [[5, 5, 99999999, 99999999, 99999999, 99999999, 99999999, 99999999],
                    [99999999, 99999999, 8, 8, 99999999, 99999999, 99999999, 99999999],
                    [99999999, 99999999, 99999999, 99999999, 6, 6, 99999999, 99999999],
                    [99999999, 99999999, 99999999, 99999999, 99999999, 99999999, 9, 9]],

                   [[5, 5, 99999999, 99999999, 99999999, 99999999, 99999999, 99999999],
                    [99999999, 99999999, 8, 8, 99999999, 99999999, 99999999, 99999999],
                    [99999999, 99999999, 99999999, 99999999, 6, 6, 99999999, 99999999],
                    [99999999, 99999999, 99999999, 99999999, 99999999, 99999999, 9, 9]],

                   [[5, 5, 99999999, 99999999, 99999999, 99999999, 99999999, 99999999],
                    [99999999, 99999999, 8, 8, 99999999, 99999999, 99999999, 99999999],
                    [99999999, 99999999, 99999999, 99999999, 6, 6, 99999999, 99999999],
                    [99999999, 99999999, 99999999, 99999999, 99999999, 99999999, 9, 9]],

                   [[5, 5, 99999999, 99999999, 99999999, 99999999, 99999999, 99999999],
                    [99999999, 99999999, 8, 8, 99999999, 99999999, 99999999, 99999999],
                    [99999999, 99999999, 99999999, 99999999, 6, 6, 99999999, 99999999],
                    [99999999, 99999999, 99999999, 99999999, 99999999, 99999999, 9, 9]],

                   [[5, 5, 99999999, 99999999, 99999999, 99999999, 99999999, 99999999],
                    [99999999, 99999999, 8, 8, 99999999, 99999999, 99999999, 99999999],
                    [99999999, 99999999, 99999999, 99999999, 6, 6, 99999999, 99999999],
                    [99999999, 99999999, 99999999, 99999999, 99999999, 99999999, 9, 9]],

                   [[5, 5, 99999999, 99999999, 99999999, 99999999, 99999999, 99999999],
                    [99999999, 99999999, 8, 8, 99999999, 99999999, 99999999, 99999999],
                    [99999999, 99999999, 99999999, 99999999, 6, 6, 99999999, 99999999],
                    [99999999, 99999999, 99999999, 99999999, 99999999, 99999999, 9, 9]],

                   [[5, 5, 99999999, 99999999, 99999999, 99999999, 99999999, 99999999],
                    [99999999, 99999999, 8, 8, 99999999, 99999999, 99999999, 99999999],
                    [99999999, 99999999, 99999999, 99999999, 6, 6, 99999999, 99999999],
                    [99999999, 99999999, 99999999, 99999999, 99999999, 99999999, 9, 9]]]

'''
J 表示各个工件对应的工序数。用键值对来表示。
Machine_status 表示当前状态下各个机器还需要Machine_status[i]个单位时间达到空闲状态。
M_num 表示机器数目。
O_Max_len 表示最大的工序数目
J_num 表示工件数目
O_num 表示所有工件的所有工序总数
'''
J = {1: 4, 2: 4, 3: 4, 4: 4, 5: 4, 6: 4, 7: 4, 8: 4}
Machine_status = [6, 2, 3, 4, 1, 2, 3, 0]
M_num = 8
O_Max_len = 4
J_num = 8
O_num = 32
INVALID = 99999999
