# coding=utf-8

#   描述: Json转CShap数据结构
#   作者: mmc
#   日期: 2020-03-20

TYPE_LIST = "System.Collections.Generic.List"
TYPE_DICT = "System.Collections.Generic.Dictionary"

def ID(parser):
    return "__%d__" % id(parser)

#   生成字符串
def GenTable(count):
    return "".join(" " for i in range(count * 4))

#   收集结构体类型
def CollectStruct(parser, output):
    for child in parser.GetChildren():
        CollectStruct(child, output)
    if parser.GetType() == "struct":
        output.append(parser)

#   生成成员
def GenMember(parser, depth):
    table = GenTable(depth)
    name = parser.GetName()
    type = parser.GetType()
    if type == "bool":
        if len(name) != 0:
            return "%spublic bool %s" % (table, name)
        else:
            return "bool"
    elif type == "float":
        if len(name) != 0:
            return "%spublic float %s" % (table, name)
        else:
            return "float"
    elif type == "str":
        if len(name) != 0:
            return "%spublic string %s" % (table, name)
        else:
            return "string"
    elif type == "list":
        ele = GenMember(parser.GetChildren()[0], depth)
        if len(name) != 0:
            return "%spublic %s<%s> %s" % (table, TYPE_LIST, ele, name)
        else:
            return "%s<%s>" % (TYPE_LIST, ele)
    elif type == "dict":
        ele = GenMember(parser.GetChildren()[1], depth)
        if len(name) != 0:
            return "%spublic %s<string, %s> %s" % (table, TYPE_DICT, ele, name)
        else:
            return "%s<string, %s>" % (TYPE_DICT, ele)
    elif type == "struct":
        if len(name) != 0:
            return "%spublic %s %s" % (table, ID(parser), name)
        else:
            return "%s" % (ID(parser))
    assert False, "类型解析错误: 未知类型[%s]" % type

def GenMembers(units, depth):
    members = [GenMember(unit, depth) + ";" for unit in units]
    return "\n".join(members)

#   生成结构
def GenStruct(unit, depth):
    structs = GenMembers(unit.GetChildren(), depth)
    return "".join(structs)

def GenStructs(units, depth):
    sFMT = "{0}public struct {1} {{\n{2}\n{0}}};"
    return "\n".join([sFMT.format(  \
        GenTable(depth), ID(unit),  \
        GenStruct(unit, depth + 1)) \
        for unit in units])

def GenFromFile(members, name):
    structs = []
    [CollectStruct(unit, structs) for unit in members]
    text_struct = GenStructs(structs, 2)
    text_member = GenMembers(members, 2)
    param = (GenTable(1), name, text_struct, text_member)
    return "{0}public struct {1} {{\n{2}\n{3}\n{0}}};".format(*param)

def Gen(namespace, unit_collect):
    body = "\n".join([                  \
        GenFromFile(unit[1], unit[0])   \
        for unit in unit_collect])
    return "namespace %s {\n%s\n}" % (namespace, body)
