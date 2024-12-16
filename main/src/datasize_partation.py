import matplotlib.pyplot as plt
import numpy as np
plt.switch_backend('tkagg')
# 数据
data_sizes = ['10^7', '10^6', '10^5']
partition_numbers = [256, 128, 64, 16, 4]

# 每个数据规模的执行时间（单位：秒）
times_10_7 = [4.11, 3.31, 2.17, 1.77, 2.85]
times_10_6 = [1.60, 1.69, 0.79, 0.35, 0.44]
times_10_5 = [1.22, 1.37, 0.61, 0.27, 0.20]

# 找到每个数据规模下的最小值及其对应的分区数
min_10_7_idx = np.argmin(times_10_7)
min_10_6_idx = np.argmin(times_10_6)
min_10_5_idx = np.argmin(times_10_5)

min_10_7_value = times_10_7[min_10_7_idx]
min_10_6_value = times_10_6[min_10_6_idx]
min_10_5_value = times_10_5[min_10_5_idx]

# 创建图形
plt.figure(figsize=(12, 7))

# 绘制不同数据规模的执行时间
plt.plot(partition_numbers, times_10_7, label=r'Data size: $10^7$', marker='o', color='b', markersize=8, linewidth=2, linestyle='-', alpha=0.8)
plt.plot(partition_numbers, times_10_6, label=r'Data size: $10^6$', marker='s', color='g', markersize=8, linewidth=2, linestyle='-', alpha=0.8)
plt.plot(partition_numbers, times_10_5, label=r'Data size: $10^5$', marker='^', color='r', markersize=8, linewidth=2, linestyle='-', alpha=0.8)

# 高亮显示最小时间的点
plt.scatter(partition_numbers[min_10_7_idx], min_10_7_value, color='b', s=100, zorder=5, edgecolor='k', linewidth=2)
plt.scatter(partition_numbers[min_10_6_idx], min_10_6_value, color='g', s=100, zorder=5, edgecolor='k', linewidth=2)
plt.scatter(partition_numbers[min_10_5_idx], min_10_5_value, color='r', s=100, zorder=5, edgecolor='k', linewidth=2)

# 添加标注
plt.annotate(f'{min_10_7_value:.2f}s',
             (partition_numbers[min_10_7_idx], min_10_7_value),
             textcoords="offset points", xytext=(0, 12), ha='center', fontsize=10, color='b', fontweight='bold')
plt.annotate(f'{min_10_6_value:.2f}s',
             (partition_numbers[min_10_6_idx], min_10_6_value),
             textcoords="offset points", xytext=(0, 12), ha='center', fontsize=10, color='g', fontweight='bold')
plt.annotate(f'{min_10_5_value:.2f}s',
             (partition_numbers[min_10_5_idx], min_10_5_value),
             textcoords="offset points", xytext=(0, 12), ha='center', fontsize=10, color='r', fontweight='bold')

# 设置图形的标题和标签
plt.title("Impact of Partition Number on Execution Time for Different Data Sizes", fontsize=14, fontweight='bold')
plt.xlabel("Number of Partitions", fontsize=12)
plt.ylabel("Average Execution Time (seconds)", fontsize=12)

# 添加图例
plt.legend(loc='upper right', fontsize=11, frameon=True, framealpha=0.7)

# 设置网格
plt.grid(True, linestyle='--', alpha=0.6)

# 调整刻度
plt.xticks(partition_numbers, fontsize=10)
plt.yticks(fontsize=10)

# 显示图像
plt.tight_layout()
plt.show()