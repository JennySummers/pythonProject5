class Fault_Message:
    def __init__(self, fault_type, fault_pos, fault_time):
        self.fault_type = fault_type  # 故障类型，0代表机器故障但可以将其中的片取出，1代表机器故障且不可将其中的片取出
        self.fault_pos = fault_pos  # 故障位置
        self.fault_time = fault_time  # 故障时间


class Arm_Message:
    def __init__(self, machine_no, cmd_time, move_type, move_from=None, move_to=None):
        self.machine_no = machine_no
        self.cmd_time = cmd_time
        self.move_type = move_type  # move_type表示机械臂指令的类型，0表示取片，1表示放片，2表示机械臂移动
        if self.move_type == 0:  # 当机械臂操作为取片，读取从哪台机器上取片
            self.move_from = move_from
        if self.move_type == 1:  # 当机械臂操作为放片，读取放到那台机器上
            self.move_to = move_to
        if self.move_type == 2:  # 当机械臂操作为移动，读取移动的起点和终点
            self.move_from = move_from
            self.move_to = move_to
