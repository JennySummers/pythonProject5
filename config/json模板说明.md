## Json Schema
Json Schema定义了一套词汇和规则，这套词汇和规则用来定义Json元数据，且元数据也是通过Json数据形式表达的。Json元数据定义了Json数据需要满足的规范，规范包括成员、结构、类型、约束等。  
有关Json Schema的用法，参见<https://blog.csdn.net/lxz352907839/article/details/127619770>
## 目录结构
config目录下存放了两个schema文件，layoutSchema用于描述layout.json，waferSchema用于描述wafer.json  
config目录下存放了示例目录example1，其中存放了测试用例的layout和wafer，后续添加其他测试用例可新增目录
## 为本目录下的机台和晶圆文件配置json schema
如果layout.json和wafer.json没有自动关联到schema（即无法自动补全和显示注释），需要手动添加关联  
配置步骤参见<https://www.jetbrains.com/help/idea/json.html#ws_json_using_schemas>中的Using custom JSON schemas章节