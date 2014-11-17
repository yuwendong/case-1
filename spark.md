# Spark配置

##1.功能说明

##2.配置内容

主节点（master）：219.224.135.46（mirage）
```
worker：
219.224.135.45(ubuntu1)
219.224.135.46(mirage)
219.224.135.47(ubuntu3)
219.224.135.48(ubuntu4)
219.224.135.60(ubuntu2)
219.224.135.126(ubuntu5)
```

参考http://spark.apache.org/docs/latest/spark-standalone.html中Installing Spark Standalone to a Cluster的Starting a Cluster Manually
在主节点的/home/spark/spark-1.0.1-bin-hadoop1/下执行./sbin/start-master.sh
在worker的/home/spark/spark-1.0.1-bin-hadoop1/下执行./bin/spark-class org.apache.spark.deploy.worker.Worker spark://mirage:7077

注意配置每台机器下的/etc/hosts

可以通过web UI查看集群的情况：http://219.224.135.46:8080/
