import gc
import os.path
import profile
import logging
import sys
import time

from read_Json import get_Recipe
from GeneticA import GA
from Logs import Logger
from Instance import Processing_time, J, M_num, J_num, O_num, Machine_status

'''
将晶圆在CM中的处理时间设置成晶圆需要等待之前的晶圆被取走的时间。
具体实现方法为：
将CM作为处理单元，其处理时间等于(编号-1)*机械臂运行时间
晶圆在CM中的可选加工单元为其编号对应的CM
'''
if __name__ == '__main__':
    layout_path = "./config/example1/layout.json"
    wafer_path = "./config/example1/wafer.json"
    wafer_noBM_path = "./config/example1/wafer_noBM.json"
    log_path = './logs/'
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    log_file_name = log_path + 'log-' + time.strftime("%Y-%m-%d %H %M %S", time.localtime()) + '.log'
    sys.stdout = Logger(log_file_name)  # 记录正常控制台输出结果
    sys.stderr = Logger(log_file_name)  # 记录traceback异常信息
    r = get_Recipe(layout_path, wafer_path, wafer_noBM_path)
    g = GA(r.Machine_status)
    g.main(r.Processing_time, r.J, r.M_num, r.J_num, r.O_num, r.TM_num, r.group_name_index, r.elements_name)
    logging.info('complete')
    del r
    del g
    gc.collect()
    # g = GA(Machine_status)
    # g.main(Processing_time, J, M_num, J_num, O_num, 0, 0)
