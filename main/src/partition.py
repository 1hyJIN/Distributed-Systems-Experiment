import matplotlib.pyplot as plt
import numpy as np
plt.switch_backend('tkagg')
# Data
partition_numbers = [4, 16, 64, 128, 256]
app_execution_time = [4, 4, 5, 8, 9]  # Application execution time (seconds)
operation_execution_time = [0.44, 0.35, 0.79, 1.69, 1.6]  # Operation execution time (seconds)
shuffle_write = [20.6, 89.9, 555.8, 1287.4, 9200]  # Shuffle Write data (KB or MB)
shuffle_read = [7.5, 7.6, 7.5, 6.9, 6.1]  # Shuffle Read data (MB)
task_max = [4, 16, 64, 128, 256]  # Maximum Task values

# Set font to use only English characters (default font)
plt.rcParams['font.family'] = 'Arial'

# Create the figure
plt.figure(figsize=(12, 10))

# Plot 1: Application execution time vs. partition numbers
plt.subplot(2, 2, 1)
plt.plot(partition_numbers, app_execution_time, marker='o', color='b', linestyle='-', label='Application execution time')
plt.title("Application Execution Time vs Partition Numbers")
plt.xlabel("Partition Numbers")
plt.ylabel("Execution Time (seconds)")
plt.grid(True)
plt.legend()

# Plot 2: Operation execution time vs. partition numbers
plt.subplot(2, 2, 2)
plt.plot(partition_numbers, operation_execution_time, marker='o', color='g', linestyle='-', label='Operation execution time')
plt.title("Operation Execution Time vs Partition Numbers")
plt.xlabel("Partition Numbers")
plt.ylabel("Execution Time (seconds)")
plt.grid(True)
plt.legend()

# Plot 3: Shuffle Write data vs. partition numbers
plt.subplot(2, 2, 3)
plt.plot(partition_numbers, shuffle_write, marker='o', color='r', linestyle='-', label='Shuffle Write Data')
plt.title("Shuffle Write Data vs Partition Numbers")
plt.xlabel("Partition Numbers")
plt.ylabel("Shuffle Write Data (KB/MB)")
plt.grid(True)
plt.legend()

# Plot 4: Shuffle Read data vs. partition numbers
plt.subplot(2, 2, 4)
plt.plot(partition_numbers, shuffle_read, marker='o', color='purple', linestyle='-', label='Shuffle Read Data')
plt.title("Shuffle Read Data vs Partition Numbers")
plt.xlabel("Partition Numbers")
plt.ylabel("Shuffle Read Data (MB)")
plt.grid(True)
plt.legend()

# Show the plot
plt.tight_layout()
plt.show()