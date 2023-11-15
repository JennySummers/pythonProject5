from memory_profiler import profile

from Instance import put_time, pick_time, switch_time


class Machine_Time_window:
    def __init__(self, Machine_index, machine_state):
        self.Machine_index = Machine_index
        self.assigned_task = []
        self.worker_for_task = []
        self.O_start = []
        self.O_end = []
        # self.End_time = 0
        self.End_time = machine_state
        self.Machine_state = machine_state

    # 机器的哪些时间窗是空的,此处只考虑内部封闭的时间窗
    def Empty_time_window(self):
        time_window_start = []
        time_window_end = []
        len_time_window = []
        if self.O_end is None:
            pass
        elif len(self.O_end) == 1:
            if self.O_start[0] > self.Machine_state:
                time_window_start = [self.Machine_state]
                time_window_end = [self.O_start[0]]
        elif len(self.O_end) > 1:
            if self.O_start[0] > self.Machine_state:
                time_window_start.append(self.Machine_state)
                time_window_end.append(self.O_start[0])
            time_window_start.extend(self.O_end[:-1])  # 因为使用时间窗的结束点就是空时间窗的开始点
            time_window_end.extend(self.O_start[1:])
        if time_window_end is not None:
            len_time_window = [time_window_end[i] - time_window_start[i] for i in range(len(time_window_end))]
        return time_window_start, time_window_end, len_time_window  # 返回0.当前机器的空闲时窗的开始时间，1.结束时间，2.时窗长度

    def Machine_Burden(self):
        if len(self.O_start) == 0:
            burden = 0
        else:
            # 处理时间 = 工件结束时间 - 工件开始时间
            processing_time = [self.O_end[i] - self.O_start[i] for i in range(len(self.O_start))]
            burden = sum(processing_time)
        return burden

    def _Input(self, Job, M_Earliest, P_t, O_num):  # 参数含义:工件编号，工件的工序最早开始时间，处理时间，工序编号
        if self.O_end:
            if self.O_start[-1] > M_Earliest:
                for i in range(len(self.O_end)):
                    if self.O_start[i] >= M_Earliest:
                        self.assigned_task.insert(i, [Job + 1, O_num + 1])
                        break
            else:
                self.assigned_task.append([Job + 1, O_num + 1])
        else:
            self.assigned_task.append([Job + 1, O_num + 1])
        self.O_start.append(M_Earliest)
        self.O_start.sort()
        self.O_end.append(M_Earliest + P_t)
        self.O_end.sort()
        self.End_time = self.O_end[-1]
