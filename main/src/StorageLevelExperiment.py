from pyspark.sql import SparkSession
import time
from pyspark import StorageLevel

# 初始化 Spark 会话
spark = SparkSession.builder.appName("StorageLevelExperiment").master("yarn") \
    .config("spark.executor.memory", "14g") \
    .config("spark.executor.cores", "16") \
    .config("spark.executor.instances", "2") \
    .getOrCreate()

sc = spark.sparkContext

# 创建一个大数据集
data = [(i, i) for i in range(10**6)]  # 10万条数据

# 创建 RDD
rdd = sc.parallelize(data)

# 测试不同的存储级别
# StorageLevel.MEMORY_ONLY_SER, StorageLevel.MEMORY_ONLY_2
for storage_level in [StorageLevel.DISK_ONLY, StorageLevel.MEMORY_ONLY_SER, StorageLevel.MEMORY_ONLY_2]:
    print(f"\nTesting with storage level: {storage_level}")
    
    # 持久化 RDD
    rdd_persisted = rdd.persist(storage_level)
    
    # 执行一个宽依赖操作 (reduceByKey)
    start_time = time.time()
    rdd_persisted.reduceByKey(lambda x, y: x + y).collect()  # 触发行动操作
    end_time = time.time()
    
    print(f"Execution time with storage level {storage_level}: {end_time - start_time} seconds")
    rdd_persisted.unpersist()

sc.stop()
