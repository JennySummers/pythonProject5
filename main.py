import profile

from read_Json import get_Recipe
from GeneticA import GA
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
    r = get_Recipe(layout_path, wafer_path, wafer_noBM_path)
    g = GA(r.Machine_status)
    g.main(r.Processing_time, r.J, r.M_num, r.J_num, r.O_num, r.TM_num, r.group_name_index)
    # g = GA(Machine_status)
    # g.main(Processing_time, J, M_num, J_num, O_num)
    g.get_TM_Move_List(r.M_num, r.TM_num, r.group_name_index)  # 打印TM机械臂操作列表
