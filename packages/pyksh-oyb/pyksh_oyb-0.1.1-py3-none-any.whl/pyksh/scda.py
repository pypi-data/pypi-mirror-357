import os


class _SCDA:
    def __init__(self):
        self._data = {
            "t1": """import numpy as np
import matplotlib.pyplot as plt

# 设置中文显示
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 数据准备
x = np.arange(5)
y1 = [1200, 2400, 1800, 2200, 1600]
y2 = [1050, 2100, 1300, 1600, 1340]
labels = ["家庭", "小说", "心理", "科技", "儿童"]

# 绘图
plt.bar(x, y1, width=0.6, color="#FFCC00", label="地区1")
plt.bar(x, y2, width=0.6, bottom=y1, color="#B0C4DE", label="地区2")

# 图表修饰
plt.ylabel("采购数量（本）")
plt.xlabel("图书种类")
plt.title("地区1和地区2对各类图书的采购情况")
plt.xticks(x, labels)
plt.grid(True, axis="y", color="gray", alpha=0.2)
plt.legend()

plt.show()
""",
            "t2": """%matplotlib auto
import numpy as np
import matplotlib.pyplot as plt

# 设置字体为SimHei以支持中文显示
plt.rcParams['font.sans-serif'] = ["SimHei"]

# 定义月份数据
x = list(range(1, 13))
# 定义产品A和产品B的销售额数据
y1 = [20, 28, 23, 16, 29, 36, 39, 33, 31, 19, 21, 25]
y2 = [17, 22, 39, 26, 35, 23, 25, 27, 29, 38, 28, 20]
# 定义月份标签
labels = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']

# 创建子图1，用于展示销售额趋势
ax1 = plt.subplot(211)
ax1.plot(x, y1, 'm--o', lw=2, ms=5, label='产品 A')  # 绘制产品A的销售额趋势
ax1.plot(x, y2, 'g--o', lw=2, ms=5, label='产品 B')  # 绘制产品B的销售额趋势
ax1.set_title("销售额趋势", fontsize=11)  # 设置子图标题
ax1.set_ylim(10, 45)  # 设置y轴范围
ax1.set_ylabel('销售额（亿元）')  # 设置y轴标签
ax1.set_xlabel('月份')  # 设置x轴标签
# 在每个数据点上添加注释
for xy1 in zip(x, y1):
    ax1.annotate("%s" % xy1[1], xy=xy1, xytext=(-5, 5), textcoords='offset points')
for xy2 in zip(x, y2):
    ax1.annotate("%s" % xy2[1], xy=xy2, xytext=(-5, 5), textcoords='offset points')
ax1.legend()  # 添加图例

# 创建子图2，用于展示产品A的销售额饼图
ax2 = plt.subplot(223)
ax2.pie(y1, radius=1, wedgeprops={'width': 0.5}, labels=labels, autopct='%3.1f%%', pctdistance=0.75)
ax2.set_title('产品 A 销售额')  # 设置子图标题

# 创建子图3，用于展示产品B的销售额饼图
ax3 = plt.subplot(224)
ax3.pie(y2, radius=1, wedgeprops={'width': 0.5}, labels=labels, autopct='%3.1f%%', pctdistance=0.75)
ax3.set_title('产品 B 销售额')  # 设置子图标题

# 调整子图布局
plt.tight_layout()
# 显示图表
plt.show()
""",
            "t3": """import numpy as np
import matplotlib.pyplot as plt

# 设置matplotlib支持中文显示和正常显示负号
plt.rcParams["font.sans-serif"] = ["SimHei"]  # 设置字体为SimHei以支持中文显示
plt.rcParams["axes.unicode_minus"] = False  # 设置正常显示负号

# 创建一个包含1到12的数组，代表一年中的12个月
month_x = np.arange(1, 13, 1)

# 平均气温数据，单位为摄氏度
data_tem = np.array([2.0, 2.2, 3.3, 4.5, 6.3, 10.2, 20.3, 33.4, 23.0, 16.5, 12.0, 6.2])

# 降水量数据，单位为毫升
data_precipitation = np.array(
    [2.6, 5.9, 9.0, 26.4, 28.7, 70.7, 175.6, 182.2, 48.7, 18.8, 6.0, 2.3]
)

# 蒸发量数据，单位为毫升
data_evaporation = np.array(
    [2.0, 4.9, 7.0, 23.2, 25.6, 76.7, 135.6, 162.2, 32.6, 20.0, 6.4, 3.3]
)

# 创建一个图形和一个轴
fig, ax = plt.subplots()

# 绘制蒸发量条形图，颜色为橙色，并设置x轴刻度标签为月份
bar_ev = ax.bar(
    month_x,
    data_evaporation,
    color="orange",
    tick_label=[
        "1月",
        "2月",
        "3月",
        "4月",
        "5月",
        "6月",
        "7月",
        "8月",
        "9月",
        "10月",
        "11月",
        "12月",
    ],
)

# 绘制降水量条形图，颜色为绿色，其底部为蒸发量数据
bar_pre = ax.bar(month_x, data_precipitation, bottom=data_evaporation, color="green")

# 设置y轴标签为"水量(ml)"
ax.set_ylabel("水量(ml)")

# 设置图表标题
ax.set_title("平均气温与降水量、蒸发量的关系")

# 创建第二个y轴，共享x轴
ax_right = ax.twinx()

# 在第二个y轴上绘制平均气温折线图，使用蓝色圆圈和线段表示
line = ax_right.plot(month_x, data_tem, "o-m")

# 设置第二个y轴标签为"气温 ($^\circ$C)"
ax_right.set_ylabel(r"气温 ($^\circ$C)")

# 添加图例，包含蒸发量、降水量和平均气温的图例项，并设置阴影和花式边框
plt.legend(
    [bar_ev, bar_pre, line[0]],
    ["蒸发量", "降水量", "平均气温"],
    shadow=True,
    fancybox=True,
)

# 显示图表
plt.show()
""",
            "t4": """import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator
days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
prices =[44.98,45.02,44.32,41.05,42.08,None,None]

fig=plt.figure(figsize=(10,6))
ax=fig.add_axes([0.2,0.2,0.5,0.5])
#绘制折线图
ax.plot(days,prices,marker='o',linestyle='-')
#设置刻度标签
ax.set_xticks(days)
ax.set_xticklabels(days)
ax.tick_params(axis='both',direction='in',width=2)
# 隐藏上和右
ax.spines['top'].set_color('none')
ax.spines['right'].set_color('none')
plt.show()
""",
            "t5": """import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
from matplotlib.animation import FuncAnimation

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

# 生成数据
xx = np.array([13, 5, 25, 13, 9, 19, 3, 39, 13, 27])
yy = np.array([4, 38, 16, 26, 7, 19, 28, 10, 17, 18])
zz = np.array([7, 19, 6, 12, 25, 19, 23, 25, 10, 15])

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# 绘制初始的3D散点图
star = ax.scatter(xx, yy, zz, c='#C71585', marker='*', s=160, linewidth=1, edgecolor='black')

# 每帧动画调用的函数
def animate(i):
    if i % 2:
        color = '#C71585'
    else:
        color = 'white'
    star.set_color(color)
    return star,

def init():
    return star,

ani = FuncAnimation(fig=fig, func=animate, frames=np.arange(100), init_func=init, interval=1000, blit=True)

ax.set_xlabel('x轴')
ax.set_ylabel('y轴')
ax.set_zlabel('z轴')
ax.set_title('3D散点图', fontproperties='simhei', fontsize=14)
plt.tight_layout()
plt.show()
""",
            "t6": """import matplotlib.pyplot as plt
import numpy as np

# 数据准备
car_hotspots = ['比亚迪 e5', '思域', '高合 HiPhi X', 'LYRIQ 锐歌', '雅阁', '迈腾', '帕萨特', '朗逸', '凯美瑞', '速腾']
search_index = [144565, 114804, 72788, 70519, 68742, 65308, 64312, 64102, 58219, 56590]
# 创建图形
plt.figure(figsize=(8, 4))
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文显示
plt.rcParams['axes.unicode_minus'] = False
# 绘制棉棒图
# 1. 绘制垂直线
for i in range(len(car_hotspots)):
    plt.vlines(x=car_hotspots[i], ymin=0, ymax=search_index[i], color='skyblue', linewidth=2)
# 2. 绘制圆点标记
plt.scatter(car_hotspots, search_index, color='orange', s=100, zorder=3)
# 3. 添加注释文本
for i, v in enumerate(search_index):
    plt.text(car_hotspots[i], v + 5000, str(v), ha='center', va='bottom')
# 设置图表标题和标签
plt.title('百度汽车热点 Top10 搜索指数')
plt.xlabel('汽车热点')
plt.ylabel('搜索指数')
# 旋转x轴标签
plt.xticks(rotation=45, ha='right')
# 调整布局
plt.tight_layout()
# 显示图表
plt.show()
""",
            "t7": """import matplotlib.pyplot as plt
from matplotlib.sankey import Sankey
import numpy as np
from matplotlib.patches import Patch

flows = np.array([20000, 500, -2000, -5000, -4000, -1000, -500, -200])
labels = np.array(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'])
orientations = np.array([1, 1, -1, -1, -1, -1, -1, -1])

legend_labels = [
    "A: 收入 20000",
    "B: 人情往来 500",
    "C: 旅行 2000",
    "D: 深造 5000",
    "E: 生活 4000",
    "F: 购物 1000",
    "G: 聚餐 500",
    "H: 其它 200"
]

fig = plt.figure(figsize=(12, 7))
ax = fig.add_subplot(1, 1, 1, xticks=[], yticks=[],
                     title="小兰当月日常生活收支流量的桑基图")

sankey = Sankey(ax=ax, scale=0.0005, unit=None)
sankey.add(flows=flows, labels=labels, orientations=orientations,
           color='black', fc='lightblue', patchlabel='小兰当月收支', alpha=0.7)
diagrams = sankey.finish()

# 手动创建图例句柄
handles = [Patch(facecolor='lightblue', edgecolor='black', label=label) for label in legend_labels]

# 用ax.legend，并调整位置
ax.legend(handles=handles, loc='lower center', bbox_to_anchor=(0.5, -0.18), ncol=4, fontsize=12, frameon=False)

# 调整底部留白，避免图例被裁剪
plt.subplots_adjust(bottom=0.28)

plt.show()
""",
        }

    @property
    def all(self):
        out = []
        files = [
            ("t1" or "图书" or "堆积柱形图", "4.2.3.py"),
            ("t2" or "销售额" or "多子图" or "组合图", "5.1.2.py"),
            ("t3" or "气温" or "天气" or "降水" or "蒸发", "5.3.3.py"),
            ("t4" or "股票" or "折线图", "6(1).py"),
            ("t5" or "星星" or "散点图", "7.2.2.py"),
            ("t6" or "汽车" or "棉棒图", "8(1).py"),
            ("t7" or "小兰" or "桑基图", "8(2).py"),
        ]
        for key, fname in files:
            out.append(f"===== {fname} ({key}) =====\n" + self._data[key])
        return "\n\n".join(out)

    @property
    def t1(self):
        return self._data["t1"]

    @property
    def t2(self):
        return self._data["t2"]

    @property
    def t3(self):
        return self._data["t3"]

    @property
    def t4(self):
        return self._data["t4"]

    @property
    def t5(self):
        return self._data["t5"]

    @property
    def t6(self):
        return self._data["t6"]

    @property
    def t7(self):
        return self._data["t7"]

    def __str__(self):
        return self.all


scda = _SCDA()
