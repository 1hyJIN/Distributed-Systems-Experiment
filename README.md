## 环境依赖
- 操作系统： `Ubuntu 18.04`

- `JDK`版本： $1.8$

- `Spark`版本： $2.4.7$

- `Hadoop`版本： $2.10.1$

- `Pyspark`版本： $2.4.7$

- `python`版本： $3.6$

  
## 目的
本项目旨在探究`Apache Spark`及`PySpark`框架下的性能优化方法，通过设置一系列实验，分析存储级别、数据分区数以及数据传输过程对作业性能的影响。  
在大数据计算中，`Spark`的性能表现受多种因素影响，例如存储策略、数据分区配置和`Shuffle`操作等。本实验通过以下三个方面进行分析：  

1. **存储级别对性能的影响**：研究不同存储策略（如`MEMORY_ONLY`、`MEMORY_AND_DISK`等）如何在`Spark`和`PySpark`中影响数据存储效率和任务执行时间。  

2. **数据分区数的优化**：探究分区数配置对`Shuffle`阶段的性能表现，重点分析分区数对负载均衡、并行度和数据传输开销的影响。  

3. **数据传输的差异性**：对比窄依赖和宽依赖操作在`Stage`内部和`Stage`之间的数据传输特性，验证`Shuffle`操作对数据重分区及作业执行效率的影响。  

   


## 实验过程 

### 实验一 ：探究不同的存储级别分析对性能的影响

**目的**：通过使用不同的存储级别（如 `MEMORY_ONLY`, `MEMORY_AND_DISK` 等），观察存储级别对性能的影响。

存储级别分类如下：

**`MEMORY_ONLY`**：数据仅缓存到内存，内存不足时丢失数据，性能较好但可能导致计算开销。

**`MEMORY_AND_DISK`**：数据先缓存到内存，不足时写入磁盘，性能稍慢但避免数据丢失。

**`MEMORY_ONLY_SER`**：与 `MEMORY_ONLY` 类似，但使用序列化格式，节省内存。

**`MEMORY_AND_DISK_SER`**：与 `MEMORY_AND_DISK` 类似，但使用序列化格式，适合大数据量且需节省内存的场景。

**`DISK_ONLY`**：数据仅缓存到磁盘，适合内存小或减少内存占用的场景，但访问较慢。

不同存储的执行时间：<br><br>
数据大小为 $10^6$ 
只执行一个宽依赖操作 (`reduceByKey`)情况下：
| Batch/level | MEMORY_ONLY      | MEMORY_AND_DISK | MEMORY_ONLY_SER | MEMORY_AND_DISK_SER | DISK_ONLY |
| ----------- | ---------------- | --------------- | --------------- | ------------------- | --------- |
| $1^{st}$    | 4.440s           | 3.210s          | 2.377s          | 2.166s              | 2.068s    |
| $2^{nd}$    | 4.314s           | 3.187s          | 2.066s          | 2.105s              | 2.104s    |
| $3^{rd}$    | 4.295s           | 3.222s          | 2.224s          | 2.107s              | 2.167s    |
| $4^{th}$    | **20.887s** (舍) | 3.245s          | 2.090s          | 2.081s              | 2.107s    |
| $5^{th}$    | 4.174s           | 3.158s          | 2.089s          | 2.091s              | 2.007s    |
| Average     | 4.306s           | 3.004s          | 2.169s          | 2.110s              | 2.091s    |

数据大小为 $10^7$，分批次操作，每个批次 $10^5$
依次执行三个宽依赖操作 (`reduceByKey`、`groupByKey`、`join`)情况下：
| MEMORY_ONLY      | MEMORY_AND_DISK | MEMORY_ONLY_SER | MEMORY_AND_DISK_SER | DISK_ONLY |
| ---------------- | --------------- | --------------- | ------------------- | --------- |
| 138.414s         | 140.131s        | 143.429s        | 145.361s            | 152.599s  |


#### 实验数据：

![GitHub图像](/assets/image-20241216124811069.png) 
![GitHub图像](/assets/20241216234953.png)


#### 理论分析:

| 存储级别                | 特点                                       | 优势                           | 劣势                                      |
| ----------------------- | ------------------------------------------ | ------------------------------ | ----------------------------------------- |
| **MEMORY_ONLY**         | 数据以非序列化形式存储在内存中             | 速度最快                       | 占用大量内存，内存不足时数据丢失          |
| **MEMORY_AND_DISK**     | 数据优先存储在内存中，内存不足时溢写到磁盘 | 内存不足时保证数据不会丢失     | 磁盘读写开销导致性能下降                  |
| **MEMORY_ONLY_SER**     | 数据以序列化形式存储在内存中               | 减少内存占用，可存储更多的数据 | 增加序列化和反序列化的 CPU 开销，速度较慢 |
| **MEMORY_AND_DISK_SER** | 数据以序列化形式存储，内存不足时写入磁盘   | 内存和磁盘结合，存储效率较高   | 序列化和磁盘写入开销，性能适中            |
| **DISK_ONLY**           | 数据完全存储在磁盘中，不占用内存           | 避免内存不足问题               | 速度最慢，完全依赖磁盘 I/O                |

#### 结果分析：

**（1）内存缓存策略（MEMORY_ONLY、MEMORY_ONLY_SER）**：这些策略在数据量较小时非常高效，特别是 `MEMORY_ONLY`，因为它将数据直接缓存到内存中，访问速度非常快。然而，当内存不足时，可能导致性能下降或甚至 OOM 错误。

**（2）磁盘与内存结合策略（MEMORY_AND_DISK、MEMORY_AND_DISK_SER）**：这些策略能容忍内存溢出，性能通常较 `MEMORY_ONLY` 稍慢，但能够避免内存溢出的问题，适合较大数据集。

**（3）磁盘缓存策略（DISK_ONLY）**：由于完全依赖磁盘存储，性能较慢，适合内存有限且数据量非常大的情况。



对于小数据量来说，`MEMORY_ONLY` 和 `MEMORY_ONLY_SER` 通常是最快的，数据直接放在内存里，读取速度很快。不过，当数据量变大时，`MEMORY_AND_DISK` 或 `DISK_ONLY` 更稳定一些，能够防止因为内存不够导致任务失败，虽然性能会慢一些。

Spark 的内存管理和序列化/反序列化操作有时会带来额外的开销，反而拖慢小数据量的性能。特别是 `DISK_ONLY`，在小数据量的情况下反而表现不错，因为磁盘 I/O 的开销并不大，而且避免了复杂的内存管理。 <br><br>



### 实验二 ：探究数据分区数对 ShuffleMapStage 的影响

#### 背景知识

在 Apache Spark 中，**分区（Partition）** 是数据分布在集群中的基本单位。Spark 的并行计算是基于分区进行的，每个分区的数据会被分配到一个 Executor 上的 Task 进行计算。因此，分区数的合理设置会直接影响作业的性能表现。

#### 分区的作用：

**（1）并行计算**

​	spark 将数据分区后，每个分区会作为一个任务并行执行，提高并行度。

**（2）数据局部性优化**

​	合理的分区能够提高数据的局部性，减少跨节点的数据传输，从而优化性能。

**（3）负载均衡**

​	设置分区数可以平衡各个任务的计算负载，避免某些节点计算过载，提升资源利用率。



#### 实验数据：

我们整理包含了三个数据规模（`10^7`，`10^6`，`10^5`）下不同分区数的原始实验数据，以及每个实验的平均值。

**（1）数据规模：`10^7`**

| Experiment  | 256 Partitions | 128 Partitions | 64 Partitions | 16 Partitions | 4 Partitions |
| ----------- | -------------- | -------------- | ------------- | ------------- | ------------ |
| $1^{th}$    | 8.01s（舍去）  | 3.95s          | 2.17s         | 1.79s         | 2.91s        |
| $2^{th}$    | 3.24s          | 3.28s          | 2.13s         | 1.69s         | 2.97s        |
| $3^{th}$    | 3.16s          | 2.97s          | 2.10s         | 1.79s         | 2.76s        |
| $4^{th}$    | 3.00s          | 3.42s          | 2.24s         | 1.74s         | 2.80s        |
| $5^{th}$    | 3.16s          | 2.91s          | 2.20s         | 1.84s         | 2.83s        |
| **Average** | **4.11s**      | **3.31s**      | **2.17s**     | **1.77s**     | **2.85s**    |

**（2）数据规模：`10^6`**

| Experiment  | 256 Partitions | 128 Partitions | 64 Partitions | 16 Partitions | 4 Partitions |
| ----------- | -------------- | -------------- | ------------- | ------------- | ------------ |
| $1^{th}$    | 1.68s          | 1.88s          | 0.69s         | 0.34s         | 0.45s        |
| $2^{th}$    | 1.44s          | 1.57s          | 0.84s         | 0.35s         | 0.43s        |
| $3^{th}$    | 1.73s          | 1.65s          | 0.76s         | 0.39s         | 0.44s        |
| $4^{th}$    | 1.56s          | 1.66s          | 0.78s         | 0.35s         | 0.43s        |
| $5^{th}$    | 1.60s          | 1.69s          | 0.90s         | 0.35s         | 0.43s        |
| **Average** | **1.60s**      | **1.69s**      | **0.79s**     | **0.35s**     | **0.44s**    |

**（3）数据规模：`10^5`**

| Experiment  | 256 Partitions | 128 Partitions | 64 Partitions | 16 Partitions | 4 Partitions |
| ----------- | -------------- | -------------- | ------------- | ------------- | ------------ |
| $1^{st}$    | 1.27s          | 1.42s          | 0.54s         | 0.40s         | 0.19s        |
| $2^{nd}$    | 1.28s          | 1.41s          | 0.69s         | 0.21s         | 0.20s        |
| $3^{rd}$    | 1.17s          | 1.37s          | 0.67s         | 0.25s         | 0.21s        |
| $4^{th}$    | 1.25s          | 1.39s          | 0.56s         | 0.26s         | 0.21s        |
| $5^{th}$    | 1.11s          | 1.28s          | 0.59s         | 0.24s         | 0.15s        |
| **Average** | **1.22s**      | **1.37s**      | **0.61s**     | **0.27s**     | **0.20s**    |

整理后得到如下表格：

| 数据规模 | 分区数 4 | 分区数 16 | 分区数 64 | 分区数 128 | 分区数 256 | 平均执行时间 (秒) |
| -------- | -------- | --------- | --------- | ---------- | ---------- | ----------------- |
| $10^7$   | 2.85s    | 1.77s     | 2.17s     | 3.31s      | 4.11s      | 4.11s             |
| $10^6$   | 0.44s    | 0.35s     | 0.79s     | 1.69s      | 1.60s      | 1.60s             |
| $10^5$   | 0.20s    | 0.27s     | 0.61s     | 1.37s      | 1.22s      | 1.22s             |

并且我们在**spark ui**界面查看数据规模为 $10^6$ 时，查看不同分区大小`shuffle read`和`shuffle write`的数据量，并且记录了每个应用的执行时间：

| 指标                    | 分区数 4 | 分区数 16 | 分区数 64 | 分区数 128 | 分区数256 |
| ----------------------- | -------- | --------- | --------- | ---------- | --------- |
| 应用执行时间            | 4s       | 4s        | 5s        | 8s         | 9s        |
| 操作执行时间            | 0.44s    | 0.35s     | 0.79s     | 1.69s      | 1.60s     |
| shuffle write（stage0） | 20.6KB   | 89.9KB    | 555.8KB   | 1287.4KB   | 9.2MB     |
| shuffle read（stage2）  | 7.5M     | 7.6M      | 7.5M      | 6.9M       | 6.1MB     |
| Task的最大值            | 4        | 16        | 64        | 128        | 256       |



**由实验结果绘制如下图表：**

![GitHub图像](/assets/image-20241216155738191.png) 

![GitHub图像](/assets/image-20241216180846011.png) 

#### 图像分析：

从横向来看：折线图的趋势成开始小部分下降后上升，最后相对趋于平稳。且数据规模越大时，折线波动越明显，意味着当数据规模越大时，分区数对`ShuffleMapStage`的影响越为直观。

从纵向来看：当分区数一定时，数据规模越大执行时间越长（显而易见），当中等及以上规模数据时，最佳的数据分区为 $16$ ，而当数据规模较小时，选取较小的分区4反而可以减少额外的计算开销。

从`shuffle`数据大小来看：随着分区数增加，写入的 `Shuffle` 数据量也有所增加。分区数为 $4$ 时，`Shuffle Write` 仅为 $20.6$ KB，而分区数为 $256$ 时，数据量增加到 $9.2$ MB。更多的分区会增加 `Shuffle` 过程中的数据交换，导致更多的 **I/O** 操作。Shuffle Read 数据量随着分区数增加变化较小，从 $7.5$ M 到 $7.6$ M，这意味着在此实验中 `Shuffle Read` 数据量在较小分区数之间变化不大。

从运行时间来看：当分区数量越大时，作业总体执行的时间越长。



#### 结论：

**（1）分区数对执行时间的影响**

| 数据规模 | 最低执行时间（秒） | 最佳分区数 | 执行时间减少幅度 (%) |
| -------- | ------------------ | ---------- | -------------------- |
| $10^7$   | 1.77               | 16         | 57%                  |
| $10^6$   | 0.35               | 16         | 78%                  |
| $10^5$   | 0.20               | 4          | 84%                  |

**（2）分区数对不同数据规模的影响**

| 数据规模 | 执行时间最小值所在分区数 | 执行时间最小值（秒） | 执行时间变化趋势               |
| -------- | ------------------------ | -------------------- | ------------------------------ |
| $10^7$   | 16                       | 1.77                 | 显著减少，分区数减少效果明显   |
| $10^6$   | 16                       | 0.35                 | 平滑下降，分区数减少有明显效果 |
| $10^5$   | 4                        | 0.20                 | 变化平缓，分区数减少效果不明显 |

**（3）趋势**

| 数据规模 | 总体结论                                               |
| -------- | ------------------------------------------------------ |
| $10^7$   | 分区数减少显著减少执行时间，最佳分区数为 **16 个分区** |
| $10^6$   | 分区数减少仍有影响，最佳分区数为 **16 个分区**         |
| $10^5$   | 执行时间变化平缓，最佳分区数为**4 个分区**             |

**（4）分区数对shuffle数据量的影响**

| 指标              | 分区数 4 | 分区数 16 | 分区数 64 | 分区数 128 | 分区数 256 |
| ----------------- | -------- | --------- | --------- | ---------- | ---------- |
| **Shuffle Write** | 20.6 KB  | 89.9 KB   | 555.8 KB  | 1287.4 KB  | 9.2 MB     |
| **Shuffle Read**  | 7.5 MB   | 7.6 MB    | 7.5 MB    | 6.9 MB     | 6.1 MB     |



**应用思考**

在处理 **大数据集** 时，过多的分区会导致 **数据 shuffle** 过程的增加，从而影响执行效率，因此 **减少分区数** 可以减轻网络和磁盘 **I/O** 压力，提高性能。

对于 **小数据集**，虽然分区数减少能稍微提升性能，但整体执行时间已经相对较短，因此此时更多的优化空间可能在于 **算法层面** 或 **硬件资源的利用**（如内存和CPU等）。



#### 实验结论：

**分区数太小**：导致并行度低、数据倾斜和内存溢出。

**分区数太大**：增加调度开销和 `Shuffle` 数据量，反而降低性能。

**最佳分区数**：取决于集群的资源（如 **CPU** 核心数、内存）和数据规模，需要根据实际情况进行调优。  <br><br>



### 实验三 ：验证Stage 内部数据传输和外部数据传输的差异

#### **背景知识：**

##### **（1）Stage 内部数据传输：**

- 发生在窄依赖（**Narrow Dependency**）操作中，如 `map`, `filter`。
- 数据流动可以在同一个分区中完成，不需要跨分区通信。
- 同一个 `Stage` 内的任务可以并行执行。

##### **（2）Stage 之间数据传输：**

- 发生在宽依赖（**Wide Dependency**）操作中，如 `groupByKey`, `reduceByKey`, `join`。

- 数据需要重新分区（`Shuffle`），导致跨节点的数据传输。

- 每次 `Shuffle` 都会触发新的 `Stage`，增加数据传输的开销。

  

#### 实验设计

设计两个 **RDD** 操作链，分别观察 **Stage 内** 和 **Stage 间** 的数据传输情况：

1. **Stage 内部传输**：使用 **窄依赖操作**（如 `map` 和 `filter`），这些操作不会触发 Shuffle，数据不会离开分区。

2. **Stage 之间传输**：使用 **宽依赖操作**（如 `groupByKey` 和 `reduceByKey`），这些操作会触发 `Shuffle`，导致数据在 `Stage` 之间传输。

   

#### 实验结果

- **窄依赖操作**

![GitHub图像](/assets/image-20241216084017977.png)

在执行时先使用窄依赖操作，由于窄依赖操作时数据没有离开分区，所有的数据操作都在一个`stage`完成。



![GitHub图像](/assets/image-20241216084126000.png) 

![GitHub图像](/assets/image-20241216084223995.png) 

在`stage0` 我们可以清晰的看到所执行的窄依赖操作确实没有触发`Shuffle`，数据并没有在`stage`之间进行传输。阶段一生成的`DAG`图如下，生成的`DAG`图对应着我们之前执行的转换操作**算子**。

![GitHub图像](/assets/image-20241216085856140.png) 

- **宽依赖操作**

![GitHub图像](/assets/image-20241216123256064.png)

对于宽依赖操作，我们使用`groupBykey`和`reduceByKey`查看是否出发`shuffle`和新的`stage`



![GitHub图像](/assets/image-20241216123445345.png)  

从**spark ui**可以看出**job id2** 和**id1** 分别对应`gourdbykey` 和`reducebyKey` 操作，每个宽依赖操作都会开启一个新的`stage`，且可以在`stage`界面看到`shffle` 读写的操作以及数据传送的大小。



![GitHub图像](/assets/image-20241216123841678.png) 

![GitHub图像](/assets/image-20241216123935555.png) 

![GitHub图像](/assets/image-20241216124003560.png) 

查看**job2** 和**job1** 的**DAG**图可以看出这两个操作的类似，验证了`stage`间的数据传输为宽依赖操作，通过触发`shuffle`从而进行数据传输。

不同`stage`的详细信息：

![GitHub图像](/assets/image-20241216124410887.png) 

![GitHub图像](/assets/image-20241216124429518.png)

![GitHub图像](/assets/image-20241216124502462.png) 

![GitHub图像](/assets/image-20241216124551127.png) 


## 参考资料

1. **徐辰, 分布式计算系统, 高等教育出版社, https://dasebigdata.github.io/, 2022.**

2. **如何在Linux服务器上安装Anaconda [https://blog.csdn.net/wyf2017/article/details/118676765]**

3. **spark调优篇-spark on yarn web UI [https://www.cnblogs.com/yanshw/p/12038633.html]**

4. **PySpark基础入门（1）：基础概念＋环境搭建 [https://juejin.cn/post/7228162548901904440]**

5. **PySpark部署安装 [https://cloud.tencent.com/developer/article/2334461]**

6. **Linux上配置Jupyter Notebook远程访问 [https://fuhailin.github.io/remote-jupyter-notebook/]**

7. **Spark大数据分析与实战笔记 [https://blog.csdn.net/u014727709/article/details/136032936]**



## 分工
- **程盛霖**（ $51275903039$ ）占比25%：编写实验代码，代码运行测试，画图分析，README编写。
- **贾茂宁**（ $51275903099$ ）占比25%：实验设计，编写实验代码，画图分析，PPT编写。
- **彭林航**（ $51275903073$ ）占比25%：搭建**spark**集群环境，**spark web UI**改进、**spark**后台管理。
- **金浩阳**（ $51275903043$ ）占比25%：搭建**pyspark**、**notebook**运行环境，编写实验代码，代码运行测试改进。

