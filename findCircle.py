import json
import numpy as np
import copy

# graph = {
#     "a": ["b", "c"],
#     "b": ["a", "d"],
#     "c": ["a", "d"],
#     # "d": [ "e"],
#     "d": ["c", "e"],  # add loop
#     "e": ["d"]
# }

# print(graph["a"])

vis = []
trace = []
graph = {}
circle = []

wafer_path = "./config/example1/wafer.json"
with open(wafer_path, 'r', encoding='utf-8') as file:
    wafer_json_data = json.load(file)
    # 有多个recipe时
    for waferGroup in wafer_json_data:
        recipe = list(waferGroup['recipe'])
        for i in range(len(recipe) - 1):
            processModule1 = recipe[i]['processModule']
            processModule2 = recipe[i + 1]['processModule']
            for module in processModule1:
                graph[module] = processModule2

layout_path = "./config/example1/layout.json"
with open(layout_path, 'r', encoding='utf-8') as file:
    layout_json_data = json.load(file)
    TM = list(layout_json_data['TM'])
    for TG in TM:
        # 加入TM->module的数据
        groupName = TG['groupName']
        graph[groupName] = TG['accessibleList']

        # TODO 加入module->TM的数据，存疑
        for module in TG['accessibleList']:
            # print(graph[module])
            if module in graph:
                graph[module].append(groupName)
            else:
                list_module = [module]
                graph[module] = list_module
            print(graph[module])

print(graph)
# print(list(graph.keys()))
# print(type(graph.keys()))


def dfs(v):
    if v in vis:
        if v in trace:
            v_index = trace.index(v)
            print("有环：")
            road = []
            for i in range(v_index, len(trace)):
                print(trace[i] + ' ', end='')
                road.append(trace[i])
            print(v)
            road.append(v)
            circle.append(road)
            print("\n")
            return
        return

    vis.append(v)
    trace.append(v)
    for vs in graph[v]:
        dfs(vs)
    trace.pop()

    # print(vis)
    # return vis

dfs(list(graph.keys())[0])
print(circle)
# dfs("a")

