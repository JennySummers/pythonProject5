import gc
import os.path
import profile
import logging
import sys
import time

from read_Json import get_Recipe
from GeneticA import GA
from Logs import Logger
from New_join import new_join
from Fault_handling import Fault
from Instance import Machine_status, Processing_time, J, M_num, J_num, O_num

'''
将晶圆在CM中的处理时间设置成晶圆需要等待之前的晶圆被取走的时间。
具体实现方法为：
将CM作为处理单元，其处理时间等于(编号-1)*机械臂运行时间
晶圆在CM中的可选加工单元为其编号对应的CM
'''


def set_Wafer(layout_path="./config/example3/layout.json",
              layout_raw_path="./config/example3/layout_raw.json",
              wafer_path="./config/example3/wafer.json",
              wafer_noBM_path="./config/example3/wafer_noBM.json"):
    return layout_path, layout_raw_path, wafer_path, wafer_noBM_path


def first_scheduler():
    Layout_path, layout_raw_path, Wafer_path, Wafer_noBM_path = set_Wafer()
    r = get_Recipe(Layout_path, layout_raw_path, Wafer_path, Wafer_noBM_path)
    g = GA(r.Machine_status)
    g.main(r.Processing_time, r.J, r.M_num, r.J_num, r.O_num, r.TM_num, r.group_name_index, r.elements_name,
           r.type_index)
    del r
    del g


if __name__ == '__main__':
    sys.setrecursionlimit(2000)
    log_path = './logs/'
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    log_file_name = log_path + 'log-' + time.strftime("%Y-%m-%d %H %M %S", time.localtime()) + '.log'
    sys.stdout = Logger(log_file_name)  # 记录正常控制台输出结果
    sys.stderr = Logger(log_file_name)  # 记录traceback异常信息
    first_scheduler()
    # 这部分为新加入的晶圆重新调度部分 开始
    # f = new_join(200)
    # f.main(g.Best_Machine, g.Best_Job, r.Processing_time, r.J, r.M_num, r.J_num, r.O_num)
    # g.main(f.New_Processing_time, f.New_J, f.New_M_num, f.New_J_num, f.New_O_num, r.TM_num, r.group_name_index, r.elements_name, r.type_index)
    # 这部分为新加入的晶圆重新调度部分 结束

    logging.info('complete')

    gc.collect()
    # g = GA(Machine_status)
    # g.main(Processing_time, J, M_num, J_num, O_num, 2, 0, 0, 0)
