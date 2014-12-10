配置spark的mesos模式

一、Mesos配置
```
master：219.224.135.46，
slave：219.224.135.47，219.224.135.48，219.224.135.60
```

1.配置master到slave服务器的无密码ssh登陆

现在确认能否不输入口令就用ssh登录localhost:
```
$ ssh localhost
```

如果不输入口令就无法用ssh登陆localhost，执行下面的命令：
```
$ ssh-keygen -t dsa -P '' -f ~/.ssh/id_dsa 
$ cat ~/.ssh/id_dsa.pub >> ~/.ssh/authorized_keys
```
至此免密码ssh登陆localhost配置完成

```
$ scp ~/.ssh/id_dsa.pub root@219.224.135.47:~/.ssh/authorized_keys
$ scp ~/.ssh/id_dsa.pub root@219.224.135.48:~/.ssh/authorized_keys
$ scp ~/.ssh/id_dsa.pub root@219.224.135.60:~/.ssh/authorized_keys
```
至此master到各个slave的免密码ssh登陆配置完成

2.配置mesos

统一安装位置：/home/spark/
参见http://mesos.apache.org/gettingstarted/
尽量使用Apache官网下载方案，git版本不稳定

mesos启动后可通过219.224.135.46:5050查看Web UI界面

二、Spark配置

1.获取spark

可直接从46服务器上获取spark编译包
```
$ cd /home/spark
$ scp -r spark-1.0.1-bin-hadoop1 root@219.224.135.47:/home/spark/
$ scp -r spark-1.0.1-bin-hadoop1 root@219.224.135.48:/home/spark/
$ scp -r spark-1.0.1-bin-hadoop1 root@219.224.135.60:/home/spark/
```
注意，修改spark包中的代码时只需在46服务器上修改，之后将修改后的代码分发到另外3台服务器上，保持代码的一致性。

2.配置spark运行模式

参考http://spark.apache.org/docs/latest/cluster-overview.html

注意配置Mesos模式时，在conf/spark-env.sh中

```
MESOS_NATIVE_LIBRARY=/usr/local/lib/libmesos.so
```

3.配置pyspark包
```
$ cd /home/spark/spark-1.0.1-bin-hadoop1/python
$ scp -r pyspark /usr/lib/python2.7/
```
4.配置环境变量

```
$ vim /etc/environment
```
添加以下内容
```
SPARK_HOME=/home/spark/spark-1.0.1-bin-hadoop1
```
执行以下命令，重新登陆服务器后，修改生效
```
$ source /etc/environment
```


