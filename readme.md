https://blog.csdn.net/crazy_girl_me/article/details/118157629

用python实现柔性作业车间调度基础数据（如Brandimarte_DATA、DAUZERE_DATA、Hurink_DDATA）的准换，转换为标准可用算例:
https://blog.csdn.net/crazy_girl_me/article/details/116058503

python实现改遗传算法解柔性作业车间调度问题的编码和初始化:
https://blog.csdn.net/crazy_girl_me/article/details/108868977

用python绘制车间调度的甘特图（JSP）:
https://blog.csdn.net/crazy_girl_me/article/details/110895843
  

用python实现利用改进遗传算法求解FJSP染色体解码部分:
https://blog.csdn.net/crazy_girl_me/article/details/108960996

用python实现利用改进遗传算法求解FJSP染色体解码部分（改进版本）:
https://blog.csdn.net/crazy_girl_me/article/details/114787030

用python实现改遗传算法解柔性作业车间调度问题的完整编码（用8*8和mk01做测例）（改进版本）:
https://blog.csdn.net/crazy_girl_me/article/details/114831730

//////////////////////////////////\
可以将机械臂看作单独的处理单元，每个工件的工序在加工完成后都需要经过机械臂的运输处理才能进入下一道工序。\
//////////////////////////////////

https://www.cnblogs.com/rgcLOVEyaya/p/RGC_LOVE_YAYA_603days_1.html
memory_profiler是用来分析每行代码的内存使用情况
1.先导入：    from memory_profiler import profile
2.函数前加装饰器：   @profile(precision=4,stream=open('memory_profiler.log','w+'))            
参数含义：precision:精确到小数点后几位 
        stream:此模块分析结果保存到 'memory_profiler.log' 日志文件。如果没有此参数，分析结果会在控制台输出
Line列记录了分析的各行代码具体行位置
Mem usage列记录了当程序执行到该行时当前进程占用内存的量
Increment记录了当前行相比上一行内存消耗的变化量
Occurrences记录了当前行的执行次数(循环、列表推导等代码行会记作多次)
Line Contents列则记录了具体对应的行代码