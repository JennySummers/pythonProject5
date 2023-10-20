import main
from Instance import Processing_time, J, M_num, J_num, O_num
from line_profiler import LineProfiler

def test_main():
    g = main.GA()
    g.main(Processing_time, J, M_num, J_num, O_num)

if __name__ == '__main__':
    lp = LineProfiler()  # 构造分析对象
    lp.add_function(main.GA.main)
    test_func=lp(test_main)
    test_func()
    lp.print_stats()