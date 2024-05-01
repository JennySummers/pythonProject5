# 一个能够解析并存储形如“Mon Apr 29 22:35:46 2024”结构的时间戳的类
from datetime import datetime


class log_element:
    def __init__(self):
        self.time = ""
        self.status=""
        self.type=""
        self.target=0
        self.robot=0


# 从config/example3/sch_log.txt每六行为一组读取内容并解析为log_element列表
def read_log():
    log_path = 'config/example3/sch_log.txt'
    log_elements = []
    with open(log_path, 'r') as f:
        lines = f.readlines()
        for i in range(0, len(lines), 6):
            log_element_instance = log_element()
            # log_element_instance.time = datetime.strptime(lines[i], "%Y-%m-%d %H:%M:%S")
            log_element_instance.time = datetime.strptime(lines[i].strip(), "%a %b %d %H:%M:%S %Y")
            log_element_instance.status = lines[i + 1].strip()[:-1]
            log_element_instance.type = lines[i + 2].strip()[5:]
            log_element_instance.target = lines[i + 3].strip()[7:]
            log_element_instance.robot = lines[i + 4].strip()[6:]
            log_elements.append(log_element_instance)
    return log_elements

def select_first_wafer(log_elements,current_module="104LP11"):
    selected=[]
    pick=True
    for elements in log_elements:
        if pick:
            if elements.target==current_module and elements.type=="pick":
                selected.append(elements)
                if elements.status=="end":
                    pick=False
                    current_module=elements.robot
        else:
            if elements.robot==current_module and elements.type=="place":
                selected.append(elements)
                if elements.status=="end":
                    pick=True
                    current_module=elements.target
    return selected

def transfer_time(log_elements):
    t1=[]
    t2 = []
    t3 = []
    for i in range(0,len(log_elements),5):
        t1.append((log_elements[i+2].time-log_elements[i+1].time).seconds)
        t2.append((log_elements[i+3].time-log_elements[i+2].time).seconds)
        t3.append((log_elements[i + 4].time - log_elements[i + 3].time).seconds)
    return t1,t2,t3




if __name__=="__main__":
    log=read_log()
    selected1=select_first_wafer(log)
    selected2=select_first_wafer(log,"105LP12")
    selected3=select_first_wafer(log,"106LP13")
    t1,t2,t3=transfer_time(selected1)
    u1,u2,u3=transfer_time(selected3)

    print(log)


