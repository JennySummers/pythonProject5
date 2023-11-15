class Message:
    def __init__(self, fault_type, fault_pos, fault_time):
        self.fault_type = fault_type  # 故障类型，0代表机器故障但可以将其中的片取出，1代表机器故障且不可将其中的片取出
        self.fault_pos = fault_pos  # 故障位置
        self.fault_time = fault_time  # 故障时间
