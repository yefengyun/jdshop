# coding=utf-8
# 导包
import numpy as np
import matplotlib
import os
import matplotlib.pyplot as plot
import pandas as pd
import pymongo

plot.rcParams['font.sans-serif'] = ['SimHei']  # 用simhei 字体显示中文
plot.rcParams['axes.unicode_minus'] = False  # 这个用来正常显示负号

# 数据库参数配置
MONGOURL = "127.0.0.1"
MONGOPORT = 27017
MONGODB = "JDSHOP"
MONGOTABLE = 'JdBarItem'

DIR = "data"
COLOR = ["肤", "红", "橙", "黄", "绿", "青", "蓝", "紫", "黑", "白", "灰", "粉"]
COLOR_DIR = {"肤色": "#EED8AE", "红色": "#FF0000", "橙色": "#FF7F0E", "黄色": "#FFF10D", "绿色": "#20FF0E", "青色": "#02FF90",
             "蓝色": "#0D09C4", "紫色": "#C4078B", "黑色": "#000000", "白色": "#FFFFFF", "灰色": "#C4C4C4", "粉色": "#FF8880",
             "其它": "#8C564B"}
CUP = ["A", "B", "C", "D", "E"]


# 获取数据库数据
def getData():
    clien = pymongo.MongoClient(host=MONGOURL, port=MONGOPORT)
    db = clien[MONGODB][MONGOTABLE]
    data = db.find()
    return data


# 对颜色的处理
def dealColor(data):
    for c in COLOR:
        if c in data:
            return c + "色"
    return "其它"


# 对大小的处理
def dealCup(data):
    if "L" in data.upper():
        return "B罩杯"
    elif "M" in data.upper():
        return "A罩杯"
    for cup in CUP:
        if cup in data.strip().upper():
            return cup + "罩杯"
    return "其它"


# 数据清洗
def dataClear(data):
    data = pd.DataFrame(list(data))  # 转换数据格式
    data.drop_duplicates()  # 去重
    data = data.drop(["_id", "id"], axis=1)  # 删除无用字段
    data["productColor"] = data["productColor"].apply(dealColor)
    # print(data["productColor"].value_counts())
    # print(data["productSize"].value_counts())
    data["productSize"] = data["productSize"].apply(dealCup)
    # print(data["productSize"].value_counts())
    return data


def findcolors(colors):
    colors = list(colors)
    for i in range(len(colors)):
        colors[i] = COLOR_DIR[colors[i]]
    return colors


# 绘制病状图
def drawPie(data, path, title, color=None, fontsize=18, size=(8, 8), mixnum=100):
    sum = data.sum()
    data_main = data[data > mixnum]
    other_num = data[data <= mixnum].sum()
    try:
        data_main["其它"] = data["其它"] + other_num
    except KeyError:
        data_main["其它"] = other_num

    data_rate = data_main / sum * 100

    # 绘制图片
    plot.figure(figsize=size)
    index = data_rate.index
    if (color): color = findcolors(index)
    plot.pie(data_rate.values, labels=index, colors=color, autopct='%.2f%%')
    plot.title(title, fontsize=fontsize)
    plot.savefig(path, dpi=500, bbox_inches='tight')
    # plot.show()
    print("{} 保存成功".format(path))


# 主方法
def main():
    data = getData()
    data = dataClear(data)
    colordata = data['productColor'].value_counts()
    drawPie(colordata, os.path.join(DIR, '胸罩颜色分布.png'), "胸罩颜色分布", color=True)
    cupdata = data['productSize'].value_counts()
    drawPie(cupdata, os.path.join(DIR, '胸罩罩杯分布.png'), "胸罩罩杯分布")


# 启动入口
if __name__ == '__main__':
    main()
